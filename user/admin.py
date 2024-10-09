from django.contrib import admin
from .models import Classification, PersonalData, Credit, UniqueTicket, DailyMenu, Meal

# Register your models here.
@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    ...

@admin.register(PersonalData)
class PersonalDataAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'cpf']
    
@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
    ...
    
@admin.register(UniqueTicket)
class UniqueTicketAdmin(admin.ModelAdmin):
    ...

@admin.register(DailyMenu)
class DailyMenuAdmin(admin.ModelAdmin):
    ...
    
@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    ...