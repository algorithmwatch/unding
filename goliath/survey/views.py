import json

from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control, never_cache
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from ratelimit.decorators import ratelimit

from goliath.survey.models import Survey, SurveyAnswer


@method_decorator(
    ratelimit(
        key="user_or_ip",
        rate="casehandling.ratelimits.per_user",
        method="POST",
        block=True,
    ),
    name="post",
)
class SurveyAnswerCreateView(View):
    @method_decorator(never_cache)
    def post(self, request, pk, slug):
        survey = get_object_or_404(Survey, pk=pk)
        answers = json.loads(request.POST["answers"])

        user = None
        if request.user.is_authenticated:
            user = request.user

        SurveyAnswer.objects.create(answers=answers, user=user, survey=survey)

        # just use last case for success page for now
        return JsonResponse(
            {
                "url": reverse(
                    "survey-success",
                    kwargs={"pk": survey.pk},
                )
            }
        )

    @method_decorator(cache_control(max_age=3600, public=True))
    def get(self, request, pk, slug):
        survey = get_object_or_404(Survey, pk=pk)

        return render(
            request,
            "survey/answer_new.html",
            {
                "survey": survey,
            },
        )


@method_decorator(cache_control(max_age=3600, public=True), name="dispatch")
class SurveySuccess(DetailView):
    model = Survey
    template_name = "survey/answer_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["share_url"] = self.request.build_absolute_uri(
            self.object.get_absolute_url()
        )
        context[
            "share_text"
        ] = f"""Jetzt an der Umfrage "{self.object.title}" teilnehmen!"""
        return context
