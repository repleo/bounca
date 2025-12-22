import json
from unittest.mock import Mock

from django import forms, template
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.postgres.forms import SimpleArrayField
from django.forms import (
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    ModelMultipleChoiceField,
    PasswordInput,
    URLField,
)
from django.test import TestCase
from django_countries.fields import LazyTypedChoiceField

from vuetifyforms.templatetags.crispy_forms_vuetify import (
    DataObjectNode,
    VeeValidateNode,
    _get_empty_value,
    _set_field_data,
    _set_password_visible_vars,
    _set_sub_field,
    dottounderscore,
    error_field,
    error_slot_suffix,
    is_array,
    make_data_object,
    rule_EmailValidator,
    rule_MaxLengthValidator,
    rule_PasswordConfirmValidator,
    rule_ProhibitNullCharactersValidator,
    rule_URLValidator,
    vee_validate_rules,
)


class ValidatorRulesTest(TestCase):
    """Unit tests voor validator rule functions"""

    def test_rule_max_length_validator(self):
        """Test MaxLengthValidator rule generatie"""
        validator = Mock()
        validator.limit_value = 100

        result = rule_MaxLengthValidator(validator)
        self.assertEqual(result, "max:100")

    def test_rule_prohibit_null_characters_validator(self):
        """Test ProhibitNullCharactersValidator rule generatie"""
        validator = Mock()

        result = rule_ProhibitNullCharactersValidator(validator)
        self.assertIsNone(result)

    def test_rule_email_validator(self):
        """Test EmailValidator rule generatie"""
        validator = Mock()

        result = rule_EmailValidator(validator)
        self.assertEqual(result, "email")

    def test_rule_url_validator(self):
        """Test URLValidator rule generatie"""
        validator = Mock()

        result = rule_URLValidator(validator)
        self.assertEqual(result, "url")

    def test_rule_password_confirm_validator(self):
        """Test PasswordConfirmValidator rule generatie"""
        validator = Mock()
        validator.field = "password"

        result = rule_PasswordConfirmValidator(validator)
        self.assertEqual(result, "confirmed:password")


class VeeValidateNodeTest(TestCase):
    """Unit tests voor VeeValidateNode"""

    def test_initialization(self):
        """Test VeeValidateNode initialisatie"""
        node = VeeValidateNode("field_name")
        self.assertIsNotNone(node.field)

    def test_render_with_required_field(self):
        """Test render met required veld"""
        from django.core.validators import MaxLengthValidator

        mock_field = Mock()
        mock_field.field.validators = [MaxLengthValidator(100)]
        mock_field.field.required = True

        context = template.Context({"field": mock_field})
        node = VeeValidateNode("field")

        result = node.render(context)
        self.assertIn("required", result)
        self.assertIn("max:100", result)

    def test_render_with_optional_field(self):
        """Test render met optioneel veld"""
        mock_field = Mock()
        mock_field.field.validators = []
        mock_field.field.required = False

        context = template.Context({"field": mock_field})
        node = VeeValidateNode("field")

        result = node.render(context)
        self.assertNotIn("required", result)

    def test_render_with_variable_does_not_exist(self):
        """Test render wanneer variabele niet bestaat"""
        context = template.Context({})
        node = VeeValidateNode("nonexistent_field")

        result = node.render(context)
        self.assertEqual(result, "")

    def test_render_filters_none_rules(self):
        """Test dat None rules worden gefilterd"""
        from django.core.validators import ProhibitNullCharactersValidator

        mock_field = Mock()
        mock_field.field.validators = [ProhibitNullCharactersValidator()]
        mock_field.field.required = False

        context = template.Context({"field": mock_field})
        node = VeeValidateNode("field")

        result = node.render(context)
        # ProhibitNullCharactersValidator returns None, so should be filtered
        self.assertEqual(result, "")

    def test_render_with_unknown_validator_raises_not_implemented(self):
        """Test dat onbekende validator NotImplementedError gooit"""

        class UnknownValidator:
            pass

        mock_field = Mock()
        mock_field.field.validators = [UnknownValidator()]
        mock_field.field.required = False

        context = template.Context({"field": mock_field})
        node = VeeValidateNode("field")

        with self.assertRaises(NotImplementedError):
            node.render(context)


class FilterFunctionsTest(TestCase):
    """Unit tests voor template filter functies"""

    def test_is_array_with_simple_array_field(self):
        """Test is_array met SimpleArrayField"""
        mock_field = Mock()
        mock_field.field = SimpleArrayField(CharField())

        result = is_array(mock_field)
        self.assertTrue(result)

    def test_is_array_with_non_array_field(self):
        """Test is_array met non-array veld"""
        mock_field = Mock()
        mock_field.field = CharField()

        result = is_array(mock_field)
        self.assertFalse(result)

    def test_dottounderscore(self):
        """Test dottounderscore filter"""
        self.assertEqual(dottounderscore("field.name.test"), "field_name_test")
        self.assertEqual(dottounderscore("simple"), "simple")
        self.assertEqual(dottounderscore("one.two"), "one_two")

    def test_error_field(self):
        """Test error_field filter"""
        self.assertEqual(error_field("field.name.test"), "field__name__test")
        self.assertEqual(error_field("simple"), "simple")
        self.assertEqual(error_field("one.two"), "one__two")

    def test_error_slot_suffix(self):
        """Test error_slot_suffix filter"""
        self.assertEqual(error_slot_suffix("field.name.test"), "_field_name")
        self.assertEqual(error_slot_suffix("one.two"), "_one")
        self.assertEqual(error_slot_suffix("simple"), "")


class PrivateFunctionsTest(TestCase):
    """Unit tests voor private helper functies"""

    def test_set_sub_field_single_key(self):
        """Test _set_sub_field met enkele key"""
        obj = {}
        _set_sub_field(obj, ["key"], "value")
        self.assertEqual(obj["key"], "value")

    def test_set_sub_field_nested_keys(self):
        """Test _set_sub_field met geneste keys"""
        obj = {}
        _set_sub_field(obj, ["level1", "level2", "level3"], "value")
        self.assertEqual(obj["level1"]["level2"]["level3"], "value")

    def test_set_sub_field_empty_keys(self):
        """Test _set_sub_field met lege keys lijst"""
        obj = {}
        _set_sub_field(obj, [], "value")
        self.assertEqual(obj, {})

    def test_set_field_data_with_lazy_typed_choice_field(self):
        """Test _set_field_data met LazyTypedChoiceField"""
        obj = {}
        mock_field = Mock(spec=LazyTypedChoiceField)
        mock_field.widget.choices = [("", "-----"), ("NL", "Netherlands"), ("US", "United States")]

        _set_field_data(obj, "myform", "country", mock_field)

        key = "formdata_myform_country_values"
        self.assertIn(key, obj)
        self.assertEqual(len(obj[key]), 2)  # Empty choice is filtered
        self.assertEqual(obj[key][0]["value"], "NL")
        self.assertEqual(obj[key][0]["text"], "Netherlands")

    def test_set_field_data_with_non_choice_field(self):
        """Test _set_field_data met non-choice veld"""
        obj = {}
        mock_field = Mock(spec=CharField)

        _set_field_data(obj, "myform", "name", mock_field)

        # Geen data zou moeten worden toegevoegd
        self.assertEqual(obj, {})

    def test_set_password_visible_vars_with_password_input(self):
        """Test _set_password_visible_vars met PasswordInput"""
        obj = {}
        mock_field = Mock()
        mock_field.widget = PasswordInput()

        _set_password_visible_vars(obj, "password", mock_field)

        self.assertIn("password_visible", obj)
        self.assertFalse(obj["password_visible"])

    def test_set_password_visible_vars_with_dotted_field_name(self):
        """Test _set_password_visible_vars met dotted field name"""
        obj = {}
        mock_field = Mock()
        mock_field.widget = PasswordInput()

        _set_password_visible_vars(obj, "user.password", mock_field)

        self.assertIn("user_password_visible", obj)
        self.assertFalse(obj["user_password_visible"])

    def test_set_password_visible_vars_with_non_password_widget(self):
        """Test _set_password_visible_vars met non-password widget"""
        obj = {}
        mock_field = Mock()
        mock_field.widget = forms.TextInput()

        _set_password_visible_vars(obj, "username", mock_field)

        # Geen data zou moeten worden toegevoegd
        self.assertEqual(obj, {})

    def test_get_empty_value_simple_array_field(self):
        """Test _get_empty_value voor SimpleArrayField"""
        field = SimpleArrayField(CharField())
        result = _get_empty_value(field)
        self.assertEqual(result, [])

    def test_get_empty_value_char_field(self):
        """Test _get_empty_value voor CharField"""
        field = CharField()
        result = _get_empty_value(field)
        self.assertEqual(result, "")

    def test_get_empty_value_url_field(self):
        """Test _get_empty_value voor URLField"""
        field = URLField()
        result = _get_empty_value(field)
        self.assertEqual(result, "")

    def test_get_empty_value_lazy_typed_choice_field(self):
        """Test _get_empty_value voor LazyTypedChoiceField"""
        field = Mock(spec=LazyTypedChoiceField)
        result = _get_empty_value(field)
        self.assertIsNone(result)

    def test_get_empty_value_date_field(self):
        """Test _get_empty_value voor DateField"""
        field = DateField()
        result = _get_empty_value(field)
        self.assertIsNone(result)

    def test_get_empty_value_datetime_field(self):
        """Test _get_empty_value voor DateTimeField"""
        field = DateTimeField()
        result = _get_empty_value(field)
        self.assertIsNone(result)

    def test_get_empty_value_boolean_field(self):
        """Test _get_empty_value voor BooleanField"""
        field = BooleanField()
        result = _get_empty_value(field)
        self.assertIsNone(result)

    def test_get_empty_value_model_multiple_choice_field(self):
        """Test _get_empty_value voor ModelMultipleChoiceField"""
        field = Mock(spec=ModelMultipleChoiceField)
        result = _get_empty_value(field)
        self.assertIsNone(result)

    def test_get_empty_value_readonly_password_hash_field(self):
        """Test _get_empty_value voor ReadOnlyPasswordHashField"""
        field = Mock(spec=ReadOnlyPasswordHashField)
        result = _get_empty_value(field)
        self.assertIsNone(result)

    def test_get_empty_value_unknown_field_raises_not_implemented(self):
        """Test dat _get_empty_value NotImplementedError gooit voor onbekend veld"""

        class UnknownField:
            pass

        field = UnknownField()

        with self.assertRaises(NotImplementedError) as cm:
            _get_empty_value(field)

        self.assertIn("UnknownField", str(cm.exception))


