import os
from crispy_forms.utils import render_crispy_form
from django.conf import settings
from django.core.management.base import BaseCommand

from vuetifyforms.vue import VuetifyFormMixin


class Command(BaseCommand):
    help = "Generate vuetify forms "

    def generate_form(self, form):
        self.stdout.write(f"Generating form {form.__name__}, writing to file {form.vue_file}")
        html_form = render_crispy_form(form, context={'form': form})
        full_path = os.path.join(settings.BASE_DIR, form.vue_file)
        with open(full_path, "w") as f:
            f.write(html_form)

    def generate_forms(self):
        forms = VuetifyFormMixin.get_subclasses()
        for form in forms:
            self.generate_form(form)

    def handle(self, *args, **options):
        self.stdout.write("Generating vuetify forms")
        self.generate_forms()
        self.stdout.write(self.style.SUCCESS("Successfully generated forms"))
