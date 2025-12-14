from django import forms
from django.test import TestCase

from vuetifyforms.vue import VuetifyFormMixin


class TestForm(forms.Form, VuetifyFormMixin):
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
        self.assertEqual(TestForm.field_error_css_classes, "djng-form-control-feedback djng-field-errors")
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

    def test_render_returns_html(self):
        """Test dat render HTML retourneert"""
        html = self.form.render()

        self.assertIsInstance(html, str)
        self.assertIn("<div", html)
        self.assertIn("</div>", html)

    def test_render_contains_field_labels(self):
        """Test dat render veld labels bevat"""
        html = self.form.render()

        self.assertIn("Name", html)
        self.assertIn("Email", html)
        self.assertIn("Message", html)

    def test_render_contains_input_fields(self):
        """Test dat render input velden bevat"""
        html = self.form.render()

        self.assertIn('name="name"', html)
        self.assertIn('name="email"', html)
        self.assertIn('name="message"', html)

    def test_render_with_errors(self):
        """Test render met form errors"""
        form = TestForm(data={})
        form.is_valid()  # Trigger validation

        html = form.render()

        # Check dat error wrapper aanwezig is
        self.assertIn('<ul class="errorlist" id="id_name_error">', html)

    def test_render_error_row_format(self):
        """Test dat error rows correct geformatteerd zijn"""
        form = TestForm(data={})
        form.is_valid()

        html = form.render()

        # Verifieer error wrapper structuur
        self.assertIn('<ul class="errorlist"', html)

    def test_render_help_text_format(self):
        """Test help text formatting"""

        class FormWithHelp(VuetifyFormMixin, forms.Form):
            field_with_help = forms.CharField(help_text="This is help text")

        form = FormWithHelp()
        html = form.render()

        self.assertIn(
            '<label for="id_field_with_help">Field with help:</label>'
            '\n\n<div class="helptext" id="id_field_with_help_helptext">This is help text</div>',
            html,
        )

    def test_render_required_fields(self):
        """Test dat required velden correct worden weergegeven"""
        html = self.form.render()

        # Required velden moeten in de HTML staan
        self.assertIn('name="name"', html)
        self.assertIn('name="email"', html)

    def test_render_optional_fields(self):
        """Test dat optionele velden correct worden weergegeven"""
        html = self.form.render()

        # Optional veld moet ook in de HTML staan
        self.assertIn('name="message"', html)

    def test_render_with_initial_data(self):
        """Test render met initial data"""
        form = TestForm(initial={"name": "John Doe", "email": "john@example.com"})
        html = form.render()

        self.assertIn("John Doe", html)
        self.assertIn("john@example.com", html)

    def test_render_textarea_widget(self):
        """Test dat textarea widget correct wordt gerenderd"""
        html = self.form.render()

        # Message veld heeft een Textarea widget
        self.assertIn('name="message"', html)
        self.assertIn("<textarea", html)
