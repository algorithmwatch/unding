from django.contrib.postgres.fields import ArrayField
from django.db import models
from goliath.users.models import User
from simple_history.models import HistoricalRecords
from markupfield.fields import MarkupField

from taggit.managers import TaggableManager


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Status(models.TextChoices):
    WAITING_RESPONSE = "WR", "Waiting for response"
    WAITING_USER = "WU", "Waiting for user input"
    CLOSED_NEGATIVE = "CN", "Closed, given up"
    CLOSED_POSITIVE = "CP", "Closed, case resolved"
    CLOSED_MIXED = "CM", "Closed, mixed feelings"


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


class CaseType(TimeStampMixin):
    name = models.CharField(max_length=255)
    description = MarkupField(default_markup_type="markdown", blank=True, null=True)
    questions = models.JSONField(
        help_text="Please go to https://surveyjs.io/create-survey and paste the JSON 'JSON Editor'. Then go to 'Survey Designer' to edit the survey. Try it out with 'Test Survey'. When you are done, paste the JSON in this field and hit save."
    )
    entity = models.ForeignKey(
        "Entity", on_delete=models.SET_NULL, null=True, blank=True
    )

    # remove those two fieds to make it work, FIXME: a least make `description_markup_type` work again
    history = HistoricalRecords(
        excluded_fields=["_description_rendered", "description_markup_type"]
    )

    def __str__(self):
        return self.name + " " + str(self.entity)

    def get_absolute_url(self):
        return f"/neu/{self.pk}/"


class Case(TimeStampMixin):
    questions = models.JSONField(null=True)
    answers = models.JSONField(null=True)
    email = models.EmailField(unique=True)
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.WAITING_RESPONSE,
    )
    case_type = models.ForeignKey(
        "CaseType", on_delete=models.SET_NULL, null=True, blank=True
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    entity = models.ForeignKey(
        "Entity", on_delete=models.SET_NULL, null=True, blank=True
    )
    answers_text = models.TextField(null=True, blank=True)

    history = HistoricalRecords()

    def get_absolute_url(self):
        return f"/anliegen/{self.pk}/"

    def all_messages(self):
        return sorted(
            list(self.receivedmessage_set.all()) + list(self.sentmessage_set.all()),
            key=lambda x: x.sent_at,
        )


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
    history = HistoricalRecords()


class ExternalSupport(TimeStampMixin):
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=255, blank=True, null=True)
    tags = TaggableManager()
