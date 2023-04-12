from django import forms
from .models import Order, Coupon


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('first_name', 'last_name', 'phone', 'email', 'address_line_1', 'address_line_2', 'country', 'state', 'city', 'order_note')

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ('code', 'discount', 'min_value', 'valid_at')

        
    def __init__(self, *args, **kwargs):
        super(CouponForm, self).__init__(*args, **kwargs)
        
        self.fields['code'].widget.attrs [ 'placeholder' ] = 'Coupon code'
        self.fields['discount'].widget.attrs [ 'placeholder' ] = 'Coupon Discount percentage'
        self.fields['min_value'].widget.attrs [ 'placeholder' ] = 'Min Value'
        self.fields['valid_at'].widget.attrs [ 'placeholder' ] = 'Valid Till'



        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'block w-full mt-1 text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input'

    