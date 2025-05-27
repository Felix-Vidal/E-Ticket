from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.contrib import messages

from django.db.models import Q

from django.contrib.auth.decorators import user_passes_test, login_required 
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User, Group

from django import template
from .forms import *
from .models import *

import base64
import qrcode
from django.core.files.base import ContentFile



import requests
from django.contrib.auth.hashers import check_password, make_password
from datetime import datetime, date
from io import BytesIO

from decimal import Decimal
import random


# Create your views here.
# ----------- usuario final ------------
@login_required
def home(request):
    # Obtém os dados pessoais do usuário logado
    personal_data = get_object_or_404(DadoPessoal, usuario=request.user)

    # Gera o QR Code a partir do número de matrícula
    qr_data = personal_data.matricula
    qr_img = qrcode.make(qr_data)

    # Salva a imagem em um buffer
    buffer = BytesIO()
    qr_img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Passa os dados para o template
    context = {
        'credito': personal_data.credito,
        'matricula': personal_data.matricula,
        'qr_image': qr_image,
    }
    return render(request, 'ETicketApp/pages/user/home.html', context)

@login_required
def aumentar_credito(request):
    if request.method == 'POST':
        valor = request.POST.get('valor')
        
        # metodo_pagamento = request.POST.get('metodo_pagamento')  # Adicione o método de pagamento no formulário
        
        # Gera um método de pagamento aleatório
        metodo_pagamento = random.choice([MetodoPagamentoEnum.PIX.value, MetodoPagamentoEnum.DINHEIRO.value, MetodoPagamentoEnum.CARTAO.value]) 
        
        if valor and metodo_pagamento:
            try:
                valor_decimal = Decimal(valor)
                
                # Verifica se o valor é positivo
                if valor_decimal <= 0:
                    messages.error(request, 'O valor deve ser positivo.')
                    return redirect('home')
                
                personal_data = get_object_or_404(DadoPessoal, usuario=request.user)
                
                # Busca a classificação com o maior peso (prioridade) do usuário
                classificacao_prioritaria = personal_data.classificacoes.order_by('prioridade').first()
                
                if classificacao_prioritaria:
                    limite_credito = classificacao_prioritaria.limite_credito
                    
                    # Verifica se a adição do valor ultrapassa o limite de crédito
                    if personal_data.credito + valor_decimal > limite_credito:
                        messages.error(request, f"O limite de crédito de R${limite_credito} será excedido.")
                        return redirect('home')
                
                # Adiciona o valor ao crédito do usuário
                personal_data.credito += valor_decimal
                personal_data.save()

                # Cria o registro de crédito
                Credito.objects.create(
                    usuario=request.user,
                    valor=valor_decimal,
                    metodo_pagamento=metodo_pagamento
                )
                
                messages.success(request, 'Crédito aumentado com sucesso!')
                return redirect('home')
            except (DadoPessoal.DoesNotExist, Decimal.InvalidOperation):
                messages.error(request, 'Falha ao aumentar crédito. Verifique o valor e tente novamente.')
                return redirect('home')
    return redirect('home')

@login_required
def pagamento(request):
    if request.method == "POST":
        valor = request.POST.get('valor')
        print(valor)
        context = {
            'valor': valor
        }
        return render(request,'ETicketApp/pages/user/pagamento.html', context)

@login_required
def menu(request):
    hoje = date.today()
    
    # Filtra o cardápio para cada tipo de refeição do dia
    cafe = Cardapio.objects.filter(data=hoje, tipo_refeicao="CAFE_DA_MANHA").first()
    almoco = Cardapio.objects.filter(data=hoje, tipo_refeicao="ALMOCO").first()
    jantar = Cardapio.objects.filter(data=hoje, tipo_refeicao="JANTAR").first()
    
    # Obtem o dado pessoal do usuário e a classificação com a maior prioridade
    dados_pessoais = DadoPessoal.objects.get(usuario=request.user)
    classificacao = dados_pessoais.classificacoes.order_by('prioridade').first()  # Assumindo prioridade ascendente

    # Prepara os valores com base na classificação
    valor_cafe = classificacao.valor_cafe_manha if classificacao else None
    valor_almoco = classificacao.valor_almoco if classificacao else None
    valor_jantar = classificacao.valor_jantar if classificacao else None

    # Adiciona os menus e os valores ao contexto
    context = {
        'cafe': cafe,
        'almoco': almoco,
        'jantar': jantar,
        'valor_cafe': valor_cafe,
        'valor_almoco': valor_almoco,
        'valor_jantar': valor_jantar,
    }
    
    return render(request, 'ETicketApp/pages/user/menu.html', context)

