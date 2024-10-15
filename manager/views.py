from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from user.models import PersonalData, MEAL_TYPES
from datetime import datetime
# Create your views here.

def home(request):
    return render(request, 'manager/pages/home.html')

def dashboard (request):
    return render(request, 'manager/pages/dashboard.html')

def validar (request):
    return render(request, 'manager/pages/validar.html')

def validarQR(request, codigo):  # Recebe o código como parâmetro
    if codigo:
        # Obtém os dados do usuário usando a matrícula
        personal_data = PersonalData.objects.get(registration_number=codigo)
        classifications = " / ".join(personal_data.classifications.values_list('name', flat=True))  # Junta as classificações
        
        current_hour = datetime.now().hour
        if 6 <= current_hour < 11:
            meal_type = 'BREAKFAST'
        elif 11 <= current_hour < 17:
            meal_type = 'LUNCH'
        else:
            meal_type = 'DINNER'
        meal_name = dict(MEAL_TYPES).get(meal_type)
        context = {
            'user_full_name': personal_data.full_name,
            'user_cpf': personal_data.cpf,
            'user_matricula': personal_data.registration_number,
            'user_balance': personal_data.credit,  # Certifique-se de ter um campo de saldo
            'user_unit': personal_data.unit,        # Adicione um campo de unidade
            'user_classifications': classifications,
            'meal_type': meal_name,
        }
        return render(request, 'manager/pages/validarQR.html', context)
    return render(request, 'manager/pages/validarQR.html')

def validar_usuario(request):
    if request.method == 'POST':
        matricula = request.POST.get('user_matricula')
        meal_type = request.POST.get('meal_type')

        try:
            # Busca o usuário pela matrícula
            personal_data = PersonalData.objects.get(registration_number=matricula)

            # Se o usuário for gratuito, não deduz crédito
            if personal_data.gratuitous:
                messages.success(request, 'Usuário gratuito, refeição validada sem desconto de crédito.')
                return redirect('validar')  # Redireciona para /manage/validar/

            # Busca a classificação com a maior prioridade (menor valor de 'priority')
            classification = personal_data.classifications.order_by('priority').first()

            if not classification:
                messages.error(request, 'Nenhuma classificação encontrada para o usuário.')
                return redirect('validar')

            # Calcula o valor da refeição com base no tipo de refeição
            if meal_type == 'Breakfast':
                total_discount = classification.breakfast_value
            elif meal_type == 'Lunch':
                total_discount = classification.lunch_value
            elif meal_type == 'Dinner':
                total_discount = classification.dinner_value
            else:
                messages.error(request, 'Tipo de refeição inválido.')
                return redirect('validar')

            # Verifica se o usuário tem crédito suficiente
            if personal_data.credit >= total_discount:
                # Deduz o valor da refeição do crédito do usuário
                personal_data.credit -= total_discount
                personal_data.save()

                messages.success(request, 'Refeição validada com sucesso!')
            else:
                messages.error(request, 'Crédito insuficiente para validar a refeição.')

        except PersonalData.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')

    return redirect('validar')

def ticketUnico (request):
    return render(request, 'manager/pages/ticketUnico.html')

def relatorio (request):
    return render(request, 'manager/pages/relatorio.html')

def cardapio (request):
    return render(request, 'manager/pages/cardapio.html')

def vender (request):
    return render(request, 'manager/pages/vender.html')

def vendaUnico (request):
    return render(request, 'manager/pages/vendaUnico.html')

def usuarioCompra (request):
    return render(request, 'manager/pages/UsuarioCompra.html')
