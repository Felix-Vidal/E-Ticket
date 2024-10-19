from django.db import models
from datetime import datetime

class Cardapio(models.Model):
    id_cardapio = models.AutoField(primary_key=True)
    cafe = models.TextField()
    almoco = models.TextField()
    jantar = models.TextField()
    data = models.DateField(auto_now_add=True)  
    
    def __str__(self):
        return f"Cardápio de {self.data}"

