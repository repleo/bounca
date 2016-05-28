<a href="https://bounca.org/">
    <img src="https://www.bounca.org/img/BounCA-logo.png" alt="BounCA logo" title="BounCA" align="right" height="60" />
</a>

Welcome to BounCA - Your Own Chain of Trust
==============


[![Code Health](https://landscape.io/github/repleo/bounca/master/landscape.svg?style=flat-square)](https://landscape.io/github/repleo/bounca/master)


**BounCA** is a tool to manage your personal SSL certificates and authorities in a central and easy to use interfaces. It provides an easy accessible web interface to manage your **rout authority** with the OpenSSL command line tool and. Bounce is also an administration tool for all your signed certificates and revocation lists. Create and manage your own X.509 / PKI key and certificate trust infrastructure in a couple of minutes.


[![BounCA](https://www.bounca.org/img/bounca/ssl_dashboard_bounca.png)](https://www.bounca.org)



Your Own Certificate Authority
----------------------------------------------

Use cases:

* Secure your internal REST micro-services and internal API's
* Client-certificate based login for web-services
* Secure access to your internal cloud services with your own HTTPS scheme
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
BounCA is Django / Python3 based, and it is recommended to deploy BounCA to its own linux environment, like a virtual machine.. Note that it is best practice to create the root pair in a secure environment. Ideally, this should be on a fully encrypted, air gapped computer that is permanently isolated from the Internet. 

More info about the installation: [BounCA Installation Tutorials](https://www.bounca.org/getting-started.html)

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


