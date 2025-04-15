from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.decorators import login_required
from eshop.accounts.forms import UserForm
from django.forms import model_to_dict
from django.contrib import messages
from eshop.accounts.models import ShippingAddress

User = get_user_model()

def signup(request):
    if request.method == "POST":
        # Traiter le formulaire
        email = request.POST["email"]
        password = request.POST["password"]
        first_name = request.POST.get("first_name", "")
        last_name = request.POST.get("last_name", "")
        date_birth = request.POST.get("date_birth", None)

        # Champs pour l'adresse
        name = request.POST.get("name", f"{first_name} {last_name}")
        address_1 = request.POST["address_1"]
        address_2 = request.POST.get("address_2", "")
        city = request.POST["city"]
        district = request.POST["district"]
        zip_code = request.POST["zip_code"]

        # Créer l'utilisateur
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            date_birth=date_birth,
        )

        # Créer une adresse de livraison par défaut
        ShippingAddress.objects.create(
            user=user,
            name=name,
            address_1=address_1,
            address_2=address_2,
            city=city,
            district=district,
            zip_code=zip_code,
            default=True,  # Adresse par défaut
        )

        login(request, user)  # Connecter l'utilisateur après l'inscription
        return redirect('index')

    return render(request, 'accounts/account/signup.html')

    return render(request, 'accounts/account/signup.html')

def login_user(request):
    if request.method == "POST":
        # Connecter l'utilisateur
        username = request.POST["username"]
        password=  request.POST["password"]

        user = authenticate(username=username, password=password) # permet de verifier les infos de login + de rediriger en cas d'erreur
        if user:
            login(request, user)
            return redirect('index')

    return render(request, 'accounts/account/login.html')

def logout_user(request):
    logout(request)
    return redirect('index')

@login_required
def profile(request):
    if request.method == "POST":
        action = request.POST.get("action")

        match action:
            case "update_profile":
                # Mise à jour des informations utilisateur
                is_valid = authenticate(email=request.POST.get("email"), password=request.POST.get("password"))
                if is_valid:
                    user = request.user
                    user.last_name = request.POST.get("last_name")
                    user.first_name = request.POST.get("first_name")
                    user.date_birth = request.POST.get("date_birth")
                    user.save()
                    messages.success(request, "Profil mis à jour avec succès.")
                else:
                    messages.error(request, "Mot de passe invalide.")
                return redirect("accounts:profile")

            case "add_address":
                # Ajout d'une nouvelle adresse
                name = request.POST["name"]
                address_1 = request.POST["address_1"]
                address_2 = request.POST.get("address_2", "")
                city = request.POST["city"]
                district = request.POST["district"]
                zip_code = request.POST["zip_code"]

                ShippingAddress.objects.create(
                    user=request.user,
                    name=name,
                    address_1=address_1,
                    address_2=address_2,
                    city=city,
                    district=district,
                    zip_code=zip_code,
                    default=False,  # Par défaut, ce n'est pas l'adresse par défaut
                )
                messages.success(request, "Nouvelle adresse ajoutée avec succès.")
                return redirect("accounts:profile")

            case "update_address":
                # Mise à jour d'une adresse existante
                address_id = request.POST["address_id"]
                address = get_object_or_404(ShippingAddress, pk=address_id, user=request.user)
                address.name = request.POST["name"]
                address.address_1 = request.POST["address_1"]
                address.address_2 = request.POST.get("address_2", "")
                address.city = request.POST["city"]
                address.district = request.POST["district"]
                address.zip_code = request.POST["zip_code"]
                address.save()
                messages.success(request, "Adresse mise à jour avec succès.")
                return redirect("accounts:profile")

            case _:
                # Action non reconnue
                messages.error(request, "Action non valide.")
                return redirect("accounts:profile")

    # Affichage du profil et des adresses
    form = UserForm(initial=model_to_dict(request.user, exclude="password"))
    addresses = request.user.shippingaddress_set.all()
    return render(request, "accounts/account/profile.html", context={"form": form, "addresses": addresses})

@login_required
def set_default_shipping_address(request, pk):
    address = get_object_or_404(ShippingAddress, pk=pk, user=request.user)
    address.set_default()
    messages.success(request, "Adresse définie comme adresse par défaut.")
    return redirect("accounts:profile")


@login_required
def delete_address(request, pk):
    address = get_object_or_404(ShippingAddress, pk=pk, user=request.user)
    address.delete()
    messages.success(request, "Adresse supprimée avec succès.")
    return redirect("accounts:profile")


