Welcome to BounCA - Your Own Chain of Trust
=======

[![Code Health](https://landscape.io/github/repleo/bounca/master/landscape.svg?style=flat-square)](https://landscape.io/github/repleo/bounca/master)

Purpose
-----------
BounCA is a tool to manage your personal SSL certificates and authorities in a central and easy to use interfaces. It provides an easy accessible web interface to the OpenSSL command line tool and an administration tool for all your signed certificates and revocation lists. Create and manage your own X.509 / PKI key and certificate trust infrastructure in a couple of seconds.

Why your own Certificate Authority
----------------------------------------------

Use cases:

* Secure your internal REST micro-services and API's
* Client-certificate based login for web-services
* Secure access to your internal cloud services with your own HTTPS scheme
* Automatic client-certificate generation via API for Internet of Things (IoT) devices

Advantages:

* No single point of failure: Decoupled en decentralized authorization management 
* You are in control of your complete trust chain: Spoofing nearly impossible as no third party is involved
* Razor fast authentication: SSL off-loading can be performed by your webservers

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
* Use the PKI without webinterface from the command line

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