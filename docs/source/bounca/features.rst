BounCA features
===============

This will serve as a list of all of the features that BounCA currently has. 
Some features are important enough to have their own page in the docs, others will simply be listed here.

Create and manage your own root certificates and certificate authorities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

BounCA offers an easy interface to generate and manage a complete Certificate Authority.
Never hassle again with complex command line tools, just create, inspect and distribute certificates from an easy to use web interface.

Create intermediate certificates for grouping of certificates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Having multiple intermediate certificates enables authorization on group level.
Create certificates for different level of grants.

Create server side certificates for setting up trusted and encrypted connections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create server side certificates for encrypted trusted connections.
Typical use cases are:
- Internal trust network in your Intranet
- Trusted peer network with reduced risk of man-in-the-middle attack
- Trusted private cloud services over Internet

Create client side certificates for authentication and authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create client certificates for authorize clients and users via certificates. 
Typical use cases are:
- Provisioning of API access of Internet of Things devices
- OpenVPN user authentication
- Internal web application authentication
- E-mail signing

Support for advanced v3 certificates containing subject alt names
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generate client and server certificates with subject alt names for supporting multiple accounts or domains.

Revoke certificates within one mouse click and download Certificate Revoke Lists (CRL)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Easily revoke a certificate from the dashboard by pressing the revoke button. 
Download the CRL file for hosting it.


Download certificates, keys, and keystore packages for your webserver and installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Download a zip containing all the important certificate and key files for configuring your webservers (Apache, nginx), OpenVPN and other services.
The package also contains a prepackages pkcs12 file with the keys and certificates.

Keep track of validity of your certificates via ics / iCal calendar export containing expiration dates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can create an iCal, ics file containing the expiration dates of your certificates. 
Import the file in your calendar and be warned on time when a certificate expires.


Protect your certificates via passphrases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All keys in BounCA are protected by passphrases. It is only allowed to have client and server certificates without passphrase.
BounCA takes care that your passphrases are strong enough, and checks if your passphrase is correct before signign a ``csr``.

.. note:: BounCA does not store passphrases. Please keep your passphrases in a secret place as you cannot restore a passphrase.

Evaluate your certificates via the info button
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every certificate can be inspected by pressing the ``I`` info button. 
This button call OpenSSL and shows you the info text of the particular certificate.

Use the PKI without webinterface from the command line
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The keys, certificates and other files belonging to your certificate authority are stored in an easy exportable folder structure including shell scripts to generate certificates.
You may generate a base PKI from BounCA and copy the files to manage your CA elsewhere. 

.. warning:: If you generate certificates from the command line you cannot use BounCA to manage that CA as the database will not be in sync with your PKI.

