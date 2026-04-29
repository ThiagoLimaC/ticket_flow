from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Chamado, EmpresaCliente, Equipamento
from .forms import EmpresaClienteForm, EquipamentoForm
from usuarios.decorators import requer_perfil


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

    context = {
        'chamados': chamados,
        'total_abertos': chamados.filter(status=Chamado.Status.ABERTO).count(),
        'total_em_atendimento': chamados.filter(status=Chamado.Status.EM_ANDAMENTO).count(),
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