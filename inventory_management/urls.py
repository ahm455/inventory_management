from django.contrib import admin
from django.urls import path
from core.views import *

urlpatterns = [
    path("admin/", admin.site.urls),

    # products
    path("products/", CreateProduct.as_view(), name="products"),
    path("products/<int:pk>/", UpdateDestroyProduct.as_view(), name="product"),

    # carts
    path("carts/", CreateListCart.as_view(), name="carts"),
    path("carts/<int:pk>/", UpdateRemoveCart.as_view(), name="cart"),

    # cart items
    path("cart-items/", CreateListCartItem.as_view(), name="cartitems"),
    path("cart-items/<int:pk>/", UpdateRemoveCartItem.as_view(), name="cartitem"),

    # reservations
    path("reservations/", CreateListReservation.as_view(), name="reservations"),
    path("reservations/<int:pk>/release/", ReleaseReservation.as_view(), name="reservation"),
    path("reservations/<int:pk>/confirm/", ConfirmReservation.as_view(), name="confirm-reservation"),

    # healthz
    path("healthz/", HealthzView.as_view(), name="healthz"),
]