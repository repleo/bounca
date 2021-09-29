import os
import pathlib

import pytz
from datetime import datetime

from crispy_forms.templatetags.crispy_forms_tags import CrispyFormNode
from crispy_forms.utils import render_crispy_form
from django.apps import AppConfig
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models.signals import post_delete
from django.template import loader, Context
from django.views.generic import FormView
from factory.django import mute_signals
from rest_framework.renderers import HTMLFormRenderer

from api.forms import AddRootCAForm, AddIntermediateCAForm, AddCertificateForm
from api.serializers import CertificateSerializer
# from vuetifyforms.forms import AddRootCAForm

from bs4 import BeautifulSoup as bs

class Command(BaseCommand):
    help = f"Generate vuetify forms "

    # def add_arguments(self, parser):
    #     parser.add_argument(
    #         '--perform',
    #         action='store_true',
    #         default=False,
    #         help="Perform loading data, warning removes ALL old data")

    # def get_form(self, form_class=None):
    #     """Return an instance of the form to be used in this view."""
    #     if form_class is None:
    #         form_class = self.get_form_class()
    #     return form_class(**self.get_form_kwargs())


    def generate_forms(self):
        form = AddCertificateForm()
        html_form = render_crispy_form(form, context={'form': form})

        print(html_form)
        #print(form.as_vuetify())

        with open("/Users/bjarnoldus/github/bounca/front/src/components/forms/Certificate.vue", "w") as f:
            f.write(html_form)

        fdsfsdfdsf
        form = AddIntermediateCAForm()
        html_form = render_crispy_form(form, context={'form': form})

        print(html_form)
        #print(form.as_vuetify())

        with open("/Users/bjarnoldus/github/bounca/front/src/components/forms/IntermediateCert.vue", "w") as f:
            f.write(html_form)
        # sdtfgsfgdfsg

        form = AddRootCAForm()
        html_form = render_crispy_form(form, context={'form': form})

        print(html_form)
        #print(form.as_vuetify())

        with open("/Users/bjarnoldus/github/bounca/front/src/components/forms/RootCert.vue", "w") as f:
            f.write(html_form)
        sdtfgsfgdfsg


        form_renderer = HTMLFormRenderer()
        serializer = CertificateSerializer()
        html_form = form_renderer.render(
            serializer.data,
            'text/html',
            {'style': {'template_pack': 'vuetifyform'}}
        )

        #root = lh.tostring(sliderRoot)  # convert the generated HTML to a string
        # soup = bs(html_form)  # make BeautifulSoup
        # prettyHTML = soup.prettify()  # prettify the html
        with open("/Users/bjarnoldus/github/bounca/front/src/components/forms/RootCert.vue", "w") as f:
            f.write(html_form)

    def handle(self, *args, **options):
        self.generate_forms()
