import pytest
from django.db.models import Sum

from core.models import Reservation
from services.constant import ReservationStatusChoices


@pytest.mark.django_db(transaction=True)
def test_final_inventory_invariant(
    product,
):

    active_total = (
        Reservation.objects.filter(
            product=product,
            status=ReservationStatusChoices.ACTIVE,
        ).aggregate(total=Sum("quantity"))["total"]
        or 0
    )

    confirmed_total = (
        Reservation.objects.filter(
            product=product,
            status=ReservationStatusChoices.CONFIRMED,
        ).aggregate(total=Sum("quantity"))["total"]
        or 0
    )

    assert (
        active_total + confirmed_total
        <= product.initial_stock
    )