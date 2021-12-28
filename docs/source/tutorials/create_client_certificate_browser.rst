:header_title: Self-Signed Client Certificate
:header_subtitle: Step-by-step guide to generate and install a client authentication SSL certificate.
.. _create_client_certificates:

Create Client Certificate
=====================================

This document will show you can generate a client certificate with BounCA.
We assume you have a working BounCA and create a certificate authority, see :ref:`create_root_certificate`.

---------------------------------

Generate Client Certificate
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Client certificates can be used to authenticate HTTP sessions, automatic login to web applications, and to sign/encrypt e-mails.
Password credentials are not necessary when using client certificate. This is useful when authenticating or provisioning
Internet of Things devices to an API. The devices don not store user credentials, and all authentication is offloaded to the SSL layer. See :ref:`api_access_via_certificate` for a guide.
CRL or OCSP can be used to revoke access by revoking the certificate.
In case the common name and/or subject alternative names field contain an email-address. The mail client will be able to sign your e-mail messages, see :ref:`create_mail_certificate`.


Enter the dashboard of your intermediate CA which must sign your client certificate.

.. figure:: ../images/generate-client-certificate/12-enter-int-ca.png
    :width: 800px
    :align: center
    :alt: Step into intermediate certificate
    :figclass: align-center

    Step into intermediate certificate

Click on the *New Server Cert* button to add a new client certificate, and a form will be shown.
For client certificates, the *Common Name* is your user name, or e-mail address. For mail signing certificates, you also need to add the e-mail address to the SubjectAltNames.

.. figure:: ../images/generate-client-certificate/13-open-client-certificate-create-form.png
    :width: 800px
    :align: center
    :alt: Empty client certificate create form
    :figclass: align-center

    Empty client certificate create form

Fill in the data for your client certificate. We use the *Copy From Intermediate* button to fill in the base information.
Certificates are usually given a validity of one year, though a CA will typically give a few days extra for convenience.

.. figure:: ../images/generate-client-certificate/14-fill-in-the-data.png
    :width: 800px
    :align: center
    :alt: Fill in the data for demo1
    :figclass: align-center

    Fill in the data for demo1

.. figure:: ../images/generate-client-certificate/15-enter-the-passphrase.png
    :width: 800px
    :align: center
    :alt: Fill in the passphrase for demo1
    :figclass: align-center

    Fill in the passphrase for demo1

The passphrase of the demo1 certificate is set to *demo1Demo1*. The passphrase secures the certificate, and should be kept secret.

    .. note::

        The passphrase is necessary for Firefox. It is not possible to load unencrypted PCKCS12 blobs in Firefox.

For this tutorial we create a second client certificate, which we will revoke later on.

.. figure:: ../images/generate-client-certificate/16-create-a-second-client-certificate.png
    :width: 800px
    :align: center
    :alt: Create a second client certificate
    :figclass: align-center

    Create a second client certificate

.. figure:: ../images/generate-client-certificate/17-enter-passphrase-of-second-certificate.png
    :width: 800px
    :align: center
    :alt: Fill in the passphrase for demo1
    :figclass: align-center

    Fill in the passphrase for demo2

You have now two generated client certificates. Download both certificate zips, we need them later
to sign in to the webserver. It is not possible to download the zip after the demo2 client has
been revoked.

.. figure:: ../images/generate-client-certificate/18-overview-generated-certificates.png
    :width: 800px
    :align: center
    :alt: Overview generated certificates
    :figclass: align-center

    Overview generated certificates

Press the *delete* icon of the demo2 certificate. A popup will be shown asking for a passphrase.
You need to fill in the passphrase of the intermediate certificate.

.. figure:: ../images/generate-client-certificate/20-enter-passphrase-of-intermediate.png
    :width: 800px
    :align: center
    :alt: Enter passphrase of intermediate certificate
    :figclass: align-center

    Enter passphrase of intermediate certificate

.. figure:: ../images/generate-client-certificate/21-revoked-demo2-certificate.png
    :width: 800px
    :align: center
    :alt: Overview with revoked certificate
    :figclass: align-center

    Overview with revoked demo2 certificate

Go to the intermediate certificate. Click on the *CRL* button to download the CRL list. You need to copy it to your webserver hosting the crl file, or in our tutorial, we store it in the configuration of nginx.
You also need to download the intermediate certificate itself. This file will be used as chain to verify the client certificate.

.. figure:: ../images/generate-client-certificate/22-download-intermediate-chain-and-crl.png
    :width: 800px
    :align: center
    :alt: Download CRL file and intermediate chain pem
    :figclass: align-center

    Download CRL file and intermediate chain pem


TODO HIER GEBLEVEN
``openssl verify -CAfile rootca.pem -untrusted intermediate.pem demo1.pem``
``cat ../int.crl.pem intermediate.pem rootca.pem > crlchain.pem``
``openssl verify -extended_crl -verbose -CAfile crlchain.pem -crl_check demo1.crt``

