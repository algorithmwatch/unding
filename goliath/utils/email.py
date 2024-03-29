from anymail.message import AnymailMessage
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlquote
from sesame.utils import get_query_string


def formated_from():
    return f"{Site.objects.get_current().name} <{settings.DEFAULT_FROM_EMAIL}>"


def send_anymail_email(
    to_email,
    text_content,
    ctaLink=None,
    ctaLabel=None,
    html_content=None,
    is_generic=True,
    rest="",
    full_user_name=None,
    **kwargs,
):
    """
    Sending generic email with anymail + returns id & status

    Optional cta link (for text email) and cta button (for HTML email).
    """

    content = text_content
    if ctaLink is not None:
        content += "\n\n" + ctaLink

    if is_generic:
        context = {"content": content, full_user_name: full_user_name}
        body_text = render_to_string(
            "account/email/generic_message.txt",
            context,
        )
    else:
        # Don't use generic opening + closing of email
        body_text = content

    no_rest = body_text
    if rest:
        body_text += "\n" + rest

    # provide a default, formatted (with site name) email address
    kwargs = {
        "from_email": formated_from(),
        **kwargs,
    }

    msg = AnymailMessage(body=body_text, **kwargs, to=[to_email])

    # HTML email is optional for now
    if html_content is not None:
        context["content"] = html_content

        if ctaLink is not None:
            if ctaLabel is None:
                ctaLabel = ctaLink

            context["content"] += (
                '<div style="margin-top: 100px"><a href='
                + ctaLink
                + ">"
                + ctaLabel
                + "</a></div>"
            )

        body_html = render_to_string(
            "account/email/generic_message.html",
            context,
        )

        msg.attach_alternative(body_html, "text/html")

    msg.send()

    status = msg.anymail_status  # available after sending
    esp_message_id = status.message_id  # e.g., '<12345.67890@example.com>'

    # can only be None during debug, don't run this section in debug?
    esp_message_status = None
    if to_email in status.recipients:
        esp_message_status = status.recipients[to_email].status  # e.g., 'queued'
    return esp_message_id, esp_message_status, body_text, no_rest


def send_magic_link(user, email, viewname):
    """
    Sending the email via django's send_mail because we do need the special features of anymail.
    """
    magic_link = settings.URL_ORIGIN + (
        reverse(viewname)
        + get_query_string(user, scope=email)
        + "&email="
        + urlquote(email)
    )

    context = {"activate_url": magic_link}

    subject = render_to_string("account/email/email_confirmation_subject.txt")

    if viewname == "magic_registration":
        body_text = render_to_string(
            "account/email/email_confirmation_signup_message.txt",
            context,
        )
        body_html = render_to_string(
            "account/email/email_confirmation_signup_message.html",
            context,
        )
    else:
        body_text = render_to_string(
            "account/email/email_confirmation_message.txt",
            context,
        )
        body_html = render_to_string(
            "account/email/email_confirmation_message.html",
            context,
        )

    send_mail(
        subject,
        body_text,
        formated_from(),
        [email],
        html_message=body_html,
    )
