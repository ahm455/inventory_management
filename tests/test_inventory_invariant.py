import uuid

import pytest

from hypothesis import given
from hypothesis import strategies as st

from django.contrib.auth.models import User
from django.db.models import Sum

from core.models import (
    Product,
    Cart,
    Reservation,
)

from core.service import (
    create_reservation,
    confirm_reservation,
    release_reservation,
)

from services.constant import ReservationStatusChoices


@pytest.mark.django_db(transaction=True)
@given(
    operations=st.lists(
        st.sampled_from(
            [
                "reserve",
                "confirm",
                "release",
            ]
        ),
        min_size=1,
        max_size=50,
    )
)
def test_inventory_invariant(operations):

    user = User.objects.create_user(
        username=f"user-{uuid.uuid4()}"
    )

    product = Product.objects.create(
        sku=f"HYPOTHESIS-SKU-{uuid.uuid4()}",
        name="Hypothesis Product",
        price=100,
        initial_stock=10,
    )

    cart = Cart.objects.create(
        user=user
    )

    reservations = []

    for idx, operation in enumerate(operations):

        try:

            if operation == "reserve":

                reservation = create_reservation(
                    product_id=product.id,
                    cart=cart,
                    quantity=1,
                    idempotency_key=f"key-{idx}",
                )

                reservations.append(reservation)

            elif operation == "confirm" and reservations:

                confirm_reservation(
                    reservations[0].id
                )

            elif operation == "release" and reservations:

                release_reservation(
                    reservations[0].id
                )

        except Exception:
            pass

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