from django.db import models
from datetime import datetime

class Cardapio(models.Model):
    id_cardapio = models.AutoField(primary_key=True)
    dia = models.DateField(auto_now_add=True)
    cafe = models.TextField(max_length=255)
    cafe_inicio = models.TextField(max_length=255)
    cafe_fim = models.TextField(max_length=255)
    almoco = models.TextField(max_length=255)
    almoco_inicio = models.TextField(max_length=255)
    almoco_fim = models.TextField(max_length=255)
    jantar = models.TextField(max_length=255)
    jantar_inicio = models.TextField(max_length=255)
    jantar_fim = models.TextField(max_length=255)

