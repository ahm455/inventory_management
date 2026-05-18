import pytest

from core.models import Reservation
from core.service import create_reservation


@pytest.mark.django_db(transaction=True)
def test_same_idempotency_key_returns_same_reservation(
    product,
    cart,
):

    reservation1 = create_reservation(
        product_id=product.id,
        cart=cart,
        quantity=2,
        idempotency_key="same-key",
        ttl_minutes=10
    )

    reservation2 = create_reservation(
        product_id=product.id,
        cart=cart,
        quantity=2,
        idempotency_key="same-key",
        ttl_minutes=10
    )

    assert reservation1.id == reservation2.id

    assert Reservation.objects.count() == 1