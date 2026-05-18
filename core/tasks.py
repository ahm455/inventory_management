from celery import shared_task
from django.utils import timezone
from .models import Reservation
from services.constant import ReservationStatusChoices


@shared_task
def expire_reservations():

    Reservation.objects.filter(
        status=ReservationStatusChoices.ACTIVE,
        expires_at__lte=timezone.now()
    ).update(
        status=ReservationStatusChoices.EXPIRED,
        released_at=timezone.now()
    )
