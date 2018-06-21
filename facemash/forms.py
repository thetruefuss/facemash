from django import forms

from .models import FaceMash


class FaceMashForm(forms.ModelForm):
    class Meta:
        model = FaceMash
        fields = ['photo']
