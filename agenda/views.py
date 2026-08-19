from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import Barbeiro, Servico, Agendamento
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib import messages
from urllib.parse import quote


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


    # Recupera o barbeiro escolhido anteriormente
    barbeiro_id = request.session.get("barbeiro_id")


    # Recupera o serviço escolhido anteriormente
    servico_id = request.session.get("servico_id")


    # Gera os horários considerando:
    # data, barbeiro e duração do serviço escolhido
    horarios = gerar_horarios(
        data,
        barbeiro_id,
        servico_id
    )



    if request.method == "POST":

        # Recebe o horário escolhido pelo usuário
        horario = request.POST.get("horario")


        # Verifica se o usuário escolheu um horário
        if horario:

            # Guarda o horário escolhido na sessão
            request.session["horario"] = horario


            # Vai para a tela de confirmação do agendamento
            return redirect("confirmar_agendamento")



    return render(
        request,
        "agenda/horario.html",
        {
            "data": data,
            "horarios": horarios,
        }
    )

@login_required
def confirmar_agendamento(request):

    # Recupera os dados escolhidos anteriormente na sessão
    barbeiro_id = request.session.get("barbeiro_id")
    servico_id = request.session.get("servico_id")
    data = request.session.get("data")
    horario = request.session.get("horario")


    # Busca o barbeiro e o serviço no banco
    barbeiro = Barbeiro.objects.get(id=barbeiro_id)
    servico = Servico.objects.get(id=servico_id)


    # Se o usuário clicar em "Confirmar agendamento"
    if request.method == "POST":

        # Gera novamente os horários disponíveis
        # para garantir que o horário ainda está livre
        horarios_disponiveis = gerar_horarios(
            data,
            barbeiro_id,
            servico_id
        )


        # Se o horário não estiver mais disponível,
        # volta para a escolha de horário
        if horario not in horarios_disponiveis:

            # Mostra uma mensagem para o usuário
            messages.error(
                request,
                "Esse horário não está mais disponível. Escolha outro horário."
            )

            # Volta para a tela de escolha de horários
            return redirect("escolher_horario")


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


        
        return redirect("sucesso_agendamento")


    # Se for apenas abrir a página, mostra os dados para conferência
    return render(
        request,
        "agenda/confirmar_agendamento.html",
        {
            "barbeiro": barbeiro,
            "servico": servico,
            "data": data,
            "horario": horario,
        }
    )



def gerar_horarios(data, barbeiro_id, servico_id):

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


    # Data de hoje
    hoje = agora.date()


    # Descobre o sábado da semana atual
    dias_ate_sabado = 5 - hoje.weekday()

    if dias_ate_sabado < 0:
        dias_ate_sabado += 7


    fim_semana_atual = hoje + timedelta(
        days=dias_ate_sabado
    )


    # Limite final:
    # sábado da próxima semana
    data_limite = fim_semana_atual + timedelta(
        days=7
    )


    # Impede escolher datas passadas
    if data_escolhida < hoje:
        return []


    # Permite somente terça até sábado
    # segunda = 0
    # terça = 1
    # quarta = 2
    # quinta = 3
    # sexta = 4
    # sábado = 5
    # domingo = 6
    if data_escolhida.weekday() not in [1, 2, 3, 4, 5]:
        return []


    # Impede datas depois do sábado da próxima semana
    if data_escolhida > data_limite:
        return []


    # Busca o serviço que o cliente escolheu
    servico_escolhido = Servico.objects.get(id=servico_id)


    # Busca os agendamentos ativos daquele barbeiro e daquela data
    agendamentos = Agendamento.objects.filter(
        barbeiro_id=barbeiro_id,
        data=data_escolhida
    ).exclude(
        status="cancelado"
    )


    while inicio <= fim:

        # Define se o horário pode aparecer
        horario_valido = True


        # Início do possível novo agendamento
        novo_inicio = datetime.combine(
            data_escolhida,
            inicio.time()
        )


        # Final do possível novo agendamento,
        # considerando a duração do serviço escolhido
        novo_fim = novo_inicio + timedelta(
            minutes=servico_escolhido.duracao
        )


        # Se a data escolhida for hoje
        if data_escolhida == agora.date():

            # Remove horários que já passaram
            if novo_inicio <= agora.replace(tzinfo=None):

                horario_valido = False


        # Verifica conflito com agendamentos já existentes
        for agendamento in agendamentos:

            # Início do agendamento já existente
            agendamento_inicio = datetime.combine(
                data_escolhida,
                agendamento.horario
            )


            # Final do agendamento já existente
            agendamento_fim = agendamento_inicio + timedelta(
                minutes=agendamento.servico.duracao
            )


            # Existe conflito quando os dois períodos se cruzam
            if novo_inicio < agendamento_fim and novo_fim > agendamento_inicio:

                horario_valido = False
                break


        # Adiciona apenas horários válidos
        if horario_valido:

            horarios.append(
                inicio.strftime("%H:%M")
            )


        # Soma 30 minutos para o próximo horário
        inicio += timedelta(minutes=30)


    return horarios

