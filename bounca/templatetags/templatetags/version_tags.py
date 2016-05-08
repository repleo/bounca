from django import template
from bounca import VERSION
from django.utils.version import get_version


register = template.Library()

@register.simple_tag
def bounca_version():
    return str(get_version(VERSION))

    