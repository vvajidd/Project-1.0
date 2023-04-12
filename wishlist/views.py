from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from .models import Wishlist, WishlistItem
from products.models import Product

# Create your views here.

def _wishlist_id(request):
    wishlist = request.session.session_key
    if not wishlist:
        wishlist = request.session.create()
    return wishlist

# ===========================================================================================================================================================================

@login_required(login_url='login')
def add_to_wishlist(request,product_id):
  product = Product.objects.get(id=product_id)

  try:
    wishlist = Wishlist.objects.get(wishlist_id=_wishlist_id(request))
  except Wishlist.DoesNotExist:
    wishlist =  Wishlist.objects.create(
      wishlist_id=_wishlist_id(request)
    )
    wishlist.save()

  try:
      wishlist_item = WishlistItem.objects.get(product=product,wishlist=wishlist)
  except WishlistItem.DoesNotExist:
      wishlist_item = WishlistItem.objects.create(
            product  = product,
            wishlist = wishlist,
        )
      wishlist_item.save()
  if request.user.is_authenticated:
    wishlist_item.user = request.user
    wishlist_item.save()

  return redirect('wishlist')

# ===========================================================================================================================================================================

@login_required(login_url='login')
def wishlist(request, wishlist_items = None):

    try:
        wishlist_items = WishlistItem.objects.filter( user = request.user, is_active = True)
    except WishlistItem.DoesNotExist:
       pass
    


    context = {
        'wishlist_items' : wishlist_items,        
    }
    return render(request, 'wishlist.html', context)

# ===========================================================================================================================================================================

@login_required(login_url='login')
def remove_wishlist(request, product_id):
   product = Product.objects.get(id = product_id)
   if request.method == 'POST':
      try:
        wishlist = WishlistItem.objects.get(user = request.user , product = product)
        wishlist.delete()
      except:
          pass
   return redirect('wishlist')


# ===========================================================================================================================================================================