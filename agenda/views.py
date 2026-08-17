from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Barbeiro, Servico

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

@login_required
def agendar(request):

    # Busca os barbeiros ativos para mostrar na tela
    barbeiros = Barbeiro.objects.filter(ativo=True)

    # Inicialmente não temos serviços selecionados
    servicos = None

    if request.method == "POST":

        # Recebe o ID do barbeiro escolhido pelo usuário
        barbeiro_id = request.POST.get("barbeiro")

        # Verifica se o barbeiro foi selecionado
        if barbeiro_id:

            # Busca o barbeiro no banco pelo ID recebido
            barbeiro = Barbeiro.objects.get(id=barbeiro_id)

            # Guarda o barbeiro escolhido na sessão do usuário
            request.session["barbeiro_id"] = barbeiro_id

            # Busca os serviços ativos disponíveis
            servicos = Servico.objects.filter(ativo=True)


        # Recebe o ID do serviço escolhido pelo usuário
        servico_id = request.POST.get("servico")

        # Verifica se o serviço foi selecionado
        if servico_id:

            # Busca o serviço no banco pelo ID recebido
            servico = Servico.objects.get(id=servico_id)

            # Recupera o barbeiro escolhido anteriormente da sessão
            barbeiro_id = request.session.get("barbeiro_id")

            # Busca novamente o barbeiro no banco
            barbeiro = Barbeiro.objects.get(id=barbeiro_id)

            # Mostra as escolhas no terminal para teste
            print("Barbeiro:", barbeiro)
            print("Serviço:", servico)


    return render(
        request,
        "agenda/agendar.html",
        {
            "barbeiros": barbeiros,
            "servicos": servicos,
        }
    )