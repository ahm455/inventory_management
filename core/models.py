from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from services.constant import TimeStamp, ReservationStatusChoices


class Product(TimeStamp):
    sku= models.CharField(max_length=120,unique=True)
    name=models.CharField(max_length=100)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    initial_stock=models.PositiveIntegerField()

class Cart(TimeStamp):
    user = models.ForeignKey(User,on_delete=models.CASCADE)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

class Reservation(TimeStamp):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="reservations")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reservations")
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(choices=ReservationStatusChoices.choices,default=ReservationStatusChoices.ACTIVE,max_length=20)
    idempotency_key = models.CharField(max_length=255,unique=True)
    expires_at = models.DateTimeField()
    released_at = models.DateTimeField(null=True,blank=True)
    confirmed_at = models.DateTimeField(null=True,blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["product", "status"]),
            models.Index(fields=["expires_at"]),
        ]