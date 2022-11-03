import os
import shutil

from celery import shared_task
import requests


from past3r.settings import WEB3_STORAGE_URL, WEB3_STORAGE_TOKEN, CACHE_DIR


@shared_task
def upload_zip(*args, **kwargs):
    _id = kwargs.get('_id')
    filename = kwargs.get('filename')
    paste = Paste.objects.get(id=_id)
    repo_path = os.path.join(CACHE_DIR, paste.uuid)

    current_path = os.getcwd()
    os.chdir(CACHE_DIR)
    shutil.make_archive(paste.uuid, 'zip', repo_path)
    os.chdir(current_path)

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {WEB3_STORAGE_TOKEN}'
    }

    with open(f'{repo_path}.zip', 'rb') as f:
        response = requests.request("POST", f"{WEB3_STORAGE_URL}/upload", headers=headers, data=f)
        paste.cid = response.json().get("cid")
        paste.save()
        print(f'== DONE: {paste.cid}')