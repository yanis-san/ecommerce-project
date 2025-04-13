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
        #Traiter le formulaire
        username = request.POST["username"] #la clé c'est le name dans le html form
        password = request.POST["password"] #la clé c'est le name dans le html form
        user = User.objects.create_user(username=username,password=password)
        login(request, user)
        return redirect('index')

    return render(request,'accounts/account/signup.html')

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
        is_valid = authenticate(email=request.POST.get("email"), password=request.POST.get("password"))
        if is_valid:
            user = request.user
            user.last_name = request.POST.get("last_name")
            user.first_name = request.POST.get("first_name")
            user.date_birth = request.POST.get("date_birth")
            user.save()

        else:
            messages.add_message(request, messages.ERROR, "Invalid password")
    
        return redirect("accounts:profile")

    form = UserForm(initial=model_to_dict(request.user, exclude='password'))
    addresses = request.user.shippingaddress_set.all()
    return render(request, 'accounts/account/profile.html', context={"form":form, "addresses": addresses})

@login_required
def set_default_shipping_address(request,pk):
    address: ShippingAddress = get_object_or_404(ShippingAddress, pk=pk)
    address.set_default()
    return redirect('accounts:profile')



@login_required
def delete_address(request, pk):
    address = get_object_or_404(ShippingAddress, pk=pk, user=request.user)
    address.delete()
    return redirect('accounts:profile')


