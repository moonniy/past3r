import json
from os import path

import requests

from app.models import Paste, File
from past3r.settings import CACHE_DIR, WEB3_STORAGE_TOKEN, WEB3_STORAGE_URL


def write_files(directory, files, metadata):
    filenames = []
    filepath_metadata = path.join(directory, 'metadata.json')

    for file in files:
        filepath = path.join(directory, file['name'])
        with open(path.join(CACHE_DIR, filepath), 'w') as file_manager:
            file_manager.write(file['content'])
        filenames.append({'path': filepath, 'syntax': file.get('syntax', 'plaintext')})

    with open(path.join(CACHE_DIR, filepath_metadata), 'w') as file_manager:
        file_manager.write(json.dumps(metadata))

    return filenames, filepath_metadata


def upload_file(*args, **kwargs):
    _id = kwargs.get('_id')
    paste = Paste.objects.get(id=_id)
    file_id = kwargs.get('file_id')
    filename = kwargs.get('filename')

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {WEB3_STORAGE_TOKEN}'
    }

    file = File.objects.get(id=file_id, paste=paste)
    with open(path.join(CACHE_DIR, file.path), 'rb') as f:
        response = requests.request("POST", f"{WEB3_STORAGE_URL}/upload", headers=headers, data=f)
        file.cid = response.json().get("cid")
        file.save()

        push = File.objects.filter(id=file_id, cid='').count() == 0
        metadata = update_metadata(paste, paste.manifest_path, file.file_name, file.cid, 'files', push=push)

        print(f'## DONE: {metadata}')
        print(f'== DONE: {file.path} - {file.cid}')


def update_metadata(paste, filepath, field, value, type_field, push=False):
    abs_path = path.join(CACHE_DIR, filepath)
    with open(abs_path, 'r+') as f:
        metadata = json.loads(f.read())
        if type_field == 'files':
            metadata['files'][field]['cid'] = value
        f.seek(0)
        f.write(json.dumps(metadata))
        f.truncate()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {WEB3_STORAGE_TOKEN}'
    }

    if push:
        with open(abs_path, 'rb') as f:
            response = requests.request("POST", f"{WEB3_STORAGE_URL}/upload", headers=headers, data=f)
            paste.manifest_cid = response.json().get("cid")

            paste.save()
            return paste.manifest_cid
    return 'No update metadata'