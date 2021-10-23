# coding: utf-8
from cryptography import x509
from cryptography.x509 import ExtensionOID
# noinspection PyUnresolvedReferences
from cryptography.x509.extensions import ExtensionNotFound
# noinspection PyUnresolvedReferences
from cryptography.x509.oid import NameOID

from certificate_engine.ssl.certificate import Certificate, PassPhraseError, PolicyError
from certificate_engine.ssl.key import Key
from certificate_engine.tests.helpers import CertificateTestCase
from x509_pki.tests.factories import CertificateFactory, DistinguishedNameFactory


class RootCertificateTest(CertificateTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.key = Key().create_key(8192)

    def root_ca_missing_attribute(self, dn, attribute_name):
        with self.assertRaises(PolicyError) as context:
            certificate_request = CertificateFactory(dn=dn)
            certhandler = Certificate()
            certhandler.create_certificate(certificate_request, self.key.serialize())

        self.assertEqual({f'dn__{attribute_name}': f"Attribute '{attribute_name}' is required"},
                         context.exception.args[0])

    def test_generate_root_ca_missing_countryName(self):
        dn = DistinguishedNameFactory(countryName=None,
                                      organizationalUnitName=None,
                                      emailAddress=None)
        self.root_ca_missing_attribute(dn, 'countryName')

    def test_generate_root_ca_missing_countryName_space(self):
        dn = DistinguishedNameFactory(countryName='',
                                      organizationalUnitName=None,
                                      emailAddress=None)
        self.root_ca_missing_attribute(dn, 'countryName')

    def test_generate_root_ca_missing_stateOrProvinceName(self):
        dn = DistinguishedNameFactory(stateOrProvinceName=None,
                                      organizationalUnitName=None,
                                      emailAddress=None)
        self.root_ca_missing_attribute(dn, 'stateOrProvinceName')

    def test_generate_root_ca_missing_stateOrProvinceName_space(self):
        dn = DistinguishedNameFactory.build(stateOrProvinceName='',
                                            organizationalUnitName=None,
                                            emailAddress=None)
        self.root_ca_missing_attribute(dn, 'stateOrProvinceName')

    def test_generate_root_ca_missing_organizationName(self):
        dn = DistinguishedNameFactory.build(organizationName=None,
                                            organizationalUnitName=None,
                                            emailAddress=None)
        self.root_ca_missing_attribute(dn, 'organizationName')

    def test_generate_root_ca_missing_organizationName_space(self):
        dn = DistinguishedNameFactory.build(organizationName='',
                                            organizationalUnitName=None,
                                            emailAddress=None)
        self.root_ca_missing_attribute(dn, 'organizationName')

    def test_generate_root_ca_missing_commonName(self):
        dn = DistinguishedNameFactory.build(commonName='',
                                            organizationalUnitName=None,
                                            emailAddress=None)
        self.root_ca_missing_attribute(dn, 'commonName')

    def test_generate_minimal_root_ca(self):
        dn = DistinguishedNameFactory(organizationalUnitName=None,
                                      emailAddress=None,
                                      localityName=None)
        certificate_request = CertificateFactory(dn=dn)
        certhandler = Certificate()
        certhandler.create_certificate(certificate_request, self.key.serialize())

        crt = certhandler.certificate

        self.assert_basic_information(crt, certificate_request)

        # subject
        self.assert_subject(crt.subject, certificate_request)
        # issuer
        self.assertIsInstance(crt.issuer, x509.Name)
        self.assert_subject(crt.issuer, certificate_request)
        self.assert_crl_distribution(crt, certificate_request)
        self.assert_root_authority(crt)

        # OCSP
        # authorityInfoAccess = OCSP;URI:{{cert.ocsp_distribution_host}}
        self.assert_oscp(crt, certificate_request)

        # authorityKeyIdentifier = keyid:always, issuer
        self.assert_authority_key(crt, self.key)

        # subjectKeyIdentifier = hash
        self.assert_hash(crt)

    def test_generate_root_ca(self):
        certificate_request = CertificateFactory()
        certhandler = Certificate()
        certhandler.create_certificate(certificate_request, self.key.serialize())

        crt = certhandler.certificate

        self.assert_basic_information(crt, certificate_request)
        # subject
        self.assert_subject(crt.subject, certificate_request)
        self.assertListEqual([], crt.subject.get_attributes_for_oid(NameOID.LOCALITY_NAME))
        # issuer
        self.assert_subject(crt.issuer, certificate_request)
        self.assertListEqual([], crt.issuer.get_attributes_for_oid(NameOID.LOCALITY_NAME))

        self.assert_crl_distribution(crt, certificate_request)
        self.assert_root_authority(crt)

        # OCSP
        # authorityInfoAccess = OCSP;URI:{{cert.ocsp_distribution_host}}
        self.assert_oscp(crt, certificate_request)

        # authorityKeyIdentifier = keyid:always, issuer
        self.assert_authority_key(crt, self.key)

        # subjectKeyIdentifier = hash
        self.assert_hash(crt)

    def test_generate_root_ca_no_crl_distribution(self):
        certificate_request = CertificateFactory(crl_distribution_url=None)
        certhandler = Certificate()
        certhandler.create_certificate(certificate_request, self.key.serialize())

        crt = certhandler.certificate

        # subject
        self.assert_subject(crt.subject, certificate_request)
        # issuer
        self.assert_subject(crt.issuer, certificate_request)
        self.assert_root_authority(crt)

        self.assertEqual(crt.serial_number, int(certificate_request.serial))
        self.assertEqual(crt.public_key().public_numbers(), self.key.key.public_key().public_numbers())

        # crlDistributionspoints
        with self.assertRaisesMessage(ExtensionNotFound, "No <ObjectIdentifier(oid=2.5.29.31, name=c"
                                                         "RLDistributionPoints)> extension was found"):
            crt.extensions.get_extension_for_oid(ExtensionOID.CRL_DISTRIBUTION_POINTS)

    def test_generate_root_ca_no_ocsp(self):
        certificate_request = CertificateFactory(ocsp_distribution_host=None)
        certhandler = Certificate()
        certhandler.create_certificate(certificate_request, self.key.serialize())

        crt = certhandler.certificate

        # subject
        self.assert_subject(crt.subject, certificate_request)
        # issuer
        self.assert_subject(crt.issuer, certificate_request)
        self.assert_crl_distribution(crt, certificate_request)
        self.assert_root_authority(crt)

        self.assertEqual(crt.serial_number, int(certificate_request.serial))
        self.assertEqual(crt.public_key().public_numbers(), self.key.key.public_key().public_numbers())

        # OCSP
        # authorityInfoAccess = OCSP;URI:{{cert.ocsp_distribution_host}}
        with self.assertRaisesMessage(ExtensionNotFound, "No <ObjectIdentifier(oid=1.3.6.1.5.5.7.1.1"
                                                         ", name=authorityInfoAccess)> extension was found"):
            crt.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_INFORMATION_ACCESS)

    def test_generate_root_ca_passphrase(self):
        certificate_request = CertificateFactory()
        certhandler = Certificate()
        certhandler.create_certificate(certificate_request, self.key.serialize(passphrase="superSecret"),
                                       passphrase="superSecret")

        crt = certhandler.certificate
        # subject
        self.assert_subject(crt.subject, certificate_request)
        # issuer
        self.assert_subject(crt.issuer, certificate_request)
        self.assert_crl_distribution(crt, certificate_request)
        self.assert_root_authority(crt)

        self.assertEqual(crt.serial_number, int(certificate_request.serial))
        self.assertEqual(crt.public_key().public_numbers(), self.key.key.public_key().public_numbers())

    def test_generate_root_ca_wrong_passphrase(self):
        certificate = CertificateFactory()
        certhandler = Certificate()
        with self.assertRaisesMessage(PassPhraseError, "Bad passphrase, could not decode private key"):
            certhandler.create_certificate(certificate, self.key.serialize(passphrase="superSecret"),
                                           passphrase="superSecret_wrong")

    def test_serialize_root_certificate(self):
        certificate_request = CertificateFactory()
        certhandler = Certificate()
        certhandler.create_certificate(certificate_request, self.key.serialize())

        pem = certhandler.serialize()

        crt = certhandler.load(pem).certificate

        self.assert_basic_information(crt, certificate_request)

    def test_serialize_no_certificate(self):
        certhandler = Certificate()
        with self.assertRaisesMessage(RuntimeError, "No certificate object"):
            certhandler.serialize()
