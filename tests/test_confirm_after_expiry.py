import pytest
from django.utils import timezone

from core.models import Reservation
from core.service import confirm_reservation
from services.constant import ReservationStatusChoices


@pytest.mark.django_db(transaction=True)
def test_confirm_after_expiry_sets_status_to_expired(
    product,
    cart,
):

    reservation = Reservation.objects.create(
        cart=cart,
        product=product,
        quantity=1,
        status=ReservationStatusChoices.ACTIVE,
        idempotency_key="expired-confirm",
        expires_at=timezone.now() - timezone.timedelta(minutes=1),
    )

    confirm_reservation(reservation.id)

    reservation.refresh_from_db()

    assert reservation.status == ReservationStatusChoices.EXPIRED