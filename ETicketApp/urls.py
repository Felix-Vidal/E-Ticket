from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import *

urlpatterns = [
    path('', home, name='home'), 
    path('aumentar-credito/', aumentar_credito, name='aumentar-credito'),
    path('pagamento/', pagamento, name='pagamento'),
    path('menu/', menu, name='menu'),
    path('perfil/', perfil, name='perfil'),
    path('login/', login, name='login'),
    
    path('historico/', historico, name='historico'),
    path('historico/refeicoes/', historico_refeicoes, name='historico_refeicoes'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),  
    path('valorPaga/', valorPaga, name='valorPaga'), 
    
    path('informacao/', informacao, name='informacao'),
    
    path('menuExterno/', menuExterno, name='menuExterno'),
    path('valorPagaExterno/', valorPagaExterno, name='valorPagaExterno'),
    
    path('manage/', dashboard, name='manage'), # home
    
    path('manage/validar/', validar, name='validar'),
    path('manage/mostrar_usuario/', mostrar_usuario, name='mostrar_usuario'),
    path('manage/validar_usuario/', validar_usuario, name='validar_usuario'),
    
    path('manage/ticketUnico/', ticketUnico, name='ticketUnico'),
    
    path('manage/gerar-ticket-unico/', gerar_ticket_unico, name='gerar_ticket_unico'),
    path('manage/ticket/<int:ticket_id>/qrcode/', gerar_qrcode, name='gerar_qrcode'),
    path('manage/listar-tickets/', listar_tickets, name='listar_tickets'),
    
    
    
    path('manage/relatorio/', relatorio, name='relatorio'),
    
    path('manage/vender/', vender, name='vender'),    
    path('manage/vendaUnico/', vendaUnico, name='vendaUnico'), 
    path('manage/usuarioCompra/', usuarioCompra, name='usuarioCompra'),
    
    path('manage/usuarios/', listar_usuarios_view, name='usuarios'),
    path('manage/add_papel/', add_papel_usuario, name='add_papel_usuario') ,
    path('manage/usuarios/excluir_papel/<int:id>/', excluir_papel_usuario, name='excluir_papel_usuario'),
    path('manage/usuarios/buscar_gerenciar/', buscar_selecionar_usuario, name='buscar_selecionar_usuario'),
    path('manage/usuarios/editar_papel/<int:usuario_id>/', editar_papel_usuario, name='editar_papel_usuario'),
    
    path('manage/classificacoes/', classificacao, name='classificacao'),
    path('manage/classificacoes/add/', classificacao_add_edit, name='classificacao_add'),  # Nova URL para adicionar
    path('manage/classificacoes/<int:pk>/edit/', classificacao_add_edit, name='classificacao_edit'),  # Editar
    path('manage/classificacoes/<int:pk>/delete/', classificacao_delete, name='classificacao_delete'),
    
    path('manage/cardapios/', cardapio, name='cardapio'),
    path('manage/cardapios/add/', adicionar_cardapio, name='adicionar_cardapio'),
    path('manage/cardapios/edit/<int:id>/', editar_cardapio, name='editar_cardapio'),
    path('manage/cardapios/delete/<int:id>/', excluir_cardapio, name='excluir_cardapio'),
    
    path('manage/informes/', informacao_manage, name='informacao_manage'),
    path('manage/informes/adicionar/', adicionar_informacao, name='adicionar_informacao'),
    path('manage/informes/editar/<int:id>/', editar_informacao, name='editar_informacao'),
    path('manage/informes/deletar/<int:id>/', deletar_informacao, name='deletar_informacao'),
    
    path('manage/permissoes/', permissoes, name='permissoes'),
    path('manage/permissoes/adicionar/', adicionar_permissoes, name='adicionar_permissoes'),
    path('manage/permissoes/editar/<int:id>/', editar_permissoes, name='editar_permissoes'),
    path('manage/permissoes/deletar/<int:id>/', deletar_permissoes, name='deletar_permissoes'),

]