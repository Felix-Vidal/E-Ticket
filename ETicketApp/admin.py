from django.contrib import admin
from .models import Classificacao, DadoPessoal, Credito, TicketUnico, Cardapio, Refeicao

# Register your models here.
@admin.register(Classificacao)
class ClassificacaoAdmin(admin.ModelAdmin):
    ...

@admin.register(DadoPessoal)
class DadoPessoalAdmin(admin.ModelAdmin):
    list_display = ['nome_completo', 'cpf']
    
@admin.register(Credito)
class CreditoAdmin(admin.ModelAdmin):
    ...
    
@admin.register(TicketUnico)
class TicketUnicoAdmin(admin.ModelAdmin):
    ...

@admin.register(Cardapio)
class CardapioAdmin(admin.ModelAdmin):
    ...
    
@admin.register(Refeicao)
class RefeicaoAdmin(admin.ModelAdmin):
    ...