:header_title: Configure Secure OpenVPN private network access
:header_subtitle: Step-by-step guide to set up OpenVPN to access your private network

.. _vpn_configuration:

Setting up OpenVPN
=====================================

This document will show you how to set up OpenVPN to access your private network over the Internet.
VPN allows to connect to your private network services.
We will show how to configure OpenVPN using BounCA in an OpenWRT router.
The complete guide of OpenVPN is out of the scope of this tutorial, for more information about configuring OpenVPN, check their documentation `OpenVPN Guide`_
We assume you have a working BounCA and create a certificate authority, see :ref:`create_root_certificate`.

To use OpenVPN, you need to have a server certificate, and for all connecting clients separate client certificates.
When you configured CRL, you can revoke access via CRL.


Setting up OpenVPN Server
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Start with creating the server certificate. Enter the dashboard of your intermediate CA which must sign your server certificate.

.. figure:: ../images/vpn-configuration/12-enter-int-ca.png
    :width: 800px
    :align: center
    :alt: Step into intermediate certificate
    :figclass: align-center

    Step into intermediate certificate

Click on the *New Server Cert* button to add a new server certificate, and a form will be shown.
You must at least define the *Common Name*, it can be everything, we will use the FQDN of our vpn server.

.. figure:: ../images/vpn-configuration/13-create-openvpn-server-certificate.png
    :width: 800px
    :align: center
    :alt: Create OpenVPN server certificate
    :figclass: align-center

    Create OpenVPN server certificate

We give the server certificates a validity of two years. The passphrase is kept empty, otherwise we cannot
automatically start OpenVPN during booting. You can copy the distinguished name information from the
intermediate certificate by pressing the *Copy From Intermediate* button.

.. figure:: ../images/vpn-configuration/14-passphrase-openvpn-server-certificate.png
    :width: 800px
    :align: center
    :alt: Empty passphrase and name of OpenVPN server certificate
    :figclass: align-center

    Empty passphrase and name of OpenVPN server certificate

Press create, and download the certificate bundle from the dashboard.

OpenVPN also needs Diffie-Hellman parameters. Generate those on the command line using openssl:
``openssl dhparam -out dhparams.pem 4096``. It might take a while to generate them.


.. figure:: ../images/vpn-configuration/15-generate-dh-params.png
    :width: 800px
    :align: center
    :alt: Generate Diffie-Hellman parameters
    :figclass: align-center

    Generate Diffie-Hellman parameters

We will discuss how to configure OpenVPN using the webinterface of an OpenWRT router.
As OpenWRT is Linux-based, the configuration can also be used on the commandline of a Linux machine.

Create the server ovpn file, like the one below:

.. code-block:: teratermmacro

    comp-lzo yes
    dev tun
    proto udp
    port 1194
    mssfix 1420
    keepalive 10 60

    ; Allow multiple logins with same certificate
    duplicate-cn

    cipher AES-256-CBC
    auth SHA256
    ; disable old insecure encryption like SHA1, disable in case old clients need to connect
    tls-version-min 1.2

    ; Optimization for windows clients
    sndbuf 393215
    rcvbuf 393215
    push "sndbuf 393215"
    push "rcvbuf 393215"


    ; The certificates and key
    ca /etc/openvpn/rootca.pem
    cert /etc/openvpn/vpndemo-chain.pem
    key /etc/openvpn/vpndemo.key
    dh /etc/openvpn/dhparams.pem
    ; Optional CRL for revocation clients
    ;crl-verify int.crl

    ; VPN subnet
    server  192.168.88.0 255.255.255.0
    ; Route to local network
    push "route 192.168.34.0 255.255.255.0"
    verb 3


Replace in this file the IPs for the route to your local network, and VPN subnet. The VPN subnet should
be different from your local network. That is also the reason a route to your local network needs to be pushed
to your clients.

Upload the certificates and keys to your OpenWRT router using scp. In our case, we stored the certificates in ``/etc/openvpn``.

Browse to the UI of your OpenWRT modem, and open de OpenVPN Pane.

.. figure:: ../images/vpn-configuration/31-OpenVPN-dashboard-OpenWRT.png
    :width: 800px
    :align: center
    :alt: OpenVPN dashboard in OpenWRT
    :figclass: align-center

    OpenVPN dashboard in OpenWRT

Upload the ovpn file.

.. figure:: ../images/vpn-configuration/32-Demo-VPN-uploaded.png
    :width: 800px
    :align: center
    :alt: The Demo VPN server has been created in OpenWRT
    :figclass: align-center

    The Demo VPN server has been created in OpenWRT

You can inspect the content of the ovpn file by pressing the edit button.

.. figure:: ../images/vpn-configuration/33-Inspect-config-Demo-VPN.png
    :width: 800px
    :align: center
    :alt: Inspect the config of the Demo VPN
    :figclass: align-center

    Inspect the config of the Demo VPN

Go back to the VPN dashboard, and press the *Save & Apply* button. When OpenWRT has been refreshed,
you can press the *Start* button of the demo VPN.

.. figure:: ../images/vpn-configuration/34-Save-Apply-and-start-Demo-VPN.png
    :width: 800px
    :align: center
    :alt: VPN Server has been started
    :figclass: align-center

    VPN Server has been started

The VPN sever is running at this point, however you are not able to reach it.
OpenWRT has strict firewall rules, and you need to open the port, and connect the ``tun`` interface
to the local lan zone.

