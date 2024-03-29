"""
This implementation of magic link authentification is not ellegant. Take a look at
https://github.com/algorithmwatch/dataskop-platform/tree/main/dataskop/users
to see a more polished solution. If this project ever gets a large refactoring, the user app
should get improved.

Things that need to get changed:

- Merge magic login and magic registration into one view

"""


from allauth.account.models import EmailAddress
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from django.views.generic import View
from django.views.generic.edit import UpdateView
from sesame.utils import get_user

from goliath.casehandling.models import PostCaseCreation

from ..utils.email import send_magic_link
from .forms import MagicLinkLoginForm, MagicLinkSignupForm

User = get_user_model()


@method_decorator(never_cache, name="dispatch")
class UserUpdate(LoginRequiredMixin, UpdateView):
    template_name = "account/index.html"
    model = User
    fields = ["first_name", "last_name"]

    def get_object(self, queryset=None):
        return self.request.user


@never_cache
def magic_link_signup_view(request):
    """
    Disables for now, can't register with magic link.
    """
    if request.method == "POST":
        form = MagicLinkSignupForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]

            try:
                user = User.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                )
                # use cleaned email address in user from now on
                email = user.email
                EmailAddress.objects.create(
                    user=user, email=email, primary=True, verified=False
                )
                send_magic_link(user, email, "magic_registration")
                messages.success(
                    request,
                    "Ein Link zum Abschluss der Registrierung wurde an Ihre E-Mail-Adresse versandt.",
                )

            except IntegrityError as e:
                if "unique constraint" in str(e.args):
                    messages.error(
                        request,
                        "Mit dieser E-mail-Adresse wurde schon ein Account erstellt.",
                    )
    else:
        form = MagicLinkSignupForm()

    return render(request, "account/signup_email.html", {"form": form})


@never_cache
def magic_link_login_view(request):
    if request.method == "POST":
        form = MagicLinkLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = EmailAddress.objects.filter(email=email).first()

            if not user:
                messages.info(
                    request,
                    "Es wurde kein Konto mit dieser E-Mail-Adresse gefunden. Bitte neu registrieren.",
                )
                return redirect("account_signup")

            user = user.user

            send_magic_link(user, email, "magic_login")
            messages.info(
                request, "Ein Link zum Login wurde an Ihre E-Mail-Adresse versandt."
            )

    else:
        form = MagicLinkLoginForm()

    return render(request, "account/login_magic.html", {"form": form})


@method_decorator(never_cache, name="dispatch")
class MagicLinkLoginEmail(View):
    def get(self, request):
        """
        login when person opened magic link from email
        """
        email = request.GET.get("email")

        if email is None:
            return redirect("account_login_magic")

        user = get_user(request, scope=email)

        if user is None:
            messages.error(
                request, "Es wurde kein Account mit diese E-Mail-Adresse gefunden."
            )
            return redirect("account_login")

        email_address = EmailAddress.objects.filter(user=user, email=email).first()

        if not email_address:
            raise PermissionDenied

        redirect_url = "cases"
        if not email_address.verified:
            email_address.verified = True
            email_address.set_as_primary(conditional=True)
            email_address.save()

            # very hacky way to determine if the post creation form was already filled or not
            # need to do it here because the new user need to be logged in
            first_post_cc = PostCaseCreation.objects.filter(
                sent_initial_emails_at__isnull=True, user=user
            ).first()
            if first_post_cc is not None:
                redirect_url = first_post_cc.get_absolute_url()

            # change status, send emails etc.
            for c in PostCaseCreation.objects.filter(user=user):
                c.user_verified_afterwards()

        messages.success(request, "Login erfolgreich")
        login(request, user)
        return redirect(redirect_url)


@method_decorator(never_cache, name="dispatch")
class MagicLinkVerifyEmail(View):
    def get(self, request):
        """
        Scope for each email to ensure the token was actually sent to this
        specific email since we are verifying it.
        """
        email = request.GET.get("email")
        user = get_user(request, scope=email)

        if user is None:
            raise PermissionDenied

        email_address = EmailAddress.objects.filter(user=user, email=email).first()

        if not email_address:
            raise PermissionDenied

        email_address.verified = True
        email_address.set_as_primary(conditional=True)
        email_address.save()

        # very hacky way to determine if the post creation form was already filled or not
        # need to do it here because the new user need to be logged in
        first_post_cc = PostCaseCreation.objects.filter(
            sent_initial_emails_at__isnull=True, user=user
        ).first()
        redirect_url = "cases"
        if first_post_cc is not None:
            redirect_url = first_post_cc.get_absolute_url()

        # change status, send emails etc.
        for c in PostCaseCreation.objects.filter(user=user):
            c.user_verified_afterwards()

        # login
        login(request, user)

        messages.success(request, "Account erfolgreich verifiziert. Danke!")
        return redirect(redirect_url)


class MagicLinkVerifySending(View):
    """
    Really ugly code. This was copied from the above view to modify it slighty for the special case
    when a user has already an account, but creates a new case without being logged in.
    This needs to be done in a better way... FIXME
    """

    def get(self, request):
        email = request.GET.get("email")
        user = get_user(request, scope=email)

        if user is None:
            raise PermissionDenied

        email_address = EmailAddress.objects.filter(user=user, email=email).first()

        if not email_address:
            raise PermissionDenied

        if not email_address.verified:
            email_address.verified = True
            email_address.set_as_primary(conditional=True)
            email_address.save()

        # very hacky way to determine if the post creation form was already filled or not
        # need to do it here because the new user need to be logged in
        first_post_cc = PostCaseCreation.objects.filter(
            sent_initial_emails_at__isnull=True, user=user
        ).first()
        redirect_url = "cases"
        if first_post_cc is not None:
            redirect_url = first_post_cc.get_absolute_url()

        # change status, send emails etc.
        for c in PostCaseCreation.objects.filter(user=user):
            c.user_verified_afterwards()

        # login
        login(request, user)

        messages.success(request, "Die Anfragen wurden verschickt. Danke!")
        return redirect(redirect_url)


@require_GET
@never_cache
def export_text(request):
    user = request.user
    export_string = ""

    for case in user.case_set.all():
        for m in case.all_messages:
            m_text = ", ".join(
                [f"{k}: {v}" for (k, v) in m.__dict__.items() if k != "_state"]
            )
            export_string += m_text + "\n\n"

    response = HttpResponse(export_string, content_type="text/plain; charset=UTF-8")
    response["Content-Disposition"] = 'attachment; filename="unding-export.txt"'
    return response
