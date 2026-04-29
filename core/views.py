from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Chamado


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