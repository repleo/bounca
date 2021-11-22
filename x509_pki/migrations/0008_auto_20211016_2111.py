# Generated by Django 3.2.7 on 2021-10-16 19:11

import django.core.validators
import django_countries.fields
from django.db import migrations, models

import x509_pki.models


class Migration(migrations.Migration):

    dependencies = [
        ('x509_pki', '0007_auto_20201115_0939'),
    ]

    operations = [
        migrations.AddField(
            model_name='certificate',
            name='crl',
            field=models.TextField(blank=True, null=True, verbose_name='Serialized CRL certificate'),
        ),
        migrations.AlterField(
            model_name='certificate',
            name='expires_at',
            field=models.DateField(help_text='Select the date that the certificate will expire: for root typically 20 years, for intermediate 10 years for other types 1 year.', validators=[x509_pki.models.validate_in_future]),
        ),
        migrations.AlterField(
            model_name='distinguishedname',
            name='countryName',
            field=django_countries.fields.CountryField(blank=True, help_text='The two-character country name in ISO 3166 format.', max_length=2, null=True, verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='distinguishedname',
            name='emailAddress',
            field=models.EmailField(blank=True, help_text='The email address to contact your organization.', max_length=64, null=True, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z@#$%^&+=\\_\\.\\-\\,\\ \\*]*$', 'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')], verbose_name='Email Address'),
        ),
    ]