from django.contrib import admin
from .models import Account, Address , Banner
# from django.utils.html import format_html

# Register your models here.
class AddressAdmin(admin.ModelAdmin):
    # def thumbnail(self, object):
        # return format_html('<img src="{}" width="30" style="border-radius: 50%;">'.format(object.profile_picture.url))
    # thumbnail.short_description = 'Profile Picture'
    list_display = ('user', 'city', 'state' , 'pin_code')            #before user -> 'thumbnail'

class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'image', 'description')




admin.site.register(Account)
admin.site.register(Address, AddressAdmin )



admin.site.register(Banner)