@login_required
def perfil(request):
    # Obtém o objeto DadoPessoal relacionado ao usuário logado
    personal_data = get_object_or_404(DadoPessoal, usuario=request.user)

    # Passa os dados do usuário e suas classificações para o template
    context = {
        'nome_completo': personal_data.nome_completo,
        'cpf': personal_data.cpf,
        'matricula': personal_data.matricula,
        'unidade': personal_data.unidade,
        'classificacoes': personal_data.classificacoes.all(),
        'foto': personal_data.foto,
    }
    
    return render(request, 'ETicketApp/pages/user/perfil.html', context)


def salvar_foto(foto_base64, usuario):
    # Decodifica a imagem
    format, imgstr = foto_base64.split(';base64,') 
    ext = format.split('/')[-1]  # Extrai a extensão do formato
    img_data = base64.b64decode(imgstr)  # Decodifica a imagem

    # Cria um arquivo temporário para a imagem
    file_name = f"{usuario.matricula}_foto.{ext}"  # Nome do arquivo
    file = ContentFile(img_data, name=file_name)

    # Salva a imagem no modelo
    usuario.foto.save(file_name, file)
    usuario.save()

# Defina a URL da API externa
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if not form.is_valid():
            return render(request, 'ETicketApp/pages/user/login.html', {'form': form})

        cpf = form.cleaned_data['cpf'].replace(".", "").replace("-", "")
        password = form.cleaned_data['password']

        # Validação de campos obrigatórios
        if not cpf:
            messages.error(request, 'CPF é obrigatório.')
            return render(request, 'ETicketApp/pages/user/login.html', {'form': form})
        # if not password:
        #     messages.error(request, 'Senha é obrigatória.')
        #     return render(request, 'ETicketApp/pages/user/login.html', {'form': form})

        # Consulta API externa
        headers = {'Authorization': f'Bearer {settings.BEARER_TOKEN}'}
        try:
            response = requests.post(settings.UFAC_API_URL, json={"cpf": cpf}, headers=headers)
            response.raise_for_status() 
        except requests.exceptions.RequestException as e:
            messages.error(request, f'Erro ao conectar')
            return render(request, 'ETicketApp/pages/user/login.html', {
                'form': form, 'error_message': 'Erro na API externa.'
            })
        
        api_data = response.json()
        active_users_data = [data for data in api_data.get('response', []) if data.get('SITUACAO') == 'Ativo']

        if not active_users_data:
            messages.error(request, 'Nenhum usuário ativo encontrado.')
            return render(request, 'ETicketApp/pages/user/login.html', {
                'form': form, 'error_message': 'Nenhum usuário ativo encontrado na API.'
            })

        user_data = None
        classifications = []
        max_priority = -1

        for data in active_users_data:
            classification_name = data.get('CLASSIFICACAO')
            if classification_name:
                classificacao, _ = Classificacao.objects.get_or_create(nome=classification_name)
                if classificacao.prioridade > max_priority:
                    user_data = data
                    max_priority = classificacao.prioridade
                    classifications = [classificacao]
                elif classificacao.prioridade == max_priority:
                    classifications.append(classificacao)


        if not user_data:
            messages.error(request, 'Nenhum usuário ativo com classificação válida encontrado.')
            return render(request, 'ETicketApp/pages/user/login.html', {
                'form': form, 'error_message': 'Nenhum usuário ativo com classificação válida encontrado.'
            })

        # Extrai dados do usuário da API
        nome_completo = user_data.get('NOME')
        nome_social = user_data.get('NOME_SOCIAL')
        email = user_data.get('EMAIL')
        foto = user_data.get('FOTO')
        matricula = user_data.get('MATRICULA')
        unidade = user_data.get('UNIDADE')
        data_entrada = user_data.get('DT_ENTRADA')
        gratuito = user_data.get('GRATUIDADE') == 'S'

        personal_data = DadoPessoal.objects.filter(cpf=cpf).first()
        
        if personal_data:
            # if not personal_data.usuario.check_password(password):
            #     messages.error(request, 'CPF ou Senha incorreta.')
            #     return render(request, 'ETicketApp/pages/user/login.html', {
            #         'form': form, 'error_message': 'CPF ou Senha incorreta.'
            #     })
            
            # Atualiza dados do usuário existente
            usuario = personal_data.usuario
            usuario.email = email
            usuario.save()

            personal_data.nome_completo = nome_completo
            personal_data.nome_social = nome_social
            personal_data.matricula = matricula
            personal_data.data_entrada = data_entrada
            personal_data.unidade = unidade
            personal_data.gratuito = gratuito
            personal_data.foto = foto
            personal_data.classificacoes.set(classifications) # Atualiza classificações
            personal_data.save()

        else:
            # Cria novo usuário
            usuario = User.objects.create(
                username=nome_completo,
                # password=make_password(password), # Use a senha fornecida para o novo usuário
                email=email,
            )
            personal_data = DadoPessoal.objects.create(
                usuario=usuario,
                nome_completo=nome_completo,
                nome_social=nome_social,
                cpf=cpf,
                matricula=matricula,
                data_entrada=data_entrada,
                unidade=unidade,
                credito=0.0,
                foto=foto,
                gratuito=gratuito,
            )
            personal_data.classificacoes.set(classifications)

        # Autentica o usuário
        auth_login(request, usuario)
        return redirect('home')

    # GET request
    form = LoginForm()
    return render(request, 'ETicketApp/pages/user/login.html', {'form': form})



