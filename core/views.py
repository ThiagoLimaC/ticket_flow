from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Chamado, EmpresaCliente, Equipamento, Categoria
from .forms import (
    EmpresaClienteForm, EquipamentoForm, AbrirChamadoForm,
    AtribuirTecnicoForm, MudarStatusForm,
    RegistrarAtendimentoForm, PecaUtilizadaForm,
)
from usuarios.decorators import requer_perfil
from .services import abrir_chamado, atribuir_tecnico, mudar_status, TRANSICOES_PERMITIDAS

STATUS_ATIVOS = (Chamado.Status.EM_ANDAMENTO, Chamado.Status.AGUARDANDO)

def _pode_registrar_atendimento(usuario, chamado):
    """Retorna True se o usuário pode registrar diagnóstico/peças neste chamado."""
    perfil = usuario.perfil
    if chamado.status not in STATUS_ATIVOS:
        return False
    if perfil.is_cliente:
        return False
    if perfil.is_tecnico and chamado.tecnico_responsavel != usuario:
        return False
    return True


@login_required
def dashboard(request):
    perfil = request.user.perfil

    # admin e técnico veem todos os chamados
    # cliente vê apenas os chamados da sua empresa
    if perfil.is_admin or perfil.is_tecnico:
        chamados = Chamado.objects.all().order_by('-data_abertura')
    else:
        chamados = Chamado.objects.filter(
            aberto_por=request.user
        ).order_by('-data_abertura')

    status_encerrados = [Chamado.Status.RESOLVIDO, Chamado.Status.FECHADO]
    context = {
        'chamados': chamados,
        'total_abertos': chamados.filter(status=Chamado.Status.ABERTO).count(),
        'total_em_atendimento': chamados.filter(status=Chamado.Status.EM_ANDAMENTO).count(),
        'total_atrasados': chamados.filter(
            sla_prazo__lt=timezone.now()
        ).exclude(status__in=status_encerrados).count(),
    }
    return render(request, 'core/dashboard.html', context)

# ─── Clientes ─────────────────────────────────────────────────────────────────

@requer_perfil('admin')
def listar_clientes(request):
    clientes = EmpresaCliente.objects.all()
    return render(request, 'core/clientes/lista.html', {'clientes': clientes})


@requer_perfil('admin')
def criar_cliente(request):
    # GET: exibe formulário vazio
    # POST: valida e salva
    if request.method == 'POST':
        form = EmpresaClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente cadastrado com sucesso.')
            return redirect('listar_clientes')
    else:
        form = EmpresaClienteForm()
    return render(request, 'core/clientes/form.html', {'form': form, 'titulo': 'Novo Cliente'})


@requer_perfil('admin')
def editar_cliente(request, cliente_id):
    # instance diz ao form que estamos editando, não criando
    cliente = get_object_or_404(EmpresaCliente, id=cliente_id)
    if request.method == 'POST':
        form = EmpresaClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso.')
            return redirect('detalhe_cliente', cliente_id=cliente.id)
    else:
        form = EmpresaClienteForm(instance=cliente)
    return render(request, 'core/clientes/form.html', {'form': form, 'titulo': 'Editar Cliente'})


@requer_perfil('admin')
def detalhe_cliente(request, cliente_id):
    cliente = get_object_or_404(EmpresaCliente, id=cliente_id)
    equipamentos = cliente.equipamentos.all()
    return render(request, 'core/clientes/detalhe.html', {
        'cliente': cliente,
        'equipamentos': equipamentos,
    })


# ─── Equipamentos ─────────────────────────────────────────────────────────────

@requer_perfil('admin')
def criar_equipamento(request, cliente_id):
    cliente = get_object_or_404(EmpresaCliente, id=cliente_id)
    if request.method == 'POST':
        form = EquipamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipamento cadastrado com sucesso.')
            return redirect('detalhe_cliente', cliente_id=cliente.id)
    else:
        # pré-seleciona o cliente no formulário
        form = EquipamentoForm(initial={'cliente': cliente})
    return render(request, 'core/equipamentos/form.html', {
        'form': form,
        'cliente': cliente,
        'titulo': 'Novo Equipamento',
    })


