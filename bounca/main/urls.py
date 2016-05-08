from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse_lazy


urlpatterns = patterns('bounca',

    url(r'^auth/views/authrequired.html$', TemplateView.as_view(template_name='bounca/auth/views/authrequired.html'), name='auth.authrequired'),
    url(r'^auth/views/login.html$', TemplateView.as_view(template_name='bounca/auth/views/login.html'), name='auth.login'),
    url(r'^auth/views/logout.html$', TemplateView.as_view(template_name='bounca/auth/views/logout.html'), name='auth.logout'),
    url(r'^auth/views/main.html$', TemplateView.as_view(template_name='bounca/auth/views/main.html'), name='auth.main'),
    url(r'^auth/views/passwordchange.html$', TemplateView.as_view(template_name='bounca/auth/views/passwordchange.html'), name='auth.passwordchange'),
    url(r'^auth/views/passwordreset.html$', TemplateView.as_view(template_name='bounca/auth/views/passwordreset.html'), name='auth.passwordreset'),
    url(r'^auth/views/passwordresetconfirm.html$', TemplateView.as_view(template_name='bounca/auth/views/passwordresetconfirm.html'), name='auth.passwordresetconfirm'),
    url(r'^auth/views/register.html$', TemplateView.as_view(template_name='bounca/auth/views/register.html'), name='auth.register'),
    url(r'^auth/views/restricted.html$', TemplateView.as_view(template_name='bounca/auth/views/restricted.html'), name='auth.restricted'),
    url(r'^auth/views/userprofile.html$', TemplateView.as_view(template_name='bounca/auth/views/userprofile.html'), name='auth.userprofile'),
    url(r'^auth/views/verifyemail.html$', TemplateView.as_view(template_name='bounca/auth/views/verifyemail.html'), name='auth.verifyemail'),


    url(r'^ca/$', TemplateView.as_view(template_name='bounca/ca.html'), name='ca'),
    url(r'^$', TemplateView.as_view(template_name='bounca/index.html'), name='index'),

)
