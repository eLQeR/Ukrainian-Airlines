from __future__ import absolute_import
from celery import shared_task
from airlines_api.models import Flight
from django.utils import timezone


@shared_task
def complete_flight():
    now = timezone.now()

    for task in Flight.objects.filter(is_completed=False):
        if task.departure_time < now:
            task.is_completed = True
            task.save()
