## Install instructions

TODO UPDATEN
===================

Create Python3 virtualenv, activate, and install `requirements.txt`.

```bash
virtualenv env -p python3.6
. env/bin/activate
pip install -r requirements.txt
pip install -r requirements.docs.txt  # for local debugging
```

# BounCA

## Local

Python setup, for mac and linux no additional actions

### Database
Install Postgres version 12 and postgresql-server-dev-12:
`sudo apt-get install postgresql-12 postgresql-server-dev-12`

Create user and database for Postgres
```
sudo su - postgres
createuser bounca
createdb --owner=bounca bounca --encoding=UTF8 --template=template0
psql -c 'alter user bounca with createdb' postgres  # this is needed for automated tests
```

Optionally, set a password for the `bounca` user.

## Installation

Create Python 3.7 virtualenv, activate, and install requirements.txt
`virtualenv env -p python3.7 && . env/bin/activate && pip install -r requirements.txt`

Configure frontend base URI

python3 manage.py site http://localhost:8080
python3 manage.py collectstatic
python3 manage.py createsuperuser


Extra requirements:

openssl

# Notes:
Protect your data, Protect your communication,
Protect your Business, get it BounCA!
