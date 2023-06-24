from django import forms
from django.forms import ModelForm, TextInput, Textarea, DateInput
from .models import Prices
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class PricesForm(forms.ModelForm):
    class Meta:
        model = Prices
        fields = ['datep', 'store', 'product', 'cost', 'details']
        widgets = {
            'datep': DateInput(attrs={"type":"date"}),
            'store': TextInput(attrs={"size":"50"}),
            'product': TextInput(attrs={"size":"50"}),
            'cost': TextInput(attrs={"type":"number"}),
            'details': Textarea(attrs={'cols': 50, 'rows': 5}),
        }

# Форма регистрации
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Repeat password'), widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')
        widgets = {
            'username': TextInput(attrs={"size":"50"}),
            'first_name': TextInput(attrs={"size":"50"}),
            'email': TextInput(attrs={"size":"50", "type":"email"}),            
        }        
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError(_('Passwords don\'t match.'))
        return cd['password2']
