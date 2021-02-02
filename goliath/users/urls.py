from django.urls import include, path, re_path
from rest_framework import routers

from goliath.users.views import (
    MagicLinkLoginEmail,
    MagicLinkVerifyEmail,
    UserUpdate,
    magic_link_login_view,
    magic_link_signup_view,
)

urlpatterns = [
    path(
        "magic/registration/",
        MagicLinkVerifyEmail.as_view(),
        name="magic_registration",
    ),
    path(
        "magic/login/",
        MagicLinkLoginEmail.as_view(),
        name="magic_login",
    ),
    path(
        "account/signup/email/",
        magic_link_signup_view,
        name="account_signup_email",
    ),
    # overriding allauth specific login page
    path(
        "account/login/",
        magic_link_login_view,
        name="account_login",
    ),
    # hacking simple account page here
    path("account/", UserUpdate.as_view(), name="account_index"),
]