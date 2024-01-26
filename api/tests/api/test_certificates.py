import io
import zipfile
from uuid import UUID

import arrow
from django.utils import timezone
from rest_framework import status

from api.tests.base import APILoginTestCase
from certificate_engine.ssl.info import get_certificate_info
from certificate_engine.types import CertificateTypes
from x509_pki.models import Certificate
from x509_pki.tests.factories import CertificateFactory, DistinguishedNameFactory


class ServerCertificateTest(APILoginTestCase):
    base_url = "/api/v1/certificates"

    @classmethod
    def setUpTestData(cls):
        cls.maxDiff = None

        super().setUpTestData()
        cls.root_dn = DistinguishedNameFactory(
            countryName="NL",
            stateOrProvinceName="Noord-Holland",
            localityName="Amsterdam",
            organizationName="Repleo",
            organizationalUnitName="IT Department",
            emailAddress="info@repleo.nl",
            commonName="ca.bounca.org",
            subjectAltNames=["demo.bounca.org"],
        )
        cls.user = cls.auth_app.user

        cls.ca = CertificateFactory(
            expires_at=arrow.get(timezone.now()).shift(years=+10).date(),
            name="repleo root ca",
            type=CertificateTypes.ROOT,
            owner=cls.user,
            passphrase_out="welkom123",
            passphrase_out_confirmation="welkom123",
            dn=cls.root_dn,
            crl_distribution_url="https://example.com/root_ca.crl",
            ocsp_distribution_host="https://example.com/ocsp/",
        )
        cls.ca.save()
        cls.ca.refresh_from_db()
        cls.ca = Certificate.objects.get(pk=cls.ca.pk)

        subject = DistinguishedNameFactory(
            countryName=cls.ca.dn.countryName,
            stateOrProvinceName=cls.ca.dn.stateOrProvinceName,
            organizationName=cls.ca.dn.organizationName,
        )

        cls.int_certificate = CertificateFactory(
            expires_at=arrow.get(timezone.now()).shift(years=+5).date(),
            name="test client intermediate certificate",
            type=CertificateTypes.INTERMEDIATE,
            parent=cls.ca,
            dn=subject,
            passphrase_out="welkom1234",
            passphrase_out_confirmation="welkom1234",
            passphrase_issuer="welkom123",
            crl_distribution_url="https://example.com/crl/cert1.crl",
            ocsp_distribution_host="https://example.com/ocsp/",
        )

        cls.int_certificate.save()

        subject2 = DistinguishedNameFactory(
            countryName=cls.ca.dn.countryName,
            stateOrProvinceName=cls.ca.dn.stateOrProvinceName,
            organizationName=cls.ca.dn.organizationName,
        )

        cls.int_certificate2 = CertificateFactory(
            expires_at=arrow.get(timezone.now()).shift(years=+5).date(),
            name="test client intermediate certificate2",
            type=CertificateTypes.INTERMEDIATE,
            parent=cls.ca,
            dn=subject2,
            passphrase_out="welkom1235",
            passphrase_out_confirmation="welkom1235",
            passphrase_issuer="welkom123",
            crl_distribution_url="https://example.com/crl/cert2.crl",
            ocsp_distribution_host="https://example.com/ocsp/",
        )

        cls.int_certificate2.save()
        cls.dn = []
        cls.cert = []
        for i in range(4):
            cls.dn.insert(
                i,
                DistinguishedNameFactory(
                    countryName="NL",
                    stateOrProvinceName="Noord-Holland",
                    localityName="Amsterdam",
                    organizationName="Repleo",
                    organizationalUnitName="IT Department",
                    emailAddress="info@repleo.nl",
                    commonName="www.repleo.nl.setup",
                    subjectAltNames=["repleo.nl"],
                ),
            )

            cert = Certificate(parent=cls.int_certificate, dn=cls.dn[i], passphrase_issuer="welkom1234")
            cert.type = CertificateTypes.SERVER_CERT
            cert.name = f"www.repleo.nl - {i}"
            cert.dn = cls.dn[i]
            cert.expires_at = arrow.get(timezone.now()).shift(years=+1).date()

            cert.revoked_at = None
            cert.owner = cls.user
            cert.save()
            cert.refresh_from_db()
            cls.cert.insert(i, cert)

    def test_retrieve_certificates(self):
        test_uri = f"{self.base_url}"
        response = self.client.get(test_uri, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()
        self.assertEqual(len(result), 7)
        for i in range(4):
            # support for leap year
            if result[3 - i]["days_valid"] == 366:
                result[3 - i]["days_valid"] = 365

            self.assertDictEqual(
                result[3 - i],
                {
                    "created_at": self.cert[i].created_at.strftime("%Y-%m-%d"),
                    "crl_distribution_url": None,
                    "days_valid": 365,
                    "dn": {
                        "commonName": "www.repleo.nl.setup",
                        "countryName": "NL",
                        "emailAddress": "info@repleo.nl",
                        "localityName": "Amsterdam",
                        "organizationName": "Repleo",
                        "organizationalUnitName": "IT Department",
                        "stateOrProvinceName": "Noord-Holland",
                        "subjectAltNames": ["repleo.nl"],
                    },
                    "expired": False,
                    "expires_at": self.cert[i].expires_at.strftime("%Y-%m-%d"),
                    "id": self.cert[i].id,
                    "keystore": {"fingerprint": self.cert[i].keystore.fingerprint},
                    "name": f"www.repleo.nl - {i}",
                    "ocsp_distribution_host": None,
                    "parent": 2,
                    "passphrase_issuer": "",
                    "passphrase_out": "",
                    "passphrase_out_confirmation": "",
                    "revoked": False,
                    "revoked_at": None,
                    "serial": str(self.cert[i].serial),
                    "type": "S",
                },
            )

    def test_retrieve_server_certificates(self):
        test_uri = f"{self.base_url}?type=S"
        response = self.client.get(test_uri, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()
        self.assertEqual(len(result), 4)
        for i in range(4):
            self.assertEqual(result[3 - i]["name"], f"www.repleo.nl - {i}")

    def test_retrieve_single_server_certificates(self):
        test_uri = f"{self.base_url}/{self.cert[0].id}"
        response = self.client.get(test_uri, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()
        self.assertEqual(result["name"], "www.repleo.nl - 0")

    def test_create_server_certificates_no_passphrase(self):
        test_uri = f"{self.base_url}"
        expire_date = arrow.get(timezone.now()).shift(years=+1).date()
        cert = {
            "crl_distribution_url": None,
            "days_valid": 365,
            "dn": {
                "commonName": "www.repleo.nl.test post",
                "countryName": "NL",
                "emailAddress": "info@repleo.nl",
                "localityName": "Amsterdam",
                "organizationName": "Repleo",
                "organizationalUnitName": "IT Department",
                "stateOrProvinceName": "Noord-Holland",
                "subjectAltNames": ["repleo.nl"],
            },
            "expired": False,
            "expires_at": expire_date,
            "name": "www.repleo.nl - test post",
            "parent": self.int_certificate.id,
            "passphrase_issuer": "",
            "type": "S",
        }
        response = self.client.post(test_uri, data=cert, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.json(), {"passphrase_issuer": ["Passphrase incorrect. Not allowed to revoke your " "certificate"]}
        )

        cert.pop("passphrase_issuer")
        response = self.client.post(test_uri, data=cert, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.json(), {"non_field_errors": ["Passphrase incorrect. Not allowed to revoke your " "certificate"]}
        )

    def test_create_server_certificate(self):
        test_uri = f"{self.base_url}"
        expire_date = arrow.get(timezone.now()).shift(years=+1).date()
        cert = {
            "crl_distribution_url": None,
            "days_valid": 365,
            "dn": {
                "commonName": "www.repleo.nl.test post",
                "countryName": "NL",
                "emailAddress": "info@repleo.nl",
                "localityName": "Amsterdam",
                "organizationName": "Repleo",
                "organizationalUnitName": "IT Department",
                "stateOrProvinceName": "Noord-Holland",
                "subjectAltNames": ["repleo.nl"],
            },
            "expired": False,
            "expires_at": expire_date,
            "name": "www.repleo.nl - test post",
            "parent": self.int_certificate.id,
            "passphrase_issuer": "welkom1234",
            "passphrase_out": None,
            "passphrase_out_confirmation": None,
            "type": "S",
        }
        response = self.client.post(test_uri, data=cert, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        result = response.json()
        self.assertIsNotNone(result.pop("created_at"))
        self.assertIsNotNone(result.pop("id"))
        self.assertIsNotNone(result.pop("keystore"))
        self.assertIsNotNone(result.pop("serial"))

        # support for leap year
        if result["days_valid"] == 366:
            result["days_valid"] = 365
        self.assertDictEqual(
            result,
            {
                "crl_distribution_url": None,
                "days_valid": 365,
                "dn": {
                    "commonName": "www.repleo.nl.test post",
                    "countryName": "NL",
                    "emailAddress": "info@repleo.nl",
                    "localityName": "Amsterdam",
                    "organizationName": "Repleo",
                    "organizationalUnitName": "IT Department",
                    "stateOrProvinceName": "Noord-Holland",
                    "subjectAltNames": ["repleo.nl"],
                },
                "expired": False,
                "expires_at": expire_date.strftime("%Y-%m-%d"),
                "name": "www.repleo.nl - test post",
                "ocsp_distribution_host": None,
                "parent": self.int_certificate.id,
                "passphrase_issuer": None,
                "passphrase_out": None,
                "passphrase_out_confirmation": None,
                "revoked": False,
                "revoked_at": None,
                "type": "S",
            },
        )

    def test_revoke_server_certificates_no_passphrase(self):
        dn = DistinguishedNameFactory(
            countryName="NL",
            stateOrProvinceName="Noord-Holland",
            localityName="Amsterdam",
            organizationName="Repleo",
            organizationalUnitName="IT Department",
            emailAddress="info@repleo.nl",
            commonName="www.repleo.nl - revoke",
            subjectAltNames=["repleo.nl"],
        )
        cert = Certificate(parent=self.int_certificate, dn=dn, passphrase_issuer="welkom1234")
        cert.type = CertificateTypes.SERVER_CERT
        cert.name = "www.repleo.nl - revoke"
        cert.expires_at = arrow.get(timezone.now()).shift(years=+1).date()
        cert.dn = dn
        cert.revoked_at = None
        cert.owner = self.user
        cert.save()
        cert.refresh_from_db()

        test_uri = f"{self.base_url}/{cert.id}"
        data = {}
        response = self.client.delete(test_uri, data=data, format="json")
        self.assertDictEqual(response.json(), {"passphrase_issuer": ["This field is required."]})
        data = {
            "passphrase_issuer": None,
        }
        response = self.client.delete(test_uri, data=data, format="json")
        self.assertDictEqual(response.json(), {"passphrase_issuer": ["This field may not be null."]})
        data = {
            "passphrase_issuer": "",
        }
        response = self.client.delete(test_uri, data=data, format="json")
        self.assertDictEqual(response.json(), {"passphrase_issuer": ["This field may not be blank."]})
        data = {
            "passphrase_issuer": "wrong",
        }
        response = self.client.delete(test_uri, data=data, format="json")
        self.assertDictEqual(
            response.json(), {"passphrase_issuer": ["Passphrase incorrect. Not allowed to revoke your " "certificate"]}
        )

    def test_revoke_server_certificate(self):
        dn = DistinguishedNameFactory(
            countryName="NL",
            stateOrProvinceName="Noord-Holland",
            localityName="Amsterdam",
            organizationName="Repleo",
            organizationalUnitName="IT Department",
            emailAddress="info@repleo.nl",
            commonName="www.repleo.nl - revoke",
            subjectAltNames=["repleo.nl"],
        )
        cert = Certificate(parent=self.int_certificate, dn=dn, passphrase_issuer="welkom1234")
        cert.type = CertificateTypes.SERVER_CERT
        cert.name = "www.repleo.nl - revoke"
        cert.expires_at = arrow.get(timezone.now()).shift(years=+1).date()
        cert.dn = dn
        cert.revoked_at = None
        cert.owner = self.user
        cert.save()
        cert.refresh_from_db()

        test_uri = f"{self.base_url}/{cert.id}"
        data = {
            "passphrase_issuer": "welkom1234",
        }
        response = self.client.delete(test_uri, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        cert.refresh_from_db()

        self.assertIsNotNone(cert.revoked_at)
        self.assertIsNotNone(cert.slug_revoked_at)
        self.assertNotEqual(cert.revoked_uuid, UUID(int=0))

    def test_info_server_certificate(self):
        test_uri = f"{self.base_url}/{self.cert[0].id}/info"
        response = self.client.get(test_uri, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()
        self.assertTrue("CN=www.repleo.nl.setup" in result["text"].replace(" ", ""))
        self.assertTrue("TLS Web Server Authentication" in result["text"])

    def test_download_server_certificate(self):
        test_uri = f"{self.base_url}/{self.cert[0].id}/download"
        response = self.client.get(test_uri, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        with zipfile.ZipFile(io.BytesIO(response.content)) as cert_zipfile:
            self.assertListEqual(
                [info.filename for info in cert_zipfile.infolist()],
                [
                    "rootca.pem",
                    "intermediate.pem",
                    "intermediate_root-chain.pem",
                    "www.repleo.nl_-_0.pem",
                    "www.repleo.nl_-_0-chain.pem",
                    "www.repleo.nl_-_0.key",
                    "www.repleo.nl_-_0.p12",
                    "www.repleo.nl_-_0.legacy.p12",
                ],
            )
            cert_pem = cert_zipfile.read("www.repleo.nl_-_0.pem").decode("utf-8")
            info_txt = get_certificate_info(cert_pem)
            self.assertTrue("CN=www.repleo.nl.setup" in info_txt.replace(" ", ""))
            self.assertTrue("TLS Web Server Authentication" in info_txt)

    def test_renew_server_certificate(self):
        dn = DistinguishedNameFactory(
            countryName="NL",
            stateOrProvinceName="Noord-Holland",
            localityName="Amsterdam",
            organizationName="Repleo",
            organizationalUnitName="IT Department",
            emailAddress="info@repleo.nl",
            commonName="www.repleo.nl-revoke",
            subjectAltNames=["repleo.nl"],
        )
        cert = Certificate(parent=self.int_certificate, dn=dn, passphrase_issuer="welkom1234")
        cert.type = CertificateTypes.SERVER_CERT
        cert.name = "www.repleo.nl - revoke"
        cert.expires_at = arrow.get(timezone.now()).shift(years=+1).date()
        cert.dn = dn
        cert.revoked_at = None
        cert.owner = self.user
        cert.save()
        cert.refresh_from_db()

        renew_expire_date = arrow.get(timezone.now()).shift(years=+2).date()
        test_uri = f"{self.base_url}/{cert.id}/renew"
        data = {
            "expires_at": renew_expire_date,
            "passphrase_issuer": "welkom1234",
            "passphrase_out": None,
            "passphrase_out_confirmation": None,
        }
        response = self.client.patch(test_uri, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        cert.refresh_from_db()

        self.assertIsNotNone(cert.revoked_at)
        self.assertIsNotNone(cert.slug_revoked_at)
        self.assertNotEqual(cert.revoked_uuid, UUID(int=0))

        result = response.json()
        self.assertIsNotNone(result.pop("created_at"))
        renewed_cert_id = result.pop("id")
        self.assertNotEqual(renewed_cert_id, cert.id)
        self.assertIsNotNone(result.pop("keystore"))
        self.assertIsNotNone(result.pop("serial"))

        self.assertDictEqual(
            result,
            {
                "crl_distribution_url": None,
                "days_valid": 731,
                "dn": {
                    "commonName": "www.repleo.nl-revoke",
                    "countryName": "NL",
                    "emailAddress": "info@repleo.nl",
                    "localityName": "Amsterdam",
                    "organizationName": "Repleo",
                    "organizationalUnitName": "IT Department",
                    "stateOrProvinceName": "Noord-Holland",
                    "subjectAltNames": ["repleo.nl"],
                },
                "expired": False,
                "expires_at": renew_expire_date.strftime("%Y-%m-%d"),
                "name": "www.repleo.nl - revoke",
                "ocsp_distribution_host": None,
                "parent": self.int_certificate.id,
                "passphrase_issuer": None,
                "passphrase_out": None,
                "passphrase_out_confirmation": None,
                "revoked": False,
                "revoked_at": None,
                "type": "S",
            },
        )

        test_uri = f"{self.base_url}/{renewed_cert_id}/download"
        response = self.client.get(test_uri, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        with zipfile.ZipFile(io.BytesIO(response.content)) as cert_zipfile:
            cert_pem = cert_zipfile.read("www.repleo.nl_-_revoke.pem").decode("utf-8")
            info_txt = get_certificate_info(cert_pem)
            self.assertTrue("CN=www.repleo.nl-revoke" in info_txt.replace(" ", ""))
            self.assertTrue("TLS Web Server Authentication" in info_txt)

    def test_renew_revoked_server_certificate(self):
        dn = DistinguishedNameFactory(
            countryName="NL",
            stateOrProvinceName="Noord-Holland",
            localityName="Amsterdam",
            organizationName="Repleo",
            organizationalUnitName="IT Department",
            emailAddress="info@repleo.nl",
            commonName="www.repleo.nl - revoke",
            subjectAltNames=["repleo.nl"],
        )
        cert = Certificate(parent=self.int_certificate, dn=dn, passphrase_issuer="welkom1234")
        cert.type = CertificateTypes.SERVER_CERT
        cert.name = "www.repleo.nl - revoke"
        cert.expires_at = arrow.get(timezone.now()).shift(years=+1).date()
        cert.dn = dn
        cert.revoked_at = None
        cert.owner = self.user
        cert.save()
        cert.refresh_from_db()
        cert.delete()
        cert.refresh_from_db()

        renew_expire_date = arrow.get(timezone.now()).shift(years=+2).date()
        test_uri = f"{self.base_url}/{cert.id}/renew"
        data = {
            "expires_at": renew_expire_date,
            "passphrase_issuer": "welkom1234",
            "passphrase_out": None,
            "passphrase_out_confirmation": None,
        }
        response = self.client.patch(test_uri, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), ["Cannot renew a revoked certificate"])
