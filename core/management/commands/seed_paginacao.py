"""
Insere 25 chamados extras para testar a paginação.

Requer que o banco já tenha sido populado com `python manage.py seed`.

Uso:
    python manage.py seed_paginacao
"""

from datetime import timedelta
import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Categoria, Chamado, EmpresaCliente, Equipamento, Movimentacao

TITULOS = [
    ('Computador lento ao inicializar', 'hw'),
    ('Falha ao conectar à VPN corporativa', 'rede'),
    ('Erro 500 no sistema de NF-e', 'sw'),
    ('Monitor sem sinal após reinicialização', 'hw'),
    ('Wi-Fi instável no andar superior', 'rede'),
    ('Antivírus não atualiza as definições', 'sw'),
    ('Impressora imprimindo com falhas', 'hw'),
    ('Usuário sem acesso ao sistema ERP', 'sw'),
    ('Cabo de rede com mau contato', 'rede'),
    ('HD com erros de leitura detectados', 'hw'),
    ('Licença do Office expirada', 'sw'),
    ('Switch secundário sem energia', 'hw'),
    ('Backup diário não concluiu ontem', 'sw'),
    ('Mouse e teclado não respondem', 'hw'),
    ('Servidor de e-mail rejeitando conexões', 'rede'),
    ('Banco de dados com alto uso de CPU', 'sw'),
    ('Nobreak emitindo alarme contínuo', 'hw'),
    ('Roteador reiniciando sozinho', 'rede'),
    ('Sistema de ponto eletrônico offline', 'sw'),
    ('Webcam não reconhecida após update', 'hw'),
    ('DNS interno resolvendo incorretamente', 'rede'),
    ('Relatório financeiro com dados errados', 'sw'),
    ('Placa de rede queimada', 'hw'),
    ('Certificado SSL do portal vencido', 'rede'),
    ('Falha no serviço de impressão remota', 'sw'),
]

DESCRICOES = {
    'hw': 'Equipamento apresenta comportamento anormal. Usuário relatou o problema durante o expediente. Necessário diagnóstico presencial.',
    'sw': 'Sistema ou aplicação apresentando erro. Usuário afetado não consegue concluir as tarefas. Log de erro disponível para análise.',
    'rede': 'Falha de conectividade identificada. Outros dispositivos na mesma rede não estão sendo afetados. Suspeita de problema pontual.',
}

STATUS_OPCOES = [
    Chamado.Status.ABERTO,
    Chamado.Status.ABERTO,
    Chamado.Status.ABERTO,
    Chamado.Status.EM_ANDAMENTO,
    Chamado.Status.EM_ANDAMENTO,
    Chamado.Status.AGUARDANDO,
    Chamado.Status.RESOLVIDO,
    Chamado.Status.FECHADO,
]

PRIORIDADES = [
    Chamado.Prioridade.BAIXA,
    Chamado.Prioridade.MEDIA,
    Chamado.Prioridade.MEDIA,
    Chamado.Prioridade.ALTA,
    Chamado.Prioridade.CRITICA,
]

TAG_LEGADO = '[seed_paginacao]'

TITULOS_PLAIN = [titulo for titulo, _ in TITULOS]


