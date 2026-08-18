from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import Barbeiro, Servico, Agendamento
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib import messages



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
    return render(
        request,
        "agenda/cadastro.html",
        {"form": form}
    )



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


    return render(
        request,
        "agenda/login.html",
        {"form": form}
    )



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



    if request.method == "POST":

        # Recebe a data escolhida pelo usuário
        data = request.POST.get("data")


        # Verifica se o usuário escolheu uma data
        if data:

            # Guarda a data escolhida na sessão
            request.session["data"] = data


            # Mostra a data escolhida no terminal para teste
            print("Data escolhida:", data)


            # Vai para escolha de horário
            return redirect("escolher_horario")



    return render(
        request,
        "agenda/data.html",
        {
            "barbeiro": barbeiro,
            "servico": servico,
        }
    )



@login_required
def escolher_horario(request):

    # Recupera a data escolhida na sessão
    data = request.session.get("data")


    # Gera os horários considerando a data escolhida
    horarios = gerar_horarios(data)



    if request.method == "POST":

        # Recebe o horário escolhido pelo usuário
        horario = request.POST.get("horario")


        # Verifica se o usuário escolheu um horário
        if horario:

            # Guarda o horário escolhido na sessão
            request.session["horario"] = horario


            # Recupera os dados escolhidos anteriormente
            barbeiro_id = request.session.get("barbeiro_id")
            servico_id = request.session.get("servico_id")
            data = request.session.get("data")


            # Busca os objetos no banco
            barbeiro = Barbeiro.objects.get(id=barbeiro_id)

            servico = Servico.objects.get(id=servico_id)


            # Cria o agendamento no banco
            Agendamento.objects.create(
                cliente=request.user,
                barbeiro=barbeiro,
                servico=servico,
                data=data,
                horario=horario,
            )


            # Mostra no terminal para teste
            print("Agendamento criado com sucesso!")
            print("Cliente:", request.user)
            print("Barbeiro:", barbeiro)
            print("Serviço:", servico)
            print("Data:", data)
            print("Horário:", horario)


            # Volta para a página inicial
            return redirect("home")



    return render(
        request,
        "agenda/horario.html",
        {
            "data": data,
            "horarios": horarios,
        }
    )



def gerar_horarios(data):

    # Define o início dos atendimentos
    inicio = datetime.strptime("08:00", "%H:%M")


    # Define o último horário que pode iniciar atendimento
    fim = datetime.strptime("19:00", "%H:%M")


    # Lista que vai armazenar os horários disponíveis
    horarios = []



    # Pega a data e hora atual
    agora = timezone.localtime()



    # Converte a data escolhida pelo usuário
    data_escolhida = datetime.strptime(
        data,
        "%Y-%m-%d"
    ).date()



    while inicio <= fim:


        # Define se o horário pode aparecer
        horario_valido = True



        # Se a data escolhida for hoje
        if data_escolhida == agora.date():


            # Monta data e horário completo
            horario_completo = datetime.combine(
                data_escolhida,
                inicio.time()
            )


            # Remove horários que já passaram
            if horario_completo <= agora.replace(tzinfo=None):

                horario_valido = False



        # Adiciona apenas horários válidos
        if horario_valido:

            horarios.append(
                inicio.strftime("%H:%M")
            )



        # Soma 30 minutos para próximo horário
        inicio += timedelta(minutes=30)



    return horarios