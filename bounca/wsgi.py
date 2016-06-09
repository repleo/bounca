"""uWSGI config"""

import os

from django.core.wsgi import get_wsgi_application

__author__ = "Jeroen Arnoldus"
__copyright__ = "Copyright 2016, Repleo, Amstelveen"
__credits__ = ["Jeroen Arnoldus"]
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Jeroen Arnoldus"
__email__ = "jeroen@repleo.nl"
__status__ = "Production"


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bounca.settings")

application = get_wsgi_application()
