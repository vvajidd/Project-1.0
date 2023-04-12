from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

#my imports
from .forms import RegisterationForm, UserForm, UserAddressForm
from .models import Account, Address
from carts.models import Cart, CartItem
from carts.views import _cart_id
from .models import Address
from orders.models import Order, Payment

#user activation imports
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode 
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
import requests


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            form = RegisterationForm(request.POST)
            if form.is_valid():
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                phone_number = form.cleaned_data['phone_number']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                username = email.split("@")[0]
                user = Account.objects.create_user(first_name = first_name, last_name = last_name, email = email, username = username, password = password)
                user.phone_number = phone_number
                user.save()

                #email verification
                current_site = get_current_site(request)
                mail_subject = 'Confirm your email before login'
                message = render_to_string('account_verification_email.html', {
                    'user' : user,
                    'domain' : current_site,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token' : default_token_generator.make_token(user),         #making/generating token
                })
                to_email = email
                send_email = EmailMessage(mail_subject, message, to=[to_email])
                send_email.send()
                
                return redirect('/accounts/login/?command=verification&email='+email)
    
        else:
            form = RegisterationForm()

    context = {
        'form' : form, 
    }
    return render(request, 'register.html', context)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def login(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']

            user = auth.authenticate(email=email, password=password)
            
            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart = cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart = cart)

                    for item in cart_item:
                        item.user = user
                        item.save()
            except:
                pass

            if user is not None:
                auth.login(request,user)
                # messages.success(request, 'Logged in Successfully.')
                url = request.META.get('HTTP_REFERER')
                try:
                    query = requests.utils.urlparse(url).query
                    params = dict(x.split('=') for x in query.split('&'))
                    if 'next' in params:
                        nextPage = params['next']
                        return redirect(nextPage)
                except:
                    return redirect('home')
            else:
                messages.error(request, 'Email or Password incorrect !')
                return redirect('login')
        return render(request, 'login.html')


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ 


@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.error(request, 'Logged Out Successfully !')
    return redirect('home')

  
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- 


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)

    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Account verified successfully ! Login now')
        return redirect('login')
    else:
        messages.error(request, 'something went wrong . try again')
        return redirect('register')


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------


@login_required(login_url='login')
def dashboard(request):
    addresses = Address.objects.filter(user=request.user)
    context = {
        'addresses' : addresses
    }
    return render(request, 'dashboard.html', context)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------


@login_required(login_url='login')
def edit_profile(request):
    try:
        address = Address.objects.all().filter(user= request.user).first()
    except Address.DoesNotExist:
        pass
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        # profile_form = UserAddressForm(request.POST, instance=address)
        if user_form.is_valid():   # and profile_form.is_valid()
            user_form.save()
            # profile_form.save()
            messages.success(request, 'Your Profile has been updated!')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        # profile_form = UserAddressForm(instance=address)
    context = {
        'user_form': user_form,
    }
    return render(request, 'edit_profile.html', context)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------


@login_required(login_url='login')
def orders(request):
    orders = Order.objects.filter(user = request.user, is_ordered=True).order_by('-created_at')

    print(orders,'    ======================================================================================')

    context = {
        'orders' : orders,
    }
    return render(request, 'my_orders.html', context)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------


@login_required(login_url='login')
def changePassword(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact = request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)        if force user to logout after changning password
                messages.success(request, 'Password updated successfully !')
                return redirect('changePassword')
            else:
                messages.error(request, 'Please enter valid Current Password.')
                return redirect('changePassword')
        else:
            messages.error(request, 'Password doesn\'t match !')
            return redirect('changePassword')
        
    return render(request, 'changePassword.html')


@login_required(login_url='userLogin')
def add_address(request):
    if request.method == 'POST':
        # form = UserAddressForm(request.POST, instance=address)
        form = UserAddressForm(request.POST,request.FILES)
        if form.is_valid():
            print('form is valid')
            address = Address()
            address.user = request.user
            address.address_line_1 =  form.cleaned_data['address_line_1']
            address.address_line_2  = form.cleaned_data['address_line_2']
            address.state =  form.cleaned_data['state']
            address.city =  form.cleaned_data['city']
            address.country = form.cleaned_data['country']
            address.pin_code =  form.cleaned_data['pin_code']
            address.save()
            messages.success(request,'Address added Successfully')
            return redirect('dashboard')
        else:
            messages.success(request,'Form is Not valid')
            return redirect('add_address')
    else:
        form = UserAddressForm()
        context={
            'form': form
        }    
    return render(request,'add_address.html',context)