``openssl crl -in ../int.crl.pem -text -noout``


You can copy the distinguished name information from the intermediate certificate by pressing the *Copy From Intermediate* button.

.. figure:: ../images/generate-client-certificate/13-copy-data-from-intermediate-certificate.png
    :width: 800px
    :align: center
    :alt: Copy DN from Intermediate
    :figclass: align-center

    Copy Distinguished Name from Intermediate

You can use the certificate for multiple domains and IP adresses using the SubjectAltNames fields of the X.509v3 extensions.

.. figure:: ../images/generate-client-certificate/14-enter-subject-alternative-names.png
    :width: 800px
    :align: center
    :alt: Enter subject alternative names
    :figclass: align-center

    Enter subject alternative names

You need to provide the passphrase of the intermediate certificate to sign the key of your server certificate.
It is not necessary to provide a passphrase for the server certificate self. If you install the certificate on a server, having a passphrase on the server key will block automatic restart.

.. figure:: ../images/generate-client-certificate/14-enter-passphrase.png
    :width: 800px
    :align: center
    :alt: Enter passphrase issuer certificate
    :figclass: align-center

    Enter passphrase issuer certificate

The server certificate will be generate.

.. figure:: ../images/generate-client-certificate/15-server-certificate-generated.png
    :width: 800px
    :align: center
    :alt: Enter passphrase issuer certificate
    :figclass: align-center

    Server certificate has been generated


You might inspect the new certificate.
The *Issuer* is the intermediate CA. The *Subject* refers to the certificate itself.

.. figure:: ../images/generate-client-certificate/15-inspect-server-certificate.png
    :width: 800px
    :align: center
    :alt: Inspect server certificate
    :figclass: align-center

    Inspect server certificate

You can also see the subject alt names in the *X509v3 extensions* section of the certificate.


.. figure:: ../images/generate-client-certificate/16-inspect-server-certificate-crl-ocsp.png
    :width: 800px
    :align: center
    :alt: Inspect CRL and OCSP revocation links
    :figclass: align-center

    Inspect CRL and OCSP revocation links


Install the SSL key on a Nginx webserver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This guide shows you in a couple of steps how to install the generated SSL certificate on Nginx to provide HTTPS access to your webserver.
You can find the configuration of this tutorial in `demo nginx ssl`_.

First, you can download a packaged key and certificate zip from BounCA.

.. figure:: ../images/generate-client-certificate/18-ssl-certificate-zip-package.png
    :height: 350px
    :align: center
    :alt: Content of the SSL certificate zip package
    :figclass: align-center

    Content of the SSL certificate zip package

The zip package contains multiple files:

- ``rootca.pem``: The root authority certificate
- ``intermediate.pem``: The intermediate authority certificate
- ``intermediate_root-chain.pem``: Chain of intermediate certificate and root certificate
- ``<domain>-chain.pem``: The certificate including its complete root chain
- ``<domain>.key``: The key of your certificate
- ``<domain>.pem``: The certificate file
- ``<domain>.p12``: A PKCS12 keystore containing the key and certificate


We assume you have added the root ca to your trusted certificates.
If you open the ``<domain>-chain.pem`` you can check the trusted chain.
Or you can use openssl to verify the chain: ``openssl verify -CAfile rootca.pem -untrusted intermediate.pem localhost.pem``.
The command should return ``OK``.

.. figure:: ../images/generate-client-certificate/19-check-ssl-certificate-chain.png
    :height: 350px
    :align: center
    :alt: Verify self-signed certificate is trusted via OpenSSL
    :figclass: align-center

    Verify self-signed certificate is trusted via OpenSSL

To enable SSL within nginx you should copy ``<domain>-chain.pem`` and ``<domain>.key`` to your nginx SSL folder.
Make sure you set the access rights:
- ``<domain>-chain.pem``: 0x644 for nginx user
- ``<domain>.key``: 0x400 for nginx user

Add the following server block to your nginx server:

.. code-block:: nginx

   server {
          listen       443 ssl;
          server_name  localhost;

          ssl_certificate      ssl/<domain>-chain.pem;
          ssl_certificate_key  ssl/<domain>.key;

          location / {
                  root   html;
                  index  index.html index.htm;
          }

   }

It specifies that the server should listen to port 443, using SSL and it defines where it can find the key/certificate pair.

Restart the server and visit your website. It should show a valid and trusted HTTPS connection, and you will see the lock in the URL bar of the browser.
When you click on the lock, you will see that the SSL connection is trusted using your personal self-signed certificate and root authority.


.. figure:: ../images/generate-client-certificate/28-visit-website-trusted-ssl-connection-https.png
    :width: 800px
    :align: center
    :alt: Verify HTTPS connection is now valid and trusted
    :figclass: align-center

    Verify HTTPS connection is now valid and trusted






.. _demo nginx ssl: /demo/nginx_ssl_TODO_FIX_LINK
