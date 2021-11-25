from django.conf import settings
from django.contrib.sites.models import Site


def settings_context(request):
    """Settings available by default to the templates context."""
    # Note: we intentionally do NOT expose the entire settings
    # to prevent accidental leaking of sensitive information
    return {
        "DEBUG": settings.DEBUG,
        "CONTACT_EMAIL": settings.CONTACT_EMAIL,
        "GOOGLE_VERIFICATION": settings.GOOGLE_VERIFICATION,
        # add site because when sending emails, we don't have access to request
        "current_site": Site.objects.get_current(),
        "IS_EMBED": request.GET.get("is-embed") is not None,
    }
