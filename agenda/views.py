from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm

def home(request):
    # Renderiza a página inicial da aplicação
    return render(request, "agenda/home.html")

def cadastro(request):
    # Se o formulário foi enviado, recebe os dados preenchidos pelo usuário
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        # Valida os dados e cria o usuário caso estejam corretos
        if form.is_valid():
            form.save()
            return redirect("home")

    else:
        # Se o usuário apenas acessou a página, cria um formulário vazio
        form = UserCreationForm()

    # Envia o formulário para o template cadastro.html
    return render(request, "agenda/cadastro.html", {"form": form})

def entrar(request):
    # Se o formulário foi enviado, tenta autenticar o usuário
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            return redirect("home")

    else:
        # Exibe o formulário de login vazio
        form = AuthenticationForm()

    return render(request, "agenda/login.html", {"form": form})

def sair(request):
    # Encerra a sessão do usuário
    logout(request)

    #Redireciona para a pagina inicial
    return redirect("home")
