
:header_title: Set-up Root Certificate Authority
:header_subtitle: Step-by-step guide to generate a basic root certificate authority.
.. _create_root_certificate:



Create Root Certificate Authority
=================================

This document will show you how to set up a root certificate authority with BounCA.
We assume you have just installed BounCA, created an account, and are logged in on the desktop.

A certificate authority (CA) is a trust entity that signs digital certificates. These certificates are used to confirm the authenticity of a web request (HTTPS),
computer code (signed code), authentication (Client certificate), etc.
In the public domain, internationally trusted CA (eg, VeriSign, DigiCert, Letsencrypt) are used to sign a certificate for domains.

In the private domain it may make more sense to have your own CA. Especially when you dont want that a third party might intercept your trust chain, like in
securing an intranet domain, or for securing clients, like Internet of Things sensors, to allow them to authenticate to a server (eg, Apache, OpenVPN).



---------------------------------

Generate Root Certificate
~~~~~~~~~~~~~~~~~~~~~~~~~

Your certificate authority (CA) starts with creating a root certificate and key.
The root certificate is a self-signed certificate at the top of your chain-of-trust.
A key and certificate are generated when you create the root certificate.
The user interface of BounCA let you only download the certificate. The key is internally used
for signing the child certificates.
The root certificate should be distributed to all hosts which need to trust your certificates.

The root certificate does not sign server or client certificates directly.
One or more intermediate certificate authorities must be created. These intermediate certificates are trusted by the root CA and are used to sign server certificates and client certificates.
This allows to keep the root key offline and unused as much as possible, as any compromise of the root key makes your authority useless.

When you login to your fresh BounCA, you will enter the overview tab.
Click on the 'Root Certificate' tab at the left side.

.. figure:: ../images/generate-ca-certificates/1-empty-root-dashboard.png
    :width: 1000px
    :align: center
    :alt: Empty root dashboard
    :figclass: align-center

    Start screen of BounCA without a root authority

Click on the *New Certificate* button, a new modal view will appear.
Enter the details of your Root Certificate.
The common name is the name of authority. Make sure you enter all information correctly, as you cannot edit it afterwards.
If you want to use revocation services, you can provide the OCSP and CRL urls. Leave them out if you don't want to use them.
CRL is supported by BounCA, in case you wants to use OCSP, you need to host an OCSP responder.

Give the root certificate a long expiry date, for example twenty years.
Once the root certificate expires, all certificates signed by the CA become invalid.

.. figure:: ../images/generate-ca-certificates/2-create-root-certificate.png
    :width: 1000px
    :align: center
    :alt: Create root certificate
    :figclass: align-center

    Create root certificate 1/2

.. figure:: ../images/generate-ca-certificates/3-create-root-certificate-crl.png
    :width: 1000px
    :align: center
    :alt: Create root certificate
    :figclass: align-center

    Create root certificate 2/2

When you scroll down you can enter revocation services, internal name and passphrase. Create a passphrase for accessing your key. Remember your passphrase or store it in a safe.
The CRL and OSCP uri's are not added to the root certificate, but to all its children. It allows to revoke the intermediate certificates.
The name is not part of the certificate, but used to name the downloaded files, and for listing the certificate in the user interface.

BounCA offers Ed25519 and RSA based key algorithms.
Ed25519 is a a modern, fast and safe key algorithm, however not supported by all operating systems, like MacOS.
The RSA-algorithm is the default configuration of BounCA. Root and intermediate keys are 4096 bits, client and server certificates
use 2048 bits keys.

.. figure:: ../images/generate-ca-certificates/4-root-certificate-generated.png
    :width: 1000px
    :align: center
    :alt: Root certificate generated
    :figclass: align-center

    Root certificate for authority generated

You can check the subject and data of the certificate by clicking on the info button.

The output shows:

- the ``Signature Algorithm`` used
- the dates of certificate ``Validity``
- the ``Public-Key`` encryption algorithm
- the ``Issuer``, which is the entity that signed the certificate
- the ``Subject``, which refers to the certificate itself

The ``Issuer`` and ``Subject`` are identical as the certificate is self-signed.
Note that all root certificates are self-signed.


.. figure:: ../images/generate-ca-certificates/5-inspect-root-certificate.png
    :width: 1000px
    :align: center
    :alt: Inspect root certificate
    :figclass: align-center

    Inspect root certificate

You can scroll down to inspect the applied *X509v3 extensions*.

.. figure:: ../images/generate-ca-certificates/6-inspect-root-certificate-X.509v3-extensions.png
    :width: 1000px
    :align: center
    :alt: The applied X509v3 extensions
    :figclass: align-center

    The applied X509v3 extensions

Install your root certificate authority
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Download the root certificate PEM by clicking on the down-arrow button.
Your operating system will trust all the child certificates of your root authority when
you add the PEM file to your trust library of your operating system.
We show here how to add the root certificate to MacOS, other operating systems are discussed in :ref:`install_root_certificates`.

