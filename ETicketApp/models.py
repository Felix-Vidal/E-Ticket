import uuid
from django.db import models
from django.contrib.auth.models import User
from .enums import TipoRefeicaoEnum, MetodoPagamentoEnum

class Classificacao(models.Model):
    nome = models.CharField(max_length=255)
    valor_cafe_manha = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_almoco = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_jantar = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
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
    ativo = models.BooleanField(default=True)  # Define um valor padrão para 'ativo'

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
    codigo = models.CharField(max_length=36, unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.codigo:  # Gera o código apenas uma vez, no momento da criação
            self.codigo = str(uuid.uuid4())
        super(TicketUnico, self).save(*args, **kwargs)

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
    ticket_unico = models.ForeignKey(TicketUnico, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Refeição no dia {self.data} às {self.hora} - Valor: {self.valor}"
    
class Informacao(models.Model):
    titulo = models.CharField(max_length=255)   # Campo 'titulo' como String
    conteudo = models.TextField()               # Campo 'conteudo' como String (text)
    data_publicacao = models.DateTimeField(auto_now_add=True)  # Data e hora de publicação

    def __str__(self):
        return self.titulo