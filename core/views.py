from django.db import connections, OperationalError
from rest_framework import generics, status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from .models import Product, Cart, CartItem, Reservation
from .serializers import *
from .service import *
from redis import Redis
from redis.exceptions import RedisError
from celery import current_app

# =========================
# PRODUCT VIEWS
# =========================

class CreateProduct(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class UpdateDestroyProduct(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


# =========================
# CART VIEWS
# =========================

class CreateListCart(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class UpdateRemoveCart(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


# =========================
# CART ITEM VIEWS
# =========================

class CreateListCartItem(generics.ListCreateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer


class UpdateRemoveCartItem(generics.RetrieveUpdateDestroyAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer


# =========================
# RESERVATION VIEWS
# =========================

class CreateListReservation(generics.ListCreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def create(self, request, *args, **kwargs):

        cart = get_object_or_404(Cart,id=request.data.get("cart_id"))

        reservation = create_reservation(
            product_id=request.data.get("product_id"),
            cart=cart,
            quantity=request.data.get("quantity"),
            idempotency_key=request.data.get("idempotency_key"),
        )

        serializer = self.get_serializer(reservation)

        return Response(serializer.data,status=status.HTTP_201_CREATED)


class ConfirmReservation(generics.GenericAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def post(self, request, pk):

        reservation = confirm_reservation(pk)

        serializer = self.get_serializer(reservation)

        return Response(serializer.data)


class ReleaseReservation(generics.GenericAPIView):

    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def delete(self, request, pk):

        reservation = release_reservation(pk)
        serializer = self.get_serializer(reservation)
        return Response(serializer.data)


# =========================
# HEALTH CHECK
# =========================

class HealthzView(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):

        health = {
            "database": "down",
            "redis": "down",
            "celery": "down",
        }

        response_status = status.HTTP_200_OK

        try:
            db_conn = connections["default"]
            db_conn.cursor()

            health["database"] = "up"

        except OperationalError:
            response_status = status.HTTP_503_SERVICE_UNAVAILABLE


        try:
            redis_client = Redis(
                host="localhost",
                port=6379,
                db=0,
                socket_connect_timeout=2,
            )

            redis_client.ping()

            health["redis"] = "up"

        except RedisError:
            response_status = status.HTTP_503_SERVICE_UNAVAILABLE

        try:
            inspect = current_app.control.inspect(timeout=1)
            stats = inspect.stats()

            if stats:
                health["celery"] = "up"
            else:
                health["celery"] = "no workers available"
                response_status = status.HTTP_503_SERVICE_UNAVAILABLE

        except Exception:
            response_status = status.HTTP_503_SERVICE_UNAVAILABLE

        if response_status == status.HTTP_200_OK:
            return Response({"status": "ok","services": health,},status=response_status,)

        return Response({"status": "error","services": health,},status=response_status,)