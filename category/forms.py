from django import forms
from .models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('category_name', 'slug', 'description')

    
    
    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)

        self.fields['category_name'].widget.attrs [ 'placeholder' ] = 'Category Name'
        self.fields['slug'].widget.attrs [ 'placeholder' ] = 'Slug'
        self.fields['description'].widget.attrs [ 'placeholder' ] = 'Category Description'

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'block w-full mt-1 text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-purple-400 focus:outline-none focus:shadow-outline-purple dark:text-gray-300 dark:focus:shadow-outline-gray form-input'

    