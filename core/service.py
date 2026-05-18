from django.db import transaction
from django.db.models import Sum,Q
from django.utils import timezone
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from inventory_management.settings.base import RESERVATION_TTL_MINUTES
from .models import Product, Reservation
from services.constant import ReservationStatusChoices
import logging

logger = logging.getLogger(__name__)

@transaction.atomic
def create_reservation(*,product_id,cart,quantity,idempotency_key,):
    ttl_minutes = RESERVATION_TTL_MINUTES

    existing = Reservation.objects.filter(idempotency_key=idempotency_key).first()

    if existing:
        return existing

    product = Product.objects.select_for_update().get(id=product_id)

    now = timezone.now()

    Reservation.objects.filter(
        product=product,
        status=ReservationStatusChoices.ACTIVE,
        expires_at__lte=now,
    ).update(status=ReservationStatusChoices.EXPIRED)

    totals = Reservation.objects.filter(product=product).aggregate(
        active_reserved=Sum("quantity",
            filter=Q(status=ReservationStatusChoices.ACTIVE,
                expires_at__gt=now,)),
        confirmed=Sum("quantity",
            filter=Q(status=ReservationStatusChoices.CONFIRMED,))
    )

    active_reserved = totals["active_reserved"] or 0
    confirmed = totals["confirmed"] or 0

    available = product.initial_stock - active_reserved - confirmed

    if quantity > available:
        raise ValidationError("Insufficient inventory")

    try:

        reservation = Reservation.objects.create(
            cart=cart,
            product=product,
            quantity=quantity,
            status=ReservationStatusChoices.ACTIVE,
            idempotency_key=idempotency_key,
            expires_at=now + timezone.timedelta(minutes=ttl_minutes),
        )

    except IntegrityError:

        reservation = Reservation.objects.get(idempotency_key=idempotency_key)

    logger.info(
        "reservation_created",
        extra={
            "reservation_id": reservation.id,
            "product_id": product.id,
            "quantity": quantity,
            "status": reservation.status,
        }
    )

    return reservation


@transaction.atomic
def confirm_reservation(reservation_id):

    reservation = Reservation.objects.select_for_update().get(id=reservation_id)

    if reservation.status == ReservationStatusChoices.CONFIRMED:
        return reservation
    
    if reservation.status != ReservationStatusChoices.ACTIVE:
        raise ValidationError("Reservation not active")

    if reservation.expires_at < timezone.now():
        reservation.status = ReservationStatusChoices.EXPIRED
        reservation.save(update_fields=["status"])
        return reservation

    reservation.status = ReservationStatusChoices.CONFIRMED
    reservation.confirmed_at = timezone.now()

    reservation.save(update_fields=["status", "confirmed_at"])

    logger.info(
        "reservation_confirmed",
        extra={
            "reservation_id": reservation.id,
            "status": reservation.status,
        }
    )
    print(reservation.status)
    return reservation

@transaction.atomic
def release_reservation(reservation_id):

    reservation = (Reservation.objects.select_for_update().get(id=reservation_id))

    if reservation.status != ReservationStatusChoices.ACTIVE:
        return reservation

    reservation.status = ReservationStatusChoices.RELEASED

    reservation.released_at = timezone.now()

    reservation.save(update_fields=["status","released_at"])

    logger.info(
        "reservation_released",
        extra={
            "reservation_id": reservation.id,
            "status": reservation.status,
        }
    )

    return reservation