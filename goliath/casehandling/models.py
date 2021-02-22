import datetime

import cleantext
from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.template import Context, Template
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from markupfield.fields import MarkupField
from simple_history.models import HistoricalRecords
from taggit.managers import TaggableManager

from .managers import CaseManager
from .search import SearchExpertnalSupportQuerySet

User = get_user_model()


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Entity(TimeStampMixin):
    """Generic complaint / request recipient"""

    name = models.CharField(max_length=255)
    description = MarkupField(default_markup_type="markdown", blank=True, null=True)
    email = models.EmailField()
    url = models.URLField(blank=True, null=True)

    # remove those two fieds to make it work, FIXME: a least make `description_markup_type` work again
    history = HistoricalRecords(
        excluded_fields=["_description_rendered", "description_markup_type"]
    )

    def __str__(self):
        return self.name


class AutoreplyKeyword(models.Model):
    text_caseinsensitiv = models.TextField()

    def __str__(self):
        return str(self.text_caseinsensitiv)


class CaseType(TimeStampMixin):
    title = models.CharField(max_length=50)
    slug = models.SlugField(
        default="", editable=False, max_length=255, null=False, blank=False
    )
    claim = models.CharField(max_length=100, null=True, blank=True)
    short_description = models.CharField(max_length=500, null=True, blank=True)
    description = MarkupField(default_markup_type="markdown", blank=True, null=True)
    questions = models.JSONField(
        help_text="Please go to https://surveyjs.io/create-survey and paste the JSON 'JSON Editor'. Then go to 'Survey Designer' to edit the survey. Try it out with 'Test Survey'. When you are done, paste the JSON in this field and hit save."
    )
    entities = models.ManyToManyField("Entity", blank=True)
    needs_approval = models.BooleanField(default=False)
    autoreply_keywords = models.ManyToManyField("AutoreplyKeyword", blank=True)
    order = models.FloatField(null=True, blank=True)
    icon_name = models.CharField(max_length=255)
    letter_subject_custom_template = models.TextField(null=True, blank=True)
    letter_template = models.TextField(null=True, blank=True)
    user_notification_custom_text = models.TextField(null=True, blank=True)

    tags = TaggableManager()

    # remove those two fieds to make it work, FIXME: a least make `description_markup_type` work again
    history = HistoricalRecords(
        excluded_fields=["_description_rendered", "description_markup_type"]
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("new-wizzard", kwargs={"pk": self.pk, "slug": self.slug})

    def is_message_autoreply(self, message):
        for keyword in self.autoreply_keywords.all():
            if keyword.text_caseinsensitiv.lower() in message.lower():
                return True
        return False

    def render_letter_subject(self, case):
        if self.letter_subject_custom_template:
            subject_text = Template(self.letter_subject_custom_template).render(
                Context(self)
            )
            return cleantext.normalize_whitespace(subject_text, no_line_breaks=True)
        else:
            return f'Neuer Fall von "{self.title}" auf Unding.de #{case.id}'

    def render_letter(self, answers: dict, username: str):
        tpl_letter = Template(self.letter_template)
        answers["username"] = username
        text = str(tpl_letter.render(Context(answers)))
        text = cleantext.normalize_whitespace(
            text,
            strip_lines=True,
            no_line_breaks=False,
            keep_two_line_breaks=True,
        )
        return text


class Case(TimeStampMixin):
    class Status(models.TextChoices):
        WAITING_EMAIL_ERROR = "EE", "There was error with sending the email"
        WAITING_USER_VERIFIED = "UV", "Waiting user verification"
        WAITING_CASE_APPROVED = "CA", "Waiting admin approval"
        WAITING_INITIAL_EMAIL_SENT = "ES", "Waiting until initial email sent"
        WAITING_RESPONSE = "WR", "Waiting for response"
        WAITING_USER_INPUT = "WU", "Waiting for user input"
        CLOSED_NEGATIVE = "CN", "Closed, given up"
        CLOSED_POSITIVE = "CP", "Closed, case resolved"
        CLOSED_MIXED = "CM", "Closed, mixed feelings"

    slug = models.SlugField(
        default="", editable=False, max_length=255, null=False, blank=False
    )
    questions = models.JSONField(null=True)
    answers = models.JSONField(null=True)
    email = models.EmailField(unique=True)
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
    )
    case_type = models.ForeignKey(
        "CaseType", on_delete=models.SET_NULL, null=True, blank=True
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    selected_entities = models.ManyToManyField("Entity", blank=True)
    answers_subject = models.CharField(max_length=255, null=True, blank=True)
    answers_text = models.TextField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_cases",
    )
    sent_user_reminders = models.IntegerField(default=0)
    last_user_reminder_sent_at = models.DateTimeField(null=True, blank=True)
    sent_entities_reminders = models.IntegerField(default=0)
    last_entities_reminder_sent_at = models.DateTimeField(null=True, blank=True)
    post_cc = models.ForeignKey(
        "PostCaseCreation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cases",
    )

    history = HistoricalRecords()
    objects = CaseManager()

    def save(self, *args, **kwargs):
        self.slug = (
            "nocasetype" if self.case_type is None else slugify(self.case_type.title)
        )
        self.answers_text = self.case_type.render_letter(
            self.answers, self.user.full_name
        )

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("cases-detail", kwargs={"pk": self.pk, "slug": self.slug})

    @property
    def print_status(self):
        if self.status in (
            self.Status.WAITING_USER_INPUT,
            self.Status.WAITING_USER_VERIFIED,
        ):
            return "0_open"
        if self.status in (
            self.Status.CLOSED_NEGATIVE,
            self.Status.CLOSED_POSITIVE,
            self.Status.CLOSED_MIXED,
        ):
            return "2_closed"
        return "1_waiting"

    @property
    def all_messages(self):
        return sorted(
            list(self.receivedmessage_set.all()) + list(self.sentmessage_set.all()),
            key=lambda x: x.sent_at,
        )

    @property
    def is_approved(self):
        return not self.case_type.needs_approval or self.approved_by is not None

    @property
    def is_user_verified(self):
        return EmailAddress.objects.filter(user=self.user, verified=True).exists()

    @property
    def is_sane(self):
        return self.is_user_verified and self.is_approved

    def handle_incoming_email(self, is_autoreply):
        if is_autoreply:
            pass
        else:
            from .tasks import send_user_notification_new_message

            text = "Sie haben eine neue Antwort erhalten."

            if self.case_type.user_notification_custom_text:
                text = self.case_type.user_notification_custom_text

            send_user_notification_new_message(
                self.user.email, settings.URL_ORIGIN + self.get_absolute_url(), text
            )
            self.status = self.Status.WAITING_USER_INPUT
            self.save()

    @property
    def last_action_at(self):
        last_action_date = None
        if self.history.all().count() == 0:
            # there is no history, the object was never updated since creation
            last_action_date = self.created_at
        else:
            # getting the most recent version (in the history)
            prev_case = self.history.first()
            while True:
                if prev_case is None:
                    # there is no history
                    break
                if prev_case.status == self.status:
                    # no status changed, go further back
                    last_action_date = prev_case.history_date
                    break
                # iterate through the all the history item
                prev_case = prev_case.prev_record
        return last_action_date

    def send_user_reminder(self):
        from .tasks import send_user_notification_reminder

        send_user_notification_reminder(
            self.user.email, settings.URL_ORIGIN + self.get_absolute_url()
        )
        self.last_user_reminder_sent_at = datetime.datetime.now()
        self.sent_user_reminders += 1
        self.save()

    def send_entities_reminder(self):
        from .tasks import send_entity_notification_reminder

        for e in self.selected_entities.all():
            send_entity_notification_reminder(e.email, self.email)

        self.last_entities_reminder_sent_at = datetime.datetime.now()
        # can't use F expression because django-simple-history does not support it
        self.sent_entities_reminders += 1
        self.save()


