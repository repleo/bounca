Getting Started
===============

This document will show you how to get up and running with BounCA.
You can start creating your root authorities and singing your certificates in 10 minutes, depending on the configuration you use.


Prepare your Environment
------------------------

BounCA is a `Django`_ application running on a `Python3`_ environment. 
While it is highly portable setup, we suggest you deploy a (virtual) machine with the following configuration:
* Debian Jessie Linux
* Key authentication for the Root user

We offer three ways to install BounCA. 

* :ref:`deploy-ansible`
* :ref:`deploy-docker`
* :ref:`deploy-bare-hand`

.. _deploy-ansible:

Ansible Deployment
~~~~~~~~~~~~~~~~~~


`Ansible`_ offers the easiest way of creating a BounCA deployment for hosting your Certificate Authority.

You need to have (root) access to a fresh installed Debian Jessie (virtual) machine. On your local machine you need to have a recent 2+ Ansible installation.
Create your playbook ``install-bounca.yml``:

.. code-block:: yaml

   - hosts: all
     remote_user: root
     roles:
       - { role: repleo.bounca,
            bounca_timezone: /usr/share/zoneinfo/Europe/Amsterdam,
            bounca_db_user: bounca,
            bounca_db_password: <YOUR DB PASSWORD>,
            bounca_db_host: localhost,
            bounca_db_name: bouncadb,
   
            bounca_secret_key: <DJANGO SECRET>,
            bounca_email_host: localhost,
            bounca_admin_mail: bounca-admin@<YOURDOMAIN>,
            bounca_from_mail: no-reply@<YOURDOMAIN>
       }
       

Ansible will install the database, webserver and so on. The parameters you provide in the playbook are used to instantiate the services.
After you created the playbook, you can install BounCA by executing the following commands:

.. code-block:: shell

   ansible-galaxy install repleo.bounca -p ./roles
   ansible-playbook install-bounca.yml -i <HOSTNAME_OR_IP>,

The first collects the ansible roles from Ansible's galaxy.
The second command installs the actual BounCA system.

.. note:: Don't forget the trailing comma in the -i argument list.


.. _deploy-docker:

Docker Deployment
~~~~~~~~~~~~~~~~~

If you want to try BounCA or you want to create a couple of self-signed certificates without having a persistent CA, the `Docker`_ deployment is the fastest way of getting BounCA.
Docker offers the ability to run BounCA as an application on your local machine by running a single command.

Make sure you have installed `Docker`_ including ``docker-compose`` and ``docker-machine``.
Clone the BounCA docker release script from the github repo: https://github.com/repleo/docker-compose-bounca.
The only prerequisite is a working Docker installation.

Create your BounCA installation with the following one-liner:

.. code-block:: shell
   
   # Cool one-liner

.. warning:: The Docker installation is not meant for a persistent certificate authority. Use this installer for trying BounCA or to generate a couple of self-signed certificates.

.. _deploy-bare-hand:

Manual Install
~~~~~~~~~~~~~~

In case you want to customize the installation of BounCA, you can install it manually.
BounCA requires the following installed and configured packages:

- nginx
- uwsg
- postgresql-9.4
- python-3.4
- virtualenv-3.4

Download BounCA from `github`_ and unpack it in your web application directory, for example ``/srv/www/``.

Go to the root of your installation and create a virtual environment and install the python packages ``pip3.4 -r requirements.txt``.

Create a database and database user in postgresql.

Create the BounCA configuration file ``/etc/bounca/main.ini`` for the machine specific configuration.
It should contain the following parameters:

.. code-block:: cfg

   [database]
   DATABASE_USER: <value>
   DATABASE_PASSWORD: <value>
   DATABASE_HOST: <value>
   DATABASE_NAME: <value>
   
   [secrets]
   SECRET_KEY: <value-django-secret-just-a-random-salt-string>
   
   [email]
   EMAIL_HOST: <value>
   ADMIN_MAIL: <value>
   FROM_MAIL: <value>
   
Replace the ``<value>`` placeholder with the right values for your installation

Next step is to collect the static files: ``python3 manage.py collectstatic --noinput``
and create the database: ``python3 manage.py migrate --noinput``

The last step is to configure uWSGI and NGINX.
The uWSGI config might look like the following example:

.. code-block:: cfg
   
   [uwsgi]
   thread=4
   master=1
   processes=80
   vacuum=true
   uid = www-data
   gid = www-data
   chmod-socket = 700
   chown-socket = www-data
   socket = /run/uwsgi/app/bounca/socket
   logto = /var/log/uwsgi/bounca/log
   chdir = /srv/www/bounca
   home  = /srv/www/bounca/env
   module = bounca.wsgi

The NGINX config should contain a proxypass on the root and a location for the static files. For example the following server block

.. code-block:: cfg
   
   server {
   
       listen 80;
       server_name example.org;
       charset utf-8;
   
       location /static {
           root /srv/www/bounca/media;
           include mime.types;
       }
   
       location / {
           include uwsgi_params;
           uwsgi_read_timeout 9600;
           uwsgi_send_timeout 9600;
           uwsgi_pass unix://run/uwsgi/app/bounca/socket;
       }
   
   }

You should restart uWSGI and NGINX to load the changes. 
BounCA should be up and running.


Post Installation
-----------------

When the installation is finished, you can reach your BounCA installation by browsing to your BounCA machine.
You will see a login screen, please create an account an login.
You are ready to create your Certificate Authorities!

.. note:: While BounCA has a login feature for internal use, your keys are protected by passphrases.
          Passphrases are not stored in BounCA, so please remember them well as they cannot be recovered from your keys.
          
.. _https://github.com/repleo/docker-compose-bounca: https://github.com/repleo/docker-compose-bounca
.. _github: https://www.github.com/repleo/bounca
.. _Python3: https://www.python.org/
.. _Debian: https://www.debian.org/
.. _Django: https://www.djangoproject.com
.. _Ansible: http://www.ansible.com/
.. _Docker: http://www.docker.com/
