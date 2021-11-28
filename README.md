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

BounCA is a python3 based application, with a javascript vuetify frontend, and
can be hosted on every platform capable of running python3 applications.
This tutorial describes how to deploy BounCA on a Debian 11 server.
Some commands needs the `root` permission level, prefix them with `sudo` if necessary.

## Server prerequisites

On a fresh Debian 11 machine, first update your repositories:
`sudo apt update`

install the following packages via apt:

  - gettext
  - nginx
  - python3
  - python3-dev
  - python3-setuptools
  - python-setuptools
  - python-is-python3
  - uwsgi
  - uwsgi-plugin-python3
  - virtualenv
  - python3-virtualenv
  - python3-pip
  - postgresql
  - postgresql-contrib

```
sudo apt install \
    gettext \
    nginx \
    python3 \
    python3-dev \
    python3-setuptools \
    python-setuptools \
    python-is-python3 \
    uwsgi \
    uwsgi-plugin-python3 \
    virtualenv \
    python3-virtualenv \
    python3-pip \
    postgresql \
    postgresql-contrib
```
# Create database

Create user and database for Postgres
```
sudo su - postgres
createuser bounca
createdb --owner=bounca bounca --encoding=UTF8 --template=template0
psql -c "ALTER USER bounca WITH createdb" postgres
```

Optionally, set a password for the `bounca` user.
```
psql -c "ALTER USER bounca PASSWORD '<your password>'"
```

Don't forget to go back to your normal user, for example by using the command `exit`.

## Create directories

Create directory for logging:
```
mkdir /var/log/bounca
chown -R www-data:www-data /var/log/bounca
mkdir -p /srv/www/
```

## Download BounCA

Get the newest BounCA release from [the packages repo](https://gitlab.com/bounca/bounca/-/packages).
Unpack it to a location where your web app will be stored, like `/srv/www/`.
Make sure the directory is owned by the nginx user:
```

cd /srv/www/
tar -xvzf bounca-<version>.tar.gz
chown www-data:www-data -R /srv/www/bounca
```

## Configuration

To run BounCA you need to configure nginx, uwsgi and BounCA.
First copy the files:

```
cp /srv/www/bounca/etc/nginx/bounca /etc/nginx/sites-available/bounca
ln -s /etc/nginx/sites-available/bounca /etc/nginx/sites-enabled/bounca

cp /srv/www/bounca/etc/uwsgi/bounca.ini /etc/uwsgi/apps-available/bounca.ini
ln -s /etc/uwsgi/apps-available/bounca.ini /etc/uwsgi/apps-enabled/bounca.ini

mkdir /etc/bounca
cp /srv/www/bounca/etc/bounca/services.yaml.example /etc/bounca/services.yaml
```

You need to change the files `/etc/bounca/services.yaml` and `/etc/nginx/sites-available/bounca` for your situation.

## Install virtualenv and python packages

Create the virtualenv and install python dependencies:

```
cd /srv/www/bounca
virtualenv env -p python3
source env/bin/activate
pip install -r requirements.txt
```

## Setup BounCA app en initialize database

The following commands will initialize the database, setup the folder with
static files. Also the fully qualified hostname must be configured, without protocol prefix.
Optionally, create a super user for the admin interface.

```
cd /srv/www/bounca
source env/bin/activate
python3 manage.py migrate
python3 manage.py collectstatic
python3 manage.py site <fully qualified hostname>

```

In case the commands give you a db connection error, make sure you start the database:

```
service postgresql start
```

## Fire the manage up

Finally restart uwsgi and nginx.
```
service uwsgi restart
service nging restart
```

BounCA should be up and running. Browse to the hostname of your BounCA machine.
Enjoy generating keys.

The admin interface can be found at:
[http://<example.com>/admin](http://example.com/admin).