class PostCaseCreation(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    case_type = models.ForeignKey(
        "CaseType", on_delete=models.SET_NULL, null=True, blank=True
    )
    is_contactable = models.BooleanField(_("Kontaktierbar"), default=False)
    post_creation_hint = models.TextField(_("Hinweis"), null=True, blank=True)
    sent_initial_emails_at = models.DateTimeField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse("post-wizzard-success", kwargs={"pk": self.pk})

    def send_all_initial_emails(self):
        from .tasks import send_initial_emails_to_entities

        send_initial_emails_to_entities(self)

    def user_verified_afterwards(self):
        """
        change status and thus trigger email sending (see tasks.py)
        """
        # if the emails were already sent, don't do anything

        send_emails = False
        for case in self.cases.all():
            if len(case.all_messages) > 0:
                return

            if case.is_approved:
                case.status = case.Status.WAITING_INITIAL_EMAIL_SENT
                send_emails = True
            else:
                case.status = case.Status.WAITING_CASE_APPROVED
            case.save()

        if send_emails:
            self.send_all_initial_emails()

    def approve_case(self, user):
        """
        change status and thus trigger email sending (see tasks.py)
        """

        send_emails = False
        for case in self.cases.all():
            # if the emails were already sent, don't do anything
            if len(case.all_messages) > 0:
                return

            case.approved_by = user
            if case.is_user_verified:
                case.status = case.Status.WAITING_INITIAL_EMAIL_SENT
                send_emails = True
            else:
                case.status = case.Status.WAITING_USER_VERIFIED
            case.save()

        if send_emails:
            self.send_all_initial_emails()


class Message(TimeStampMixin):
    from_email = models.EmailField()
    to_email = models.EmailField()
    subject = models.CharField(max_length=255)
    content = models.TextField()
    case = models.ForeignKey("Case", on_delete=models.SET_NULL, null=True, blank=True)
    sent_at = models.DateTimeField()

    class Meta:
        abstract = True
        ordering = ["sent_at"]

    def __str__(self):
        return self.from_email + self.to_email + self.subject


class SentMessage(Message):
    esp_message_id = models.CharField(max_length=255, null=True)
    esp_message_status = models.CharField(max_length=255, null=True)
    error_message = models.TextField(blank=True, null=True)
    history = HistoricalRecords()


class ReceivedMessage(Message):
    received_at = models.DateTimeField()
    html = models.TextField(blank=True, null=True)
    from_display_name = models.TextField(null=True, blank=True)
    from_display_email = models.EmailField()
    spam_score = models.FloatField()
    to_addresses = ArrayField(models.TextField())
    cc_addresses = ArrayField(models.TextField(), null=True, blank=True)
    is_autoreply = models.BooleanField(null=True)
    parsed_content = models.TextField()
    history = HistoricalRecords()


class UserReplyChoice(models.Model):
    subject = models.CharField(max_length=255)
    content = models.TextField()


class ExternalSupport(TimeStampMixin):
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=255, blank=True, null=True)
    tags = TaggableManager()
    search_vector = SearchVectorField(null=True)

    objects = SearchExpertnalSupportQuerySet.as_manager()

    class Meta(object):
        indexes = [GinIndex(fields=["search_vector"])]


# TODO: put into seperate app
from django.contrib.flatpages.models import FlatPage


class GoliathFlatPage(FlatPage):
    markdown_content = MarkupField(
        default_markup_type="markdown", blank=True, null=True
    )