class Command(BaseCommand):
    help = 'Insere 25 chamados extras para testar paginação.'

    def handle(self, *args, **options):
        titulos_para_remover = TITULOS_PLAIN + [f'{TAG_LEGADO} {t}' for t in TITULOS_PLAIN]
        removidos, _ = Chamado.objects.filter(titulo__in=titulos_para_remover).delete()
        if removidos:
            self.stdout.write(self.style.WARNING(f'Removidos {removidos} chamado(s) de teste de paginação.'))

        try:
            admin    = User.objects.get(username='admin')
            tecnico1 = User.objects.get(username='tecnico1')
            tecnico2 = User.objects.get(username='tecnico2')
        except User.DoesNotExist:
            raise SystemExit(
                self.style.ERROR('Usuários não encontrados. Rode `python manage.py seed` primeiro.')
            )

        categorias = {
            'hw':   Categoria.objects.filter(nome='Hardware').first(),
            'sw':   Categoria.objects.filter(nome='Software').first(),
            'rede': Categoria.objects.filter(nome='Rede').first(),
        }
        if not all(categorias.values()):
            raise SystemExit(
                self.style.ERROR('Categorias não encontradas. Rode `python manage.py seed` primeiro.')
            )

        equipamentos = list(Equipamento.objects.all())
        if not equipamentos:
            raise SystemExit(
                self.style.ERROR('Equipamentos não encontrados. Rode `python manage.py seed` primeiro.')
            )

        tecnicos = [tecnico1, tecnico2]
        abridores = [admin, tecnico1, tecnico2]

        criados = 0
        for i, (titulo, cat_key) in enumerate(TITULOS):
            eq = equipamentos[i % len(equipamentos)]
            status = STATUS_OPCOES[i % len(STATUS_OPCOES)]
            prioridade = PRIORIDADES[i % len(PRIORIDADES)]
            aberto_por = abridores[i % len(abridores)]
            dias_atras = (i % 10) + 1
            data_abertura = timezone.now() - timedelta(days=dias_atras, hours=i % 8)

            chamado = Chamado(
                titulo=titulo,
                descricao=DESCRICOES[cat_key],
                categoria=categorias[cat_key],
                prioridade=prioridade,
                equipamento=eq,
                cliente=eq.cliente,
                aberto_por=aberto_por,
                status=status,
                data_abertura=data_abertura,
            )
            chamado.save()

            Movimentacao.objects.create(
                chamado=chamado,
                responsavel=aberto_por,
                status_anterior=Chamado.Status.ABERTO,
                status_novo=Chamado.Status.ABERTO,
                comentario='Chamado aberto.',
            )

            if status in (Chamado.Status.EM_ANDAMENTO, Chamado.Status.AGUARDANDO,
                          Chamado.Status.RESOLVIDO, Chamado.Status.FECHADO):
                tecnico = tecnicos[i % len(tecnicos)]
                chamado.tecnico_responsavel = tecnico
                chamado.status = Chamado.Status.EM_ANDAMENTO
                chamado.save()
                Movimentacao.objects.create(
                    chamado=chamado,
                    responsavel=admin,
                    status_anterior=Chamado.Status.ABERTO,
                    status_novo=Chamado.Status.EM_ANDAMENTO,
                    comentario=f'Atribuído ao {tecnico.username}.',
                )

            if status in (Chamado.Status.AGUARDANDO, Chamado.Status.RESOLVIDO, Chamado.Status.FECHADO):
                chamado.status = Chamado.Status.AGUARDANDO
                chamado.save()
                Movimentacao.objects.create(
                    chamado=chamado,
                    responsavel=tecnicos[i % len(tecnicos)],
                    status_anterior=Chamado.Status.EM_ANDAMENTO,
                    status_novo=Chamado.Status.AGUARDANDO,
                    comentario='Aguardando peça ou aprovação do cliente.',
                )

            if status in (Chamado.Status.RESOLVIDO, Chamado.Status.FECHADO):
                chamado.diagnostico = 'Problema identificado e diagnosticado pelo técnico.'
                chamado.solucao = 'Solução aplicada com sucesso após análise técnica.'
                chamado.tempo_gasto = round(1.0 + (i % 5) * 0.5, 1)
                chamado.status = Chamado.Status.RESOLVIDO
                chamado.save()
                Movimentacao.objects.create(
                    chamado=chamado,
                    responsavel=tecnicos[i % len(tecnicos)],
                    status_anterior=Chamado.Status.AGUARDANDO,
                    status_novo=Chamado.Status.RESOLVIDO,
                    comentario='Chamado resolvido.',
                )

            if status == Chamado.Status.FECHADO:
                chamado.status = Chamado.Status.FECHADO
                chamado.save()
                Movimentacao.objects.create(
                    chamado=chamado,
                    responsavel=admin,
                    status_anterior=Chamado.Status.RESOLVIDO,
                    status_novo=Chamado.Status.FECHADO,
                    comentario='Serviço validado e chamado encerrado.',
                )

            self.stdout.write(f'  [criado]  {titulo[:70]}  [{status}]')
            criados += 1

        total = Chamado.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f'\n{criados} chamado(s) criado(s). Total no banco: {total} chamados.\n'
        ))
