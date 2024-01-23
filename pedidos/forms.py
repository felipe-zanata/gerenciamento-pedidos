from django import forms
from pedidos.models import DadosPedidos

class NovoPedidoForm(forms.ModelForm):
    class Meta:
        model = DadosPedidos
        fields = '__all__'