"""Version template tag"""

# TODO replace by setting export
from django import template
from django.utils.version import get_version

from bounca import VERSION


register = template.Library()


@register.simple_tag
def bounca_version():
    return str(get_version(VERSION))
