import datetime

from django.conf import settings

from config import celery_app

from ..utils.email import send_anymail_email
from .models import Case, ReceivedMessage, SentMessage, Status


@celery_app.task()
def send_initial_emails(case):
    """
    send initial email to entity of case type
    """
    subject = "New Case"
    content = case.answers_text

    if not case.is_sane():
        raise ValueError("can't send email because the case is broken")

    to_emails = case.selected_entities.values_list("email", flat=True)
    was_error = False

    for to_email in to_emails:
        from_email = case.email

        esp_message_id, esp_message_status = send_anymail_email(
            to_email,
            subject=subject,
            from_email=from_email,
            text_content=content,
        )

        error_message = None
        if esp_message_status not in ("sent", "queued"):
            error_message = esp_message_status

        if error_message is not None:
            was_error = True

        SentMessage.objects.create(
            case=case,
            to_email=to_email,
            from_email=from_email,
            subject=subject,
            content=content,
            esp_message_id=esp_message_id,
            esp_message_status=esp_message_status,
            error_message=error_message,
            sent_at=datetime.datetime.utcnow(),
        )

    if was_error:
        case.status = Status.WAITING_EMAIL_ERROR
    else:
        # all good, waiting for response
        case.status = Status.WAITING_RESPONSE
    case.save()


@celery_app.task()
def send_notifical_email(to_email, from_email, subject, content):
    """Notify user about incoming new email"""
    send_anymail_email(
        to_email, subject=subject, text_content=content, from_email=from_email
    )


@celery_app.task()
def send_admin_notification_email(subject, content):
    to_email = settings.ADMIN_NOTIFICATION_EMAIL
    from_email = settings.DEFAULT_FROM_EMAIL
    """Notify user about incoming new email"""
    send_anymail_email(
        to_email, subject=subject, text_content=content, from_email=from_email
    )


@celery_app.task()
def persist_inbound_email(message):
    all_to_addresses = [x.addr_spec for x in message.to] + [message.envelope_recipient]

    to_address, case = None, None
    for x in all_to_addresses:
        # can be None
        case = Case.objects.filter(email=x).first()
        if case is not None:
            to_address = x
            break

    msg = ReceivedMessage.objects.create(
        case=case,
        from_email=message.envelope_sender,
        to_email=to_address,
        content=message.text,
        html=message.html,
        subject=message.subject,
        sent_at=message.date,
        spam_score=message.spam_score,
        from_display_name=message.from_email.display_name
        if message.from_email is not None
        else None,
        from_display_email=message.from_email.addr_spec
        if message.from_email is not None
        else None,
        received_at=datetime.datetime.utcnow(),
        to_addresses=[str(x) for x in message.to] + [message.envelope_recipient],
        cc_addresses=[str(x) for x in message.cc],
    )

    if case is not None:
        send_notifical_email(
            case.user.email,
            settings.DEFAULT_FROM_EMAIL,
            "Neue Antwort auf Goliath",
            "Hallo, Sie haben eine neue E-Mai auf Goliath.\n\n"
            + settings.URL_ORIGIN
            + case.get_absolute_url(),
        )
