# coding: utf-8
import datetime

import arrow
from cryptography import x509
from cryptography.x509 import ExtensionOID
from cryptography.x509.extensions import ExtensionNotFound, _key_identifier_from_public_key
from cryptography.x509.oid import AuthorityInformationAccessOID, NameOID
from django.utils import timezone

from bounca.certificate_engine.ssl.certificate import Certificate
from bounca.certificate_engine.ssl.key import Key
from bounca.certificate_engine.tests.testcases import CertificateTestCase
from bounca.x509_pki.tests.factories import CertificateFactory, DistinguishedNameFactory
from bounca.x509_pki.types import CertificateTypes


class CertificateTest(CertificateTestCase):

    def test_generate_root_ca(self):
        certificate = CertificateFactory()
        key = Key(self.repo)
        key.create_key(2048)
        certhandler = Certificate(self.repo)
        certhandler.create_certificate(certificate, key)

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
            x509.NameAttribute(NameOID.COMMON_NAME, certificate.dn.commonName),
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
            path_length=None
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
        self.assertEqual(ext.value.key_identifier, _key_identifier_from_public_key(key.key.public_key()))

        # subjectKeyIdentifier = hash
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_KEY_IDENTIFIER)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value.digest, _key_identifier_from_public_key(key.key.public_key()))

    def test_generate_root_ca_no_crl_distribution(self):
        certificate = CertificateFactory(crl_distribution_url=None)
        key = Key(self.repo)
        key.create_key(2048)
        certhandler = Certificate(self.repo)
        certhandler.create_certificate(certificate, key)

        crt = certhandler.certificate

        self.assertEqual(crt.serial_number, int(certificate.serial))
        self.assertEqual(crt.public_key().public_numbers(), key.key.public_key().public_numbers())

        # crlDistributionspoints
        with self.assertRaisesMessage(ExtensionNotFound, "No <ObjectIdentifier(oid=2.5.29.31, name=c"
                                                         "RLDistributionPoints)> extension was found"):
            crt.extensions.get_extension_for_oid(ExtensionOID.CRL_DISTRIBUTION_POINTS)

    def test_generate_root_ca_no_ocsp(self):
        certificate = CertificateFactory(ocsp_distribution_host=None)
        key = Key(self.repo)
        key.create_key(2048)
        certhandler = Certificate(self.repo)
        certhandler.create_certificate(certificate, key)

        crt = certhandler.certificate

        self.assertEqual(crt.serial_number, int(certificate.serial))
        self.assertEqual(crt.public_key().public_numbers(), key.key.public_key().public_numbers())

        # OCSP
        # authorityInfoAccess = OCSP;URI:{{cert.ocsp_distribution_host}}
        with self.assertRaisesMessage(ExtensionNotFound, "No <ObjectIdentifier(oid=1.3.6.1.5.5.7.1.1"
                                                         ", name=authorityInfoAccess)> extension was found"):
            crt.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_INFORMATION_ACCESS)

    def test_store_root_certificate(self):
        certificate = CertificateFactory()
        key = Key(self.repo)
        key.create_key(2048)
        certhandler = Certificate(self.repo)
        certhandler.create_certificate(certificate, key)

        certhandler.write_certificate('test_root_Ca.pem')

        crt = certhandler.read_certificate('test_root_Ca.pem').certificate

        self.assertEqual(crt.serial_number, int(certificate.serial))
        self.assertEqual(crt.public_key().public_numbers(), key.key.public_key().public_numbers())
        self.assertEqual(crt.not_valid_before, datetime.datetime(
            year=certificate.created_at.year,
            month=certificate.created_at.month,
            day=certificate.created_at.day
        ))

    def test_store_no_certificate(self):
        certhandler = Certificate(self.repo)
        with self.assertRaisesMessage(RuntimeError, "No certificate object"):
            certhandler.write_certificate('test_root_Ca.pem')

    def test_generate_intermediate_certificate(self):
        root_certificate = CertificateFactory(expires_at=arrow.get(timezone.now()).replace(days=+3).date())
        root_key = Key(self.repo)
        root_key.create_key(2048)
        root_certhandler = Certificate(self.repo)
        root_certhandler.create_certificate(root_certificate, root_key)

        subject = DistinguishedNameFactory(countryName=root_certificate.dn.countryName,
                                           stateOrProvinceName=root_certificate.dn.stateOrProvinceName,
                                           organizationName=root_certificate.dn.organizationName)
        certificate = CertificateFactory(type=CertificateTypes.INTERMEDIATE, parent=root_certificate, dn=subject)
        certhandler = Certificate(self.repo)
        key = Key(self.repo)
        key.create_key(2048)
        certhandler.create_certificate(certificate, key, root_cert=root_certhandler, issuer_key=root_key)

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
            x509.NameAttribute(NameOID.COMMON_NAME, certificate.dn.commonName),
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

        # subjectKeyIdentifier = hash
        ext = crt.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_KEY_IDENTIFIER)
        self.assertTrue(ext.critical)
        self.assertEqual(ext.value.digest, _key_identifier_from_public_key(key.key.public_key()))
