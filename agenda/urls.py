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
]