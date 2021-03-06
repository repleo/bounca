# Generated by Django 3.0.8 on 2020-07-19 20:33

import django.core.validators
import django_countries.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('x509_pki', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='certificate',
            name='revoked_uuid',
            field=models.UUIDField(default=0),
        ),
        migrations.AlterField(
            model_name='distinguishedname',
            name='countryName',
            field=django_countries.fields.CountryField(blank=True, help_text='The two-character country name in ISO 3166 format.', max_length=2, null=True, verbose_name='Country Name'),
        ),
        migrations.AlterField(
            model_name='distinguishedname',
            name='emailAddress',
            field=models.EmailField(blank=True, default='ca@repleo.nl', help_text='The email address to contact your organization. Also used by BounCA for authentication.', max_length=64, null=True, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z@#$%^&+=\\_\\.\\-\\,\\ \\*]*$', 'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')], verbose_name='Email Address'),
        ),
        migrations.AlterField(
            model_name='distinguishedname',
            name='localityName',
            field=models.CharField(blank=True, help_text='The city where your organization is located. (1–128 characters)', max_length=128, null=True, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z@#$%^&+=\\_\\.\\-\\,\\ \\*]*$', 'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')], verbose_name='Locality Name'),
        ),
        migrations.AlterField(
            model_name='distinguishedname',
            name='organizationName',
            field=models.CharField(blank=True, help_text='The legal name of your organization. This should not be abbreviated and should include suffixes such as Inc, Corp, or LLC.', max_length=64, null=True, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z@#$%^&+=\\_\\.\\-\\,\\ \\*]*$', 'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')], verbose_name='Organization Name'),
        ),
        migrations.AlterField(
            model_name='distinguishedname',
            name='organizationalUnitName',
            field=models.CharField(blank=True, help_text='The division of your organization handling the certificate.', max_length=64, null=True, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z@#$%^&+=\\_\\.\\-\\,\\ \\*]*$', 'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')], verbose_name='Organization Unit Name'),
        ),
        migrations.AlterField(
            model_name='distinguishedname',
            name='stateOrProvinceName',
            field=models.CharField(blank=True, help_text="The state/region where your organization is located. This shouldn't be abbreviated. (1–128 characters)", max_length=128, null=True, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z@#$%^&+=\\_\\.\\-\\,\\ \\*]*$', 'Only alphanumeric characters and [@#$%^&+=_,-.] are allowed.')], verbose_name='State or Province Name'),
        ),
    ]
