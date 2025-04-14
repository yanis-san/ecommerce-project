from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from eshop.store.models import Product, Cart, Order
from django.forms import modelformset_factory
from eshop.store.forms import OrderForm
from django.contrib import messages
from django.utils import timezone


def index(request):
    products = Product.objects.all()
    return render(request, 'store/index.html', context={"products": products})


def product_detail(request,slug):

    product = get_object_or_404(Product, slug=slug)
    return render(request, 'store/detail.html', context={"product":product})


def add_to_cart(request, slug):
    user = request.user
    product = get_object_or_404(Product, slug=slug)
    cart, _ = Cart.objects.get_or_create(user=user)
    order, created = Order.objects.get_or_create(user=user, ordered=False, product=product)

    if created:
        cart.orders.add(order)
        cart.save()
    else:
        order.quantity += 1
        order.save()

    return redirect(reverse("store:product", kwargs={"slug": slug}))


def cart(request):
    orders = Order.objects.filter(user=request.user)
    if orders.count() == 0:
        return redirect("index")
    OrderFormSet = modelformset_factory(Order, form=OrderForm, extra=0)
    formset = OrderFormSet(queryset=orders)
    return render(request, 'store/cart.html', context={"forms":formset})

def update_quantities(request):
    OrderFormSet = modelformset_factory(Order, form=OrderForm, extra=0)
    formset = OrderFormSet(request.POST, queryset=Order.objects.filter(user=request.user))
    if formset.is_valid():
        formset.save()

    return redirect('store:cart')

def delete_cart(request):

    if cart := request.user.cart:
        cart.delete()

    return redirect('index')



def validate_cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    orders = cart.orders.filter(ordered=False)

    for order in orders:
        product = order.product
        if product.stock < order.quantity:
            messages.error(request, f"Il n'y a pas assez de stock pour {product.name}. Stock disponible : {product.stock}.")
            return redirect('store:cart')

    for order in orders:
        order.ordered = True
        order.ordered_date = timezone.now()
        order.product.stock -= order.quantity  # Déduire du stock
        order.product.save()
        order.save()

    messages.success(request, "Votre commande a été validée avec succès.")
    return redirect('store:order_confirmation')


def order_confirmation(request):
    return render(request, 'store/order_confirmation.html')
