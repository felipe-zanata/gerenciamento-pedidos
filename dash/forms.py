from django import forms
from .models import UrlDashBoard

class IndicatorForm(forms.ModelForm):
    class Meta:
        model = UrlDashBoard
        fields = '__all__'