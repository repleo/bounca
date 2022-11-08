from django.contrib.auth.models import User
from django.db import models

from api import utils


class AuthorisedApp(models.Model):

    name = models.TextField()
    token = models.TextField(unique=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        ordering = ["name"]
        unique_together = ("name", "user")

    def save(self, *args, **kwargs):
        if not self.id:
            self.token = utils.new_token(44)
        super(AuthorisedApp, self).save(*args, **kwargs)

    def __str__(self):
        return "{} - {}".format(self.name, self.token)
