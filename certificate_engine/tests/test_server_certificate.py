# coding: utf-8
import arrow
from cryptography.x509 import ExtensionOID
# noinspection PyUnresolvedReferences
from cryptography.x509.extensions import ExtensionNotFound
# noinspection PyUnresolvedReferences
from cryptography.x509.general_name import DNSName, IPAddress
# noinspection PyUnresolvedReferences
from cryptography.x509.oid import ExtendedKeyUsageOID
from django.utils import timezone
from ipaddress import IPv4Address

from certificate_engine.ssl.certificate import Certificate, CertificateError, PolicyError
from certificate_engine.ssl.key import Key
from certificate_engine.tests.helpers import CertificateTestCase
from certificate_engine.types import CertificateTypes
from x509_pki.tests.factories import CertificateFactory, DistinguishedNameFactory


class ServerCertificateTest(CertificateTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root_key = Key().create_key(4096)
        subject = DistinguishedNameFactory(countryName='NL',
                                           stateOrProvinceName='Noord Holland',
                                           organizationName='Repleo')

        cls.root_certificate = CertificateFactory(dn=subject,
                                                  shortname="test_server_root_certificate",
                                                  expires_at=arrow.get(timezone.now()).shift(days=+3).date(),
                                                  key=cls.root_key.serialize())
        certhandler = Certificate()
        certhandler.create_certificate(cls.root_certificate)

        cls.root_certificate.crt = certhandler.serialize()
        cls.root_certificate.save()

        cls.int_key = Key().create_key(4096)
        subject = DistinguishedNameFactory(countryName=cls.root_certificate.dn.countryName,
                                           stateOrProvinceName=cls.root_certificate.dn.stateOrProvinceName,
                                           organizationName=cls.root_certificate.dn.organizationName)
        cls.int_certificate = CertificateFactory(expires_at=arrow.get(timezone.now()).shift(days=+5).date(),
                                                 shortname="test_server_intermediate_certificate",
                                                 type=CertificateTypes.INTERMEDIATE,
                                                 parent=cls.root_certificate, dn=subject,
                                                 key=cls.int_key.serialize())
        int_certhandler = Certificate()
        int_certhandler.create_certificate(cls.int_certificate)
        cls.int_certificate.crt = int_certhandler.serialize()
        cls.int_certificate.save()
        cls.key = Key().create_key(4096)

    def test_generate_server_certificate(self):
        server_subject = DistinguishedNameFactory(subjectAltNames=["www.repleo.nl",
                                                                   "*.bounca.org",
                                                                   "www.mac-usb-serial.com",
                                                                   "127.0.0.1"])
        certificate = CertificateFactory(type=CertificateTypes.SERVER_CERT,
                                         shortname="test_generate_server_certificate",
                                         parent=self.int_certificate, dn=server_subject,
                                         key=self.key.serialize())
        certhandler = Certificate()
        certhandler.create_certificate(certificate)

        crt = certhandler.certificate

        # basicConstraints = CA:FALSE
        # keyUsage = critical, digitalSignature, keyEncipherment
        self.assert_user_certificate(crt)

        # authorityKeyIdentifier = keyid:always, issuer
        self.assert_authority_key(crt, self.int_key, issuer_certificate=self.int_certificate)

        # subjectKeyIdentifier = hash
        self.assert_hash(crt)

        # extendedKeyUsage = serverAuth
        self.assert_extension(crt, ExtensionOID.EXTENDED_KEY_USAGE, [ExtendedKeyUsageOID.SERVER_AUTH])

        # subjectAltName = @alt_names
        self.assert_extension(crt, ExtensionOID.SUBJECT_ALTERNATIVE_NAME,
                              [DNSName('www.repleo.nl'),
                               DNSName('*.bounca.org'),
                               DNSName('www.mac-usb-serial.com'),
                               IPAddress(IPv4Address('127.0.0.1'))])

        # crlDistributionPoints
        self.assert_crl_distribution(crt, self.int_certificate)

        # OCSP
        # authorityInfoAccess = OCSP;URI:{{cert.ocsp_distribution_host}}
        self.assert_oscp(crt, self.int_certificate)

        # subject
        self.assert_subject(crt.subject, certificate)
        # issuer
        self.assert_subject(crt.issuer, self.int_certificate)

    def test_generate_server_certificate_minimal(self):
        server_subject = DistinguishedNameFactory(countryName=None,
                                                  stateOrProvinceName=None,
                                                  localityName=None,
                                                  organizationName=None,
                                                  organizationalUnitName=None,
                                                  emailAddress=None,
                                                  subjectAltNames=None)
        certificate = CertificateFactory(type=CertificateTypes.SERVER_CERT,
                                         shortname="test_generate_server_certificate_minimal",
                                         parent=self.int_certificate, dn=server_subject,
                                         key=self.key.serialize())
        certhandler = Certificate()
        certhandler.create_certificate(certificate)

        crt = certhandler.certificate

        # basicConstraints = CA:FALSE
        # keyUsage = critical, digitalSignature, keyEncipherment
        self.assert_user_certificate(crt)

        # authorityKeyIdentifier = keyid:always, issuer
        self.assert_authority_key(crt, self.int_key, issuer_certificate=self.int_certificate)

        # subjectKeyIdentifier = hash
        self.assert_hash(crt)

        # extendedKeyUsage = serverAuth
        self.assert_extension(crt, ExtensionOID.EXTENDED_KEY_USAGE, [ExtendedKeyUsageOID.SERVER_AUTH])

        # crlDistributionPoints
        self.assert_crl_distribution(crt, self.int_certificate)

        # OCSP
        # authorityInfoAccess = OCSP;URI:{{cert.ocsp_distribution_host}}
        self.assert_oscp(crt, self.int_certificate)

        # subject
        self.assert_subject(crt.subject, certificate)
        # issuer
        self.assert_subject(crt.issuer, self.int_certificate)

    def test_generate_server_certificate_no_subject_altnames(self):
        server_subject = DistinguishedNameFactory(subjectAltNames=None)
        certificate = CertificateFactory(type=CertificateTypes.SERVER_CERT,
                                         parent=self.int_certificate, dn=server_subject,
                                         key=self.key.serialize())
        certhandler = Certificate()
        certhandler.create_certificate(certificate)

        crt = certhandler.certificate

        self.assertEqual(crt.serial_number, int(certificate.serial))
        self.assertEqual(crt.public_key().public_numbers(), self.key.key.public_key().public_numbers())

        with self.assertRaises(ExtensionNotFound):
            crt.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)

    def test_generate_server_certificate_no_intermediate_ca(self):
        server_subject = DistinguishedNameFactory(subjectAltNames=None)
        certificate = CertificateFactory(type=CertificateTypes.SERVER_CERT,
                                         parent=self.root_certificate, dn=server_subject,
                                         key=self.key.serialize())
        certhandler = Certificate()
        certhandler.create_certificate(certificate)

        crt = certhandler.certificate

        self.assertEqual(crt.serial_number, int(certificate.serial))
        self.assertEqual(crt.public_key().public_numbers(), self.key.key.public_key().public_numbers())

        # extendedKeyUsage = serverAuth
        self.assert_extension(crt, ExtensionOID.EXTENDED_KEY_USAGE, [ExtendedKeyUsageOID.SERVER_AUTH])

        # subject
        self.assert_subject(crt.subject, certificate)

        # issuer
        self.assert_subject(crt.issuer, self.root_certificate)

        # authorityKeyIdentifier = keyid:always, issuer
        self.assert_authority_key(crt, self.root_key, issuer_certificate=self.root_certificate)

        # subjectKeyIdentifier = hash
        self.assert_hash(crt)

    def test_generate_server_certificate_duplicate_commonname_intermediate(self):
        server_subject = DistinguishedNameFactory(commonName=self.int_certificate.dn.commonName)
        with self.assertRaises(PolicyError) as context:
            certificate_request = CertificateFactory(type=CertificateTypes.SERVER_CERT,
                                                     shortname="test_certificate_duplicate_commonName_intermediate",
                                                     parent=self.int_certificate, dn=server_subject,
                                                     key=self.key.serialize())
            certhandler = Certificate()
            certhandler.create_certificate(certificate_request)

        self.assertEqual("CommonName '{}' should not be equal to common "
                         "name of parent".format(self.int_certificate.dn.commonName),
                         str(context.exception))

    def test_generate_server_certificate_duplicate_commonname_root(self):
        server_subject = DistinguishedNameFactory(commonName=self.root_certificate.dn.commonName)

        with self.assertRaises(PolicyError) as context:
            certificate_request = CertificateFactory(type=CertificateTypes.SERVER_CERT,
                                                     shortname="test_certificate_duplicate_commonName_root",
                                                     parent=self.int_certificate, dn=server_subject,
                                                     key=self.key.serialize())
            certhandler = Certificate()
            certhandler.create_certificate(certificate_request)

        self.assertEqual("CommonName '{}' should not be equal to common "
                         "name of parent".format(self.root_certificate.dn.commonName),
                         str(context.exception))

    def test_generate_server_certificate_no_parent(self):
        server_subject = DistinguishedNameFactory()
        with self.assertRaises(CertificateError) as context:
            certificate_request = CertificateFactory(type=CertificateTypes.SERVER_CERT,
                                                     shortname="test_generate_server_certificate_no_parent",
                                                     parent=None, dn=server_subject,
                                                     key=self.key.serialize())
            certhandler = Certificate()
            certhandler.create_certificate(certificate_request)

        self.assertEqual("A parent certificate is expected", str(context.exception))

    def test_generate_server_certificate_parent_server_cert(self):
        server_subject = DistinguishedNameFactory(subjectAltNames=None)
        certificate = CertificateFactory(type=CertificateTypes.SERVER_CERT,
                                         shortname="test_generate_server_certificate_parent_server_cert_1",
                                         parent=self.int_certificate, dn=server_subject,
                                         key=self.key.serialize())
        certhandler = Certificate()
        certhandler.create_certificate(certificate)

        server_subject = DistinguishedNameFactory()
        with self.assertRaises(CertificateError) as context:
            certificate_request = CertificateFactory(type=CertificateTypes.SERVER_CERT,
                                                     shortname="test_generate_server_certificate_parent_server_cert_2",
                                                     parent=certificate, dn=server_subject,
                                                     key=self.key.serialize())
            certhandler = Certificate()
            certhandler.create_certificate(certificate_request)

        self.assertEqual("A root or intermediate parent is expected", str(context.exception))
