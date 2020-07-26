# coding: utf-8
import arrow
import datetime
from cryptography import x509
from cryptography.x509 import ExtensionOID
from cryptography.x509.extensions import ExtensionNotFound, _key_identifier_from_public_key
from cryptography.x509.oid import AuthorityInformationAccessOID, ExtendedKeyUsageOID, NameOID
from django.test import TestCase
from django.utils import timezone
from ipaddress import IPv4Address

from certificate_engine.ssl.certificate import Certificate, PassPhraseError
from certificate_engine.ssl.key import Key
from certificate_engine.types import CertificateTypes
from x509_pki.tests.factories import CertificateFactory, DistinguishedNameFactory


class IntermediateCertificateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        root_key = Key().create_key(8192)
        cls.root_certificate = CertificateFactory(expires_at=arrow.get(timezone.now()).shift(days=+3).date(),
                                              key=root_key.serialize())
        certificate = Certificate()
        certificate.create_certificate(cls.root_certificate)

        cls.root_certificate.crt = certificate.serialize()
        cls.root_certificate.key = root_key.serialize()
        cls.root_certificate.save()

    def test_generate_intermediate_certificate(self):
        key = Key().create_key(4096)

        subject = DistinguishedNameFactory(countryName=self.root_certificate.dn.countryName,
                                           stateOrProvinceName=self.root_certificate.dn.stateOrProvinceName,
                                           organizationName=self.root_certificate.dn.organizationName)

        certificate = CertificateFactory(type=CertificateTypes.INTERMEDIATE,
                                         parent=self.root_certificate, dn=subject,
                                         key=key.serialize())

        certhandler = Certificate()
        certhandler.create_certificate(certificate)

        crt = certhandler.certificate

        self.assertEqual(crt.serial_number, int(certificate.serial))
        self.assertEqual(crt.public_key().public_numbers(), key.key.public_key().public_numbers())
        self.assertEqual(crt.not_valid_before, datetime.datetime(
            year=certificate.created_at.year,
            month=certificate.created_at.month,
            day=certificate.created_at.day
        ))

        self.assertEqual(crt.not_valid_after, datetime.datetime(
            year=certificate.expires_at.year,
            month=certificate.expires_at.month,
            day=certificate.expires_at.day
        ))

        # subject
        subject = crt.subject
        self.assertIsInstance(subject, x509.Name)
        self.assertListEqual(list(subject), [
            x509.NameAttribute(NameOID.COMMON_NAME, certificate.dn.commonName),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, certificate.dn.organizationName),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, certificate.dn.organizationalUnitName),
            x509.NameAttribute(NameOID.LOCALITY_NAME, certificate.dn.localityName),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, certificate.dn.stateOrProvinceName),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, certificate.dn.emailAddress),
            x509.NameAttribute(NameOID.COUNTRY_NAME, str(certificate.dn.countryName)),
        ])

        # issuer
        issuer = crt.issuer
        self.assertIsInstance(issuer, x509.Name)
        self.assertListEqual(list(issuer), [
            x509.NameAttribute(NameOID.COMMON_NAME, root_certificate.dn.commonName),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, root_certificate.dn.organizationName),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, root_certificate.dn.organizationalUnitName),
            x509.NameAttribute(NameOID.LOCALITY_NAME, root_certificate.dn.localityName),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, root_certificate.dn.stateOrProvinceName),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, root_certificate.dn.emailAddress),
            x509.NameAttribute(NameOID.COUNTRY_NAME, str(root_certificate.dn.countryName)),
        ])

        # crlDistributionspoints
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.CRL_DISTRIBUTION_POINTS)
        self.assertTrue(ext.critical)
        crl_dp = ext.value
        self.assertEqual(crl_dp[0].full_name[0].value,
                         'URI:{}{}.crl'.format(certificate.crl_distribution_url, certificate.shortname))
        self.assertEqual(crl_dp[0].reasons,
                         frozenset([
                             x509.ReasonFlags.key_compromise,
                             x509.ReasonFlags.ca_compromise,
                             x509.ReasonFlags.affiliation_changed,
                             x509.ReasonFlags.superseded,
                             x509.ReasonFlags.privilege_withdrawn,
                             x509.ReasonFlags.cessation_of_operation,
                             x509.ReasonFlags.aa_compromise,
                             x509.ReasonFlags.certificate_hold,
                         ]))

        # keyUsage = basicConstraints = critical, CA:true
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.BASIC_CONSTRAINTS)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value, x509.BasicConstraints(
            ca=True,
            path_length=0
        ))

        # keyUsage = critical, digitalSignature, cRLSign, keyCertSign
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.KEY_USAGE)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value, x509.KeyUsage(
            digital_signature=True,
            content_commitment=False,
            key_encipherment=False,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=True,
            crl_sign=True,
            encipher_only=False,
            decipher_only=False
        ))

        # OCSP
        # authorityInfoAccess = OCSP;URI:{{cert.ocsp_distribution_host}}
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_INFORMATION_ACCESS)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value[0], x509.AccessDescription(
            AuthorityInformationAccessOID.OCSP,
            x509.UniformResourceIdentifier(certificate.ocsp_distribution_host)
        ))

        # authorityKeyIdentifier = keyid:always, issuer
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_KEY_IDENTIFIER)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value.key_identifier, _key_identifier_from_public_key(root_key.key.public_key()))
        self.assertEqual(ext.value.authority_cert_serial_number, int(root_certificate.serial))
        self.assertEqual([x for x in ext.value.authority_cert_issuer[0].value.rdns[0]][0].value,
                         str(root_certificate.dn))

        # subjectKeyIdentifier = hash
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_KEY_IDENTIFIER)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value.digest, _key_identifier_from_public_key(key.key.public_key()))

    def test_generate_intermediate_certificate_passphrase(self):
        root_key = Key().create_key(2048)
        root_certificate = CertificateFactory(expires_at=arrow.get(timezone.now()).shift(days=+3).date(),
                                              key=root_key.serialize(passphrase=b'SecretRootPP'))
        root_certhandler = Certificate()
        root_certhandler.create_certificate(root_certificate, passphrase=b'SecretRootPP')

        subject = DistinguishedNameFactory(countryName=root_certificate.dn.countryName,
                                           stateOrProvinceName=root_certificate.dn.stateOrProvinceName,
                                           organizationName=root_certificate.dn.organizationName,
                                           localityName=root_certificate.dn.localityName)

        key = Key().create_key(2048)

        certificate = CertificateFactory(type=CertificateTypes.INTERMEDIATE,
                                         parent=root_certificate, dn=subject,
                                         key=key.serialize(passphrase=b'SecretPP'))
        certhandler = Certificate()
        certhandler.create_certificate(certificate, passphrase=b'SecretPP', passphrase_issuer=b'SecretRootPP')

        crt = certhandler.certificate

        self.assertEqual(crt.serial_number, int(certificate.serial))
        self.assertEqual(crt.public_key().public_numbers(), key.key.public_key().public_numbers())
        self.assertEqual(crt.not_valid_before, datetime.datetime(
            year=certificate.created_at.year,
            month=certificate.created_at.month,
            day=certificate.created_at.day
        ))

    def test_generate_intermediate_certificate_passphrase_wrong_issuer(self):
        root_key = Key().create_key(2048)
        root_certificate = CertificateFactory(expires_at=arrow.get(timezone.now()).shift(days=+3).date(),
                                              key=root_key.serialize(passphrase=b'SecretRootPP'))
        root_certhandler = Certificate()
        root_certhandler.create_certificate(root_certificate, passphrase=b'SecretRootPP')

        subject = DistinguishedNameFactory(countryName=root_certificate.dn.countryName,
                                           stateOrProvinceName=root_certificate.dn.stateOrProvinceName,
                                           organizationName=root_certificate.dn.organizationName)

        key = Key().create_key(2048)

        certificate = CertificateFactory(type=CertificateTypes.INTERMEDIATE,
                                         parent=root_certificate, dn=subject,
                                         key=key.serialize(passphrase=b'SecretPP'))
        certhandler = Certificate()
        with self.assertRaisesMessage(PassPhraseError, "Bad passphrase, could not decode issuer key"):
            certhandler.create_certificate(certificate,
                                           passphrase=b'SecretPP',
                                           passphrase_issuer=b'SecretRootPPInvalid')

    def test_generate_server_certificate(self):
        root_key = Key().create_key(2048)
        root_certificate = CertificateFactory(expires_at=arrow.get(timezone.now()).shift(days=+6).date(),
                                              key=root_key.serialize())
        root_certhandler = Certificate()
        root_certhandler.create_certificate(root_certificate)

        subject = DistinguishedNameFactory(countryName=root_certificate.dn.countryName,
                                           stateOrProvinceName=root_certificate.dn.stateOrProvinceName,
                                           organizationName=root_certificate.dn.organizationName)

        int_key = Key().create_key(2048)

        int_certificate = CertificateFactory(expires_at=arrow.get(timezone.now()).shift(days=+5).date(),
                                             type=CertificateTypes.INTERMEDIATE,
                                             parent=root_certificate, dn=subject,
                                             key=int_key.serialize())
        int_certhandler = Certificate()
        int_certhandler.create_certificate(int_certificate)

        key = Key().create_key(2048)
        server_subject = DistinguishedNameFactory(subjectAltNames=["www.repleo.nl",
                                                                   "*.bounca.org",
                                                                   "wwww.mac-usb-serial.com",
                                                                   "127.0.0.1"])
        certificate = CertificateFactory(type=CertificateTypes.SERVER_CERT,
                                         parent=int_certificate, dn=server_subject,
                                         key=key.serialize())
        certhandler = Certificate()
        certhandler.create_certificate(certificate)

        crt = certhandler.certificate

        self.assertEqual(crt.serial_number, int(certificate.serial))
        self.assertEqual(crt.public_key().public_numbers(), key.key.public_key().public_numbers())
        self.assertEqual(crt.not_valid_before, datetime.datetime(
            year=certificate.created_at.year,
            month=certificate.created_at.month,
            day=certificate.created_at.day
        ))

        self.assertEqual(crt.not_valid_after, datetime.datetime(
            year=certificate.expires_at.year,
            month=certificate.expires_at.month,
            day=certificate.expires_at.day
        ))
        # basicConstraints = CA:FALSE
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.BASIC_CONSTRAINTS)
        self.assertFalse(ext.critical)
        self.assertEqual(ext.value, x509.BasicConstraints(
            ca=False,
            path_length=None
        ))

        # authorityKeyIdentifier = keyid:always, issuer
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_KEY_IDENTIFIER)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value.key_identifier, _key_identifier_from_public_key(int_key.key.public_key()))

        # subjectKeyIdentifier = hash
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_KEY_IDENTIFIER)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value.digest, _key_identifier_from_public_key(key.key.public_key()))

        # keyUsage = critical, digitalSignature, keyEncipherment
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.KEY_USAGE)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value, x509.KeyUsage(
            digital_signature=True,
            content_commitment=False,
            key_encipherment=True,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=False,
            crl_sign=False,
            encipher_only=False,
            decipher_only=False
        ))

        # extendedKeyUsage = serverAuth
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.EXTENDED_KEY_USAGE)
        self.assertFalse(ext.critical)
        self.assertEqual([x for x in ext.value], [ExtendedKeyUsageOID.SERVER_AUTH])

        # { % if cert.dn.subjectAltNames %}
        # subjectAltName = @alt_names
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
        self.assertFalse(ext.critical)
        self.assertEqual([x.value for x in ext.value], [
            'www.repleo.nl', '*.bounca.org', 'wwww.mac-usb-serial.com', IPv4Address('127.0.0.1')])

        # crlDistributionPoints
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.CRL_DISTRIBUTION_POINTS)
        self.assertTrue(ext.critical)
        crl_dp = ext.value
        self.assertEqual(crl_dp[0].full_name[0].value,
                         'URI:{}{}.crl'.format(int_certificate.crl_distribution_url, int_certificate.shortname))
        self.assertEqual(crl_dp[0].reasons,
                         frozenset([
                             x509.ReasonFlags.key_compromise,
                             x509.ReasonFlags.ca_compromise,
                             x509.ReasonFlags.affiliation_changed,
                             x509.ReasonFlags.superseded,
                             x509.ReasonFlags.privilege_withdrawn,
                             x509.ReasonFlags.cessation_of_operation,
                             x509.ReasonFlags.aa_compromise,
                             x509.ReasonFlags.certificate_hold,Ss
                         ]))

        # OCSP
        # authorityInfoAccess = OCSP;URI:{{cert.ocsp_distribution_host}}
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_INFORMATION_ACCESS)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value[0], x509.AccessDescription(
            AuthorityInformationAccessOID.OCSP,
            x509.UniformResourceIdentifier(int_certificate.ocsp_distribution_host)
        ))

        # subject
        subject = crt.subject
        self.assertIsInstance(subject, x509.Name)
        self.assertListEqual(list(subject), [
            x509.NameAttribute(NameOID.COMMON_NAME, certificate.dn.commonName),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, certificate.dn.organizationName),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, certificate.dn.organizationalUnitName),
            x509.NameAttribute(NameOID.LOCALITY_NAME, certificate.dn.localityName),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, certificate.dn.stateOrProvinceName),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, certificate.dn.emailAddress),
            x509.NameAttribute(NameOID.COUNTRY_NAME, str(certificate.dn.countryName)),
        ])

        # issuer
        issuer = crt.issuer
        self.assertIsInstance(issuer, x509.Name)
        self.assertListEqual(list(issuer), [
            x509.NameAttribute(NameOID.COMMON_NAME, int_certificate.dn.commonName),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, int_certificate.dn.organizationName),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, int_certificate.dn.organizationalUnitName),
            x509.NameAttribute(NameOID.LOCALITY_NAME, int_certificate.dn.localityName),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, int_certificate.dn.stateOrProvinceName),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, int_certificate.dn.emailAddress),
            x509.NameAttribute(NameOID.COUNTRY_NAME, str(int_certificate.dn.countryName)),
        ])


    def test_generate_server_certificate(self):
        root_key = Key().create_key(2048)
        root_certificate = CertificateFactory(expires_at=arrow.get(timezone.now()).shift(days=+6).date(),
                                              key=root_key.serialize())
        root_certhandler = Certificate()
        root_certhandler.create_certificate(root_certificate)

        subject = DistinguishedNameFactory(countryName=root_certificate.dn.countryName,
                                           stateOrProvinceName=root_certificate.dn.stateOrProvinceName,
                                           organizationName=root_certificate.dn.organizationName,
                                           localityName=root_certificate.dn.localityName)

        int_key = Key().create_key(2048)

        int_certificate = CertificateFactory(expires_at=arrow.get(timezone.now()).shift(days=+5).date(),
                                             type=CertificateTypes.INTERMEDIATE,
                                             parent=root_certificate, dn=subject,
                                             key=int_key.serialize())
        int_certhandler = Certificate()
        int_certhandler.create_certificate(int_certificate)

        key = Key().create_key(2048)
        server_subject = DistinguishedNameFactory(commonName=None)
        certificate = CertificateFactory(type=CertificateTypes.SERVER_CERT,
                                         parent=int_certificate, dn=server_subject,
                                         key=key.serialize())
        certhandler = Certificate()
        certhandler.create_certificate(certificate)


    def test_generate_server_certificate_no_subject_altnames(self):
        root_key = Key().create_key(2048)
        root_certificate = CertificateFactory(expires_at=arrow.get(timezone.now()).shift(days=+6).date(),
                                              key=root_key.serialize())
        root_certhandler = Certificate()
        root_certhandler.create_certificate(root_certificate)

        subject = DistinguishedNameFactory(countryName=root_certificate.dn.countryName,
                                           stateOrProvinceName=root_certificate.dn.stateOrProvinceName,
                                           organizationName=root_certificate.dn.organizationName)

        int_key = Key().create_key(2048)

        int_certificate = CertificateFactory(expires_at=arrow.get(timezone.now()).shift(days=+5).date(),
                                             type=CertificateTypes.INTERMEDIATE,
                                             parent=root_certificate, dn=subject,
                                             key=int_key.serialize())
        int_certhandler = Certificate()
        int_certhandler.create_certificate(int_certificate)

        key = Key().create_key(2048)
        server_subject = DistinguishedNameFactory(subjectAltNames=None)
        certificate = CertificateFactory(type=CertificateTypes.SERVER_CERT,
                                         parent=int_certificate, dn=server_subject,
                                         key=key.serialize())
        certhandler = Certificate()
        certhandler.create_certificate(certificate)

        crt = certhandler.certificate

        self.assertEqual(crt.serial_number, int(certificate.serial))
        self.assertEqual(crt.public_key().public_numbers(), key.key.public_key().public_numbers())

        # { % if cert.dn.subjectAltNames %}
        # subjectAltName = @alt_names
        with self.assertRaises(ExtensionNotFound):
            crt.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)

    def test_generate_server_certificate_no_intermediate_ca(self):
        root_key = Key().create_key(2048)
        root_certificate = CertificateFactory(expires_at=arrow.get(timezone.now()).shift(days=+6).date(),
                                              key=root_key.serialize())
        root_certhandler = Certificate()
        root_certhandler.create_certificate(root_certificate)

        key = Key().create_key(2048)
        server_subject = DistinguishedNameFactory(subjectAltNames=None)
        certificate = CertificateFactory(type=CertificateTypes.SERVER_CERT,
                                         parent=root_certificate, dn=server_subject,
                                         key=key.serialize())
        certhandler = Certificate()
        certhandler.create_certificate(certificate)

        crt = certhandler.certificate

        self.assertEqual(crt.serial_number, int(certificate.serial))
        self.assertEqual(crt.public_key().public_numbers(), key.key.public_key().public_numbers())

        # subject
        subject = crt.subject
        self.assertIsInstance(subject, x509.Name)
        self.assertListEqual(list(subject), [
            x509.NameAttribute(NameOID.COMMON_NAME, certificate.dn.commonName),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, certificate.dn.organizationName),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, certificate.dn.organizationalUnitName),
            x509.NameAttribute(NameOID.LOCALITY_NAME, certificate.dn.localityName),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, certificate.dn.stateOrProvinceName),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, certificate.dn.emailAddress),
            x509.NameAttribute(NameOID.COUNTRY_NAME, str(certificate.dn.countryName)),
        ])

        # issuer
        issuer = crt.issuer
        self.assertIsInstance(issuer, x509.Name)
        self.assertListEqual(list(issuer), [
            x509.NameAttribute(NameOID.COMMON_NAME, root_certificate.dn.commonName),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, root_certificate.dn.organizationName),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, root_certificate.dn.organizationalUnitName),
            x509.NameAttribute(NameOID.LOCALITY_NAME, root_certificate.dn.localityName),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, root_certificate.dn.stateOrProvinceName),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, root_certificate.dn.emailAddress),
            x509.NameAttribute(NameOID.COUNTRY_NAME, str(root_certificate.dn.countryName)),
        ])

        # authorityKeyIdentifier = keyid:always, issuer
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_KEY_IDENTIFIER)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value.key_identifier, _key_identifier_from_public_key(root_key.key.public_key()))

        # subjectKeyIdentifier = hash
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_KEY_IDENTIFIER)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value.digest, _key_identifier_from_public_key(key.key.public_key()))

    def test_generate_user_certificate(self):
        root_key = Key().create_key(2048)
        root_certificate = CertificateFactory(expires_at=arrow.get(timezone.now()).shift(days=+6).date(),
                                              key=root_key.serialize())
        root_certhandler = Certificate()
        root_certhandler.create_certificate(root_certificate)

        subject = DistinguishedNameFactory(countryName=root_certificate.dn.countryName,
                                           stateOrProvinceName=root_certificate.dn.stateOrProvinceName,
                                           organizationName=root_certificate.dn.organizationName)

        int_key = Key().create_key(2048)

        int_certificate = CertificateFactory(expires_at=arrow.get(timezone.now()).shift(days=+5).date(),
                                             type=CertificateTypes.INTERMEDIATE,
                                             parent=root_certificate, dn=subject,
                                             key=int_key.serialize())
        int_certhandler = Certificate()
        int_certhandler.create_certificate(int_certificate)

        key = Key().create_key(2048)
        server_subject = DistinguishedNameFactory(subjectAltNames=["jeroen",
                                                                   "info@bounca.org"])
        certificate = CertificateFactory(type=CertificateTypes.CLIENT_CERT,
                                         parent=int_certificate, dn=server_subject,
                                         key=key.serialize())
        certhandler = Certificate()
        certhandler.create_certificate(certificate)

        crt = certhandler.certificate

        self.assertEqual(crt.serial_number, int(certificate.serial))
        self.assertEqual(crt.public_key().public_numbers(), key.key.public_key().public_numbers())
        self.assertEqual(crt.not_valid_before, datetime.datetime(
            year=certificate.created_at.year,
            month=certificate.created_at.month,
            day=certificate.created_at.day
        ))

        self.assertEqual(crt.not_valid_after, datetime.datetime(
            year=certificate.expires_at.year,
            month=certificate.expires_at.month,
            day=certificate.expires_at.day
        ))
        # basicConstraints = CA:FALSE
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.BASIC_CONSTRAINTS)
        self.assertFalse(ext.critical)
        self.assertEqual(ext.value, x509.BasicConstraints(
            ca=False,
            path_length=None
        ))

        # authorityKeyIdentifier = keyid:always, issuer
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_KEY_IDENTIFIER)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value.key_identifier, _key_identifier_from_public_key(int_key.key.public_key()))

        # subjectKeyIdentifier = hash
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_KEY_IDENTIFIER)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value.digest, _key_identifier_from_public_key(key.key.public_key()))

        # keyUsage = critical, nonRepudiation, digitalSignature, keyEncipherment
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.KEY_USAGE)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value, x509.KeyUsage(
            digital_signature=True,
            content_commitment=True,
            key_encipherment=True,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=False,
            crl_sign=False,
            encipher_only=False,
            decipher_only=False
        ))

        # extendedKeyUsage = clientAuth, emailProtection
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.EXTENDED_KEY_USAGE)
        self.assertFalse(ext.critical)
        self.assertEqual([x for x in ext.value],
                         [ExtendedKeyUsageOID.CLIENT_AUTH, ExtendedKeyUsageOID.EMAIL_PROTECTION])

        # { % if cert.dn.subjectAltNames %}
        # subjectAltName = @alt_names
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
        self.assertFalse(ext.critical)
        self.assertEqual([x.value for x in ext.value], [
            'jeroen', 'info@bounca.org'])

        # crlDistributionPoints
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.CRL_DISTRIBUTION_POINTS)
        self.assertTrue(ext.critical)
        crl_dp = ext.value
        self.assertEqual(crl_dp[0].full_name[0].value,
                         'URI:{}{}.crl'.format(int_certificate.crl_distribution_url, int_certificate.shortname))
        self.assertEqual(crl_dp[0].reasons,
                         frozenset([
                             x509.ReasonFlags.key_compromise,
                             x509.ReasonFlags.ca_compromise,
                             x509.ReasonFlags.affiliation_changed,
                             x509.ReasonFlags.superseded,
                             x509.ReasonFlags.privilege_withdrawn,
                             x509.ReasonFlags.cessation_of_operation,
                             x509.ReasonFlags.aa_compromise,
                             x509.ReasonFlags.certificate_hold,
                         ]))

        # OCSP
        # authorityInfoAccess = OCSP;URI:{{cert.ocsp_distribution_host}}
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_INFORMATION_ACCESS)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value[0], x509.AccessDescription(
            AuthorityInformationAccessOID.OCSP,
            x509.UniformResourceIdentifier(int_certificate.ocsp_distribution_host)
        ))

        # subject
        subject = crt.subject
        self.assertIsInstance(subject, x509.Name)
        self.assertListEqual(list(subject), [
            x509.NameAttribute(NameOID.COMMON_NAME, certificate.dn.commonName),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, certificate.dn.organizationName),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, certificate.dn.organizationalUnitName),
            x509.NameAttribute(NameOID.LOCALITY_NAME, certificate.dn.localityName),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, certificate.dn.stateOrProvinceName),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, certificate.dn.emailAddress),
            x509.NameAttribute(NameOID.COUNTRY_NAME, str(certificate.dn.countryName)),
        ])

        # issuer
        issuer = crt.issuer
        self.assertIsInstance(issuer, x509.Name)
        self.assertListEqual(list(issuer), [
            x509.NameAttribute(NameOID.COMMON_NAME, int_certificate.dn.commonName),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, int_certificate.dn.organizationName),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, int_certificate.dn.organizationalUnitName),
            x509.NameAttribute(NameOID.LOCALITY_NAME, int_certificate.dn.localityName),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, int_certificate.dn.stateOrProvinceName),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, int_certificate.dn.emailAddress),
            x509.NameAttribute(NameOID.COUNTRY_NAME, str(int_certificate.dn.countryName)),
        ])