@login_required
def historico(request):
    
    # Busca o histórico de créditos do usuário logado
    historico = Credito.objects.filter(usuario=request.user).order_by('-data', '-hora')
    
    context = {
        'historico': historico        # Passa o histórico para o template
    }
    
    return render(request, 'ETicketApp/pages/user/historico.html', context)

@login_required
def historico_refeicoes(request):

    historico_refeicoes = Refeicao.objects.filter(usuario=request.user).select_related('usuario', 'menu', 'ticket_unico').order_by('-data', '-hora')

    context = {
        'historico_refeicoes': historico_refeicoes,
    }
    
    return render(request, 'ETicketApp/pages/user/historico_refeicoes.html', context)

@login_required
def valorPaga(request):
    return render(request, 'ETicketApp/pages/user/valorPaga.html')

@login_required
def informacao(request):
    informacao = Informacao.objects.all().order_by('-data_publicacao')  # Ordena pela data de publicação, mais recente primeiro
    return render(request, 'ETicketApp/pages/user/informacao.html', {'informacao': informacao})

# ----------- usuario externo ------------

def valorPagaExterno (request):
    return render(request, 'ETicketApp/pages/user/valorPagaExterno.html')

def menuExterno (request):
    return render(request, 'ETicketApp/pages/user/menuExterno.html')



# ----------- usuario gerenciador ------------

def is_in_group(user, group_names):

    return user.groups.filter(name__in=group_names).exists()

def is_superuser(user):
    grupos = ['ADM', 'Colaborador', 'Bolsista']
    return user.is_superuser or is_in_group(user, grupos)

register = template.Library()

@register.filter
def in_groups(user, group_names):
    return user.groups.filter(name__in=group_names).exists()

@user_passes_test(is_superuser)
def dashboard (request):
    return render(request, 'ETicketApp/pages/manager/dashboard.html')

@user_passes_test(is_superuser)
def validar (request):
    return render(request, 'ETicketApp/pages/manager/validar.html')

