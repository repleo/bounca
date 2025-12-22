from __future__ import absolute_import, unicode_literals

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from api.admin import AuthorisedAppForm
from api.models import AuthorisedApp

User = get_user_model()


class AuthorisedAppFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", is_superuser=True)
        self.authorised_app = AuthorisedApp.objects.create(name="TestApp", token="testtoken", user=self.user)

    @patch("api.admin.utils.new_token", return_value="new_generated_token")
    def test_clean_generates_new_token(self, mock_new_token):
        form_data = {"name": "TestApp", "generate_new_token": True, "user": self.user}
        form = AuthorisedAppForm(data=form_data, instance=self.authorised_app, current_user=self.user)

        self.assertTrue(form.is_valid())
        cleaned_data = form.clean()
        self.assertEqual(cleaned_data["token"], "new_generated_token")
        mock_new_token.assert_called_once_with(44)

    def test_clean_does_not_generate_new_token(self):
        form_data = {"name": "TestApp", "generate_new_token": False, "user": self.user}
        form = AuthorisedAppForm(data=form_data, instance=self.authorised_app, current_user=self.user)
        self.assertTrue(form.is_valid())
        cleaned_data = form.clean()
        self.assertEqual(cleaned_data["token"], self.authorised_app.token)

    def test_fields_disabled_for_non_superuser(self):
        non_superuser = User.objects.create(username="non_superuser", is_superuser=False)
        form = AuthorisedAppForm(instance=self.authorised_app, current_user=non_superuser)

        self.assertTrue(form.fields["token"].disabled)

    def test_fields_enabled_for_superuser(self):
        form = AuthorisedAppForm(instance=self.authorised_app, current_user=self.user)

        self.assertFalse(form.fields["token"].disabled)

    def test_save_commits_changes(self):
        form_data = {"name": "UpdatedApp", "generate_new_token": False, "user": self.user}
        form = AuthorisedAppForm(data=form_data, instance=self.authorised_app, current_user=self.user)

        self.assertTrue(form.is_valid())
        updated_instance = form.save(commit=True)
        self.assertEqual(updated_instance.name, "UpdatedApp")

    def test_save_without_commit(self):
        form_data = {"name": "IntermediateApp", "generate_new_token": False, "user": self.user}
        form = AuthorisedAppForm(data=form_data, instance=self.authorised_app, current_user=self.user)

        self.assertTrue(form.is_valid())

        # Mock de save methode van de parent class om te verifiëren dat commit=False wordt doorgegeven
        with patch("django.forms.models.ModelForm.save") as mock_parent_save:
            mock_parent_save.return_value = self.authorised_app
            result = form.save(commit=False)

            # Verifieer dat de parent save is aangeroepen met commit=False
            mock_parent_save.assert_called_once_with(commit=False)
            # Verifieer dat het object wordt geretourneerd
            self.assertEqual(result.name, "IntermediateApp")
