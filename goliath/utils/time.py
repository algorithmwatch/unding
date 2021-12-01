from django.utils import timezone
import datetime


def date_within_margin(date: datetime.datetime, margin: datetime.timedelta):
    now = timezone.now()
    return now - margin <= date <= now + margin
