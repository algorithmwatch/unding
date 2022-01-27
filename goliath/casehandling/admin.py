from cleantext import clean
from django.contrib import admin
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from simple_history.admin import SimpleHistoryAdmin

from .models import (
    AutoreplyKeyword,
    Campaign,
    Case,
    CaseType,
    Entity,
    ExternalSupport,
    PublicFile,
    ReceivedAttachment,
    ReceivedMessage,
    SentMessage,
    SentUserNotification,
)


class RemoveAdminAddButtonMixin(object):
    def has_add_permission(self, request, obj=None):
        return False


class HistoryDeletedFilter(admin.SimpleListFilter):
    """
    Instances deleted with django-simple-history are not shown it admin view.
    Make them visible via a list filter.
    """

    title = _("deleted")
    parameter_name = "is_deleted"

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        self.model = model

    def lookups(self, request, model_admin):
        return (("deleted", _("deleted")),)

    def queryset(self, request, queryset):
        if self.value() == "deleted":
            return queryset.union(self.model.history.filter(history_type="-"))
        return queryset


class HistoryDeletedFilterMixin(object):
    list_filter = (HistoryDeletedFilter,)


class ApprovalFilter(admin.SimpleListFilter):
    """
    Instances deleted with django-simple-history are not shown it admin view.
    Make them visible via a list filter.
    """

    title = _("approval")
    parameter_name = "approval"

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        self.model = model

    def lookups(self, request, model_admin):
        return (
            ("needs_approval", _("needs approval")),
            ("was_approved", _("was approved")),
        )

    def queryset(self, request, queryset):
        if self.value() == "needs_approval":
            return queryset.filter(
                Q(case_type__needs_approval=True) & Q(approved_by=None)
            )
        if self.value() == "was_approved":
            return queryset.filter(
                Q(case_type__needs_approval=True) & ~Q(approved_by=None)
            )
        return queryset


class CaseAdmin(RemoveAdminAddButtonMixin, SimpleHistoryAdmin):
    list_display = [
        "id",
        "created_at",
        "status",
        "case_type",
        "user",
        "email",
    ]
    search_fields = [
        "answers_text",
        "user__first_name",
        "user__last_name",
        "user__email",
    ]
    list_filter = (
        ApprovalFilter,
        HistoryDeletedFilter,
        "selected_entities",
        "approved_by",
        "case_type",
        "status",
        "sent_user_reminders",
        "sent_entities_reminders",
        "last_entities_reminder_sent_at",
        "last_user_reminder_sent_at",
    )
    actions = ["aprove_case"]

    def aprove_case(self, request, queryset):
        done_ids = set()
        # prevent calling approve case multiple times
        for case in queryset:
            post_cc_pk = case.post_cc.pk
            if not post_cc_pk in done_ids:
                case.post_cc.approve_case(user=request.user)
                done_ids.add(post_cc_pk)

    aprove_case.short_description = "Mark selected cases as approved"


class CaseTypeAdmin(HistoryDeletedFilterMixin, SimpleHistoryAdmin):
    list_display = [
        "id",
        "created_at",
        "title",
    ]
    exclude = ("search_vector",)


class EntityAdmin(HistoryDeletedFilterMixin, SimpleHistoryAdmin):
    list_display = [
        "id",
        "created_at",
        "name",
        "email",
        "url",
    ]


class SentSubjectFilter(admin.SimpleListFilter):
    title = _("Subject")

    parameter_name = "subject"

    def lookups(self, request, model_admin):
        subjects = SentMessage.objects.values_list("subject", flat=True)
        subjects = [
            clean(s, lower=False, no_numbers=True, replace_with_number=" ").strip()
            for s in subjects
        ]
        subjects = list(set(subjects))

        return [(x, x) for x in subjects]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(subject__startswith=self.value())


class SentMessageAdmin(RemoveAdminAddButtonMixin, SimpleHistoryAdmin):
    list_display = [
        "id",
        "created_at",
        "subject",
        "from_email",
        "to_email",
        "esp_message_status",
    ]
    list_filter = ("created_at", "to_email", HistoryDeletedFilter, SentSubjectFilter)
    ordering = ("-created_at",)


class ReceivedMessageAdmin(SentMessageAdmin):
    list_display = [
        "id",
        "created_at",
        "subject",
        "from_email",
        "to_email",
        "is_autoreply",
    ]


class SentUserNotificationAdmin(RemoveAdminAddButtonMixin, admin.ModelAdmin):
    list_display = [
        "id",
        "created_at",
        "notification_type",
        "to_email",
        "esp_message_status",
        "case",
    ]
    list_filter = ("created_at", "to_email", "notification_type")
    ordering = ("-created_at",)


class ExternalSupportAdmin(HistoryDeletedFilterMixin, SimpleHistoryAdmin):
    list_display = [
        "id",
        "created_at",
        "name",
        "url",
    ]
    exclude = ("search_vector",)


class AutoreplyKeywordAdmin(HistoryDeletedFilterMixin, SimpleHistoryAdmin):
    view_on_site = False


class ReceivedAttachmentAdmin(RemoveAdminAddButtonMixin, admin.ModelAdmin):
    list_display = [
        "id",
        "filename",
        "message",
    ]


class CampaignAdmin(HistoryDeletedFilterMixin, SimpleHistoryAdmin):
    list_display = [
        "id",
        "title",
    ]


admin.site.register(Entity, EntityAdmin)
admin.site.register(CaseType, CaseTypeAdmin)
admin.site.register(Case, CaseAdmin)
admin.site.register(ExternalSupport, ExternalSupportAdmin)
admin.site.register(ReceivedMessage, ReceivedMessageAdmin)
admin.site.register(ReceivedAttachment, ReceivedAttachmentAdmin)
admin.site.register(SentMessage, SentMessageAdmin)
admin.site.register(SentUserNotification, SentUserNotificationAdmin)
admin.site.register(AutoreplyKeyword, AutoreplyKeywordAdmin)
admin.site.register(Campaign, CampaignAdmin)

# TODO: put into seperate app

from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage

from .models import GoliathFlatPage


# Define a new FlatPageAdmin
class GoliathFlatPageAdmin(FlatPageAdmin, SimpleHistoryAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "url",
                    "title",
                    "social_media_description",
                    "social_media_image",
                    "markdown_content",
                    "sites",
                )
            },
        ),
        (
            _("Advanced options"),
            {
                "classes": ("collapse",),
                "fields": (
                    # "enable_comments",
                    # "registration_required",
                    "template_name",
                ),
            },
        ),
    )


# Re-register FlatPageAdmin
admin.site.unregister(FlatPage)
admin.site.register(GoliathFlatPage, GoliathFlatPageAdmin)

admin.site.register(PublicFile)
