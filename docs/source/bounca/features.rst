:header_title: BounCA features


BounCA features
===============

This will serve as a list of all of the features that BounCA currently has.

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
- Trusted S/MIME e-mail signing

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


Protect your certificates via passphrases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All keys in BounCA are protected by passphrases. It is only allowed to have client and server certificates without passphrase.
BounCA takes care that your passphrases are strong enough, and checks if your passphrase is correct before singing a ``csr``.

.. note:: BounCA does not store passphrases. Please keep your passphrases in a secret place as you cannot restore a passphrase.

Evaluate your certificates via the info button
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every certificate can be inspected by pressing the ``I`` info button.
This button shows you the info text of the particular certificate.

Use the PKI without webinterface via the API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The BounCA backend offers an API to control the PKI. You can directly access the API to generate and access your certificates.
This enables automatic revoking, and provisioning of certificates.