MacOS
````````

Download the root certificate from the BounCA interface and double click on the downloaded PEM.
The key manager program will start and it will show you the certificate. You might need to filter on the certificate common name to
find it in the list. Check the validity of the certificate.


.. figure:: ../images/generate-ca-certificates/20-listed-root-pem-certificate.png
    :width: 500px
    :align: center
    :alt: Install root CA pem file MacOS
    :figclass: align-center

    Install root CA pem file on MacOS

Right click on the certificate to inspect it.

.. figure:: ../images/generate-ca-certificates/21-inspect-root-pem-certificate.png
    :width: 500px
    :align: center
    :alt: Install root CA pem file MacOS
    :figclass: align-center

    Validate root CA PEM on MacOS

If everything is correct, you can trust the certificate as root authority. A dialog pops up to enter
your password.
MacOS will trust the root CA's signed certificates after you have added the certificate to your trust chain.


.. figure:: ../images/generate-ca-certificates/22-trust-root-ca-pem.png
    :height: 500px
    :align: center
    :alt: Add root CA pem to MacOS
    :figclass: align-center

    Trust your root certificate

Re-open the key manager, search for your root certificate. You will notice it is now trusted by MacOS.

.. figure:: ../images/generate-ca-certificates/24-trusted-self-signed-root-ca-pem.png
    :height: 500px
    :align: center
    :alt: Trust added root authority pem
    :figclass: align-center

    Trusted root certificate

If you inspect the certificate you see it is valid and trusted.

.. figure:: ../images/generate-ca-certificates/26-root-ca-is-trusted.png
    :height: 500px
    :align: center
    :alt: Verify root CA has been trusted
    :figclass: align-center

    Verify root CA has been trusted


Generate the intermediate certificate authority
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The intermediate certificate authority (CA) signs certificates on behalf of the root CA.
A root CA can sign multiple intermediate certificate, and each form a chain of trust.

The purpose of using an intermediate CA is primarily for security.
The root key can be kept offline and used as infrequently as possible.
If the intermediate key is compromised, the root CA can revoke the intermediate certificate and create a new intermediate cryptographic pair.

Enter the root CA view in BounCA by clicking on the name of the root certificate.
You will enter a screen with an empty table.

.. figure:: ../images/generate-ca-certificates/7-enter-root-ca.png
    :width: 1000px
    :align: center
    :alt: Use root certificate as context
    :figclass: align-center

    Use root certificate as context

Click on the ``new certificate`` certificate button. You will get a form where where you can fill in the details of your intermediate CA.
Give the intermediate CA a common name which distinguish from the root certificate.
The distinguished name is pre-filled with the values from the root certificate. You are not able to edit all the fields,
as these fields must have the same value as your root authority.

The intermediate certificate should be valid for a shorter period than the root certificate.
Ten years would be reasonable.

.. figure:: ../images/generate-ca-certificates/8-generate-intermediate-certificate.png
    :width: 1000px
    :align: center
    :alt: Generate intermediate certificate authority
    :figclass: align-center

    Generate intermediate certificate authority

You need to provide a passphrase to secure the intermediate certificate, and provide the passphrase of the root certificate.
The passphrase of the root certificate is used to sign the intermediate certificate.
Use again a strong passphrase to protect your intermediate certificate.

You can also provide a CRL uri and OCSP uri. These are used for the revocation of the server, and client certificates signed by the intermediate certificate.

.. figure:: ../images/generate-ca-certificates/9-generate-intermediate-certificate-enter-passphrases.png
    :width: 1000px
    :align: center
    :alt: Enter passphrases for generating intermediate certificate
    :figclass: align-center

    Enter passphrases for generating intermediate certificate

.. figure:: ../images/generate-ca-certificates/9-generated-intermediate-ca.png
    :width: 1000px
    :align: center
    :alt: The generated intermediate certificate
    :figclass: align-center

    The generated intermediate certificate

The intermediate certificate will be generated and you can inspect its subject by clicking on the ``i`` button.

.. figure:: ../images/generate-ca-certificates/10-inspect-intermediate-certificate.png
    :width: 1000px
    :align: center
    :alt: Inspect intermediate certificate authority
    :figclass: align-center

    Inspect intermediate certificate authority

The CRL and OCSP uris of the intermediate certificate are based on the values provided when generating the root certificate.

.. figure:: ../images/generate-ca-certificates/11-inspect-intermediate-certificate-crl-ocsp.png
    :width: 1000px
    :align: center
    :alt: Inspect CRL and OCSP links of intermediate certificate
    :figclass: align-center

    Inspect CRL and OCSP links of intermediate certificate

This guide has shown you how to setup a root certificate authority with BounCA and how to generate an intermediate certificate.
You can now generate server certificates (:ref:`create_server_certificates`) and client certificates (:ref:`create_client_certificates`) to enable encrypted HTTPS connections and client authorisation.


