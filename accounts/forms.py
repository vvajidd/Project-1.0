from django import forms
from .models import Account, Address


class RegisterationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder'  :  'Create new password',
        'class' : 'input100',
    }))  #css or placeholder in {}

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder'  :  'Confirm password',
        'class' : 'input100',
    }))

    # first_name = forms.CharField(widget=forms.TextInput(attrs={
    #     'placeholder'  :  'First Name',
    #     'class' : 'input100',
    # })) 

    # last_name = forms.CharField(widget=forms.TextInput(attrs={
    #     'placeholder'  :  'Last Name',
    #     'class' : 'input100',
    # })) 

    # phone_number = forms.CharField(widget=forms.TextInput(attrs={
    #     'placeholder'  :  'Phone Number',
    #     'class' : 'input100',
    # }))

    # email = forms.CharField(widget=forms.EmailInput(attrs={
    #     'placeholder'  :  'Email Address',
    #     'class' : 'input100',
    # }))

    class Meta:
        model = Account
        fields = ['first_name','last_name', 'phone_number', 'email', 'password']





    def clean(self):
        cleaned_data = super(RegisterationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "Password doesn\'t match"
            )
            
#for apply css to every fields as a loop


    def __init__ (self, *args, **kwargs):
        super(RegisterationForm, self).__init__(*args, **kwargs)

        self.fields['first_name'].widget.attrs [ 'placeholder' ] = 'First Name'
        self.fields['last_name'].widget.attrs [ 'placeholder' ] = 'Last Name'
        self.fields['phone_number'].widget.attrs [ 'placeholder' ] = 'Phone Number'
        self.fields['email'].widget.attrs [ 'placeholder' ] = 'Email'
        
        for field in self.fields:
            self.fields[field].widget.attrs [ 'class' ] = 'input100'

    
class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name','email', 'username', 'phone_number')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'



class UserAddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('address_line_1', 'address_line_2', 'city', 'state', 'country', 'pin_code')
    def __init__(self, *args, **kwargs):
        super(UserAddressForm, self).__init__(*args, **kwargs)
        
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'