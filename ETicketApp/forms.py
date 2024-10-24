from django import forms
from .models import Classificacao

class ClassificacaoForm(forms.ModelForm):
    class Meta:
        model = Classificacao
        fields = ['nome', 'valor_cafe_manha', 'valor_almoco', 'valor_jantar', 'prioridade']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da Classificação'}),
            'valor_cafe_manha': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor Café da Manhã'}),
            'valor_almoco': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor Almoço'}),
            'valor_jantar': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor Jantar'}),
            'prioridade': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Prioridade'}),
        }