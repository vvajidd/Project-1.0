from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('product_name', 'slug', 'description', 'price', 'product_image', 'stock', 'category')
    
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        
        self.fields['product_name'].widget.attrs [ 'placeholder' ] = 'Product Name'
        self.fields['slug'].widget.attrs [ 'placeholder' ] = 'Product Slug'
        self.fields['description'].widget.attrs [ 'placeholder' ] = 'Product Description'
        self.fields['stock'].widget.attrs [ 'placeholder' ] = 'Stock'
        self.fields['price'].widget.attrs [ 'placeholder' ] = 'Price'
        self.fields['category'].widget.attrs [ 'placeholder' ] = 'Category'


        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'block w-full mt-1 text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input'

    