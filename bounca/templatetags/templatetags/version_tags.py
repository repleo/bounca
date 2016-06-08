__author__ = "Jeroen Arnoldus"
__copyright__ = "Copyright 2016, Repleo, Amstelveen"
__credits__ = ["Jeroen Arnoldus"]
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Jeroen Arnoldus"
__email__ = "jeroen@repleo.nl"
__status__ = "Production"

from django import template
from django.utils.version import get_version

from bounca import VERSION

register = template.Library()

@register.simple_tag
def bounca_version():
    return str(get_version(VERSION))
