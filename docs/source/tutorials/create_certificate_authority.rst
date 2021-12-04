
:header_title: Set-up Root Certificate Authority
:header_subtitle: Step-by-step guide how to generate a basic root certificate authority.



Create Root Certificate Authority
=================================

This document will show you how to set up a root certificate authority with BounCA.
We assume you have just installed BounCA, created an account, and are logged in on the desktop.

---------------------------------

Generate Root Certificate
~~~~~~~~~~~~~~~~~~~~~~~~~

Your certificate authority (CA) starts with creating a root certificate.
The root certificate is a self-signed certificate at the top of your chain-of-trust.
A key and certificate are generated when you create the root certificate.
The user interface of BounCA let you only download the certificate. The key is internally used
for signing the child certificates.
The root certificate should be distributed to all hosts which need to trust your certificates.

The root certificate does not sign server or client certificates directly.
One or more intermediate certificate authorities, which are trusted by the root CA to sign certificates on their behalf, must be created.
This allows to keep the root key offline and unused as much as possible, as any compromise of the root key makes your authority useless.

When you login to your fresh BounCA, you will enter the overview tab.
Click on the 'Root Certificate' tab at the left side.

.. figure:: ../images/generate-server-certificate/1-empty-root-dashboard.png
    :width: 800px
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

.. figure:: ../images/generate-server-certificate/2-create-root-certificate.png
    :width: 800px
    :align: center
    :alt: Create root certificate
    :figclass: align-center

    Create root certificate

You will see the passphrases when you scroll down. Create a passphrase for accessing your key. Remember your passphrase or store it in a safe.

BounCA offers Ed25519 and RSA based key algorithms.
Ed25519 is a a modern, fast and safe key algorithm, however not supported by all operating systems, like MacOS.
The RSA-algorithm is the default configuration of BounCA. Root and intermediate keys are 4096 bits, client and server certificates
use 2048 bits keys.

.. figure:: ../images/generate-server-certificate/4-root-certificate-generated.png
    :width: 800px
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


.. figure:: ../images/generate-server-certificate/5-inspect-root-certificate.png
    :width: 800px
    :align: center
    :alt: Inspect root certificate
    :figclass: align-center

    Inspect root certificate

And you can check if the OCSP and/or CRL links are available in the X.509v3 fields of the certificate.
The output also shows the applied *X509v3 extensions*.

.. figure:: ../images/generate-server-certificate/6-inspect-root-certificate-revoke-crl.png
    :width: 800px
    :align: center
    :alt: Inspect revocation services CRL and OCSP links in certificate
    :figclass: align-center

    Inspect revocation services CRL uri in certificate

Install your root certificate authority
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Download the root certificate PEM by clicking on the down-arrow button.
Your operating system will trust all the child certificates of your root authority when
you add the PEM file to your trust library of your operating system.
We show here how to add the root certificate to MacOS, other operating systems are discussed in :ref:`install_root_certificates`.

MacOS
````````

Download the root certificate from the BounCA interface and double click on the downloaded PEM.
The key manager program will start and it will show you the certificate.
Check the validity of the certificate.


.. figure:: ../images/generate-server-certificate/20-install-root-pem-certificate.png
    :width: 800px
    :align: center
    :alt: Install root CA pem file MacOS
    :figclass: align-center

    Install root CA pem file on MacOS



.. figure:: ../images/generate-server-certificate/21-validate-root-ca-pem.png
    :height: 500px
    :align: center
    :alt: Validate root CA pem on MacOS
    :figclass: align-center

    Validate root CA PEM on MacOS

In case you trust the certificate you can add it to your operating system. Add it on system level, MacOS will ask for your administrator password.
When you have added the certificate to your trust chain, MacOS will trust the root CA's signed certificates.


.. figure:: ../images/generate-server-certificate/22-add-root-ca-pem.png
    :height: 350px
    :align: center
    :alt: Add root CA pem to MacOS
    :figclass: align-center

    Add root CA PEM to MacOS

Enter your administator password.

.. figure:: ../images/generate-server-certificate/23-enter-password.png
    :height: 350px
    :align: center
    :alt: Enter administrator password
    :figclass: align-center

    Enter your administrator password

Add the root authority pem as trusted root certificate to your system.

.. figure:: ../images/generate-server-certificate/24-trust-self-signed-root-ca-pem.png
    :height: 500px
    :align: center
    :alt: Trust added root authority pem
    :figclass: align-center

    Trust added root authority PEM

Enable system-wide trust of your root certificate

.. figure:: ../images/generate-server-certificate/25-trust-rules-enabled.png
    :height: 500px
    :align: center
    :alt: Trust rules enabled
    :figclass: align-center

    Trust rules enabled

Re-open the root PEM certificate in the key manager. You will notice it is now trusted by MacOS.

.. figure:: ../images/generate-server-certificate/26-root-ca-is-trusted.png
    :height: 500px
    :align: center
    :alt: Verify root CA has been trusted
    :figclass: align-center

    Verify root CA has been trusted


Generate the intermediate certificate authority
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An intermediate certificate authority (CA) is an entity that can sign certificates on behalf of the root CA.
The root CA signs the intermediate certificate, forming a chain of trust.

The purpose of using an intermediate CA is primarily for security.
The root key can be kept offline and used as infrequently as possible.
If the intermediate key is compromised, the root CA can revoke the intermediate certificate and create a new intermediate cryptographic pair.

Enter the root CA view in BounCA by clicking on the blue ``edit`` button or by clicking on the shortname of the root certificate.
You will enter a screen with an empty table.

.. figure:: ../images/generate-server-certificate/7-enter-root-ca.png
    :width: 800px
    :align: center
    :alt: Use root certificate as context
    :figclass: align-center

    Use root certificate as context

Click on the yellow add intermediate root certificate button. You will get a form where you can fill in the details of your intermediate CA.
Give the intermediate CA a common name which distinguish from the root certificate.
You will not be able to edit all the fields, as they must be the same as of your root authority.

The intermediate certificate should be valid for a shorter period than the root certificate.
Ten years would be reasonable.

.. figure:: ../images/generate-server-certificate/8-generate-intermediate-certificate.png
    :width: 800px
    :align: center
    :alt: Generate intermediate certificate authority
    :figclass: align-center

    Generate intermediate certificate authority

Enter the passphrase of the root certificate to be able to sign the intermediate certificate and enter the passphrase of the certificate self.
Use again a strong passphrase to protect your intermediate certificate.

.. figure:: ../images/generate-server-certificate/9-generate-intermediate-certificate-enter-passphrases.png
    :width: 800px
    :align: center
    :alt: Enter passphrases for generating intermediate certificate
    :figclass: align-center

    Enter passphrases for generating intermediate certificate

The intermediate certificate will be generated and you can inspect its subject by clicking on the ``info`` button.

.. figure:: ../images/generate-server-certificate/10-inspect-intermediate-certificate.png
    :width: 800px
    :align: center
    :alt: Inspect intermediate certificate authority
    :figclass: align-center

    Inspect intermediate certificate authority

The CRL and OCSP urls are automatically assigned to the same as the root certificate, and in case of the CRL url, it refers to the name of your intermediate authority.

.. figure:: ../images/generate-server-certificate/11-inspect-intermediate-certificate-crl-ocsp.png
    :width: 800px
    :align: center
    :alt: Inspect CRL and OCSP links of intermediate certificate
    :figclass: align-center

    Inspect CRL and OCSP links of intermediate certificat

This guide has shown you how to setup a root certificate authority with BounCA and how to generate an intermediate certificate.
You can now generate server and client certificates to enable encrypted HTTPS connections and client authorisation.


