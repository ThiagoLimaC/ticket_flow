from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Chamado

@login_required
def dashboard(request):
    # Se for staff (técnico/admin), vê todos os chamados
    if request.user.is_staff:
        chamados = Chamado.objects.all().order_by('-data_abertura')
    else:
        # Se for cliente comum, vê apenas os seus chamados
        chamados = Chamado.objects.filter(aberto_por=request.user).order_by('-data_abertura')
    
    context = {
        'chamados': chamados,
        'total_abertos': chamados.filter(status='aberto').count(),
        'total_em_atendimento': chamados.filter(status='em_atendimento').count(),
    }
    return render(request, 'core/dashboard.html', context)