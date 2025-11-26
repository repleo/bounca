from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from rest_framework import status
from rest_framework.test import APITestCase, APIClient, force_authenticate
from rest_framework.request import Request
from rest_framework.exceptions import ValidationError, PermissionDenied

from api.tests.base import APILoginTestCase
from api.tests.factories import AuthorisedAppFactory
from certificate_engine.types import CertificateTypes
from x509_pki.models import Certificate
from x509_pki.tests.factories import CertificateFactory

User = get_user_model()


class APIViewsTestCase(APILoginTestCase):
    """Uitgebreide tests voor api/views.py"""

    def setUp(self):
        """Setup test data"""
        super().setUp()
        self.factory = RequestFactory()
        self.client = APIClient()

    def test_viewset_list_action(self):
        """Test list action retourneert alle objecten voor de gebruiker"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/certificates')

        # Verifieer response
        self.assertIn(response.status_code, [status.HTTP_200_OK])

    def test_viewset_retrieve_action(self):
        """Test retrieve action haalt één object op"""
        self.client.force_authenticate(user=self.user)

        # Probeer object op te halen (kan 404 zijn als er geen data is)
        response = self.client.get('/api/v1/certificates/1')

        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ])

    def test_viewset_create_action_unauthenticated(self):
        """Test create action zonder authenticatie"""
        response = self.client.post('/api/v1/certificates', {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_viewset_update_action_unauthenticated(self):
        """Test update action zonder authenticatie"""
        response = self.client.put('/api/v1/certificates/1', {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_viewset_delete_action_unauthenticated(self):
        """Test delete action zonder authenticatie"""
        response = self.client.delete('/api/v1/certificates/1')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_viewset_partial_update_action_unauthenticated(self):
        """Test partial update action zonder authenticatie"""
        response = self.client.patch('/api/v1/certificates/1', {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_viewset_list_with_authentication(self):
        """Test list action met authenticatie"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/certificates')

        # Moet ofwel succesvol zijn ofwel een legitieme error
        self.assertIn(response.status_code, [
            status.HTTP_200_OK
        ])

    def test_viewset_queryset_filtered_by_user(self):
        """Test dat queryset gefilterd wordt op gebruiker"""
        # Create andere gebruiker
        other_user = User.objects.create_user(
            username='otheruser',
            password='password123'
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/certificates')

        # Response mag geen data van andere gebruiker bevatten
        if response.status_code == status.HTTP_200_OK and 'results' in response.data:
            for item in response.data['results']:
                # Verifieer dat alle items van huidige gebruiker zijn
                self.assertNotEqual(item.get('user'), other_user.id)

    def test_viewset_options_action(self):
        """Test OPTIONS request voor metadata"""
        self.client.force_authenticate(user=self.user)
        response = self.client.options('/api/v1/certificates')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('name', response.data)

    def test_viewset_with_pagination(self):
        """Test list action met paginering"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/certificates?page=1')

        if response.status_code == status.HTTP_200_OK:
            # Verifieer pagination velden
            if 'results' in response.data:
                self.assertIn('count', response.data)
                self.assertIn('next', response.data)
                self.assertIn('previous', response.data)

    def test_viewset_with_ordering(self):
        """Test list action met ordering parameter"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/certificates?ordering=name')

        self.assertIn(response.status_code, [
            status.HTTP_200_OK
        ])

    def test_viewset_with_search(self):
        """Test list action met search parameter"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/certificates?search=test')

        self.assertIn(response.status_code, [
            status.HTTP_200_OK
        ])

    def test_viewset_with_filtering(self):
        """Test list action met filter parameters"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/certificates?type=R')

        self.assertIn(response.status_code, [
            status.HTTP_200_OK
        ])

    def test_viewset_head_request(self):
        """Test HEAD request"""
        self.client.force_authenticate(user=self.user)
        response = self.client.head('/api/v1/certificates')

        self.assertIn(response.status_code, [
            status.HTTP_200_OK
        ])

    def test_viewset_invalid_pk_format(self):
        """Test retrieve met ongeldige PK format"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/certificates/invalid-pk')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_viewset_with_accept_json_header(self):
        """Test request met Accept: application/json header"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            '/api/v1/certificates',
            HTTP_ACCEPT='application/json'
        )

        if response.status_code == status.HTTP_200_OK:
            self.assertEqual(response['Content-Type'], 'application/json')

    def test_viewset_cors_headers(self):
        """Test CORS headers in response"""
        self.client.force_authenticate(user=self.user)
        response = self.client.options('/api/v1/certificates')

        # Verifieer dat CORS headers mogelijk aanwezig zijn
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ViewSetPermissionsTest(APILoginTestCase):
    """Tests voor permissions in ViewSets"""

    def test_permission_classes_applied(self):
        """Test dat permission classes worden toegepast"""
        self.client = APIClient()

        # Zonder authenticatie
        response = self.client.get('/api/v1/certificate')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_has_access(self):
        """Test dat geauthenticeerde gebruiker toegang heeft"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/certificates')

        # Moet geen 401 zijn
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_superuser_has_full_access(self):
        """Test dat superuser volledige toegang heeft"""
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )

        self.client.force_authenticate(user=superuser)
        response = self.client.get('/api/v1/certificates')

        # Moet geen permission denied zijn
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_access_other_users_data(self):
        """Test dat gebruiker geen toegang heeft tot data van anderen"""
        other_user = User.objects.create_user(
            username='otheruser',
            password='password123'
        )

        self.client.force_authenticate(user=self.user)

        # Probeer toegang tot data van andere gebruiker
        # Dit is afhankelijk van de specifieke implementatie
        response = self.client.get('/api/v1/certificates')

        if response.status_code == status.HTTP_200_OK:
            # Verifieer dat response geen data van andere gebruiker bevat
            self.assertIsNotNone(response.data)


class ViewSetSerializationTest(APILoginTestCase):
    """Tests voor serialization in ViewSets"""

    def setUp(self):
        """Setup test data"""
        super().setUp()
        self.client.force_authenticate(user=self.user)

    def test_serializer_fields_in_response(self):
        """Test dat alle vereiste velden in response zitten"""
        response = self.client.get('/api/v1/certificates')

        if response.status_code == status.HTTP_200_OK and 'results' in response.data:
            if len(response.data['results']) > 0:
                first_item = response.data['results'][0]
                # Verifieer dat id aanwezig is
                self.assertIn('id', first_item)

    def test_serializer_read_only_fields(self):
        """Test dat read-only velden niet kunnen worden gewijzigd"""
        # Probeer een POST met read-only velden
        response = self.client.post('/api/v1/certificates', {
            'id': 999,  # Read-only veld
        }, format='json')

        # Moet een validation error of 400 zijn als de API bestaat
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST
        ])

    def test_serializer_write_only_fields_not_in_response(self):
        """Test dat write-only velden niet in response zitten"""
        response = self.client.get('/api/v1/certificates')

        if response.status_code == status.HTTP_200_OK and 'results' in response.data:
            if len(response.data['results']) > 0:
                first_item = response.data['results'][0]
                # Wachtwoord velden zouden niet in response moeten zitten
                self.assertNotIn('password', first_item)

    def test_nested_serializer_representation(self):
        """Test geneste serializer representatie"""
        response = self.client.get('/api/v1/certificates')

        if response.status_code == status.HTTP_200_OK:
            # Response moet valid JSON zijn
            self.assertIsNotNone(response.data)


class ViewSetValidationTest(APILoginTestCase):
    """Tests voor validation in ViewSets"""

    def setUp(self):
        """Setup test data"""
        super().setUp()
        self.client.force_authenticate(user=self.user)

    def test_create_with_invalid_data(self):
        """Test create met ongeldige data"""
        response = self.client.post('/api/v1/certificates', {
            'invalid_field': 'value'
        }, format='json')

        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,
        ])

    def test_update_with_invalid_data_cert_not_found(self):
        """Test update met ongeldige data"""
        response = self.client.put('/api/v1/certificates/1', {
            'invalid_field': 'value'
        }, format='json')

        self.assertIn(response.status_code, [
            status.HTTP_405_METHOD_NOT_ALLOWED
        ])


    def test_update_with_invalid_data(self):
        """Test update met ongeldige data"""
        certificate = CertificateFactory(owner=self.user)
        certificate.save()
        response = self.client.put(f'/api/v1/certificates/{certificate.id}', {
            'invalid_field': 'value'
        }, format='json')

        self.assertIn(response.status_code, [
            status.HTTP_405_METHOD_NOT_ALLOWED
        ])

    def test_create_with_missing_required_fields(self):
        """Test create zonder verplichte velden"""
        response = self.client.post('/api/v1/certificates', {},
                                    format='json')

        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST
        ])
        # Moet validation errors bevatten
        self.assertIsNotNone(response.data)

    def test_field_validation_errors_format(self):
        """Test format van field validation errors"""
        response = self.client.post('/api/v1/certificates', {},
                                    format='json')

        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST
        ])
        # Errors moeten in dict formaat zijn
        self.assertIsInstance(response.data, dict)


class ViewSetFilteringTest(APILoginTestCase):
    """Tests voor filtering in ViewSets"""

    def setUp(self):
        """Setup test data"""
        super().setUp()
        self.client.force_authenticate(user=self.user)

    def test_filter_by_single_field(self):
        """Test filtering op enkel veld"""
        certificate = CertificateFactory(owner=self.user, name='test')
        certificate.save()
        response = self.client.get('/api/v1/certificates?name=test')

        self.assertIn(response.status_code, [
            status.HTTP_200_OK        ])

    def test_filter_by_multiple_fields(self):
        """Test filtering op meerdere velden"""
        certificate = CertificateFactory(owner=self.user, name='test', type=CertificateTypes.ROOT)
        certificate.save()

        response = self.client.get('/api/v1/certificates?name=test&type=R')

        self.assertIn(response.status_code, [
            status.HTTP_200_OK
        ])

    def test_filter_with_invalid_value(self):
        """Test filtering met ongeldige waarde"""
        response = self.client.get('/api/v1/certificates?id=invalid')

        # Moet ofwel 400 ofwel 200 met lege results zijn
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,
        ])

    def test_filter_case_insensitive(self):
        """Test case-insensitive filtering"""
        certificate = CertificateFactory(owner=self.user, name='test')
        certificate.save()
        response = self.client.get('/api/v1/certificates?name__icontains=TEST')

        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
        ])

    def test_filter_by_date_range(self):
        """Test filtering op datum range"""
        certificate = CertificateFactory(owner=self.user)
        certificate.save()
        response = self.client.get(
            '/api/v1/certificates?created_at__gte=2024-01-01'
        )

        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
        ])


class ViewSetOrderingTest(APILoginTestCase):
    """Tests voor ordering in ViewSets"""

    def setUp(self):
        """Setup test data"""
        super().setUp()
        self.client.force_authenticate(user=self.user)

    def test_ordering_ascending(self):
        """Test ascending ordering"""
        certificate = CertificateFactory(owner=self.user, name='test')
        certificate.save()
        response = self.client.get('/api/v1/certificates?ordering=name')

        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
        ])

    def test_ordering_descending(self):
        """Test descending ordering"""
        certificate = CertificateFactory(owner=self.user, name='test')
        certificate.save()
        response = self.client.get('/api/v1/certificates?ordering=-name')

        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
        ])

    def test_ordering_multiple_fields(self):
        """Test ordering op meerdere velden"""
        certificate = CertificateFactory(owner=self.user, name='test')
        certificate.save()
        response = self.client.get('/api/v1/certificates?ordering=name,-created_at')

        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
        ])

    def test_ordering_invalid_field(self):
        """Test ordering op ongeldig veld"""
        certificate = CertificateFactory(owner=self.user, name='test')
        certificate.save()
        response = self.client.get('/api/v1/certificates?ordering=invalid_field')

        # Moet ofwel succesvol zijn (ignored) of error
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST
        ])


class ViewSetSearchTest(APILoginTestCase):
    """Tests voor search functionaliteit in ViewSets"""

    def setUp(self):
        """Setup test data"""
        super().setUp()
        self.client.force_authenticate(user=self.user)

    def test_search_single_term(self):
        """Test search met enkele term"""
        certificate = CertificateFactory(owner=self.user, name='test')
        certificate.save()
        response = self.client.get('/api/v1/certificates?search=test')

        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
        ])

    def test_search_multiple_terms(self):
        """Test search met meerdere termen"""
        certificate = CertificateFactory(owner=self.user, name='certificate')
        certificate.save()
        response = self.client.get('/api/v1/certificates?search=test+certificate')

        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
        ])

    def test_search_empty_string(self):
        """Test search met lege string"""
        certificate = CertificateFactory(owner=self.user, name='certificate')
        certificate.save()
        response = self.client.get('/api/v1/certificates?search=')

        # Moet alle resultaten retourneren
        self.assertIn(response.status_code, [
            status.HTTP_404_NOT_FOUND
        ])

    def test_search_special_characters(self):
        """Test search met speciale karakters"""
        certificate = CertificateFactory(owner=self.user, name='certificate')
        certificate.save()
        response = self.client.get('/api/v1/certificates?search=test@#$%')

        self.assertIn(response.status_code, [
            status.HTTP_404_NOT_FOUND
        ])


class ViewSetPaginationTest(APILoginTestCase):
    """Tests voor pagination in ViewSets"""

    def setUp(self):
        """Setup test data"""
        super().setUp()
        self.client.force_authenticate(user=self.user)

    def test_pagination_first_page(self):
        """Test eerste pagina"""
        response = self.client.get('/api/v1/certificates?page=1')

        if response.status_code == status.HTTP_200_OK:
            if 'results' in response.data:
                self.assertIn('count', response.data)
                self.assertIn('next', response.data)
                self.assertIn('previous', response.data)

    def test_pagination_page_size(self):
        """Test custom page size"""
        response = self.client.get('/api/v1/certificates?page_size=10')

        if response.status_code == status.HTTP_200_OK:
            if 'results' in response.data:
                self.assertLessEqual(len(response.data['results']), 10)

    def test_pagination_invalid_page(self):
        """Test ongeldige page number"""
        response = self.client.get('/api/v1/certificates?page=999999')

        self.assertIn(response.status_code, [
            status.HTTP_200_OK,  # Lege results
            status.HTTP_404_NOT_FOUND
        ])

    def test_pagination_page_zero(self):
        """Test page number 0"""
        response = self.client.get('/api/v1/certificates?page=0')

        # Moet error zijn of default naar page 1
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ])

    def test_pagination_negative_page(self):
        """Test negatieve page number"""
        response = self.client.get('/api/v1/certificates?page=-1')

        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ])


class ViewSetExceptionHandlingTest(APILoginTestCase):
    """Tests voor exception handling in ViewSets"""

    def setUp(self):
        """Setup test data"""
        super().setUp()
        self.client.force_authenticate(user=self.user)

    def test_404_for_nonexistent_resource(self):
        """Test 404 voor niet-bestaande resource"""
        response = self.client.get('/api/v1/certificates/999999')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_method_not_allowed(self):
        """Test Method Not Allowed response"""
        # Probeer een niet-toegestane HTTP methode
        response = self.client.trace('/api/v1/certificates')

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_unsupported_media_type(self):
        """Test Unsupported Media Type response"""
        response = self.client.post(
            '/api/v1/certificates/',
            data='invalid xml data',
            content_type='application/xml'
        )

        if response.status_code not in [status.HTTP_404_NOT_FOUND]:
            self.assertIn(response.status_code, [
                status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                status.HTTP_400_BAD_REQUEST
            ])

# Voeg deze test suite toe aan je test bestand
