from django.db import models
from django.contrib.auth.models import User

# Create your models here.
MEAL_TYPES = [
    ('BREAKFAST', 'Breakfast'),
    ('LUNCH', 'Lunch'),
    ('DINNER', 'Dinner'),
]

PAYMENT_METHODS = [
    ('PIX', 'Pix'),
    ('DEBIT', 'Cartão de Débito'),
    ('CASH', 'Dinheiro'),
]

class Classification(models.Model):
    name = models.CharField(max_length=255)
    breakfast_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    lunch_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    dinner_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    priority = models.IntegerField(default=0)  # Adiciona prioridade (menor valor significa maior prioridade)

    def __str__(self):
        return self.name
    
class PersonalData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    social_name = models.CharField(max_length=255, blank=True, null=True)
    registration_number = models.BigIntegerField(unique=True)
    classifications = models.ManyToManyField(Classification, blank=True)
    cpf = models.CharField(max_length=14, unique=True)
    entry_date = models.DateField()
    unit = models.CharField(max_length=255)
    credit = models.DecimalField(max_digits=10, decimal_places=2)
    gratuitous = models.BooleanField(default=False)
    active = models.BooleanField(default=True)  # Define um valor padrão para 'active'

    def __str__(self):
        return self.full_name
    
class Credit(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=2)  
    payment_method = models.CharField(max_length=6, choices=PAYMENT_METHODS, blank=True, null=True)
    transaction = models.BooleanField(default=True)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user} - {self.value} ({self.payment_method})"

class UniqueTicket(models.Model):
    
    value = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=6, choices=PAYMENT_METHODS)  
    purchase_date = models.DateField(auto_now_add=True)
    purchase_time = models.TimeField(auto_now_add=True)
    meal_type = models.CharField(max_length=10, choices=MEAL_TYPES)
    classification = models.ForeignKey(Classification, on_delete=models.CASCADE)
    valid = models.BooleanField(default=True)

    def __str__(self):
        return f"Ticket: {self.value} - {self.payment_method} - {self.meal_type} - Valid: {self.valid}"
    
class DailyMenu(models.Model):
    
    meal_type = models.CharField(max_length=10, choices=MEAL_TYPES)
    menu = models.TextField()
    date = models.DateField()  
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['meal_type', 'date'], name='unique_meal_per_day')
        ]

    def __str__(self):
        return f"{self.meal_type} Menu on {self.date}"
    
class Meal(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # ForeignKey to User, can be null if ticket is used
    value = models.DecimalField(max_digits=10, decimal_places=2)
    gratuitous = models.BooleanField(default=False)
    date = models.DateField()
    time = models.TimeField()
    menu = models.ForeignKey(DailyMenu, on_delete=models.SET_NULL, null=True, blank=True)
    unique_ticket = models.ForeignKey(UniqueTicket, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Meal on {self.date} at {self.time} - Value: {self.value}"