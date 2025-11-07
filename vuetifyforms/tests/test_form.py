from django import forms
from django.test import TestCase

from vuetifyforms.vue import VuetifyFormMixin


class TestForm(VuetifyFormMixin, forms.Form):
    """Test form voor VuetifyFormMixin tests"""
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=False)


class ChildForm(TestForm):
    """Child form voor get_subclasses test"""
    extra_field = forms.CharField(max_length=50)


class GrandChildForm(ChildForm):
    """Grandchild form voor get_subclasses test"""
    another_field = forms.IntegerField()


class VuetifyFormMixinTest(TestCase):
    """Unit tests voor VuetifyFormMixin"""

    def setUp(self):
        """Setup test data"""
        self.form = TestForm()

    def test_class_attributes(self):
        """Test dat class attributes correct zijn ingesteld"""
        self.assertEqual(TestForm.field_css_classes, "form-group has-feedback")
        self.assertEqual(TestForm.widget_css_classes, "form-control")
        self.assertEqual(TestForm.form_error_css_classes, "djng-form-errors")
        self.assertEqual(TestForm.field_error_css_classes,
                         "djng-form-control-feedback djng-field-errors")
        self.assertEqual(TestForm.label_css_classes, "control-label")

    def test_get_subclasses_returns_direct_children(self):
        """Test dat get_subclasses directe child classes retourneert"""
        subclasses = list(TestForm.get_subclasses())

        self.assertIn(ChildForm, subclasses)

    def test_get_subclasses_returns_nested_children(self):
        """Test dat get_subclasses geneste child classes retourneert"""
        subclasses = list(TestForm.get_subclasses())

        self.assertIn(ChildForm, subclasses)
        self.assertIn(GrandChildForm, subclasses)

    def test_get_subclasses_with_no_children(self):
        """Test get_subclasses met een class zonder children"""
        # GrandChildForm heeft geen subclasses
        subclasses = list(GrandChildForm.get_subclasses())

        self.assertEqual(len(subclasses), 0)

    def test_as_vuetify_returns_html(self):
        """Test dat as_vuetify HTML retourneert"""
        html = self.form.as_vuetify()

        self.assertIsInstance(html, str)
        self.assertIn('<div', html)
        self.assertIn('</div>', html)

    def test_as_vuetify_contains_field_labels(self):
        """Test dat as_vuetify veld labels bevat"""
        html = self.form.as_vuetify()

        self.assertIn('Name', html)
        self.assertIn('Email', html)
        self.assertIn('Message', html)

    def test_as_vuetify_contains_input_fields(self):
        """Test dat as_vuetify input velden bevat"""
        html = self.form.as_vuetify()

        self.assertIn('name="name"', html)
        self.assertIn('name="email"', html)
        self.assertIn('name="message"', html)

    def test_as_vuetify_with_errors(self):
        """Test as_vuetify met form errors"""
        form = TestForm(data={})
        form.is_valid()  # Trigger validation

        html = form.as_vuetify()

        # Check dat error wrapper aanwezig is
        self.assertIn('djng-line-spreader', html)

    def test_as_vuetify_error_row_format(self):
        """Test dat error rows correct geformatteerd zijn"""
        form = TestForm(data={})
        form.is_valid()

        html = form.as_vuetify()

        # Verifieer error wrapper structuur
        self.assertIn('<div class="djng-line-spreader">', html)

    def test_as_vuetify_help_text_format(self):
        """Test help text formatting"""

        class FormWithHelp(VuetifyFormMixin, forms.Form):
            field_with_help = forms.CharField(help_text="This is help text")

        form = FormWithHelp()
        html = form.as_vuetify()

        self.assertIn('<span class="help-block">This is help text</span>', html)

    def test_as_vuetify_required_fields(self):
        """Test dat required velden correct worden weergegeven"""
        html = self.form.as_vuetify()

        # Required velden moeten in de HTML staan
        self.assertIn('name="name"', html)
        self.assertIn('name="email"', html)

    def test_as_vuetify_optional_fields(self):
        """Test dat optionele velden correct worden weergegeven"""
        html = self.form.as_vuetify()

        # Optional veld moet ook in de HTML staan
        self.assertIn('name="message"', html)

    def test_as_vuetify_with_initial_data(self):
        """Test as_vuetify met initial data"""
        form = TestForm(initial={'name': 'John Doe', 'email': 'john@example.com'})
        html = form.as_vuetify()

        self.assertIn('John Doe', html)
        self.assertIn('john@example.com', html)

    def test_as_vuetify_textarea_widget(self):
        """Test dat textarea widget correct wordt gerenderd"""
        html = self.form.as_vuetify()

        # Message veld heeft een Textarea widget
        self.assertIn('name="message"', html)
        self.assertIn('<textarea', html)
