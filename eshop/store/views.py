from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from eshop.store.models import Product, Cart, Order
from django.forms import modelformset_factory
from eshop.store.forms import OrderForm
from django.contrib import messages
from django.utils import timezone
from eshop.accounts.forms import ShippingAddressForm
from eshop.accounts.models import ShippingAddress



def index(request):
    products = Product.objects.all()
    return render(request, 'store/index.html', context={"products": products})


def product_detail(request,slug):

    product = get_object_or_404(Product, slug=slug)
    return render(request, 'store/detail.html', context={"product":product})


def add_to_cart(request, slug):
    user = request.user
    product = get_object_or_404(Product, slug=slug)

    if user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=user)
        
        order, created = Order.objects.get_or_create(user=user, ordered=False, product=product)

        if created:
            cart.orders.add(order)
            cart.save()
        else:
            order.quantity += 1
            order.save()

    else:
        cart = request.session.get("cart", {})  # Récupère ou crée un panier vide dans la session
        product_id = str(product.id)

        if product_id in cart:
            cart[product_id] += 1
        else:
            cart[product_id] = 1

        request.session["cart"] = cart
        request.session.modified = True  
    return redirect(reverse("store:product", kwargs={"slug": slug}))



def cart(request):
    if request.user.is_authenticated:
        # Pour un utilisateur authentifié, récupérer les commandes en cours dans son panier
        orders = Order.objects.filter(user=request.user, ordered=False)
        
        if orders.count() == 0:
            return redirect("index")  # Si le panier est vide, rediriger vers la page d'accueil
        
        OrderFormSet = modelformset_factory(Order, form=OrderForm, extra=0)
        formset = OrderFormSet(queryset=orders)
        
        return render(request, 'store/cart.html', context={"forms": formset})
    
    else:
        # Pour un utilisateur non authentifié, récupérer les produits dans la session
        cart_data = request.session.get("cart", {})
        
        if not cart_data:
            return redirect("index")  # Panier vide, rediriger vers la page d'accueil
        
        # Récupérer les produits à partir des IDs dans le panier de la session
        product_ids = cart_data.keys()
        products = Product.objects.filter(id__in=product_ids)
        
        # Construire une liste des produits et de leurs quantités pour l'affichage
        session_cart = []
        for product in products:
            quantity = cart_data.get(str(product.id), 0)
            session_cart.append({
                "product": product,
                "quantity": quantity,
            })
        
        return render(request, 'store/cart.html', context={"session_cart": session_cart})
    

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
    if request.user.is_authenticated:
        # Utilisateur authentifié
        cart = get_object_or_404(Cart, user=request.user)
        orders = cart.orders.filter(ordered=False)

        # Vérifier si l'utilisateur a une adresse par défaut
        shipping_address = request.user.shippingaddress_set.filter(default=True).first()
        if not shipping_address:
            # Si l'utilisateur n'a qu'une seule adresse, elle devient par défaut
            addresses = request.user.shippingaddress_set.all()
            if addresses.count() == 1:
                shipping_address = addresses.first()
                shipping_address.default = True
                shipping_address.save()
            else:
                messages.error(request, "Veuillez définir une adresse de livraison avant de valider votre commande.")
                return redirect("accounts:profile")

        # Associer l'adresse par défaut à chaque commande
        for order in orders:
            order.shipping_address = shipping_address
            order.save()

    else:
        # Utilisateur non authentifié
        cart_data = request.session.get("cart", {})
        if not cart_data:
            messages.error(request, "Votre panier est vide.")
            return redirect("index")

        # Récupérer les informations de livraison depuis la session
        shipping_address_data = request.session.get("shipping_address")
        if not shipping_address_data:
            messages.error(request, "Veuillez fournir vos informations de livraison.")
            return redirect("store:checkout")

        # Créer une adresse de livraison temporaire
        shipping_address = ShippingAddress.objects.create(**shipping_address_data)

        # Créer les commandes pour les utilisateurs non connectés
        orders = []
        for product_id, quantity in cart_data.items():
            product = get_object_or_404(Product, id=product_id)
            order = Order.objects.create(
                product=product,
                quantity=quantity,
                shipping_address=shipping_address,
                ordered=False
            )
            orders.append(order)

    # Vérification du stock pour chaque produit
    for order in orders:
        product = order.product
        if product.stock < order.quantity:
            messages.error(request, f"Il n'y a pas assez de stock pour {product.name}. Stock disponible : {product.stock}.")
            return redirect('store:cart')

    # Marquer les ordres comme validés et mettre à jour les stocks
    for order in orders:
        order.ordered = True
        order.ordered_date = timezone.now()
        order.save()

        # Déduire du stock du produit
        product = order.product
        product.stock -= order.quantity
        product.save()

    # Vider le panier pour les utilisateurs non authentifiés
    if not request.user.is_authenticated:
        request.session["cart"] = {}
        request.session["shipping_address"] = {}
        request.session.modified = True

    messages.success(request, "Votre commande a été validée avec succès.")
    return redirect('store:order_confirmation')

def order_confirmation(request):
    return render(request, 'store/order_confirmation.html')



def checkout(request):
    if request.user.is_authenticated:
  
        return redirect('store:validate-cart')

    cart_data = request.session.get("cart", {})
    if not cart_data:
        messages.error(request, "Votre panier est vide.")
        return redirect("store:cart")


    product_ids = cart_data.keys()
    products = Product.objects.filter(id__in=product_ids)

    if request.method == "POST":
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            request.session["shipping_address"] = form.cleaned_data
            messages.success(request, "Vos informations de livraison ont été enregistrées.")
            return redirect('store:validate-cart')
    else:
        form = ShippingAddressForm()

    return render(request, "store/checkout.html", context={"form": form, "cart": cart_data, "products": products})