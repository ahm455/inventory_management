import multiprocessing

import pytest

from django.contrib.auth.models import User
from django.db import close_old_connections
from django.db.models import Sum

from core.models import (
    Product,
    Cart,
    Reservation,
)

from core.service import create_reservation
from services.constant import ReservationStatusChoices


PROCESS_COUNT = 50


def reservation_worker(product_id):

    close_old_connections()

    try:

        user = User.objects.first()

        cart = Cart.objects.create(
            user=user
        )

        create_reservation(
            product_id=product_id,
            cart=cart,
            quantity=1,
            idempotency_key=str(
                multiprocessing.current_process().pid
            ),
        )

    except Exception:
        pass

    finally:
        close_old_connections()


@pytest.mark.django_db(transaction=True)
def test_no_oversell_under_concurrency():

    user = User.objects.create_user(
        username="load-user"
    )

    product = Product.objects.create(
        sku="CONCURRENT-SKU",
        name="Concurrent Product",
        price=100,
        initial_stock=10,
    )

    processes = []

    for _ in range(PROCESS_COUNT):

        process = multiprocessing.Process(
            target=reservation_worker,
            args=(product.id,),
        )

        process.start()
        processes.append(process)

    for process in processes:
        process.join()

    close_old_connections()

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

    assert active_total <= 10