@login_required
def sucesso_agendamento(request):

    # Recupera os dados do último agendamento pela sessão
    barbeiro_id = request.session.get("barbeiro_id")
    servico_id = request.session.get("servico_id")
    data = request.session.get("data")
    horario = request.session.get("horario")


    # Busca barbeiro e serviço no banco
    barbeiro = Barbeiro.objects.get(id=barbeiro_id)
    servico = Servico.objects.get(id=servico_id)


    # Converte a data para o formato brasileiro
    data_formatada = datetime.strptime(
        data,
        "%Y-%m-%d"
    ).strftime("%d/%m/%Y")


    # Converte o valor para o formato brasileiro
    valor_formatado = f"{servico.preco:.2f}".replace(".", ",")


    # Monta a mensagem que será enviada pelo WhatsApp
    mensagem_whatsapp = (
        f"Olá, {barbeiro.nome}! \n\n"
        f"Estou enviando a confirmação do meu agendamento:\n"
        f"Cliente: {request.user.username.title()}\n"
        f"Serviço: {servico.nome}\n"
        f"Data: {data_formatada}\n"
        f"Horário: {horario}\n"
        f"Valor: R$ {valor_formatado}\n\n"
        f"Agendamento confirmado pelo sistema."
    )


    # Codifica a mensagem para usar dentro do link do WhatsApp
    mensagem_codificada = quote(mensagem_whatsapp)


    # Remove espaços, traços e parênteses do telefone
    telefone = barbeiro.telefone.replace(
        " ", ""
    ).replace(
        "-", ""
    ).replace(
        "(", ""
    ).replace(
        ")", ""
    )


    # Adiciona o código do Brasil caso ainda não exista
    if not telefone.startswith("55"):
        telefone = "55" + telefone


    # Monta o link do WhatsApp com a mensagem pronta
    link_whatsapp = (
        f"https://wa.me/{telefone}?text={mensagem_codificada}"
    )


    # Mostra a tela de sucesso com os dados do agendamento
    return render(
        request,
        "agenda/sucesso.html",
        {
            "barbeiro": barbeiro,
            "servico": servico,
            "data": data_formatada,
            "horario": horario,
            "valor_formatado": valor_formatado,
            "mensagem_whatsapp": mensagem_whatsapp,
            "link_whatsapp": link_whatsapp,
        }
    )

@login_required
def meus_agendamentos(request):

    # Atualiza automaticamente os agendamentos
    # cujo horário final já passou
    atualizar_agendamentos_concluidos()


    # Mostra somente os agendamentos confirmados
    # do usuário que está logado
    agendamentos = Agendamento.objects.filter(
        cliente=request.user,
        status="confirmado"
    ).order_by(
        "data",
        "horario"
    )


    return render(
        request,
        "agenda/meus_agendamentos.html",
        {
            "agendamentos": agendamentos,
        }
    )

@login_required
def cancelar_agendamento(request, agendamento_id):

    # Busca o agendamento do usuário logado
    agendamento = Agendamento.objects.get(
        id=agendamento_id,
        cliente=request.user
    )


    # Se o usuário confirmar o cancelamento
    if request.method == "POST":

        # Altera o status para cancelado
        agendamento.status = "cancelado"

        # Salva a alteração no banco
        agendamento.save()

        # Volta para Meus agendamentos
        return redirect("meus_agendamentos")


    # Se apenas abriu a página,
    # mostra a tela de confirmação
    return render(
        request,
        "agenda/confirmar_cancelamento.html",
        {
            "agendamento": agendamento,
        }
    )

@login_required
def historico_agendamentos(request):

    # Atualiza automaticamente os agendamentos
    # cujo horário final já passou
    atualizar_agendamentos_concluidos()


    # Busca somente os agendamentos concluídos
    # do usuário que está logado
    agendamentos = Agendamento.objects.filter(
        cliente=request.user,
        status="concluido"
    ).order_by(
        "-data",
        "-horario"
    )


    return render(
        request,
        "agenda/historico_agendamentos.html",
        {
            "agendamentos": agendamentos,
        }
    )

def atualizar_agendamentos_concluidos():

    # Pega a data e hora atual
    agora = timezone.localtime()


    # Busca somente agendamentos que ainda estão confirmados
    agendamentos = Agendamento.objects.filter(
        status="confirmado"
    )


    for agendamento in agendamentos:

        # Monta a data e hora de início do agendamento
        inicio_agendamento = datetime.combine(
            agendamento.data,
            agendamento.horario
        )


        # Calcula o horário final usando a duração do serviço
        fim_agendamento = inicio_agendamento + timedelta(
            minutes=agendamento.servico.duracao
        )


        # Compara com a hora atual
        if fim_agendamento <= agora.replace(tzinfo=None):

            # Marca o agendamento como concluído
            agendamento.status = "concluido"

            # Salva a alteração no banco
            agendamento.save()