class DataObjectNodeTest(TestCase):
    """Unit tests voor DataObjectNode"""

    def test_initialization(self):
        """Test DataObjectNode initialisatie"""
        node = DataObjectNode("form")
        self.assertIsNotNone(node.form)

    def test_render_with_valid_form(self):
        """Test render met geldige form"""
        mock_form = Mock()
        mock_form.form_object = "testform"
        mock_form.fields = {"name": CharField(), "email": forms.EmailField()}

        context = template.Context({"form": mock_form})
        node = DataObjectNode("form")

        result = node.render(context)
        data = json.loads(result)

        self.assertIn("dialog", data)
        self.assertIn("testform", data)
        self.assertFalse(data["dialog"])

    def test_render_without_form_object_raises_runtime_error(self):
        """Test dat render RuntimeError gooit zonder form_object"""
        mock_form = Mock()
        mock_form.fields = {}
        delattr(mock_form, "form_object")

        context = template.Context({"form": mock_form})
        node = DataObjectNode("form")

        with self.assertRaises(RuntimeError) as cm:
            node.render(context)

        self.assertIn("'form_object' not set for form", str(cm.exception))

    def test_render_with_variable_does_not_exist(self):
        """Test render wanneer form variabele niet bestaat"""
        context = template.Context({})
        node = DataObjectNode("nonexistent_form")

        result = node.render(context)
        self.assertEqual(result, json.dumps({}))

    def test_render_with_nested_field_names(self):
        """Test render met geneste field namen"""
        mock_form = Mock()
        mock_form.form_object = "myform"
        mock_form.fields = {"user.name": CharField(), "user.email": forms.EmailField()}

        context = template.Context({"form": mock_form})
        node = DataObjectNode("form")

        result = node.render(context)
        data = json.loads(result)

        self.assertIn("myform", data)
        self.assertIn("user", data["myform"])
        self.assertIn("name", data["myform"]["user"])
        self.assertIn("email", data["myform"]["user"])

    def test_render_with_password_field(self):
        """Test render met password veld"""
        mock_form = Mock()
        mock_form.form_object = "loginform"
        password_field = CharField(widget=PasswordInput())
        mock_form.fields = {"password": password_field}

        context = template.Context({"form": mock_form})
        node = DataObjectNode("form")

        result = node.render(context)
        data = json.loads(result)

        self.assertIn("password_visible", data)
        self.assertFalse(data["password_visible"])


class TemplateTagsTest(TestCase):
    """Unit tests voor template tag functies"""

    def test_vee_validate_rules_tag(self):
        """Test vee_validate_rules template tag"""
        parser = Mock()
        token = Mock()
        token.split_contents.return_value = ["vee_validate_rules", "field"]

        result = vee_validate_rules(parser, token)

        self.assertIsInstance(result, VeeValidateNode)

    def test_vee_validate_rules_tag_without_argument(self):
        """Test vee_validate_rules zonder argument gooit error"""
        parser = Mock()
        token = Mock()
        token.split_contents.return_value = ["vee_validate_rules"]
        token.contents = "vee_validate_rules"

        with self.assertRaises(template.TemplateSyntaxError):
            vee_validate_rules(parser, token)

    def test_make_data_object_tag(self):
        """Test make_data_object template tag"""
        parser = Mock()
        token = Mock()
        token.split_contents.return_value = ["make_data_object", "form"]

        result = make_data_object(parser, token)

        self.assertIsInstance(result, DataObjectNode)

    def test_make_data_object_tag_without_argument(self):
        """Test make_data_object zonder argument gooit error"""
        parser = Mock()
        token = Mock()
        token.split_contents.return_value = ["make_data_object"]
        token.contents = "make_data_object"

        with self.assertRaises(template.TemplateSyntaxError):
            make_data_object(parser, token)
