import pytest
from django.contrib.auth.models import User

from core.models import Product, Cart


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser",
        password="password123"
    )


@pytest.fixture
def product(db):
    return Product.objects.create(
        sku="SKU-TEST-1",
        name="Test Product",
        price=100,
        initial_stock=10,
    )


@pytest.fixture
def cart(db, user):
    return Cart.objects.create(user=user)