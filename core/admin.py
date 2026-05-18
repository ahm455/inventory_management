from django.contrib import admin
from .models import *

admin.site.register(Product)
admin.site.register(Reservation)
admin.site.register(Cart)
admin.site.register(CartItem)