@user_passes_test(is_superuser)
def mostrar_usuario(request):  
    if request.method == 'POST':
        codigo = request.POST.get('matricula')  # Pode ser matrícula (numérica) ou código do ticket (UUID)

        # Verifica se o código é numérico para tentar buscar DadoPessoal
        if codigo.isdigit():
            try:
                dados_pessoais = DadoPessoal.objects.get(matricula=codigo)
                # Obtém as classificações do usuário
                classificacoes = " / ".join(dados_pessoais.classificacoes.values_list('nome', flat=True))
            except DadoPessoal.DoesNotExist:
                dados_pessoais = None
        else:
            dados_pessoais = None
            
        classificacao = dados_pessoais.classificacoes.order_by('prioridade').first()
        # Identifica o tipo de refeição com base no horário atual
        current_hour = datetime.now().hour
        if 6 <= current_hour < 10:
            tipo_refeicao = "CAFE_DA_MANHA"
            valor = classificacao.valor_cafe_manha
        elif 10 <= current_hour < 17:
            tipo_refeicao = "ALMOCO"
            valor = classificacao.valor_almoco
        elif 17 <= current_hour < 19:
            tipo_refeicao = "JANTAR"
            valor = classificacao.valor_jantar
        nome_refeicao = TipoRefeicaoEnum.get_name_by_value(tipo_refeicao)
    

        # Se dados_pessoais não existe, tenta buscar como TicketUnico
        if not dados_pessoais:
            try:
                ticket = TicketUnico.objects.get(codigo=codigo)
                if ticket.valido:
                    # Verifica se o tipo de refeição do ticket corresponde ao horário atual
                    if ticket.tipo_refeicao == tipo_refeicao:
                        ticket.valido = False
                        ticket.save()
                        
                        # Registra a refeição
                        Refeicao.objects.create(
                            valor=ticket.valor,
                            gratuito=False,
                            data=datetime.now().date(),
                            hora=datetime.now().time(),
                            tipo_refeicao=tipo_refeicao,
                            menu=Cardapio.objects.filter(data=datetime.now().date(), tipo_refeicao=tipo_refeicao).first(),
                            ticket_unico=ticket
                        )
                        messages.success(request, 'Ticket validado com sucesso!')
                        return None
                    else:
                        messages.error(request, 'Tipo de refeição inválido para o horário atual.')

                        return redirect('validar')
                else:
                    messages.error(request, 'Ticket já foi utilizado ou está inválido.')

                    return redirect('validar')
            except TicketUnico.DoesNotExist:
                messages.error(request, 'Código inválido. Não corresponde a uma matrícula ou ticket válido.')
                return redirect('validar')

        # Prepara o contexto e renderiza a página
        if dados_pessoais:
            context = {
                'nome_completo': dados_pessoais.nome_completo,
                'cpf': dados_pessoais.cpf,
                'matricula': dados_pessoais.matricula,
                'credito': dados_pessoais.credito,
                'unidade': dados_pessoais.unidade,
                'classificacoes': classificacoes,
                'tipo_refeicao': nome_refeicao,
                'valor': valor,
            }
            return render(request, 'ETicketApp/pages/manager/validarUsuario.html', context)

    return render(request, 'ETicketApp/pages/manager/validarUsuario.html')

@user_passes_test(is_superuser)
def validar_usuario(request):
    if request.method == 'POST':
        matricula = request.POST.get('matricula')
        tipo_refeicao = request.POST.get('tipo_refeicao')
        
        
        
        

        try:
            # Busca o usuário pela matrícula
            dados_pessoais = DadoPessoal.objects.get(matricula=matricula)\
                
            if dados_pessoais and Refeicao.objects.filter(usuario=dados_pessoais.usuario, data=date.today(), tipo_refeicao=tipo_refeicao).exists():
                messages.error(request, f'{tipo_refeicao} já foi registrado para hoje.')
                print(f'Debug: {tipo_refeicao} já registrado para {dados_pessoais.usuario} na data {date.today()}')
                return redirect('validar')
            
            print(f'Debug: {tipo_refeicao} não registrado para {dados_pessoais.usuario} na data {date.today()}')
            refeicao = Refeicao.objects.filter(usuario=dados_pessoais.usuario, data=date.today(), tipo_refeicao=tipo_refeicao).first()
            print(refeicao)

            # Se o usuário for gratuito, não deduz crédito
            if dados_pessoais.gratuito:
                messages.success(request, 'Usuário gratuito, refeição validada sem desconto de crédito.')

                # Registra a refeição gratuita
                Refeicao.objects.create(
                    usuario=dados_pessoais.usuario,
                    valor=0.00,
                    gratuito=True,
                    data=datetime.now().date(),
                    hora=datetime.now().time(),
                    tipo_refeicao=tipo_refeicao,
                    menu=Cardapio.objects.filter(data=datetime.now().date(), tipo_refeicao=tipo_refeicao).first(),
                )

                return redirect('validar')  # Redireciona para /manage/validar/

            # Busca a classificação com a maior prioridade (menor valor de 'prioridade')
            classificacao = dados_pessoais.classificacoes.order_by('prioridade').first()

            if not classificacao:
                messages.error(request, 'Nenhuma classificação encontrada para o usuário.')
                return redirect('validar')

            # Calcula o valor da refeição com base no tipo de refeição
            if tipo_refeicao == 'CAFE_DA_MANHA':
                valor = classificacao.valor_cafe_manha
            elif tipo_refeicao == 'ALMOCO':
                valor = classificacao.valor_almoco
            elif tipo_refeicao == 'JANTAR':
                valor = classificacao.valor_jantar
            else:
                messages.error(request, 'Tipo de refeição inválido.')
                return redirect('validar')

            # Verifica se o usuário tem crédito suficiente
            if dados_pessoais.credito >= valor:
                # Deduz o valor da refeição do crédito do usuário
                dados_pessoais.credito -= valor
                dados_pessoais.save()

                # Registra a refeição
                Refeicao.objects.create(
                    usuario=dados_pessoais.usuario,
                    valor=valor,
                    gratuito=False,
                    data=datetime.now().date(),
                    hora=datetime.now().time(),
                    tipo_refeicao=tipo_refeicao,
                    menu=Cardapio.objects.filter(data=datetime.now().date(), tipo_refeicao=tipo_refeicao).first()
                )

                messages.success(request, 'Refeição validada com sucesso!')
            else:
                messages.error(request, 'Crédito insuficiente para validar a refeição.')

        except DadoPessoal.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')

    return redirect('validar')

