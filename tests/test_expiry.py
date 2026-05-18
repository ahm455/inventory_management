import pytest
from django.utils import timezone

from core.models import Reservation
from core.tasks import expire_reservations
from services.constant import ReservationStatusChoices


@pytest.mark.django_db(transaction=True)
def test_expired_reservation_becomes_expired(
    product,
    cart,
):

    reservation = Reservation.objects.create(
        cart=cart,
        product=product,
        quantity=2,
        status=ReservationStatusChoices.ACTIVE,
        idempotency_key="expiry-test",
        expires_at=timezone.now() - timezone.timedelta(minutes=1),
    )

    expire_reservations()

    reservation.refresh_from_db()

    assert reservation.status == ReservationStatusChoices.EXPIRED