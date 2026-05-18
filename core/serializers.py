from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Product, Cart, CartItem, Reservation


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class MiniProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name"]


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"


class CartItemSerializer(serializers.ModelSerializer):
    product = MiniProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True,source="product")

    class Meta:
        model = CartItem
        fields = "__all__"


class ReservationSerializer(serializers.ModelSerializer):
    cart = CartSerializer(read_only=True)
    cart_id = serializers.IntegerField(write_only=True,source="cart")
    product = MiniProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True,source="product")

    class Meta:
        model = Reservation
        fields = "__all__"

    def validate(self, data):
        quantity = data.get("quantity")

        if quantity <= 0 or quantity is None:
            raise ValidationError("Quantity must be greater than 0")