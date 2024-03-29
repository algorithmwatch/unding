from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CaseHandlingAppConfig(AppConfig):
    name = "goliath.casehandling"
    verbose_name = _("Case handling for the Goliath project")

    def ready(self):
        from . import signals  # noqa F401
