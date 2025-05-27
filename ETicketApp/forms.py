from django import forms
from .models import *
from django.contrib.auth.models import Group

class LoginForm(forms.Form):
    cpf = forms.CharField(
        label="CPF",
        max_length=14,
        widget=forms.TextInput(attrs={
            'placeholder': '000.000.000-00',
            'oninput': "this.value = this.value.replace(/\\D/g, '').replace(/(\\d{3})(\\d)/, '$1.$2').replace(/(\\d{3})(\\d)/, '$1.$2').replace(/(\\d{3})(\\d{1,2})$/, '$1-$2')"
        })
    )
    password = forms.CharField(label="Senha", widget=forms.PasswordInput())

class ClassificacaoForm(forms.ModelForm):
    class Meta:
        model = Classificacao
        fields = ['nome', 'valor_cafe_manha', 'valor_almoco', 'valor_jantar', 'limite_credito', 'prioridade']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da Classificação'}),
            'valor_cafe_manha': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor Café da Manhã'}),
            'valor_almoco': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor Almoço'}),
            'valor_jantar': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor Jantar'}),
            'limite_credito': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'limite_credito'}),
            'prioridade': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Prioridade'}),
        }        

class CardapioForm(forms.ModelForm):
    class Meta:
        model = Cardapio
        fields = ['tipo_refeicao', 'menu', 'data']
        widgets = {
            'tipo_refeicao': forms.Select(attrs={'class': 'form-control'}),
            'menu': forms.Textarea(attrs={'class': 'form-control'}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }      

class InformacaoForm(forms.ModelForm):
    class Meta:
        model = Informacao
        fields = ['titulo', 'conteudo']

class GroupForm(forms.ModelForm):

    class Meta:
        model = Group
        fields = '__all__'

    # bolsista so valida ticket e criar cardapio, adicionar informes
    # colaborador tem todas do bolsista + vender ticket, relatorio, gerenciar usuarios 
    # adm faz tudo