@user_passes_test(is_superuser)
def ticketUnico (request):
    return render(request, 'ETicketApp/pages/manager/ticketUnico.html')

@user_passes_test(is_superuser)
def relatorio (request):
    return render(request, 'ETicketApp/pages/manager/relatorio.html')

@user_passes_test(is_superuser)
def cardapio(request):
    # Recupera todos os cardápios ordenados pela data, do mais recente ao mais antigo
    cardapios = Cardapio.objects.all().order_by('-data')
    
    context = {
        'cardapios': cardapios,
    }
    
    return render(request, 'ETicketApp/pages/manager/cardapio.html', context)

@user_passes_test(is_superuser)
def adicionar_cardapio(request):
    if request.method == 'POST':
        form = CardapioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cardapio')
    else:
        form = CardapioForm()
    return render(request, 'ETicketApp/pages/manager/cardapio_form.html', {'form': form})

@user_passes_test(is_superuser)
def editar_cardapio(request, id):
    cardapio = get_object_or_404(Cardapio, id=id)
    if request.method == 'POST':
        form = CardapioForm(request.POST, instance=cardapio)
        if form.is_valid():
            form.save()
            return redirect('cardapio')
    else:
        form = CardapioForm(instance=cardapio)
    return render(request, 'ETicketApp/pages/manager/cardapio_form.html', {'form': form})

@user_passes_test(is_superuser)
def excluir_cardapio(request, id):
    cardapio = get_object_or_404(Cardapio, id=id)
    cardapio.delete()
    return redirect('cardapio')

@user_passes_test(is_superuser)
def vender (request):
    return render(request, 'ETicketApp/pages/manager/vender.html')

@user_passes_test(is_superuser)
def vendaUnico (request):
    return render(request, 'ETicketApp/pages/manager/vendaUnico.html')

