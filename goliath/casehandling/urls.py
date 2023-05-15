from django.urls import include, path, re_path
from rest_framework import routers

from .api_views import CaseTypeViewSet, ExternalSupportViewSet
from .views import (
    CampaignView,
    CaseCreateView,
    CaseDetailAndUpdateView,
    CaseListView,
    CaseSuccessView,
    CaseTypeListView,
    CaseVerifyEmailView,
    DashboardPageView,
    HomePageView,
    OverPageView,
    PrivateAttachmentFileDownload,
    PublicFileDownload,
    admin_preview_letter_view,
    preview_letter_text_view,
    send_autoreply,
    send_user_message_history_view,
)

router = routers.DefaultRouter()
router.register(r"externalsupport", ExternalSupportViewSet, basename="externalsupport")
router.register(r"casetype", CaseTypeViewSet, basename="casetype")

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("dashboard/", DashboardPageView.as_view(), name="dashboard"),
    path("neu/", view=OverPageView.as_view(), name="new"),
    path("neu/<str:slug>/<int:pk>/", view=OverPageView.as_view(), name="new-wizzard"),
    # If you want to reuse the code, remove the two lines above and uncomment the next two lines
    # path("neu/", view=CaseTypeListView.as_view(), name="new"),
    # path("neu/<str:slug>/<int:pk>/", view=CaseCreateView.as_view(), name="new-wizzard"),
    path(
        "erfolg/<int:pk>/",
        view=CaseSuccessView.as_view(),
        name="post-wizzard-success",
    ),
    path(
        "email-bestaetigen/",
        view=CaseVerifyEmailView.as_view(),
        name="post-wizzard-email",
    ),
    path("fall/", view=CaseListView.as_view(), name="cases"),
    path(
        "fall/<str:slug>/<int:pk>/",
        view=CaseDetailAndUpdateView.as_view(),
        name="cases-detail",
    ),
    path(
        "kampagne/<str:slug>/<int:pk>/",
        view=CampaignView.as_view(),
        name="campaign-detail",
    ),
    path("fall-auto-reply/<int:pk>/", view=send_autoreply, name="case-sent-autoreply"),
    path(
        "fall-nachrichten-verlauf/<int:pk>/",
        view=send_user_message_history_view,
        name="case-message-history",
    ),
    path(
        "falltyp-text/<int:pk>/",
        view=preview_letter_text_view,
        name="casetype-letter-text",
    ),
    path(
        "vorschau/<int:pk>/",
        view=admin_preview_letter_view,
        name="casetype-letter-text-admin-preview",
    ),
    path(
        "media/public_files/<path:relative_path>",
        PublicFileDownload.as_view(),
        name="public-file-download",
    ),
    path(
        "media/private_attachments/<path:relative_path>",
        PrivateAttachmentFileDownload.as_view(),
        name="private-attachment-download",
    ),
    re_path(r"^anymail/", include("anymail.urls")),
    re_path(r"^comments/", include("django_comments.urls")),
    path("api/", include(router.urls)),
]
