from django import forms
from .models import Contact

class MyContact(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['full_name','email','subject','message']

