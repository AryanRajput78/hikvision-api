from django import forms
from .models import userDetails

class image(forms.ModelForm):
    class Meta:
        model = userDetails
        fields = "__all__"