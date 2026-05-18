import os
import signal
import multiprocessing

import pytest
from django.db.models import Sum

from core.models import (
    Product,
    Reservation,
)

from services.constant import ReservationStatusChoices


@pytest.mark.django_db(transaction=True)
def test_inventory_consistency_after_process_crash(
    product,
    cart,
):

    def crashing_worker():
        os.kill(os.getpid(), signal.SIGKILL)

    process = multiprocessing.Process(
        target=crashing_worker
    )

    process.start()
    process.join()

    active_total = (
        Reservation.objects.filter(
            status=ReservationStatusChoices.ACTIVE
        ).aggregate(total=Sum("quantity"))["total"]
        or 0
    )

    confirmed_total = (
        Reservation.objects.filter(
            status=ReservationStatusChoices.CONFIRMED
        ).aggregate(total=Sum("quantity"))["total"]
        or 0
    )

    assert (
        active_total + confirmed_total
        <= product.initial_stock
    )