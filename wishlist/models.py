from django.db import models
from accounts.models import Account
from products.models import Product
# Create your models here.


class Wishlist(models.Model):
    wishlist_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.wishlist_id
    
class WishlistItem(models.Model):
  user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  wishlist = models.ForeignKey(Wishlist,on_delete=models.CASCADE,null=True)
  is_active = models.BooleanField(default=True)
  cart_status = models.BooleanField(default=False)
  
  def __unicode__(self):
    return self.product