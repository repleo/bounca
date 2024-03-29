:header_title: Get started
:header_subtitle: An overview of BounCA, how to download and use, basic examples, and more.

.. _getting_started:


Install BounCA
===============

This guide shows how you can install BounCA on your platform.
Hosting BounCA yourself is the safest option for keeping your keys secret. Even
better to not connect you BounCA installation to the Internet.
If you just want to generate some certificates, but don't consider a high level
of safety, you can use our `Bounca Cloud`_.

---------------

Prepare your Environment
------------------------

BounCA is a `Django`_ application running on a `Python3`_ environment.
We suggest you deploy a (virtual) machine with the following configuration:

 - Debian Bullseye 11 Linux
 - SSH access via key authentication, and ``sudo`` for the Root user

Ofcourse other distributions will work, but we have not tested it.

.. _deploy-manual:


Server prerequisites
~~~~~~~~~~~~~~~~~~~~


On a fresh Debian 11 machine, first update your repositories:
``sudo apt update``

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

.. code-block:: none

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


Create database
~~~~~~~~~~~~~~~

Create user and database for Postgres

.. code-block:: none

    sudo su - postgres
    createuser bounca
    createdb --owner=bounca bounca --encoding=UTF8 --template=template0
    psql -c "ALTER USER bounca WITH createdb" postgres


Optionally, set a password for the ``bounca`` user.

.. code-block:: none

    psql -c "ALTER USER bounca PASSWORD '<your password>'"


Don't forget to go back to your normal user, for example by using the command ``exit``.

Create directories
~~~~~~~~~~~~~~~~~~

Create directory for logging:

.. code-block:: none

    mkdir /var/log/bounca
    chown -R www-data:www-data /var/log/bounca
    mkdir -p /srv/www/


Download BounCA
~~~~~~~~~~~~~~~

Get the newest BounCA release from our `gitlab package repository`_.
Unpack it to a location where your web app will be stored, like ``/srv/www/``.
Make sure the directory is owned by the nginx user:

.. code-block:: none

    cd /srv/www/
    tar -xvzf bounca-<version>.tar.gz
    chown www-data:www-data -R /srv/www/bounca

Configuration
~~~~~~~~~~~~~

To run BounCA you need to configure nginx, uwsgi and BounCA.
First copy the files:

.. code-block:: none

    cp /srv/www/bounca/etc/nginx/bounca /etc/nginx/sites-available/bounca
    ln -s /etc/nginx/sites-available/bounca /etc/nginx/sites-enabled/bounca

    cp /srv/www/bounca/etc/uwsgi/bounca.ini /etc/uwsgi/apps-available/bounca.ini
    ln -s /etc/uwsgi/apps-available/bounca.ini /etc/uwsgi/apps-enabled/bounca.ini

    mkdir /etc/bounca
    cp /srv/www/bounca/etc/bounca/services.yaml.example /etc/bounca/services.yaml


You need to change the files ``/etc/bounca/services.yaml`` and ``/etc/nginx/sites-available/bounca`` for your situation.
The values for the database must be changed in ``/etc/bounca/services.yaml``, and you need to add a ``secret_key`` in the django section,
and add your host name to the  ``hosts`` section.
The NGINX configuration file has a default config for non-ssl, in case you need https, change the file accordingly.

Install virtualenv and python packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create the virtualenv and install python dependencies:

.. code-block:: none

    cd /srv/www/bounca
    virtualenv env -p python3
    source env/bin/activate
    pip install -r requirements.txt

Setup BounCA app and initialize database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following commands will initialize the database, initialize the folder with
static files. Also the fully qualified hostname must be configured, without protocol prefix.
Optionally, create a super user for the admin interface.

.. code-block:: none

    cd /srv/www/bounca
    source env/bin/activate
    python3 manage.py migrate
    python3 manage.py collectstatic
    python3 manage.py site <fully qualified hostname>


In case the commands give you a db connection error, make sure you start the database:

.. code-block:: none

    service postgresql start

Check permissions
~~~~~~~~~~~~~~~~~~~~~~~~

Check the permissions of ``/var/log/bounca``. The uwsgi user, in case of debian www-data, should have
write permissions.
In case you face the error ``` no python application found, check your startup logs for errors ``` when
starting uwsgi, it is probably related to the permission of the log file, directory.

Starting the application
~~~~~~~~~~~~~~~~~~~~~~~~

Finally restart uwsgi and nginx.

.. code-block:: none

    service uwsgi restart
    service nging restart


Post Installation
-----------------

The admin interface can be found at:
``https://<your bounca url>/admin``.

To access the admin interface you need an super user account. You can also create the super user via a webform, or via the commandline.
You need to have enabled ``superuser_signup`` in your config file to enable the webform to create a super user. The signup form can be reached at
this URI: ``https://<your bounca url>/accounts/signup/``.

This create super user form will only be shown if no users exists. After the database is filled with users you can only create super users via the command line:

.. code-block:: none

    python manage.py createsuperuser --username myAdminUser --email myAdminEmail@example.com


(Optionally: Set DJANGO_SUPERUSER_PASSWORD Environment variable to set new passwords for ``python manage.py createsuperuser`` command, and execute with ``python manage.py createsuperuser --noinput --username myAdminUser --email myAdminEmail@example.com``)


BounCA should be up and running, you can reach your BounCA installation by browsing to your BounCA machine.
You will see a login screen, please create an account an login.
You are ready to create your Certificate Authorities!


Update BounCA
===============

To update BounCA you need to execute a couple of manual steps.

Backup old installation
~~~~~~~~~~~~~~~~~~~~~~~

First, backup your database:

.. code-block:: none

    su - postgres -c "pg_dumpall -f /tmp/dbexport.pgsql"


Make sure you move the file from the ``/tmp`` directory to a safe place.
The database will probably not very large, so zipping the file is not necessary,
You can also decide to backup the code by copying or compressing the bounca installation
folder.

Download BounCA
~~~~~~~~~~~~~~~

Remove the contents of ``/srv/www``.

.. code-block:: none

    rm /srv/www
    rm -rf ./bounca


Get the newest BounCA release from [the packages repo](https://gitlab.com/bounca/bounca/-/packages).
Unpack it to a location where your web app will be stored, like `/srv/www/`.
Make sure the directory is owned by the nginx user:

.. code-block:: none

    cd /srv/www/
    tar -xvzf bounca-<version>.tar.gz
    chown www-data:www-data -R /srv/www/bounca


### Install virtualenv and python packages

Create the virtualenv and install python dependencies:

.. code-block:: none

    cd /srv/www/bounca
    virtualenv env -p python3
    source env/bin/activate
    pip install -r requirements.txt


Setup BounCA app and migrate database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After installing the new BounCA version, you need to update the database, and
setup the static files. Execute the following commands:

.. code-block:: none

    cd /srv/www/bounca
    source env/bin/activate
    python3 manage.py migrate
    python3 manage.py collectstatic


Retarting the application
~~~~~~~~~~~~~~~~~~~~~~~~~

Finally restart uwsgi and nginx.

.. code-block:: none

    service uwsgi restart
    service nginx restart


.. note:: Your keys are protected by passphrases.
          These passphrases are not stored in BounCA, so please remember them as they cannot be recovered from your keys.

.. _Bounca Cloud: https://app.bounca.org
.. _gitlab: https://www.gitlab.com/bounca/bounca
.. _Python3: https://www.python.org/
.. _Debian: https://www.debian.org/
.. _Django: https://www.djangoproject.com
.. _BounCA source: https://gitlab.com/bounca/bounca/-/packages
.. _gitlab package repository: https://gitlab.com/bounca/bounca/-/packages

