<a href="https://bounca.org/">
    <img src="https://www.bounca.org/_images/BounCA-logo.png" alt="BounCA logo" title="BounCA" align="right" height="60" />
</a>

Welcome to BounCA - Your Own Chain of Trust
==============


[![Code Health](https://landscape.io/github/repleo/bounca/master/landscape.svg?style=flat-square)](https://landscape.io/github/repleo/bounca/master)
[![Build Status](https://travis-ci.org/repleo/ansible-role-bounca.svg?branch=master)](https://travis-ci.org/repleo/ansible-role-bounca)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/d510fe80ef94442f96d071e31f5cdce8)](https://www.codacy.com/app/jeroen/bounca?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=repleo/bounca&amp;utm_campaign=Badge_Grade)

**BounCA** is a tool to manage your personal SSL certificates and authorities in a central and easy to use interfaces. It provides an easy accessible web interface to manage your openssl based **root authority** without the hassle of knowing all the arguments of the command line tools. BounCA is also an administration tool for all your signed certificates and revocation lists. Create and manage your own X.509 / PKI key and certificate trust infrastructure in a couple of minutes.


[![BounCA](https://www.bounca.org/_images/ssl_dashboard_bounca.png)](https://www.bounca.org)



Your Own Certificate Authority
----------------------------------------------

Use cases:

* Trusted encrypted communication with your peers (man-in-the-middle attack prevention)
* Secure your internal REST micro-services and internal API's
* Client-certificate based login for web services, web applications and OpenVPN connections
* Secure access to your private cloud services with your own HTTPS scheme
* Secure your Internet of Things (IoT) network with your certificates and provision them via the BounCA API

Advantages:

* No single point of failure: Decoupled en decentralized authorization management 
* You are in control of your complete trust chain: Spoofing nearly impossible as no third party is involved
* Rocket fast authentication: SSL off-loading can be performed by your webservers

Main Features
--------------

* Create and manage your own root certificates and certificate authorities
* Create intermediate certificates for grouping of certificates
* Create server side certificates for setting up trusted and encrypted connections
* Create client side certificates for authentication and authorization
* Support for advanced v3 certificates containing subject alt names
* Revoke certificates within one mouse click and download Certificate Revoke Lists (CRL)
* Download certificates, keys, and keystore packages for your webserver and installation
* Keep track of validity of your certificates via ics / iCal calendar export containing expiration dates
* Protect your certificates via passphrases
* Evaluate your certificates via the info button
* Use the PKI without web interface from the command line

Installation
--------------

BounCA is a Django application running on a Python3 environment. 
While it is highly portable setup, we suggest you deploy a (virtual) machine with the following configuration:

* Debian Jessie Linux
* Key authentication for the Root user

Ansible offers the easiest way of creating a BounCA deployment for hosting your Certificate Authority.

You need to have (root) access to a fresh installed Debian Jessie (virtual) machine. On your local machine you need to have a recent 2+ Ansible installation.
Create your playbook ``install-bounca.yml``:

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

    ansible-galaxy install repleo.bounca -p ./roles
    ansible-playbook install-bounca.yml -i <HOSTNAME_OR_IP>,

The first collects the ansible roles from Ansible's galaxy.
The second command installs the actual BounCA system.
 
More installation options, such as docker and manual: [BounCA Installation Tutorials](https://www.bounca.org/getting-started.html)

Requirements
------------------
Modern Linux Environment, tested on Debian Jessie, supporting Python 3.4+, PostgreSQL 9.4+ and Django 1.9+. The application is hosted using NGINX and uWSGI.

Contributing
------------------

#### Bug Reports & Feature Requests

Please use the [issue tracker](https://github.com/repleo/bounca/issues) to report any bugs or file feature requests.

#### Contributing

1. Create an issue and describe your idea
2. [Fork it] (https://github.com/repleo/bounca/fork)
3. Create your feature branch (`git checkout -b my-new-feature`)
4. Commit your changes (`git commit -am 'Add some feature'`)
5. Publish the branch (`git push origin my-new-feature`)
6. Create a new Pull Request
7. Profit! :white_check_mark:

License
------------------

Apache License v2 - (c) 2016, Repleo, Amstelveen

Author Information
------------------

Jeroen Arnoldus (jeroen@repleo.nl)

Repleo, Amstelveen, Holland -- www.repleo.nl  


