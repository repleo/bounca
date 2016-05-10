Welcome to BounCA - Your Own Chain of Trust
=======

Purpose
-----------
Bounce aims for a central, easy to use interface for managing all your certificates. It provides an easy accessible interface to OpenSSL command line tool and an administration tool for all your signed certificates and revocation lists. BounCA is a web interface for creating and managing your X.509 / PKI key and certificate trust infrastructure and provides an easy interface for creating signing requests (CSRs) for popular trust networks like StartSSL and Comodo. 

Why your own Certificate Authority
----------------------------------------------

Use cases:

* Secure your internal REST micro-services and API's
* Client-certificate based login for web-services
* Secure access to your internal cloud services with your own HTTPS scheme

Advantages:

* No single point of failure: Decoupled en decentralized authorization management 
* You are in control of your complete trust chain: Spoofing nearly impossible as no third party is involved
* Razor fast: SSL offloading can be performed in your webservers




Installation
--------------
BounCA is Django / Python3 based, and can be best installed in its own linux environment. Easiest way is to use a virtual machine to deploy the application. Note that it is best practice to create the root pair in a secure environment. Ideally, this should be on a fully encrypted, air gapped computer that is permanently isolated from the Internet. 

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