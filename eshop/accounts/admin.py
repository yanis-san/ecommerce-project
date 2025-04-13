from django.contrib import admin
from eshop.accounts.models import Shopper, ShippingAddress

admin.site.register(Shopper)
admin.site.register(ShippingAddress)