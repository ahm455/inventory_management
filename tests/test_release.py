import pytest

from core.service import (
    create_reservation,
    release_reservation,
)

from services.constant import ReservationStatusChoices


@pytest.mark.django_db(transaction=True)
def test_release_reservation(
    product,
    cart,
):

    reservation = create_reservation(
        product_id=product.id,
        cart=cart,
        quantity=2,
        idempotency_key="release-key",
        ttl_minutes=5
    )

    released = release_reservation(
        reservation.id
    )

    assert released.status == ReservationStatusChoices.RELEASED