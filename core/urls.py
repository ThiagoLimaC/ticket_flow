from django.urls import path
from . import views

urlpatterns = [
    # dashboard
    path('', views.dashboard, name='dashboard'),

    # clientes
    path('clientes/', views.listar_clientes, name='listar_clientes'),
    path('clientes/novo/', views.criar_cliente, name='criar_cliente'),
    path('clientes/<int:cliente_id>/', views.detalhe_cliente, name='detalhe_cliente'),
    path('clientes/<int:cliente_id>/editar/', views.editar_cliente, name='editar_cliente'),

    # equipamentos
    path('clientes/<int:cliente_id>/equipamentos/novo/', views.criar_equipamento, name='criar_equipamento'),
    path('equipamentos/<int:equipamento_id>/editar/', views.editar_equipamento, name='editar_equipamento'),
]