.. figure:: ../images/vpn-configuration/35-Add-firewall-rule-accepting-UDP-OpenVPN.png
    :width: 800px
    :align: center
    :alt: Add firewall rule for the UPD port 1194 of OpenVPN
    :figclass: align-center

    Add firewall rule for the UPD port 1194 of OpenVPN

The firewall rule allows external clients to connect to the OpenVPN server, you can verify via nmap:
``nmap <ip> -p 1194 -sU``. You will only notice you cannot reach any device in your internal network.
The ``tun`` interface of the OpenVPN server must be added to the local zone, so no traffic will be blocked.
We added an *unmanaged* interface in the Interfaces dashboard of OpenWRT.

.. figure:: ../images/vpn-configuration/36-Allow-tun-interface-in-local-LAN-zone.png
    :width: 800px
    :align: center
    :alt: Add unmanaged interface to OpenWRT
    :figclass: align-center

    Add unmanaged interface to OpenWRT

.. figure:: ../images/vpn-configuration/36a-Allow-tun-interface-in-local-LAN-zone.png
    :width: 800px
    :align: center
    :alt: Add OpenVPN interface to local lan zone
    :figclass: align-center

    Add OpenVPN interface to local lan zone

The OpenVPN server is now ready. The next section will discuss how to connect to it.

Creating Client Certificates and Connecting to OpenVPN Server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To connect to the VPN server, you need a valid client certificate.
Click on the *New Client Cert* button to add a new client certificate in the intermediate dashboard.
The *Common Name* should be unique. Use for example the user name.

.. figure:: ../images/vpn-configuration/20-create-openvpn-client-certificate.png
    :width: 800px
    :align: center
    :alt: Create client certificate
    :figclass: align-center

    Create client certificate

The client certificate should be protected by a passphrase as it allows to connect to your
OpenVPN server.

.. figure:: ../images/vpn-configuration/20-passphrase-openvpn-client-certificate.png
    :width: 800px
    :align: center
    :alt: Add passphrase to your client certificate
    :figclass: align-center

    Add passphrase to your client certificate

Download the created client certificate, and use the connect to complete the ovpn
file shown below.

.. code-block:: teratermmacro

    client
    comp-lzo
    dev tun
    proto udp
    remote <HOSTNAME or IP of Server> 1194
    resolv-retry infinite
    nobind
    persist-key
    persist-tun
    cipher AES-256-CBC
    auth SHA256

    <ca>
    -----BEGIN CERTIFICATE-----
    ***Paste Intermediate CA Cert Text Here***

    -----END CERTIFICATE-----
    -----BEGIN CERTIFICATE-----
    ***Paste Root CA Cert Text Here***

    -----END CERTIFICATE-----
    </ca>
    <cert>
    -----BEGIN CERTIFICATE-----
    ***Paste Your Cert Text Here***

    -----END CERTIFICATE-----
    </cert>
    <key>
    -----BEGIN PRIVATE KEY-----
    ***Paste Your Cert Private Key Here***

    -----END PRIVATE KEY-----
    </key>


Instead of copying the keys to your ovpn file, you can also refer to the key and certificate via the ``key`` and ``cert`` directive,
and distribute the key/certificate-pair separately. OpenVPN Connect is be able to handle separated certificate files.

You can now connect your OpenVPN server. For example, you can connect from linux with the following command:
``openvpn --config demovpn.ovpn``.

Or you can connect via your iPhone using the OpenVPN Connect app. Share the file to your phone using iTunes, and open the OpenVPN Connect app.


.. figure:: ../images/vpn-configuration/40-import-ovpn-file.png
    :width: 350px
    :align: center
    :alt: Import ovpn file in OpenVPN Connect
    :figclass: align-center

    Import ovpn file in OpenVPN Connect


When you import the ovpn file, the app ask to store your passphrase. Depending on your security needs
you can decide to store it, and via the edit button you can modify your choice.

.. figure:: ../images/vpn-configuration/41-imported-profile.png
    :width: 350px
    :align: center
    :alt: Profile has been imported in OpenVPN Connect
    :figclass: align-center

    Profile has been imported in OpenVPN Connect


.. figure:: ../images/vpn-configuration/42-disconnected-profile.png
    :width: 350px
    :align: center
    :alt: Disconnected profile
    :figclass: align-center

    Disconnected profile

Slide the connect button of your profile, and OpenVPN Connect will ask for your passphrase.
When you entered your passphrase it will connect to your VPN server.

.. figure:: ../images/vpn-configuration/43-enter-passphrase.png
    :width: 350px
    :align: center
    :alt: Connect, and enter passphrase
    :figclass: align-center

    Connect, and enter passphrase

.. figure:: ../images/vpn-configuration/44-connected-vpn.png
    :width: 350px
    :align: center
    :alt: VPN has been connected
    :figclass: align-center

    VPN has been connected

You will see a statistics screen after the connection has been established. You can leave the app, the connection
will remain in background. Your iPhone is now connected to your local network via the VPN. You can browse for example
to a local webserver, in this example the local hosted BounCA server.


.. figure:: ../images/vpn-configuration/45-browse-to-internal-network.png
    :width: 350px
    :align: center
    :alt: Browsing via the VPN to a locally hosted server
    :figclass: align-center

    Browsing via the VPN to a locally hosted server

This guide showed how to set up an OpenVPN server. The configuration options are plenty for OpenVPN, and you can increase the
security by improving the checking of the certificates, and require more strict encryption. We refer for these options to the `OpenVPN Guide`_.


.. _OpenVPN Guide: https://openvpn.net/community-resources/how-to/



