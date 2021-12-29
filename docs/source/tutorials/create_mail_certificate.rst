:header_title: Secure and encrypted E-mail with self-generated Client Certificate
:header_subtitle: Step-by-step guide to secure your E-mail with self-generated Client Certificates

.. _create_mail_certificate:

Setting up secure E-mail
=====================================

This tutorial will show you how to setup secure e-mail using S/MIME with a client certificate generated with BounCA.
E-mail can be encrypted using the S/MIME standard. S/MIME stands for "secure multipurpose internet mail extension". Normally, e-mails are send unencrypted over the web, which make them an easy target for cyber criminals.
Normally you don't consider it, when sending your photos, notary documents, financial information, and so on.
Or consider phishing, the e-mail protocol doesn't prevent identity theft. Just as physical mail, the sender information can be freely entered, and thus spoofed.
Using certificates can secure your e-mail traffic, we will explain in this tutorial how to enable S/MIME.

We assume you have a working BounCA and create a certificate authority, see :ref:`create_root_certificate`.


Generate E-mail S/MIME Certificate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, you need an S/MIME certificate. Actually, that is just a client certificate with your full e-mail address.

Enter the dashboard of your intermediate CA which must sign your client certificate.

.. figure:: ../images/generate-mail-certificate/12-enter-int-ca.png
    :width: 800px
    :align: center
    :alt: Step into intermediate certificate
    :figclass: align-center

    Step into intermediate certificate

Click on the *New Client Cert* button to add a new client certificate, and a form will be shown.
The *Common Name* is your main e-mail address. You also need to add the e-mail address to the SubjectAltNames, and you can add extra mail addresses.
Fill in the data for your client certificate. We use the *Copy From Intermediate* button to fill in the base information.
Certificates are usually given a validity of one year.

.. figure:: ../images/generate-mail-certificate/14-fill-in-the-data.png
    :width: 800px
    :align: center
    :alt: Fill in the data for S/MIME certificate
    :figclass: align-center

    Fill in the data for the S/MIME certificate

.. figure:: ../images/generate-mail-certificate/15-enter-the-passphrase.png
    :width: 800px
    :align: center
    :alt: Fill in the passphrase for S/MIME certificate
    :figclass: align-center

    Fill in the passphrase

The passphrase secures your key. You should keep it secret.

.. figure:: ../images/generate-mail-certificate/16-generated-smime-certificate.png
    :width: 800px
    :align: center
    :alt: Generated S/MIME certificate
    :figclass: align-center

    Generated S/MIME certificate

You can inspect the generated certificate

.. figure:: ../images/generate-mail-certificate/17-inspect-subject-client-certificate.png
    :width: 800px
    :align: center
    :alt: Inspect subject of the certificate
    :figclass: align-center

    Inspect subject of the certificate

.. figure:: ../images/generate-mail-certificate/18-inspect-subject-alt-names-certificate.png
    :width: 800px
    :align: center
    :alt: Inspect subject alt names of the certificate
    :figclass: align-center

    Inspect subject alt names of the certificate

Download the certificate bundle. It contains all files necessary for sending encrypted / signed e-mails.


Sending S/MIME signed E-mails
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this section we will discuss how to send S/MIME mail with Apple macOS Mail, and Thunderbird.
In general, you need to install the p12 bundle into your mail client, and receivers need to install the root certificate to
be able to validate your signature.

First we discuss how to configure Apple macOS Mail. Install your client certificate by double clicking on the p12
file. Keychain will open, and ask for the passphrase. When you have entered it correctly, the client certificate is
added to the keychain.

.. figure:: ../images/generate-mail-certificate/19-install-client-certificate.png
    :width: 800px
    :align: center
    :alt: Install client certificate macOS
    :figclass: align-center

    Install client certificate macOS

Open the Mail application, and create a new mail. We assume your mail address is equal to the one in the client certificate.
You will notice Mail has detected your certificate and a certificate symbol at the right is shown in blue. Blue means it will
sign your email, to disbale click on the symbol, it will be greyed out. The lock is for encryption, when grey, the mail will be unencrypted.
The lock symbol will only be shown for installed public S/MIME certificates, and ofcourse for our own mail that certificate is included in the p12 bundle.

.. figure:: ../images/generate-mail-certificate/20-create-signed-mail.png
    :width: 800px
    :align: center
    :alt: Create signed mail
    :figclass: align-center

    Create signed mail

After sending the mail to our self, we open it. When the mail is opened, it shows that the mail has been signed.
You can see the trust chain by clicking on the certificate symbol.

.. figure:: ../images/generate-mail-certificate/21-received-signed-mail.png
    :width: 800px
    :align: center
    :alt: Receive signed mail trusted
    :figclass: align-center

    Receive signed mail trusted

