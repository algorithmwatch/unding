import datetime
import json
import traceback

from allauth.account.models import EmailAddress
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls.base import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, View
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from ..utils.email import send_magic_link
from .forms import CaseStatusForm, get_admin_form_preview
from .models import Case, CaseType, Status
from .tasks import send_admin_waiting_approval_case, send_initial_emails

User = get_user_model()


def get_user_for_case(request, answers):
    """
    Create a new user or return current logged in user
    """
    is_logged_in = request.user.is_authenticated
    if is_logged_in:
        user = request.user
    else:
        # need to create a new, unverified user
        # https://stackoverflow.com/q/29147550/4028896

        first_name, last_name, email = (
            answers["awfirstnamequestion"],
            answers["awlastnamequestion"],
            answers["awemailquestion"],
        )
        user = User.objects.create_user(
            first_name=first_name, last_name=last_name, email=email
        )
        # cleaned version
        email = user.email

        EmailAddress.objects.create(
            user=user, email=email, primary=True, verified=False
        )

        send_magic_link(user, email, "magic_registration")
    return user, is_logged_in


class CaseTypeListView(ListView):
    model = CaseType


class CaseCreateView(View):
    def post(self, request, pk, slug):
        case_type = get_object_or_404(CaseType, pk=pk)
        answers = json.loads(request.POST["answers"])
        user, is_logged_in = get_user_for_case(request, answers)
        text = case_type.render_letter(answers, user.full_name)

        if (
            not is_logged_in
            or not EmailAddress.objects.filter(user=user, verified=True).exists()
        ):
            status = Status.WAITING_USER_VERIFIED
        elif case_type.needs_approval:
            status = Status.WAITING_CASE_APPROVED
        else:
            # this will send the initial email via Signal
            status = Status.WAITING_INITIAL_EMAIL_SENT

        # try 20 times to generate unique email for this case and then give up
        # increase the number of digits for each try
        error_count = 0
        while True:
            try:
                # Nest the already atomic transaction to let the database safely fail.
                with transaction.atomic():
                    case = Case.objects.create(
                        case_type=case_type,
                        email=user.gen_case_email(error_count + 1),
                        answers_text=text,
                        user=user,
                        answers=answers,
                        status=status,
                    )
                break
            except IntegrityError as e:
                if "unique constraint" in e.args[0]:
                    error_count += 1
                    if error_count > 20:
                        raise e
        # if the user selected entities, we may need need to send the email to more than 1 entity
        if "awentitycheckbox" in answers:
            entity_ids = answers["awentitycheckbox"]
            case.selected_entities.add(*case_type.entities.filter(pk__in=entity_ids))
        else:
            case.selected_entities.add(case_type.entities.first())
            assert case_type.entities.all().count() == 1

        if case.status == Status.WAITING_INITIAL_EMAIL_SENT:
            send_initial_emails(case)
        elif case.case_type.needs_approval:
            send_admin_waiting_approval_case()

        if is_logged_in:
            return JsonResponse(
                {
                    "url": reverse(
                        "post-wizzard-success",
                        kwargs={"slug": case.slug, "pk": case.pk},
                    )
                }
            )
        else:
            return JsonResponse(
                {
                    "url": reverse(
                        "post-wizzard-email",
                    )
                }
            )

    def get(self, request, pk, slug):
        case_type = get_object_or_404(CaseType, pk=pk)

        return render(
            request,
            "casehandling/case_new.html",
            {
                "case_type": case_type,
                "entities_values": json.dumps(
                    list(case_type.entities.values_list("id", "name"))
                ),
            },
        )


class CaseStatusUpdateView(LoginRequiredMixin, UpdateView):
    """
    Adapted from https://docs.djangoproject.com/en/3.1/topics/class-based-views/mixins/
    """

    template_name = "casehandling/case_detail.html"
    form_class = CaseStatusForm
    model = Case

    def get_success_url(self):
        return self.object.get_absolute_url()


class CaseDetailView(LoginRequiredMixin, DetailView):
    model = Case

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CaseStatusForm()
        return context


class CaseDetailAndUpdateView(View):
    def get(self, request, *args, **kwargs):
        view = CaseDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CaseStatusUpdateView.as_view()
        return view(request, *args, **kwargs)


class CaseListView(LoginRequiredMixin, ListView):
    model = Case
    template_name = "casehandling/case_list.html"

    def get_queryset(self):
        """
        limit to user
        """
        qs = Case.objects.filter(user=self.request.user)
        return qs


class CaseSuccessView(LoginRequiredMixin, UpdateView):
    model = Case
    fields = ["is_contactable", "post_creation_hint"]
    template_name = "casehandling/case_success.html"


class CaseVerifyEmailView(TemplateView):
    template_name = "casehandling/case_email.html"


class HomePageView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_case_types"] = CaseType.objects.filter(
            order__isnull=False
        ).order_by("order")
        return context


class DashboardPageView(TemplateView):
    template_name = "pages/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # `print_status` is a propery of the model and thus we can't use the ORM's filter functions
        now = datetime.datetime.now()
        time_open_cases = [
            now - x.created_at
            for x in Case.objects.all()
            if x.print_status != "3_closed"
        ]
        context["num_open_cases"] = len(time_open_cases)
        context["avg_time_open_cases"] = (
            sum(time_open_cases, datetime.timedelta(0, 0)).days / len(time_open_cases)
            if len(time_open_cases) > 0
            else 0
        )

        time_closed_cases = [
            now - x.created_at
            for x in Case.objects.all()
            if x.print_status == "3_closed"
        ]
        context["num_closed_cases"] = len(time_closed_cases)
        context["avg_time_closed_cases"] = (
            sum(time_closed_cases, datetime.timedelta(0, 0)).days
            / len(time_closed_cases)
            if len(time_closed_cases) > 0
            else 0
        )

        # most used case types
        context["top_case_types"] = CaseType.objects.annotate(
            total=Count("case")
        ).order_by("-total")[:3]

        return context


@staff_member_required
def admin_preview_letter_view(request, pk):
    ct = get_object_or_404(CaseType, pk=pk)

    AdminPreviewForm = get_admin_form_preview(ct)
    letter_text = None
    render_error_message = None

    if request.method == "POST":
        form = AdminPreviewForm(request.POST)
        if form.is_valid():
            username = (
                form.cleaned_data["username"] if "username" in form.cleaned_data else ""
            )
            try:
                letter_text = ct.render_letter(dict(form.cleaned_data), username)
            except Exception as e:
                render_error_message = str(e)

                render_error_message += "\n\n".join(
                    traceback.format_exception(
                        etype=type(e), value=e, tb=e.__traceback__
                    )
                )

    else:
        form = AdminPreviewForm()

    return render(
        request,
        "casehandling/casetype_preview_letter.html",
        {
            "form": form,
            "letter_text": letter_text,
            "case_type": ct,
            "error": render_error_message,
        },
    )


@require_POST
@csrf_exempt
def preview_letter_text_view(request, pk):
    ct = get_object_or_404(CaseType, pk=pk)
    answers = json.loads(request.POST["answers"])
    username = request.POST["username"] if "username" in request.POST else ""
    return HttpResponse(ct.render_letter(answers, username), content_type="text/plain")