@user_passes_test(is_superuser)
def usuarioCompra (request):
    if request.method == 'POST':
        if request.POST.get('matricula'):
            matricula = request.POST.get('matricula')
            print(matricula)
            dados_pessoais = DadoPessoal.objects.get(matricula=matricula)
            context = {
                'nome_completo': dados_pessoais.nome_completo,
                'cpf': dados_pessoais.cpf,
                'matricula': dados_pessoais.matricula,
                'credito': dados_pessoais.credito,
                'unidade': dados_pessoais.unidade,
            }
            return render(request, 'ETicketApp/pages/manager/usuarioCompra.html', context)
        if request.POST.get('valor'):
            valor = request.POST.get('valor')
            # metodo_pagamento = request.POST.get('metodo_pagamento')  # Adicione o método de pagamento no formulário
        
            # Gera um método de pagamento aleatório
            metodo_pagamento = random.choice([MetodoPagamentoEnum.PIX.value, MetodoPagamentoEnum.DINHEIRO.value, MetodoPagamentoEnum.CARTAO.value]) 
            if valor:         
                try:
                    valor_decimal = Decimal(valor)
                    
                    if valor_decimal <= 0:
                        messages.error(request, 'O valor deve ser positivo.')  # Mensagem de erro se o valor for negativo ou zero
                        return redirect('vender')
                    
                    personal_data = get_object_or_404(DadoPessoal, usuario=request.user)
                    
                                    # Busca a classificação com o maior peso (prioridade) do usuário
                    classificacao_prioritaria = personal_data.classificacoes.order_by('prioridade').first()
                    
                    if classificacao_prioritaria:
                        limite_credito = classificacao_prioritaria.limite_credito
                        
                        # Verifica se a adição do valor ultrapassa o limite de crédito
                        if personal_data.credito + valor_decimal > limite_credito:
                            messages.error(request, f"O limite de crédito de R${limite_credito} será excedido.")
                            return redirect('vender')
                    
                    personal_data.credito += valor_decimal
                    personal_data.save()
                    
                                    # Cria o registro de crédito
                    Credito.objects.create(
                        usuario=request.user,
                        valor=valor_decimal,
                        metodo_pagamento=metodo_pagamento
                    )
                    messages.success(request, 'Crédito aumentado com sucesso!')  # Mensagem de sucesso
                    return redirect('vender')  # Redireciona para a página inicial
                except (DadoPessoal.DoesNotExist, Decimal.InvalidOperation):
                    messages.error(request, 'Falha ao aumentar crédito. Verifique o valor e tente novamente.')  # Mensagem de erro
                    return redirect('vender')  # Volta para a mesma página
            
    return render(request, 'ETicketApp/pages/manager/usuarioCompra.html')

@user_passes_test(is_superuser)
def usuarios (request):
    usuarios = User.objects.filter(groups__isnull=False).distinct()


    # Passar os dados para o template
    context = {
        'usuarios': usuarios
    }
    return render(request, 'ETicketApp/pages/manager/usuarios.html', context)

@user_passes_test(is_superuser)
def listar_usuarios_grupo(request):
    grupo_colaboradores = Group.objects.get(name="Colaboradores")  # Nome do grupo
    usuarios = grupo_colaboradores.user_set.all()  # Todos os usuários no grupo

    # Passar os usuários para o template
    context = {
        'usuarios': usuarios,
    }
    return render(request, 'ETicketApp/pages/manager/usuarios.html', context)

@user_passes_test(is_superuser)
def add_papel_usuario (request):
    return render(request, 'ETicketApp/pages/manager/add_user.html')

@user_passes_test(is_superuser)
def buscar_selecionar_usuario(request):
    
    search_term = request.GET.get('search_query', '')
    users_found_with_dados = None 

    if search_term:
        users_found_with_dados = DadoPessoal.objects.filter(
            Q(nome_completo__icontains=search_term) |
            Q(cpf__icontains=search_term) |         
            Q(unidade__icontains=search_term) |
            Q(usuario__username__icontains=search_term)
        ).select_related('usuario').distinct()
        
        if not users_found_with_dados:
            messages.info(request, 'Nenhum usuário encontrado com os critérios fornecidos.')
            
    print(f"Debug: search_term={search_term}, users_found_with_dados={users_found_with_dados}")

    context = {
        'users_found_with_dados': users_found_with_dados,
        'search_term': search_term,
        'page_title': 'Buscar e Gerenciar Usuários'
    }
    # This template will display the search form and results
    return render(request, 'ETicketApp/pages/manager/buscar_selecionar_usuario.html', context)

