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
Install Postgres version 9.4 and postgresql-server-dev-9.4:
`sudo apt-get install postgresql-9.4 postgresql-server-dev-9.4`

Create user and database for Postgres
```
sudo su - postgres
createuser bounca
createdb --owner=bounca bounca --encoding=UTF8 --template=template0
psql -c 'alter user bounca with createdb' postgres  # this is needed for automated tests
```

Optionally, set a password for the `bounca` user.

## Installation

Create Python 3.4 virtualenv, activate, and install requirements.txt
`virtualenv env -p python3.6 && . env/bin/activate && pip install -r requirements.txt`
