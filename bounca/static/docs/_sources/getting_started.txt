Getting Started
===============

This document will show you how to get up and running with BounCA.
You can start creating your root authorities and singing your certificates in 10 minutes, depending on the configuration you use.


Prepare your environment
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

.. code-block:: shell

   ansible-galaxy install repleo.bounca -p ./roles
   ansible-playbook install-bounca.yml -i <YOUR_BOUNCA_NAME>,





There is `a screencast`_ that will help you get started if you prefer.

Sphinx_ is a tool that makes it easy to create beautiful documentation.
Assuming you have Python_ already, `install Sphinx`_::

    $ pip install sphinx sphinx-autobuild

Create a directory inside your project to hold your docs::

    $ cd /path/to/project
    $ mkdir docs

Run ``sphinx-quickstart`` in there::

    $ cd docs
    $ sphinx-quickstart

This quick start will walk you through creating the basic configuration; in most cases, you
can just accept the defaults. When it's done, you'll have an ``index.rst``, a
``conf.py`` and some other files. Add these to revision control.

Now, edit your ``index.rst`` and add some information about your project.
Include as much detail as you like (refer to the reStructuredText_ syntax
or `this template`_ if you need help). Build them to see how they look::

    $ make html

.. note:: You can use ``sphinx-autobuild`` to auto-reload your docs. Run ``sphinx-autobuild . _build_html`` instead.

Edit your files and rebuild until you like what you see, then commit your changes and push to your public repository.
Once you have Sphinx documentation in a public repository, you can start using Read the Docs.

.. _deploy-docker:

Docker Deployment
~~~~~~~~~~~~~~~~~

If you want to try BounCA or you want to create a couple of certificates without having a persistent CA, the `Docker`_ deployment is the fastest way of getting BounCA.

The only prerequisite is a working Docker installation.

Create your BounCA installation with the following one-liner:

.. code-block:: shell
   
   # Cool one-liner

.. warning:: Don't use the Docker installation for a persistent certificate authority. 


Manual Install
~~~~~~~~~~~~~~

In case you want to customize the installation of BounCA, you can install it manually.
BounCA is a `Django`_ installation, and as long as Django 1.9 is available en openssl is available you would be able to install it.

BounCA needs one configuration file ``/etc/bounca/main.ini`` for machine specific configuration.

.. code-block:: cfg
   
   # Cool one-liner



Post Installation
-----------------

When the installation is finished, you can reach your BounCA installation by browsing to your BounCA machine.
You will see a login screen, please create an account an login.
You are ready to create your Certificate Authorities!

.. note:: While BounCA has a login feature, your keys are protected by passphrases.
          Passphrases are not stored in BounCA, so please remember them well as they cannot be recovered from your keys.
          

.. _Python3: https://www.python.org/
.. _Debian: https://www.debian.org/
.. _Django: https://www.djangoproject.com
.. _Ansible: http://www.ansible.com/
.. _Docker: http://www.docker.com/
