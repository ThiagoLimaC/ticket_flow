from .models import Chamado, Movimentacao


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