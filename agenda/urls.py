from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("cadastro/", views.cadastro, name='cadastro'),
    path("login/", views.entrar, name="login"),
    path("logout/", views.sair, name="logout"),
    path("agendar/", views.agendar, name="agendar"),
    path("data/", views.escolher_data, name="escolher_data"),
    path("servico/", views.escolher_servico, name="escolher_servico"),
    path("horario/", views.escolher_horario, name="escolher_horario"),
    path("confirmar/", views.confirmar_agendamento, name="confirmar_agendamento"),
    path("sucesso/",views.sucesso_agendamento,name="sucesso_agendamento"),
    path("meus-agendamentos/",views.meus_agendamentos,name="meus_agendamentos"),
    path("cancelar/<int:agendamento_id>/",views.cancelar_agendamento,name="cancelar_agendamento"),
    path("historico/",views.historico_agendamentos,name="historico_agendamentos"),
]