When opening the same mail in Thunderbird, it shows a broken S/MIME verification. It is still untrusted.
The root certificate of our CA needs to be added to Thunderbird to make the signature valid.

.. figure:: ../images/generate-mail-certificate/22-received-signed-mail-thunderbird-not-trusted.png
    :width: 800px
    :align: center
    :alt: Receive signed mail not trusted in Thunderbird
    :figclass: align-center

    Receive signed mail not trusted in Thunderbird

Go to settings in Thunderbird, select the end-to-end encryption pane, and add the root certificate by pressing Manage S/MIME-certificates.
Select the organisations tab to add the root certificate.

.. figure:: ../images/generate-mail-certificate/23-add-root-certificate-thunderbird.png
    :width: 800px
    :align: center
    :alt: Add root certificate to Thunderbird
    :figclass: align-center

    Add root certificate to Thunderbird

Trust the root certificate for sending e=mails.

.. figure:: ../images/generate-mail-certificate/24-trust-root-certificate-thunderbird.png
    :width: 800px
    :align: center
    :alt: Trust root certificate in Thunderbird
    :figclass: align-center

    Trust root certificate in Thunderbird

When succeeded, go back to the received e-mail. Thunderbird will now show a valid and trusted signature.

.. figure:: ../images/generate-mail-certificate/25-received-signed-mail-trusted-thunderbird.png
    :width: 800px
    :align: center
    :alt: Receive signed mail trusted in Thunderbird
    :figclass: align-center

    Receive signed mail trusted in Thunderbird

The S/MIME client certificate need to be added to Thunderbird to send signed e-mails. Go to settings
menu, select the end-to-end encryption pane, and add the root certificate by pressing Manage S/MIME-certificates.
Select the your certificates tab to add the S/MIME certificate.

.. figure:: ../images/generate-mail-certificate/26-add-client-certificate-to-thunderbird.png
    :width: 800px
    :align: center
    :alt: Select the your certificates tab
    :figclass: align-center

    Select the your certificates tab

Press the import button and select the p12 bundle file.

.. figure:: ../images/generate-mail-certificate/27-select-p12-file-thunderbird.png
    :width: 800px
    :align: center
    :alt: Select the p12 bundle
    :figclass: align-center

    Select the p12 bundle

.. figure:: ../images/generate-mail-certificate/28-client-certificate-added-thunderbird.png
    :width: 800px
    :align: center
    :alt: The client certificate has been added
    :figclass: align-center

    The client certificate has been added

The S/MIME certificate needs to be connected to your account. Press the select button of the
personal certificate for signing field.

.. figure:: ../images/generate-mail-certificate/29-select-client-certificate-to-sign-and-encrypt-mail-thunderbird.png
    :width: 800px
    :align: center
    :alt: Select client certificate for signing
    :figclass: align-center

    Select client certificate for signing

It will also ask to add certificate for encryption, answer positive on that dialog. You have configured the
client certificate in Thunderbird. You might enable adding digital signature as default option, and turn off encryption by default.

.. figure:: ../images/generate-mail-certificate/30-client-certificate-configured-thunderbird.png
    :width: 800px
    :align: center
    :alt: Client certificate for signing configured
    :figclass: align-center

    Client certificate for signing configured

Compose a new e-mail, and the compose view shows an extra security menu option.

.. figure:: ../images/generate-mail-certificate/31-send-signed-mail-thunderbird.png
    :width: 800px
    :align: center
    :alt: Send signed mail Thunderbird
    :figclass: align-center

    Send signed mail Thunderbird


Sending S/MIME encrypted E-mails
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The S/MIME certificate can also be used to encrypt the complete message. This enables end-to-end encrypted e-mail communication,
and as we use a self-generated CA, harder to perform a man-in-the-middle attack.

To enable encrypted e-mail, you need to share your public certificate to your senders. Share with them your ``pem`` file and root certificate.
The senders of e-mails to your account need to install these public certificate.
If they have installed these file in their mail client, they are able to send you encrypted e-mails.
Ofcourse, you should never share your private key or p12 file, the private key is used for decryption and should only be known by you.

Create a new message in the Mail application, and click on the lock icon. The icon will become blue.

.. figure:: ../images/generate-mail-certificate/32-send-encrypted-mail-Mail.png
    :width: 800px
    :align: center
    :alt: Send encrypted mail
    :figclass: align-center

    Send encrypted mail

When you open the mail in Thunderbird, you will be able to read it. You see the mail is encrypted
by the icons in the top bar. And when clicking on the lock, Thunderbird shows that the message is encrypted.

.. figure:: ../images/generate-mail-certificate/33-received-encrypted-mail-Firefox.png
    :width: 800px
    :align: center
    :alt: Received encrypted mail Thunderbird
    :figclass: align-center

    Received encrypted mail Thunderbird

If you don't have the private key, you will not be able to read the mail. The only thing shown in that case, is
a S/MIME attachment.
