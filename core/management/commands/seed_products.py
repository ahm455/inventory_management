from django.core.management.base import BaseCommand
from core.models import Product

class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        products = []

        for i in range(1, 35):
            products.append(
                Product(
                    sku=f"SKU{i:03d}",
                    name=f"Product {i}",
                    price=100 * i,
                    initial_stock=10 * i
                )
            )

        Product.objects.bulk_create(products)

        self.stdout.write(self.style.SUCCESS("25 Products seeded successfully"))