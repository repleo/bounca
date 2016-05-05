Welcome to BounCA - Key management made easy
=======

Purpose
-----------
Bounce aims for a central, easy to use interface for managing all your certificates. It provides an accessible interface to the difficult OpenSSL command line tool and an administration tool for all signed certificates and revocation lists. BounCA is a web interface for creating and managing your X.509 / PKI key and certificate infrastructure and provides an easy interface for creating signing requests (CSRs) for popular trust networks like StartSSL and Comodo. 

Installation
--------------
BounCA is Django / Python3 based, and can be best installed in its own linux environment. Easiest way is to use a virtual machine to deploy the application. Note that it is best practice to create the root pair in a secure environment. Ideally, this should be on a fully encrypted, air gapped computer that is permanently isolated from the Internet. 


Currently there is no formal installation procedure so just copy pyfling.py
to whatever directory you wish to use it in.

Requirements
------------------
Modern Linux Environment supporting Python 3.4+ and Django 1.9+. The application is hosted using NGINX and UWSGi.

License
------------------

Apache License v2 - (c) 2016, Repleo, Amstelveen

Author Information
------------------

Repleo, Amstelveen, Holland -- www.repleo.nl  
Jeroen Arnoldus (jeroen@repleo.nl)