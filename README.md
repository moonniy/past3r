# Past3r

[Project demo](https://past3r.online)


The pastebin for the web3 era.

## Setup

Requires docker-compose installed before start.

1. Create virtual enviroment and install dependencies
```shell
$ python3 -m venv --prompt paster  .env
$ sudo apt install postgresql-server postgresql-server-dev-all redis
$ pip install -r requirements.txt
```
2. Run migrations and start the server
```shell
$ python manage.py migrate
$ python manage.py runserver
celery -A past3r worker -l INFO
```

## Flow 

### Create gist
![](/screenshots/new.png)

### Get a gist
All files are stored and downloaded from the skynet, no server is needed to access the files.
![](/screenshots/details.png)

### View all gists
![](/screenshots/list.png)

## LICENSE
See [LICENSE](/LICENSE)
