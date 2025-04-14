from eshop.store.views import index, product_detail, add_to_cart, cart, delete_cart, update_quantities, validate_cart, order_confirmation
from django.urls import path

app_name = "store"

urlpatterns = [
    path('cart/', cart, name="cart"),
    path('cart/update_quantities', update_quantities, name="update-quantities"),
    path('cart/delete/', delete_cart, name="delete-cart"),
    path('product/<str:slug>/', product_detail,name='product'),
    path('product/<str:slug>/add-to-cart', add_to_cart,name='add-to-cart'),
        path('cart/validate/', validate_cart, name='validate-cart'),
    path('order/confirmation/', order_confirmation, name='order_confirmation'),
]
