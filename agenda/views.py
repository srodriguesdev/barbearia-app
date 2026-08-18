from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import Barbeiro, Servico
from datetime import datetime, timedelta


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

    # Redireciona para a página inicial
    return redirect("home")


@login_required
def agendar(request):

    # Busca os barbeiros ativos para mostrar na tela
    barbeiros = Barbeiro.objects.filter(ativo=True)


    if request.method == "POST":

        # Recebe o ID do barbeiro escolhido pelo usuário
        barbeiro_id = request.POST.get("barbeiro")

        # Verifica se o barbeiro foi selecionado
        if barbeiro_id:

            # Busca o barbeiro escolhido no banco
            barbeiro = Barbeiro.objects.get(id=barbeiro_id)

            # Guarda o barbeiro escolhido na sessão
            request.session["barbeiro_id"] = barbeiro_id

            # Vai para escolha do serviço
            return redirect("escolher_servico")


    return render(
        request,
        "agenda/agendar.html",
        {
            "barbeiros": barbeiros,
        }
    )


@login_required
def escolher_data(request):

    # Recupera o barbeiro escolhido anteriormente na sessão
    barbeiro_id = request.session.get("barbeiro_id")

    # Recupera o serviço escolhido anteriormente na sessão
    servico_id = request.session.get("servico_id")


    # Busca o barbeiro no banco pelo ID salvo
    barbeiro = Barbeiro.objects.get(id=barbeiro_id)

    # Busca o serviço no banco pelo ID salvo
    servico = Servico.objects.get(id=servico_id)

    # Inicialmente não existem horários carregados
    horarios = []


    if request.method == "POST":

        # Recebe a data escolhida pelo usuário
        data = request.POST.get("data")

        # Mostra a data escolhida no terminal para teste
        print("Data escolhida:", data)

        # Gera os horários disponíveis da barbearia
        horarios = gerar_horarios()

        # Mostra os horários gerados no terminal para teste
        print(horarios)


    return render(
        request,
        "agenda/data.html",
        {
            "barbeiro": barbeiro,
            "servico": servico,
            "horarios": horarios,
        }
    )



def gerar_horarios():

    # Define o início dos atendimentos
    inicio = datetime.strptime("08:00", "%H:%M")

    # Define o último horário que pode iniciar atendimento
    fim = datetime.strptime("19:00", "%H:%M")

    # Lista que vai armazenar os horários disponíveis
    horarios = []


    # Enquanto o horário atual for menor ou igual ao final
    while inicio <= fim:

        # Adiciona o horário formatado na lista
        horarios.append(
            inicio.strftime("%H:%M")
        )

        # Soma 30 minutos para criar o próximo horário
        inicio += timedelta(minutes=30)


    # Retorna a lista completa de horários
    return horarios

@login_required
def escolher_servico(request):

    # Recupera o barbeiro escolhido na sessão
    barbeiro_id = request.session.get("barbeiro_id")

    # Busca o barbeiro no banco
    barbeiro = Barbeiro.objects.get(id=barbeiro_id)

    # Busca os serviços ativos
    servicos = Servico.objects.filter(ativo=True)


    if request.method == "POST":

        # Recebe o serviço escolhido
        servico_id = request.POST.get("servico")

        # Guarda o serviço na sessão
        request.session["servico_id"] = servico_id

        # Vai para escolha de data
        return redirect("escolher_data")


    return render(
        request,
        "agenda/servico.html",
        {
            "barbeiro": barbeiro,
            "servicos": servicos,
        }
    )