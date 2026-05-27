from .models import Chamado, Movimentacao

# mapa de transições válidas: status_atual → [status possíveis]
TRANSICOES_PERMITIDAS = {
    Chamado.Status.EM_ANDAMENTO: [Chamado.Status.AGUARDANDO, Chamado.Status.RESOLVIDO],
    Chamado.Status.AGUARDANDO:   [Chamado.Status.EM_ANDAMENTO, Chamado.Status.RESOLVIDO],
    Chamado.Status.RESOLVIDO:    [Chamado.Status.FECHADO, Chamado.Status.ABERTO],
}


def abrir_chamado(form, usuario):
    chamado = form.save(commit=False)

    chamado.status = Chamado.Status.ABERTO
    chamado.aberto_por = usuario

    # preenche o cliente automaticamente a partir do equipamento selecionado
    chamado.cliente = chamado.equipamento.cliente

    chamado.save()

    Movimentacao.objects.create(
        chamado=chamado,
        responsavel=usuario,
        status_anterior=Chamado.Status.ABERTO,
        status_novo=Chamado.Status.ABERTO,
        comentario='Chamado aberto.',
    )

    return chamado

def mudar_status(chamado, novo_status, responsavel, comentario=''):
    status_anterior = chamado.status
    chamado.status = novo_status
    # ao reabrir, limpa o técnico para permitir nova atribuição
    if novo_status == Chamado.Status.ABERTO:
        chamado.tecnico_responsavel = None
    chamado.save()
    Movimentacao.objects.create(
        chamado=chamado,
        responsavel=responsavel,
        status_anterior=status_anterior,
        status_novo=novo_status,
        comentario=comentario,
    )
    return chamado


def atribuir_tecnico(chamado, tecnico, responsavel):
    """
    Atribui um técnico ao chamado e transiciona o status para em_andamento.
    chamado: instância de Chamado
    tecnico: instância de User com perfil técnico
    responsavel: usuário logado que executou a ação (admin)
    """
    status_anterior = chamado.status

    chamado.tecnico_responsavel = tecnico
    chamado.status = Chamado.Status.EM_ANDAMENTO
    chamado.save()

    Movimentacao.objects.create(
        chamado=chamado,
        responsavel=responsavel,
        status_anterior=status_anterior,
        status_novo=Chamado.Status.EM_ANDAMENTO,
        comentario=f'Chamado atribuído ao técnico {tecnico.username}.',
    )