@user_passes_test(is_superuser)
def editar_papel_usuario(request, id): # Your existing view, slightly adapted
    usuario = get_object_or_404(User, id=id)
    try:
        dadopessoal = usuario.dadopessoal # Access DadoPessoal via the related name
    except DadoPessoal.DoesNotExist:
        dadopessoal = None
        messages.warning(request, f'Dados pessoais não encontrados para o usuário {usuario.username}.')

    # Mapeamento de papéis (valores do select para nomes de Grupos)
    papeis_map = {
        '1': 'ADM',
        '2': 'Colaborador',
        '3': 'Bolsista'
    }
    # Para popular o select no template
    papeis_options = [
        {'value': '1', 'name': 'ADM'},
        {'value': '2', 'name': 'Colaborador'},
        {'value': '3', 'name': 'Bolsista'}
    ]

    current_group_value = None
    if usuario.groups.exists():
        current_user_group_name = usuario.groups.first().name
        for p_opt in papeis_options:
            if p_opt['name'] == current_user_group_name:
                current_group_value = p_opt['value']
                break

    if request.method == 'POST':
        novo_papel_value = request.POST.get('papel') # e.g., '1', '2', '3'
        
        if novo_papel_value in papeis_map:
            nome_grupo = papeis_map[novo_papel_value]
            try:
                grupo = Group.objects.get(name=nome_grupo)
                usuario.groups.clear()  # Remove de todos os grupos atuais
                usuario.groups.add(grupo) # Adiciona ao novo grupo
                messages.success(request, f'O papel do usuário {usuario.username} foi atualizado para {grupo.name} com sucesso!')
            except Group.DoesNotExist:
                messages.error(request, f'O grupo "{nome_grupo}" não existe. Verifique se os grupos ADM, Colaborador, Bolsista existem.')
            except Exception as e:
                messages.error(request, f'Ocorreu um erro ao atualizar o papel: {e}')
        else:
            messages.error(request, 'Papel inválido selecionado.')
        
        # Redirect back to the search page or a user list page
        return redirect('buscar_selecionar_usuario') # Use the name of your search URL

    context = {
        'usuario': usuario,
        'dadopessoal': dadopessoal,
        'papeis_options': papeis_options,
        'current_group_value': current_group_value,
        'page_title': f'Editar Papel de {usuario.username}'
    }
    # This template will show user details and the form to assign/change role
    return render(request, 'ETicketApp/pages/manager/definir_papel_usuario.html', context)

@user_passes_test(is_superuser)
def excluir_papel_usuario(request, id):
    usuario = get_object_or_404(User, id=id)  # Busca o usuário pelo ID
    
    # Remove o usuário de todos os grupos
    usuario.groups.clear()
    
    messages.success(request, 'Usuário removido de todos os grupos!')
    return redirect('usuarios')  # Redireciona para a lista de usuários



@user_passes_test(is_superuser)
def cadastrar_cardapio(request):
    if request.method == 'POST':
        # Obtém os dados do formulário
        data = request.POST.get('data')
        cafe = request.POST.get('cafe')
        almoco = request.POST.get('almoco')
        jantar = request.POST.get('jantar')

        # Valida se todos os campos estão preenchidos
        if data and cafe and almoco and jantar:
            try:
                # Converte a data para o formato correto
                data_formatada = datetime.strptime(data, '%Y-%m-%d')

                # Cria um novo cardápio e salva no banco de dados
                novo_cardapio = Cardapio(
                    data=data_formatada,
                    cafe=cafe,
                    almoco=almoco,
                    jantar=jantar
                )
                novo_cardapio.save()

                # Mensagem de sucesso
                messages.success(request, 'Cardápio cadastrado com sucesso!')
                return redirect('cardapio')  # Redireciona para a página de cardápio

            except Exception as e:
                # Em caso de erro, mostra uma mensagem de erro
                messages.error(request, f'Erro ao cadastrar o cardápio: {str(e)}')
                return redirect('cardapio')  # Redireciona para a mesma página para tentar novamente

        else:
            # Se algum campo estiver vazio, mostra uma mensagem de erro
            messages.error(request, 'Por favor, preencha todos os campos.')
            return redirect('cardapio')
        


    # Caso contrário, exibe o formulário de cadastro de cardápio
    return render(request, 'ETicketApp/pages/manager/cardapio.html')

@user_passes_test(is_superuser)
def classificacao(request):
    classificacoes = Classificacao.objects.all()
    return render(request, 'ETicketApp/pages/manager/classificacao.html', {'classificacoes': classificacoes})

@user_passes_test(is_superuser)
def classificacao_add_edit(request, pk=None):
    if pk:
        classificacao = get_object_or_404(Classificacao, pk=pk)
    else:
        classificacao = None

    if request.method == "POST":
        form = ClassificacaoForm(request.POST, instance=classificacao)
        if form.is_valid():
            form.save()
            return redirect('classificacao')
    else:
        form = ClassificacaoForm(instance=classificacao)

    return render(request, 'ETicketApp/pages/manager/classificacao_form.html', {'form': form})

