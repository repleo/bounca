# Change Log
The BounCA change history

## [0.4.5] - Release 2024-01-31]
* Generate CRL file updates via button, and set expire day 365 days in the future
* Added legacy pkcs12 support for macOS
* Mail template fix
* Fixed ALL option in table views

## [0.4.4] - Release 2023-04-20
* Bugfix allow retrieving crls with old extension crl.pem

## [0.4.3] - Release 2023-02-21
* Bugfix when creating root certificate dont check for issuer passphrase

## [0.4.2] - Release 2023-02-15
* Dont check policies when revoking a certificate

## [0.4.1] - Release 2023-02-05
* Added migration for Django 4.1.6
* Update Readme

## [0.4.0] - Release 2023-02-05
* Added support for generating code signing certificates
* Added Serial and Fingerprint to certificate table, including search
* Added preset expire dates when creating certificates
* Made Subject Alternative Name mandatory for client, server certificate as browsers require them
* Added revoke prefix to revoked certificates name
* Don't display revoked certificates in overview screen
* App token for downloading CRL certificate
* Added renew certificate button
* Renamed extension revocation list crl.pem to crl

## [0.3.0] - Release 2022-01-14
* Added resend e-mail button if user has not verified email yet
* Form for admin account generation for fresh installs
* Filter switch to not display revoked expired certificates
* Download button of client keys when they are expired/revoked
* Fixed date in expires_at field in certificate forms in safari
* Updated installation documents
* Updated packages

## [0.2.1] - Release 2022-01-06
* Removed owner from certificate API, disabled HTML Form

## [0.2.0] - Release 2021-12-29
* Rebuild of BounCA, old db not compatible
* Python based certificate factory
* Vuetify based frontend
* Updated all dependencies

## [0.1.1] - Release 2016-06-12

* Bug fix in generation of intermediate CA
* Code quality improvements

## [0.1] - Release 2016-05-31

* Version bump

## [0.1rc0] - Release Candidate 2016-05-28

### Added
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
