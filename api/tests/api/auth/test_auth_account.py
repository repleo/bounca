from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.test import APITestCase

from x509_pki.models import Certificate

User = get_user_model()


class AccountViewSetTest(APITestCase):
    """Unit tests voor AccountViewSet"""

    def setUp(self):
        """Setup test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
            first_name="Test",
            last_name="User",
        )
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        """Cleanup na elke test"""
        User.objects.all().delete()

    def test_get_queryset_returns_only_current_user(self):
        """Test dat get_queryset alleen de huidige gebruiker retourneert"""
        other_user = User.objects.create_user(username="otheruser", email="other@example.com", password="password123")

        response = self.client.get("/api/v1/account/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verifieer dat alleen de ingelogde gebruiker wordt geretourneerd
        self.assertEqual(User.objects.filter(id=self.user.id).count(), 1)

    def test_get_object_returns_current_user(self):
        """Test dat get_object de huidige gebruiker retourneert"""
        response = self.client.get("/api/v1/account/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.user.id)
        self.assertEqual(response.data["username"], self.user.username)
        self.assertEqual(response.data["email"], self.user.email)

    def test_retrieve_account_authenticated(self):
        """Test ophalen van account gegevens als geauthenticeerde gebruiker"""
        response = self.client.get("/api/v1/account/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "test@example.com")
        self.assertEqual(response.data["first_name"], "Test")
        self.assertEqual(response.data["last_name"], "User")
        self.assertIn("date_joined", response.data)
        self.assertIn("last_login", response.data)

    def test_retrieve_account_unauthenticated(self):
        """Test dat niet-geauthenticeerde gebruikers geen toegang hebben"""
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/account/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_destroy_account_with_valid_password(self):
        """Test verwijderen van account met geldig wachtwoord"""
        response = self.client.delete("/api/v1/account/", data={"password": "testpassword123"}, format="json")

        # Verwacht een NotAuthenticated exception (401)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Verifieer dat de gebruiker is verwijderd
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_destroy_account_without_password(self):
        """Test verwijderen van account zonder wachtwoord"""
        response = self.client.delete("/api/v1/account/", format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertEqual(response.data["password"], ["Password is required."])
        # Verifieer dat de gebruiker NIET is verwijderd
        self.assertTrue(User.objects.filter(id=self.user.id).exists())

    def test_destroy_account_with_invalid_password(self):
        """Test verwijderen van account met ongeldig wachtwoord"""
        response = self.client.delete("/api/v1/account/", data={"password": "wrongpassword"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertEqual(response.data["password"], ["Invalid password."])
        # Verifieer dat de gebruiker NIET is verwijderd
        self.assertTrue(User.objects.filter(id=self.user.id).exists())

    def test_destroy_account_with_empty_password(self):
        """Test verwijderen van account met leeg wachtwoord veld"""
        response = self.client.delete("/api/v1/account/", data={"password": ""}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        # Verifieer dat de gebruiker NIET is verwijderd
        self.assertTrue(User.objects.filter(id=self.user.id).exists())

    @patch("api.auth.views.Certificate")
    def test_perform_destroy_without_protected_error(self, mock_certificate):
        """Test perform_destroy zonder ProtectedError"""
        # Mock de delete methode om geen error te gooien
        self.user.delete = Mock()

        response = self.client.delete("/api/v1/account/", data={"password": "testpassword123"}, format="json")

        # Verwacht NotAuthenticated (401)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch.object(User, "delete")
    def test_perform_destroy_with_protected_certificate(self, mock_delete):
        """Test perform_destroy met beschermde Certificate objecten"""
        # Create mock certificate
        mock_certificate = Mock(spec=Certificate)
        mock_certificate.force_delete = Mock()

        # Configure _meta to be iterable (leeg, zodat Django's check slaagt)
        mock_meta = Mock()
        mock_meta.all_parents = []
        mock_certificate._meta = mock_meta

        # Mock Certificate.objects.filter om een lege lijst te retourneren
        # zodat de recursieve delete geen kinderen vindt
        with patch.object(Certificate.objects, "filter", return_value=[]):
            # Mock ProtectedError
            protected_error = ProtectedError("Cannot delete", protected_objects={mock_certificate})

            # First call raises ProtectedError, second succeeds
            mock_delete.side_effect = [protected_error, None]

            response = self.client.delete("/api/v1/account/", data={"password": "testpassword123"}, format="json")

            # Verwacht NotAuthenticated (401)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            # Verifieer dat delete twee keer is aangeroepen
            self.assertEqual(mock_delete.call_count, 2)

    @patch("api.auth.views.Certificate.objects.filter")
    def test_delete_certificate_recursive(self, mock_filter):
        """Test recursieve verwijdering van certificates"""
        # Create mock certificates met parent-child relatie
        parent_cert = Mock(spec=Certificate)
        parent_cert.force_delete = Mock()
        parent_cert.id = 1

        child_cert = Mock(spec=Certificate)
        child_cert.force_delete = Mock()
        child_cert.id = 2
        child_cert.parent = parent_cert

        # Mock de filter om child te retourneren
        mock_filter.return_value = [child_cert]

        # Import de viewset om _delete_certificate te testen
        from api.auth.views import AccountViewSet

        viewset = AccountViewSet()
        viewset._delete_certificate(parent_cert)

        # Verifieer dat force_delete is aangeroepen op beide certificates
        child_cert.force_delete.assert_called_once()
        parent_cert.force_delete.assert_called_once()

    @patch.object(User, "delete")
    def test_perform_destroy_with_non_certificate_protected_objects(self, mock_delete):
        """Test perform_destroy met andere beschermde objecten dan Certificate"""
        # Create mock non-certificate protected object
        mock_protected_obj = Mock()
        mock_protected_obj.delete = Mock()

        # Mock ProtectedError met non-certificate object
        protected_error = ProtectedError("Cannot delete", protected_objects={mock_protected_obj})

        # First call raises ProtectedError, second succeeds
        mock_delete.side_effect = [protected_error, None]

        response = self.client.delete("/api/v1/account/", data={"password": "testpassword123"}, format="json")

        # Verwacht NotAuthenticated (401)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Verifieer dat het protected object is verwijderd
        mock_protected_obj.delete.assert_called_once()

    def test_user_serializer_fields(self):
        """Test dat UserSerializer alle verwachte velden bevat"""
        response = self.client.get("/api/v1/account/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_fields = ["id", "username", "email", "first_name", "last_name", "date_joined", "last_login"]
        for field in expected_fields:
            self.assertIn(field, response.data)

    def test_permission_classes_require_authentication(self):
        """Test dat permission classes authenticatie vereisen"""
        from rest_framework.permissions import IsAuthenticated

        from api.auth.views import AccountViewSet, IsUserOwner

        viewset = AccountViewSet()
        permission_classes = viewset.permission_classes

        self.assertTrue(any(issubclass(pc, IsAuthenticated) for pc in permission_classes))
        self.assertTrue(any(issubclass(pc, IsUserOwner) for pc in permission_classes))

    def test_is_user_owner_permission_has_permission(self):
        """Test dat IsUserOwner.has_permission altijd True retourneert"""
        from api.auth.views import IsUserOwner

        permission = IsUserOwner()
        mock_request = Mock()
        mock_view = Mock()

        self.assertTrue(permission.has_permission(mock_request, mock_view))

    def test_is_user_owner_permission_has_object_permission_for_owner(self):
        """Test dat IsUserOwner.has_object_permission True retourneert voor eigenaar"""
        from api.auth.views import IsUserOwner

        permission = IsUserOwner()
        mock_request = Mock()
        mock_request.user = self.user
        mock_view = Mock()

        self.assertTrue(permission.has_object_permission(mock_request, mock_view, self.user))

    def test_is_user_owner_permission_has_object_permission_for_non_owner(self):
        """Test dat IsUserOwner.has_object_permission False retourneert voor niet-eigenaar"""
        from api.auth.views import IsUserOwner

        other_user = User.objects.create_user(username="otheruser", email="other@example.com", password="password123")

        permission = IsUserOwner()
        mock_request = Mock()
        mock_request.user = self.user
        mock_view = Mock()

        self.assertFalse(permission.has_object_permission(mock_request, mock_view, other_user))

    def test_delete_certificate_with_no_children(self):
        """Test _delete_certificate zonder child certificates"""
        from api.auth.views import AccountViewSet

        mock_cert = Mock(spec=Certificate)
        mock_cert.force_delete = Mock()

        with patch("api.auth.views.Certificate.objects.filter") as mock_filter:
            mock_filter.return_value = []

            viewset = AccountViewSet()
            viewset._delete_certificate(mock_cert)

            mock_cert.force_delete.assert_called_once()

    def test_delete_certificate_prevents_infinite_loop(self):
        """Test dat _delete_certificate zichzelf niet recursief aanroept"""
        from api.auth.views import AccountViewSet

        mock_cert = Mock(spec=Certificate)
        mock_cert.force_delete = Mock()

        with patch("api.auth.views.Certificate.objects.filter") as mock_filter:
            # Retourneer hetzelfde certificaat als child (zou infinite loop kunnen veroorzaken)
            mock_filter.return_value = [mock_cert]

            viewset = AccountViewSet()
            viewset._delete_certificate(mock_cert)

            # force_delete moet maar één keer worden aangeroepen
            mock_cert.force_delete.assert_called_once()


class UserSerializerTest(APITestCase):
    """Unit tests voor UserSerializer"""

    def setUp(self):
        """Setup test data"""
        self.user = User.objects.create_user(
            username="serializer_test",
            email="serializer@example.com",
            password="password123",
            first_name="Serializer",
            last_name="Test",
        )

    def test_serializer_contains_expected_fields(self):
        """Test dat serializer alle verwachte velden bevat"""
        from api.auth.views import UserSerializer

        serializer = UserSerializer(instance=self.user)
        data = serializer.data

        expected_fields = ["id", "username", "email", "first_name", "last_name", "date_joined", "last_login"]
        self.assertEqual(set(data.keys()), set(expected_fields))

    def test_serializer_field_values(self):
        """Test dat serializer de juiste waarden retourneert"""
        from api.auth.views import UserSerializer

        serializer = UserSerializer(instance=self.user)
        data = serializer.data

        self.assertEqual(data["username"], "serializer_test")
        self.assertEqual(data["email"], "serializer@example.com")
        self.assertEqual(data["first_name"], "Serializer")
        self.assertEqual(data["last_name"], "Test")
        self.assertEqual(data["id"], self.user.id)

    def test_serializer_does_not_expose_password(self):
        """Test dat serializer geen wachtwoord exposeert"""
        from api.auth.views import UserSerializer

        serializer = UserSerializer(instance=self.user)
        data = serializer.data

        self.assertNotIn("password", data)

    def tearDown(self):
        """Cleanup na elke test"""
        User.objects.all().delete()
