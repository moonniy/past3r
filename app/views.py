from os import path
import uuid

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

import requests
from git import Repo

from app.models import Paste, File
from past3r.settings import DOMAIN, CACHE_DIR, WEB3_STORAGE_TOKEN, WEB3_STORAGE_URL
from app.utils import write_files, upload_file
from past3r.tasks import upload_zip

@csrf_exempt
@api_view(['POST'])
@renderer_classes([JSONRenderer])
def create_paster(request):
    _id = uuid.uuid1().hex

    files = request.data.get('files')
    raw_metadata = request.data.get('metadata')

    repo_path = path.join(CACHE_DIR, _id)
    repo = Repo.init(repo_path)

    parent = raw_metadata.get('parent', None),
    parent_gist = None
    if parent:
        gist = Paste.objects.filter(path=parent)
        if gist.exists():
            parent_gist = gist.first()

    base_metadata = {
        'visibility': raw_metadata.get('visibility', 'public'),
        'parent': parent_gist,
        'description': raw_metadata.get('description', ''),
        'expiration': raw_metadata.get('expiration', 'never'),
        'categories': raw_metadata.get('categories', []),
        'user_address': raw_metadata.get('address', ''),
        'uuid': _id
    }
    params = base_metadata.copy()
    params['path'] = f'{_id}.zip'
    params['cid'] = ''

    new_paste = Paste.objects.create(**params)

    metadata = base_metadata.copy()
    metadata['package_path'] = f'{_id}.zip'
    metadata['cid_package'] = ''
    metadata['files'] = {file['name']: {'syntax': file['syntax'], 'cid': ''} for file in files}
    metadata['created'] = timezone.now().isoformat()
    # Write and commit files
    [filepaths, metadata_path] = write_files(_id, files, metadata)
    paths = [path.join(CACHE_DIR, filepath['path']) for filepath in filepaths]
    metadata_abs_path = path.join(CACHE_DIR, metadata_path)
    repo.index.add([metadata_abs_path] + paths)
    repo.index.commit('Initial revision')

    # Set manifest
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {WEB3_STORAGE_TOKEN}'
    }
    with open(metadata_abs_path, 'rb') as f:
        response = requests.request("POST", f"{WEB3_STORAGE_URL}/upload", headers=headers, data=f)
        new_paste.manifest_cid = response.json().get("cid")
        new_paste.manifest_path = metadata_path
        new_paste.save()

    for filepath in filepaths:
        filename = filepath['path'].split(f'{_id}/')[1]
        file = File.objects.create(path=filepath['path'], cid='', file_name=filename, paste=new_paste, syntax=filepath['syntax'])
        upload_file(_id=new_paste.id, file_id=file.id, filename=filename)

    upload_zip.delay(_id=new_paste.id, filename=f'{_id}.zip')

    return Response({
        'id': _id,
        'url': f'{DOMAIN}/p/{_id}',
        'gist': new_paste.get_default_dict()
    })


def new_paste(request):
    return render(request, 'new.html', context={
        'title': 'Create Paste'
    })