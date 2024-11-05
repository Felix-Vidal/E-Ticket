import random
import string
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from .enums import TipoRefeicaoEnum, MetodoPagamentoEnum

class Classificacao(models.Model):
    nome = models.CharField(max_length=255)
    valor_cafe_manha = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_almoco = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_jantar = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    limite_credito = models.DecimalField(max_digits=10, decimal_places=2, default=60.00)
    prioridade = models.IntegerField(default=5)

    def __str__(self):
        return self.nome
    
class DadoPessoal(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nome_completo = models.CharField(max_length=255)
    nome_social = models.CharField(max_length=255, blank=True, null=True)
    matricula = models.BigIntegerField(unique=True)
    classificacoes = models.ManyToManyField(Classificacao, blank=True)
    cpf = models.CharField(max_length=14, unique=True)
    data_entrada = models.DateField()
    unidade = models.CharField(max_length=255)
    credito = models.DecimalField(max_digits=10, decimal_places=2)
    gratuito = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)
    foto = models.TextField(blank=True, null=True) 

    def __str__(self):
        return self.nome_completo
    
class Credito(models.Model):
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2)  
    metodo_pagamento = models.CharField(max_length=15, choices=MetodoPagamentoEnum.choices(), blank=True, null=True)
    transacao = models.BooleanField(default=True)
    data = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.usuario} - {self.valor} ({self.metodo_pagamento})"

class TicketUnico(models.Model):
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pagamento = models.CharField(max_length=15, choices=MetodoPagamentoEnum.choices())  
    data_compra = models.DateField(auto_now_add=True)
    hora_compra = models.TimeField(auto_now_add=True)
    tipo_refeicao = models.CharField(max_length=15, choices=TipoRefeicaoEnum.choices())
    classificacao = models.ForeignKey(Classificacao, on_delete=models.CASCADE)
    valido = models.BooleanField(default=True)
    codigo = models.CharField(max_length=8, unique=True, blank=True)

    def save(self, *args, **kwargs):
            if not self.codigo:
                self.codigo = self.gerar_codigo_unico()
            super().save(*args, **kwargs)

    def gerar_codigo_unico(self):
        # Gera um sufixo baseado na data e hora atual
        datetime_suffix = 'Ticket:' + datetime.now().strftime('%y%m%d%H%M%S')

        # Tenta usar o sufixo de data e hora como código inicial
        codigo = datetime_suffix
        
        # Verifica se o código já existe
        if not TicketUnico.objects.filter(codigo=codigo).exists():
            return codigo  # Retorna se único
        
        # Se existir, gera um código curto de 8 caracteres
        caracteres = string.ascii_uppercase + string.digits
        base_codigo = ''.join(random.choices(caracteres, k=8))
        codigo_final = f"{codigo}{base_codigo}"

        while TicketUnico.objects.filter(codigo=codigo_final).exists():
            base_codigo = ''.join(random.choices(caracteres, k=8))
            codigo_final = f"{codigo}{base_codigo}"

        return codigo_final

    def __str__(self):
        return f"Ticket: {self.valor} - {self.metodo_pagamento} - {self.tipo_refeicao} - Válido: {self.valido} - Código: {self.codigo}"
        
class Cardapio(models.Model):
    
    tipo_refeicao = models.CharField(max_length=15, choices=TipoRefeicaoEnum.choices())
    menu = models.TextField()
    data = models.DateField()  
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['tipo_refeicao', 'data'], name='refeicao_unica_por_dia')
        ]

    def __str__(self):
        return f"Menu de {self.tipo_refeicao} no dia {self.data}"
    
class Refeicao(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # ForeignKey para o usuário, pode ser nulo se o ticket for usado
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    gratuito = models.BooleanField(default=False)
    data = models.DateField()
    hora = models.TimeField()
    menu = models.ForeignKey(Cardapio, on_delete=models.SET_NULL, null=True, blank=True)
    tipo_refeicao = models.CharField(max_length=15, choices=TipoRefeicaoEnum.choices(), null=True, blank=True)
    ticket_unico = models.ForeignKey(TicketUnico, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Refeição no dia {self.data} às {self.hora} - Tipo: {self.tipo_refeicao} - Valor: {self.valor}"
    
class Informacao(models.Model):
    titulo = models.CharField(max_length=255)   
    conteudo = models.TextField()               
    data_publicacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo