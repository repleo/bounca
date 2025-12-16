import json
import sys

from django import template
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.postgres.forms import SimpleArrayField
from django.forms import (
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    ModelMultipleChoiceField,
    PasswordInput,
    TypedChoiceField,
    URLField,
)

register = template.Library()


def rule_MaxLengthValidator(v):
    return f"max:{v.limit_value}"


def rule_ProhibitNullCharactersValidator(v):
    return None


def rule_EmailValidator(v):
    return "email"


def rule_URLValidator(v):
    return "url"


def rule_PasswordConfirmValidator(v):
    return f"confirmed:{v.field}"


class VeeValidateNode(template.Node):
    def __init__(self, field):
        self.field = template.Variable(field)

    def render(self, context):
        try:
            field = self.field.resolve(context)

            rules = [getattr(sys.modules[__name__], f"rule_{type(v).__name__}")(v) for v in field.field.validators]
            if field.field.required:
                rules.append("required")
            return "|".join(filter(None, rules))
        except template.VariableDoesNotExist:
            return ""
        except AttributeError as e:
            raise NotImplementedError(f"Implement rule for: {e}")


@register.tag
def vee_validate_rules(parser, token):
    """
    Generates vee validate rules based on django validators. Throws exception when validator is unknown.
    """
    try:
        tag_name, field = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])

    return VeeValidateNode(field)


@register.filter
def is_array(field):
    return isinstance(field.field, SimpleArrayField)


@register.filter
def dottounderscore(val):
    return val.replace(".", "_")


@register.filter
def error_field(val):
    return val.replace(".", "__")


@register.filter
def error_slot_suffix(val):
    suffix = val.split(".")
    suffix.pop()
    return "".join([f"_{v}" for v in suffix])


def _set_sub_field(obj, keys, value):
    if len(keys) > 1:
        key = keys.pop(0)
        if key not in obj:
            obj[key] = {}
        _set_sub_field(obj[key], keys, value)
    elif keys:
        obj[keys[0]] = value


def _set_field_data(obj, form_object_name, field_name, field):
    if isinstance(field, TypedChoiceField):
        obj[f'formdata_{form_object_name}_{field_name.replace(".", "_")}_values'] = [
            {"text": v[1], "value": v[0]} for v in field.widget.choices if v[0]
        ]


def _set_password_visible_vars(obj, field_name, field):
    if isinstance(field.widget, PasswordInput):
        obj[f'{field_name.replace(".", "_")}_visible'] = False


def _get_empty_value(field):
    if isinstance(field, SimpleArrayField):
        return []
    elif isinstance(field, CharField) or isinstance(field, URLField):
        return ""
    elif isinstance(field, TypedChoiceField):
        return None
    elif isinstance(field, DateField):
        return None
    elif isinstance(field, DateTimeField):
        return None
    elif isinstance(field, BooleanField):
        return None
    elif isinstance(field, ModelMultipleChoiceField):
        return None
    elif isinstance(field, ReadOnlyPasswordHashField):
        return None
    else:
        raise NotImplementedError(f"Implement empty value for field class '{type(field).__name__}'")


class DataObjectNode(template.Node):
    def __init__(self, form):
        self.form = template.Variable(form)

    def render(self, context):
        try:
            form = self.form.resolve(context)

            data = {
                "dialog": False,
            }
            if not hasattr(form, "form_object"):
                raise RuntimeError("'form_object' not set for form")
            fields = {}
            for k in form.fields:
                _set_sub_field(fields, k.split("."), _get_empty_value(form.fields[k]))
                _set_password_visible_vars(data, k, form.fields[k])
                _set_field_data(data, form.form_object, k, form.fields[k])

            data[form.form_object] = fields

            return json.dumps(data)
        except template.VariableDoesNotExist:
            return json.dumps({})


@register.tag
def make_data_object(parser, token):
    """
    Generates data object for vue
    """
    try:
        tag_name, form = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])

    return DataObjectNode(form)
