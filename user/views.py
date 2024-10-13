from django.shortcuts import render
from django.http import HttpResponse

from django.contrib.auth import login as auth_login
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import PersonalData, Classification
from django.contrib.auth.decorators import login_required
import requests
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password, make_password
from io import BytesIO
import base64
import qrcode

from .models import DailyMenu
import datetime

# Create your views here.
@login_required
def home(request):
    # Obtém os dados pessoais do usuário logado
    personal_data = PersonalData.objects.get(user=request.user)

    # Gera o QR Code a partir do número de matrícula
    qr_data = personal_data.registration_number
    qr_img = qrcode.make(qr_data)

    # Salva a imagem em um buffer
    buffer = BytesIO()
    qr_img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Passa os dados para o template
    context = {
        'credit': personal_data.credit,
        'registration_number': personal_data.registration_number,
        'qr_image': qr_image,
    }
    return render(request, 'user/pages/home.html', context)

@login_required
def pagamento(request):
    return render(request,'user/pages/payment.html')

@login_required
def menu(request):
    today = datetime.date.today()  # Obtém a data de hoje
    
    # Filtra um item para cada tipo de refeição no menu do dia
    breakfast_menu = DailyMenu.objects.filter(date=today, meal_type="BREAKFAST").first()
    lunch_menu = DailyMenu.objects.filter(date=today, meal_type="LUNCH").first()
    dinner_menu = DailyMenu.objects.filter(date=today, meal_type="DINNER").first()
    
    # Adiciona os menus ao contexto
    context = {
        'breakfast_menu': breakfast_menu,
        'lunch_menu': lunch_menu,
        'dinner_menu': dinner_menu,
    }
    
    return render(request, 'user/pages/menu.html', context)
@login_required
def profile(request):
    # Obtém o objeto PersonalData relacionado ao usuário logado
    personal_data = PersonalData.objects.get(user=request.user)

    # Passa os dados do usuário e suas classificações para o template
    context = {
        'user_full_name': personal_data.full_name,
        'user_cpf': personal_data.cpf,
        'user_matricula': personal_data.registration_number,
        'user_unit': personal_data.unit,
        'user_classifications': personal_data.classifications.all(),
    }
    
    return render(request, 'user/pages/profile.html', context)

# Defina a URL da API externa
UFAC_API_URL = "https://sistemas.ufac.br/api/csi/usuarios-ru/"
BEARER_TOKEN = ""
def login(request):
    if request.method == 'POST':
        cpf = request.POST.get('cpf')
        password = request.POST.get('password')

        if not cpf or not password:
            return render(request, 'user/pages/login.html', {'error_message': 'CPF e senha são obrigatórios.'})

        try:
            # Tenta buscar o usuário localmente usando o CPF
            personal_data = PersonalData.objects.get(cpf=cpf)
            user = personal_data.user

            # Verifica se a senha está correta
            if check_password(password, user.password):
                auth_login(request, user) 
                return redirect('home')  # Redireciona para a página inicial

            else:
                return render(request, 'user/pages/login.html', {'error_message': 'Senha incorreta.'})

        except PersonalData.DoesNotExist:
            # Se o CPF não existe localmente, fazer a requisição à API externa
            headers = {
                'Authorization': f'Bearer {BEARER_TOKEN}',
            }
            response = requests.post(UFAC_API_URL, json={"cpf": cpf}, headers=headers)
            
        
         
            if response.status_code == 200:
                external_data = response.json()

                if external_data['record_count'] == 0:
                    return render(request, 'user/pages/login.html', {'error_message': 'Usuário não encontrado na API externa.'})

                # Acessa o primeiro registro da lista "response"
                user_data = external_data['response'][0]

                # Extrai os dados do usuário
                matricula = user_data.get('MATRICULA')
                full_name = user_data.get('NOME')
                social_name = user_data.get('NOME_SOCIAL')
                cpf = user_data.get('CPF')
                unit = user_data.get('UNIDADE')
                entry_date = user_data.get('DT_ENTRADA')
                classification_name = user_data.get('CLASSIFICACAO')
                gratuitous = user_data.get('GRATUIDADE') == 'S'  # Converte 'S' ou 'N' para booleano

                # Busca ou cria uma classificação com base no nome retornado
                classification, created = Classification.objects.get_or_create(name=classification_name)

                # Cria um novo usuário localmente
                user = User.objects.create(
                    username=cpf,
                    password=make_password(password),  # Criptografa a senha
                )
                personal_data = PersonalData.objects.create(
                    user=user,
                    full_name=full_name,
                    social_name=social_name,
                    cpf=cpf,
                    registration_number=matricula,
                    entry_date=entry_date,
                    unit=unit,
                    credit=0.0,  # Inicialmente, crédito zero
                    gratuitous=gratuitous,
                )
                personal_data.classifications.add(classification)
                auth_login(request, user)
                return redirect('home')  # Redireciona para a página inicial após sucesso

            else:
                return render(request, 'user/pages/login.html', {'error_message': 'Erro na API externa.'})

    return render(request, 'user/pages/login.html')



@login_required
def history(request):
    return render(request, 'user/pages/history.html')






