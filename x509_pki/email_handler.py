from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.encoding import force_str


def get_from_email():
    return settings.DEFAULT_FROM_EMAIL


def format_email_subject(subject) -> str:
    """
    Formats the given email subject.
    """
    prefix = settings.EMAIL_SUBJECT_PREFIX
    if prefix is None:
        site = Site.objects.get(id=settings.SITE_ID)
        prefix = "[{name}] ".format(name=site.name)
    return f"{prefix} {force_str(subject)}"


def render_mail(template_prefix, email, context, headers=None):
    """
    Renders an email to `email`.  `template_prefix` identifies the
    email that is to be sent, e.g. "app_name/email/email_confirmation"
    """
    to = [email] if isinstance(email, str) else email
    subject = render_to_string("{0}_subject.txt".format(template_prefix), context)
    # remove superfluous line breaks
    subject = " ".join(subject.splitlines()).strip()
    subject = format_email_subject(subject)

    from_email = get_from_email()

    bodies = {}
    html_ext = settings.TEMPLATE_EXTENSION
    for ext in [html_ext, "txt"]:
        try:
            template_name = "{0}_message.{1}".format(template_prefix, ext)
            req = globals()["context"].request if "context" in globals() else None
            bodies[ext] = render_to_string(
                template_name,
                context,
                req,
            ).strip()
        except TemplateDoesNotExist:
            if ext == "txt" and not bodies:
                # We need at least one body
                raise
    if "txt" in bodies:
        msg = EmailMultiAlternatives(subject, bodies["txt"], from_email, to, headers=headers)
        if html_ext in bodies:
            msg.attach_alternative(bodies[html_ext], "text/html")
    else:
        msg = EmailMessage(subject, bodies[html_ext], from_email, to, headers=headers)
        msg.content_subtype = "html"  # Main content is now text/html
    return msg


def send_mail(template_prefix: str, email: str, context: dict) -> None:
    req = globals()["context"].request if "context" in globals() else None
    site = get_current_site(req) if req else Site.objects.get(id=settings.SITE_ID)
    ctx = {
        "request": req,
        "email": email,
        "current_site": site,
    }
    ctx.update(context)
    msg = render_mail(template_prefix, email, ctx)
    msg.send()
