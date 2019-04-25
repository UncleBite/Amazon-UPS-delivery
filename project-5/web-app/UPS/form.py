from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UpsSearch(forms.Form):
    TrackingNumber = forms.IntegerField(label = 'Input tracking number')

class UpsUpdate(forms.Form):
    location_x = forms.CharField(label = 'Location_x')
    location_y = forms.CharField(label = 'Location_y')
    