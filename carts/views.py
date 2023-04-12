from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from carts import utils
from products.models import Product
from .models import Cart, CartItem
from accounts.models import Address
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

from orders.models import Coupon, UserCoupon


# Create your views here.

def _cart_id(request):                                    #function name starting with _ is prvt fnction ...... 
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()                   #this function is taking / creating and taking sessionid for seperate cart for seperate user
    return cart

# ===========================================================================================================================================================================

def add_cart(request, product_id):
    current_user = request.user

    if current_user.is_authenticated:
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            pass

        cart_item, created = CartItem.objects.get_or_create(
            user = request.user,
            product = product,
            quantity = 1
        )
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        return redirect('cart')


    else:
        product = Product.objects.get(id=product_id)
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))          #get the cart using the cart_id present in the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()

        try:
            cart_item = CartItem.objects.get(product=product, cart=cart)
            cart_item.quantity += 1  #increment by 1
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )
            cart_item.save()
        return redirect('cart')

# ===========================================================================================================================================================================

def remove_cart(request, product_id):

    if request.user.is_authenticated:
        pass
    else:
        cart = Cart.objects.get(cart_id =_cart_id(request))
        product = get_object_or_404(Product, id = product_id)
        cart_item = CartItem.objects.get(product = product, cart = cart)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1 
            cart_item.save()
        else:
            cart_item.delete()
        return redirect('cart')

# ===========================================================================================================================================================================

def delete_cart(request, product_id):
    cart = Cart.objects.get(cart_id =_cart_id(request))
    # product = get_object_or_404(Product, id = product_id)
    try:
        product = Product.objects.get(id = product_id)
    except Product.DoesNotExist:
        pass
    cart_item = CartItem.objects.get(product = product, cart = cart)
    if cart_item.quantity >= 1:
        cart_item.delete()
    return redirect('cart')


# ===========================================================================================================================================================================

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        
        tax = utils.tax(total)
        grand_total = utils.grand_total(total,tax)
    except ObjectDoesNotExist:
        pass

    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total' : grand_total,
    }
    return render(request, 'cart.html', context)

# ===========================================================================================================================================================================

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart, is_active=True)
            
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        
        tax = utils.tax(total)
        grand_total = utils.grand_total(total,tax)
    except ObjectDoesNotExist:
        pass

    coupons = Coupon.objects.filter(active = True)

    for item in coupons:
        try:
            coupon = UserCoupon.objects.get(user = request.user,coupon = item)
        except:
            coupon = UserCoupon()
            coupon.user = request.user
            coupon.coupon = item
            coupon.save() 

    coupons = UserCoupon.objects.filter(user = request.user, used=False)
    active_coupons = Coupon.objects.filter(active=True)

    try:
        addresses = Address.objects.filter(user=request.user)
    except Address.DoesNotExist:
        pass


    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total' : grand_total,
        'addresses' : addresses,
        'coupons':coupons,
        'active_coupons':active_coupons,
    }
    return render(request, 'checkout.html', context)