@user_passes_test(is_superuser)
def classificacao_delete(request, pk):
    classificacao = get_object_or_404(Classificacao, pk=pk)
    if request.method == "POST":
        classificacao.delete()
        return redirect('classificacao')
    return render(request, 'ETicketApp/pages/manager/classificacao.html', {'classificacao': classificacao})

def gerar_ticket_unico(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        classificacao = request.POST.get('classificacao')
        pagamento = request.POST.get('pagamento')
        cafe = int(request.POST.get('cafe', 0))
        almoco = int(request.POST.get('almoco', 0))
        janta = int(request.POST.get('janta', 0))
        refeicao = int(request.POST.get('refeicao', 0))

        try:
            classificacao_obj = Classificacao.objects.get(nome=classificacao)
            tickets_criados = []

            for _ in range(cafe):
                ticket = TicketUnico.objects.create(
                    valor=classificacao_obj.valor_cafe_manha,
                    metodo_pagamento=pagamento,
                    tipo_refeicao='CAFE_DA_MANHA',
                    classificacao=classificacao_obj
                )
                tickets_criados.append(ticket)
            
            for _ in range(almoco):
                ticket = TicketUnico.objects.create(
                    valor=classificacao_obj.valor_almoco,
                    metodo_pagamento=pagamento,
                    tipo_refeicao='ALMOCO',
                    classificacao=classificacao_obj
                )
                tickets_criados.append(ticket)

            for _ in range(janta):
                ticket = TicketUnico.objects.create(
                    valor=classificacao_obj.valor_jantar,
                    metodo_pagamento=pagamento,
                    tipo_refeicao='JANTAR',
                    classificacao=classificacao_obj
                )
                tickets_criados.append(ticket)

            messages.success(request, 'Tickets gerados com sucesso!')
            
            # Armazena os IDs dos tickets criados na sessão
            request.session['tickets_criados_ids'] = [ticket.id for ticket in tickets_criados]
            return redirect('listar_tickets')  # Redireciona para a página de listagem de tickets

        except Classificacao.DoesNotExist:
            messages.error(request, 'Classificação não encontrada.')

    return render(request, 'ETicketApp/pages/manager/vendaUnico.html')

def listar_tickets(request):
    # Recupera os IDs dos tickets criados armazenados na sessão
    tickets_ids = request.session.get('tickets_criados_ids', [])
    tickets_criados = TicketUnico.objects.filter(id__in=tickets_ids)

    # Limpa os IDs da sessão após exibir os tickets
    request.session['tickets_criados_ids'] = []

    return render(request, 'ETicketApp/pages/manager/mostra_ticket_unico.html', {'tickets': tickets_criados})

def gerar_qrcode(request, ticket_id):
    ticket = TicketUnico.objects.get(id=ticket_id)
    # Gera o QR code com o valor de `codigo` do ticket
    qr = qrcode.make(str(ticket.codigo))
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    return HttpResponse(buffer, content_type="image/png")

def informacao_manage(request):
    informacao = Informacao.objects.all()
    return render(request, 'ETicketApp/pages/manager/informacao.html', {'informacao': informacao})

def adicionar_informacao(request):
    if request.method == 'POST':
        form = InformacaoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "informação adicionado com sucesso!")
            return redirect('informacao_manage')
    else:
        form = InformacaoForm()
    return render(request, 'ETicketApp/pages/manager/informacao_form.html', {'form': form})

def editar_informacao(request, id):
    informacao = get_object_or_404(Informacao, id=id)
    if request.method == 'POST':
        form = InformacaoForm(request.POST, instance=informacao)
        if form.is_valid():
            form.save()
            messages.success(request, "informação atualizado com sucesso!")
            return redirect('informacao_manage')
    else:
        form = InformacaoForm(instance=informacao)
    return render(request, 'ETicketApp/pages/manager/informacao_form.html', {'form': form, 'informacao': informacao})

def deletar_informacao(request, id):
    informacao = get_object_or_404(Informacao, id=id)
    if request.method == 'POST':
        informacao.delete()
        messages.success(request, "informacao deletado com sucesso!")
        return redirect('informacao_manage')