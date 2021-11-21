BounCA PKI - Key Management
===========================

Protect your Data, Protect your Communication,
Protect your Business, BounCA!

# Introduction

BounCA let you setup a trusted encrypted communication network with your peers in a couple of minutes.
Create a PKI, sign and revoke server and client X.509 v3 SSL certificates.
With BounCA you can secure your web applications and OpenVPN connections without passwords,
and secure access to your private cloud services with your own HTTPS scheme.
Setting up a provisioning service for your Internet of Things devices was never so easy.

# Installation

## Server prerequisite

BounCA is a python3 based application, with an javascript vuetify frontend.
It can be hosted on every platform capable of running python3 applications.

## Dependencies
Extra requirements:

openssl
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

## Install instructions

Create Python3 virtualenv, activate, and install `requirements.txt`.

```bash
virtualenv env -p python3.6
. env/bin/activate
pip install -r requirements.txt
pip install -r requirements.docs.txt  # for local debugging
```

## Installation

Create Python 3.7 virtualenv, activate, and install requirements.txt
`virtualenv env -p python3.7 && . env/bin/activate && pip install -r requirements.txt`

Configure frontend base URI

python3 manage.py site http://localhost:8080
python3 manage.py collectstatic
python3 manage.py createsuperuser

## Local

Python setup, for mac and linux no additional actions