@requer_perfil('admin')
def editar_equipamento(request, equipamento_id):
    equipamento = get_object_or_404(Equipamento, id=equipamento_id)
    if request.method == 'POST':
        form = EquipamentoForm(request.POST, instance=equipamento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipamento atualizado com sucesso.')
            return redirect('detalhe_cliente', cliente_id=equipamento.cliente.id)
    else:
        form = EquipamentoForm(instance=equipamento)
    return render(request, 'core/equipamentos/form.html', {
        'form': form,
        'cliente': equipamento.cliente,
        'titulo': 'Editar Equipamento',
    })

@login_required
def abrir_chamado_view(request):
    # técnico não pode abrir chamado — redireciona para o dashboard
    if request.user.perfil.is_tecnico:
        messages.error(request, 'Técnicos não podem abrir chamados.')
        return redirect('dashboard')

    if request.method == 'POST':
        # passa o usuário logado como primeiro argumento do form
        form = AbrirChamadoForm(request.user, request.POST)
        if form.is_valid():
            # delega a criação do chamado e da movimentação para o service
            chamado = abrir_chamado(form, request.user)
            messages.success(request, f'Chamado #{chamado.id} aberto com sucesso.')
            return redirect('detalhe_chamado', chamado_id=chamado.id)
    else:
        # GET: form vazio já filtrado pelo usuário logado
        form = AbrirChamadoForm(request.user)

    return render(request, 'core/chamados/abrir.html', {'form': form})

@login_required
def detalhe_chamado(request, chamado_id):
    chamado = get_object_or_404(Chamado, id=chamado_id)
    perfil = request.user.perfil

    # cliente só acessa chamados que ele mesmo abriu
    if perfil.is_cliente and chamado.aberto_por != request.user:
        messages.error(request, 'Você não tem acesso a este chamado.')
        return redirect('dashboard')

    # técnico só acessa chamados atribuídos a ele
    if perfil.is_tecnico and chamado.tecnico_responsavel != request.user:
        messages.error(request, 'Você não tem acesso a este chamado.')
        return redirect('dashboard')

    movimentacoes = chamado.movimentacoes.all()
    pecas = chamado.pecas.all()

    # forms de registro de atendimento e peças — só para quem tem permissão
    pode_registrar = _pode_registrar_atendimento(request.user, chamado)
    form_atendimento = RegistrarAtendimentoForm(instance=chamado) if pode_registrar else None
    form_peca = PecaUtilizadaForm() if pode_registrar else None

    # form de mudança de status — só quando há transições disponíveis
    form_status = None
    if not perfil.is_cliente and chamado.status != Chamado.Status.FECHADO:
        form_candidato = MudarStatusForm(perfil, chamado.status)
        if form_candidato.fields['novo_status'].choices:
            form_status = form_candidato

    return render(request, 'core/chamados/detalhe.html', {
        'chamado': chamado,
        'movimentacoes': movimentacoes,
        'pecas': pecas,
        'form_atendimento': form_atendimento,
        'form_peca': form_peca,
        'form_status': form_status,
    })

@login_required
def registrar_atendimento_view(request, chamado_id):
    chamado = get_object_or_404(Chamado, id=chamado_id)

    if not _pode_registrar_atendimento(request.user, chamado):
        messages.error(request, 'Ação não permitida.')
        return redirect('detalhe_chamado', chamado_id=chamado.id)

    if request.method == 'POST':
        form = RegistrarAtendimentoForm(request.POST, instance=chamado)
        if form.is_valid():
            form.save()
            messages.success(request, 'Atendimento registrado com sucesso.')
        else:
            messages.error(request, 'Erro ao salvar. Verifique os campos.')

    return redirect('detalhe_chamado', chamado_id=chamado.id)


@login_required
def adicionar_peca_view(request, chamado_id):
    chamado = get_object_or_404(Chamado, id=chamado_id)

    if not _pode_registrar_atendimento(request.user, chamado):
        messages.error(request, 'Ação não permitida.')
        return redirect('detalhe_chamado', chamado_id=chamado.id)

    if request.method == 'POST':
        form = PecaUtilizadaForm(request.POST)
        if form.is_valid():
            peca = form.save(commit=False)
            peca.chamado = chamado
            peca.save()
            messages.success(request, f'Peça "{peca.descricao}" adicionada com sucesso.')
        else:
            messages.error(request, 'Erro ao adicionar peça. Verifique os campos.')

    return redirect('detalhe_chamado', chamado_id=chamado.id)


@login_required
def mudar_status_view(request, chamado_id):
    chamado = get_object_or_404(Chamado, id=chamado_id)
    perfil = request.user.perfil

    # cliente não tem essa permissão
    if perfil.is_cliente:
        messages.error(request, 'Você não tem permissão para alterar o status de um chamado.')
        return redirect('detalhe_chamado', chamado_id=chamado.id)

    # chamado fechado é imutável
    if chamado.status == Chamado.Status.FECHADO:
        messages.error(request, 'Chamado fechado não pode ser alterado.')
        return redirect('detalhe_chamado', chamado_id=chamado.id)

    # técnico só pode alterar chamados atribuídos a ele
    if perfil.is_tecnico and chamado.tecnico_responsavel != request.user:
        messages.error(request, 'Você não tem acesso a este chamado.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = MudarStatusForm(perfil, chamado.status, request.POST)
        if form.is_valid():
            novo_status = form.cleaned_data['novo_status']
            comentario = form.cleaned_data['comentario']
            chamado = mudar_status(chamado, novo_status, request.user, comentario)
            messages.success(request, f'Status atualizado para "{chamado.get_status_display()}".')
            return redirect('detalhe_chamado', chamado_id=chamado.id)

    # form inválido (transição não permitida): avisa e volta
    if request.method == 'POST':
        messages.error(request, 'Transição de status inválida.')
    return redirect('detalhe_chamado', chamado_id=chamado.id)


@requer_perfil('admin')
def atribuir_tecnico_view(request, chamado_id):
    chamado = get_object_or_404(Chamado, id=chamado_id)

    # chamado fechado é imutável — bloqueia qualquer ação
    if chamado.status == Chamado.Status.FECHADO:
        messages.error(request, 'Chamado fechado não pode ser alterado.')
        return redirect('detalhe_chamado', chamado_id=chamado.id)

    # chamado já tem técnico — bloqueia reatribuição no MVP
    if chamado.tecnico_responsavel:
        messages.error(request, 'Este chamado já possui um técnico atribuído.')
        return redirect('detalhe_chamado', chamado_id=chamado.id)

    if request.method == 'POST':
        form = AtribuirTecnicoForm(request.POST)
        if form.is_valid():
            tecnico = form.cleaned_data['tecnico']
            # delega toda a lógica de negócio para o service
            atribuir_tecnico(chamado, tecnico, request.user)
            messages.success(request, f'Chamado atribuído a {tecnico.username} com sucesso.')
            return redirect('detalhe_chamado', chamado_id=chamado.id)
    else:
        form = AtribuirTecnicoForm()

    return render(request, 'core/chamados/atribuir.html', {
        'form': form,
        'chamado': chamado,
    })