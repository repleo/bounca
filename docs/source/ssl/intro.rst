Your Own Certificate Authority
==============================

A certificate authority (CA) is an entity that signs digital certificates. 
Many websites need to let their customers know that the connection is secure, so they pay an internationally trusted CA (eg, VeriSign, DigiCert) to sign a certificate for their domain.

In some cases it may make more sense to act as your own CA, rather than paying a CA like DigiCert. 
Common cases include securing an intranet website, or for issuing certificates to clients to allow them to authenticate to a server.
Main use cases for having your own CA:

- Trusted encrypted communication with your peers (man-in-the-middle attack prevention)
- Secure your internal REST micro-services and internal API's
- Client-certificate based login for web services, web applications and OpenVPN connections
- Secure access to your private cloud services with your own HTTPS scheme
- Secure your Internet of Things (IoT) network with your certificates



