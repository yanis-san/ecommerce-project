from eshop.accounts.views import signup, logout_user, login_user, profile, delete_address, set_default_shipping_address
from django.urls import path

app_name = 'accounts'

urlpatterns = [
    path('profile/', profile, name="profile"),
    path('profile/set_default_shipping/<int:pk>', set_default_shipping_address, name="set-default-shipping"),
    path('signup/', signup, name="signup"),
    path('delete_address/<int:pk>', delete_address, name="delete-address"),
    path('login/', login_user, name="login"),
    path('logout/', logout_user, name="logout"),
    path("set-default-address/<int:pk>/", set_default_shipping_address, name="set_default_shipping_address"),

]

