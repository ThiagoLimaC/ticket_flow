"""
Popula o banco com dados de teste para desenvolvimento.

Uso:
    python manage.py seed           # cria tudo, pula o que já existe
    python manage.py seed --reset   # apaga chamados/peças/movimentações antes de recriar
"""

from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import (
    Categoria,
    Chamado,
    EmpresaCliente,
    Equipamento,
    Movimentacao,
    PecaUtilizada,
)
from core.services import atribuir_tecnico, mudar_status


class Command(BaseCommand):
    help = 'Popula o banco com dados de teste para desenvolvimento.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Apaga chamados, peças e movimentações antes de recriar.',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self._reset()

        self.stdout.write('\n── Usuários ──────────────────────────────────')
        admin    = self._criar_usuario('admin',    'admin123', 'admin',   superuser=True)
        tecnico1 = self._criar_usuario('tecnico1', 'admin123', 'tecnico')
        tecnico2 = self._criar_usuario('tecnico2', 'admin123', 'tecnico')
        cliente1 = self._criar_usuario('cliente1', 'admin123', 'cliente')
        cliente2 = self._criar_usuario('cliente2', 'admin123', 'cliente')

        self.stdout.write('\n── Empresas clientes ─────────────────────────')
        empresa_a, _ = EmpresaCliente.objects.get_or_create(
            cnpj='12.345.678/0001-99',
            defaults={
                'nome': 'Empresa Alpha Ltda',
                'contato': 'Carlos Mendes',
                'telefone': '(11) 91234-5678',
                'endereco': 'Rua das Palmeiras, 200 — São Paulo/SP',
            },
        )
        self._log('EmpresaCliente', 'Empresa Alpha Ltda', _)

        empresa_b, _ = EmpresaCliente.objects.get_or_create(
            cnpj='98.765.432/0001-10',
            defaults={
                'nome': 'Beta Comércio S.A.',
                'contato': 'Ana Souza',
                'telefone': '(21) 98765-4321',
                'endereco': 'Av. Brasil, 1500 — Rio de Janeiro/RJ',
            },
        )
        self._log('EmpresaCliente', 'Beta Comércio S.A.', _)

        # vincula clientes às empresas
        self._vincular_empresa(cliente1, empresa_a)
        self._vincular_empresa(cliente2, empresa_b)

        self.stdout.write('\n── Categorias ────────────────────────────────')
        cat_hw, _ = Categoria.objects.get_or_create(nome='Hardware', defaults={'sla_horas': 8})
        self._log('Categoria', 'Hardware (SLA 8h)', _)

        cat_sw, _ = Categoria.objects.get_or_create(nome='Software', defaults={'sla_horas': 4})
        self._log('Categoria', 'Software (SLA 4h)', _)

        cat_rede, _ = Categoria.objects.get_or_create(nome='Rede', defaults={'sla_horas': 2})
        self._log('Categoria', 'Rede (SLA 2h)', _)

        self.stdout.write('\n── Equipamentos ──────────────────────────────')
        eq1, _ = Equipamento.objects.get_or_create(
            numero_serie='SN-001',
            defaults={'cliente': empresa_a, 'tipo': 'Servidor', 'modelo': 'Dell PowerEdge R740', 'localizacao': 'Sala de TI'},
        )
        self._log('Equipamento', 'Servidor Dell (Alpha)', _)

        eq2, _ = Equipamento.objects.get_or_create(
            numero_serie='SN-002',
            defaults={'cliente': empresa_a, 'tipo': 'Impressora', 'modelo': 'HP LaserJet Pro', 'localizacao': 'Recepção'},
        )
        self._log('Equipamento', 'Impressora HP (Alpha)', _)

        eq3, _ = Equipamento.objects.get_or_create(
            numero_serie='SN-003',
            defaults={'cliente': empresa_b, 'tipo': 'Switch', 'modelo': 'Cisco Catalyst 2960', 'localizacao': 'Rack CPD'},
        )
        self._log('Equipamento', 'Switch Cisco (Beta)', _)

        eq4, _ = Equipamento.objects.get_or_create(
            numero_serie='SN-004',
            defaults={'cliente': empresa_b, 'tipo': 'Desktop', 'modelo': 'Lenovo ThinkCentre', 'localizacao': 'Financeiro'},
        )
        self._log('Equipamento', 'Desktop Lenovo (Beta)', _)

        self.stdout.write('\n── Chamados ──────────────────────────────────')

        # Chamado 1 — Aberto, aguardando atribuição
        c1 = self._criar_chamado(
            titulo='Servidor não responde após queda de energia',
            descricao='Após o retorno de energia ontem às 18h, o servidor principal da sala de TI não inicializou corretamente. Serviços de backup e autenticação estão fora.',
            categoria=cat_hw,
            prioridade=Chamado.Prioridade.CRITICA,
            equipamento=eq1,
            aberto_por=cliente1,
        )

        # Chamado 2 — Em andamento (atribuído ao tecnico1)
        c2 = self._criar_chamado(
            titulo='Impressora da recepção não imprime',
            descricao='A impressora da recepção parou de imprimir após atualização de driver. Exibe erro "offline" no painel.',
            categoria=cat_hw,
            prioridade=Chamado.Prioridade.MEDIA,
            equipamento=eq2,
            aberto_por=cliente1,
        )
        if c2.status == Chamado.Status.ABERTO:
            atribuir_tecnico(c2, tecnico1, admin)
            c2.refresh_from_db()

        # Chamado 3 — Aguardando peça (atribuído ao tecnico1)
        c3 = self._criar_chamado(
            titulo='Switch com porta com defeito',
            descricao='Porta 12 do switch do CPD perdeu conectividade. Dois computadores do setor financeiro estão sem acesso à rede.',
            categoria=cat_rede,
            prioridade=Chamado.Prioridade.ALTA,
            equipamento=eq3,
            aberto_por=cliente2,
        )
        if c3.status == Chamado.Status.ABERTO:
            atribuir_tecnico(c3, tecnico1, admin)
            c3.refresh_from_db()
        if c3.status == Chamado.Status.EM_ANDAMENTO:
            mudar_status(c3, Chamado.Status.AGUARDANDO, tecnico1, 'Aguardando chegada da peça substituta. Prazo estimado: 3 dias.')
            c3.refresh_from_db()
            # adiciona peça
            PecaUtilizada.objects.get_or_create(
                chamado=c3,
                descricao='Módulo SFP Cisco GLC-SX-MMD',
                defaults={'quantidade': 1, 'custo_unitario': '420.00'},
            )

        # Chamado 4 — Resolvido, aguardando fechamento pelo admin
        c4 = self._criar_chamado(
            titulo='Desktop do financeiro travando frequentemente',
            descricao='Computador do setor financeiro trava a cada ~2 horas, especialmente ao usar o sistema de NF-e. Memória RAM suspeita.',
            categoria=cat_hw,
            prioridade=Chamado.Prioridade.MEDIA,
            equipamento=eq4,
            aberto_por=admin,
        )
        if c4.status == Chamado.Status.ABERTO:
            atribuir_tecnico(c4, tecnico2, admin)
            c4.refresh_from_db()
        if c4.status == Chamado.Status.EM_ANDAMENTO:
            # registra diagnóstico
            c4.diagnostico = 'Pente de memória RAM com defeito identificado via teste MemTest86.'
            c4.solucao = 'Substituição do pente defeituoso por módulo de 8GB DDR4.'
            c4.tempo_gasto = 2.5
            c4.save()
            PecaUtilizada.objects.get_or_create(
                chamado=c4,
                descricao='Memória RAM DDR4 8GB 2666MHz',
                defaults={'quantidade': 1, 'custo_unitario': '185.00'},
            )
            mudar_status(c4, Chamado.Status.RESOLVIDO, tecnico2, 'Problema resolvido após troca de memória. Máquina estável por 4h de teste.')
            c4.refresh_from_db()

        # Chamado 5 — Fechado
        c5 = self._criar_chamado(
            titulo='Configuração de VPN para acesso remoto',
            descricao='Preciso de acesso remoto seguro ao servidor para trabalhar de casa. Solicito configuração de VPN.',
            categoria=cat_rede,
            prioridade=Chamado.Prioridade.BAIXA,
            equipamento=eq3,
            aberto_por=cliente2,
        )
        if c5.status == Chamado.Status.ABERTO:
            atribuir_tecnico(c5, tecnico2, admin)
            c5.refresh_from_db()
        if c5.status == Chamado.Status.EM_ANDAMENTO:
            c5.diagnostico = 'Sem VPN configurada. Servidor com OpenVPN disponível.'
            c5.solucao = 'Instalação e configuração do OpenVPN com certificado gerado para o usuário.'
            c5.tempo_gasto = 1.0
            c5.save()
            mudar_status(c5, Chamado.Status.RESOLVIDO, tecnico2, 'VPN configurada e testada com sucesso.')
            c5.refresh_from_db()
        if c5.status == Chamado.Status.RESOLVIDO:
            mudar_status(c5, Chamado.Status.FECHADO, admin, 'Serviço concluído e validado pelo cliente.')
            c5.refresh_from_db()

        # Chamado 6 — Aberto com SLA já vencido (para testar o indicador visual)
        c6 = self._criar_chamado(
            titulo='Sistema de backup com falha silenciosa',
            descricao='O software de backup não está gerando logs de sucesso há 5 dias. Possível falha no job agendado.',
            categoria=cat_sw,
            prioridade=Chamado.Prioridade.ALTA,
            equipamento=eq1,
            aberto_por=admin,
            data_abertura=timezone.now() - timedelta(days=3),  # aberto há 3 dias — SLA de 4h já venceu
        )

        self.stdout.write('\n── Resumo ────────────────────────────────────')
        self.stdout.write(f'  Usuários:     admin, tecnico1, tecnico2, cliente1, cliente2  (senha: admin123)')
        self.stdout.write(f'  Empresas:     Empresa Alpha Ltda, Beta Comércio S.A.')
        self.stdout.write(f'  Categorias:   Hardware (8h), Software (4h), Rede (2h)')
        self.stdout.write(f'  Equipamentos: {Equipamento.objects.count()} cadastrados')
        self.stdout.write(f'  Chamados:     {Chamado.objects.count()} cadastrados')
        self.stdout.write(self.style.SUCCESS('\nBanco populado com sucesso. Acesse http://localhost:8080\n'))

    # ── helpers ───────────────────────────────────────────────────────────────

    def _reset(self):
        self.stdout.write(self.style.WARNING('Removendo chamados, movimentações e peças...'))
        PecaUtilizada.objects.all().delete()
        Movimentacao.objects.all().delete()
        Chamado.objects.all().delete()

    def _criar_usuario(self, username, senha, tipo, superuser=False):
        user, created = User.objects.get_or_create(username=username)
        user.set_password(senha)
        if superuser:
            user.is_superuser = True
            user.is_staff = True
        user.save()
        user.perfil.tipo = tipo
        user.perfil.save()
        self._log('Usuário', f'{username} ({tipo})', created)
        return user

    def _vincular_empresa(self, usuario, empresa):
        if usuario.perfil.empresa != empresa:
            usuario.perfil.empresa = empresa
            usuario.perfil.save()

    def _criar_chamado(self, titulo, descricao, categoria, prioridade, equipamento, aberto_por, data_abertura=None):
        existente = Chamado.objects.filter(titulo=titulo).first()
        if existente:
            self.stdout.write(f'  [existe]  Chamado: {titulo[:60]}')
            return existente

        chamado = Chamado(
            titulo=titulo,
            descricao=descricao,
            categoria=categoria,
            prioridade=prioridade,
            equipamento=equipamento,
            cliente=equipamento.cliente,
            aberto_por=aberto_por,
            status=Chamado.Status.ABERTO,
            data_abertura=data_abertura or timezone.now(),
        )
        chamado.save()
        Movimentacao.objects.create(
            chamado=chamado,
            responsavel=aberto_por,
            status_anterior=Chamado.Status.ABERTO,
            status_novo=Chamado.Status.ABERTO,
            comentario='Chamado aberto.',
        )
        self.stdout.write(f'  [criado]  Chamado: {titulo[:60]}')
        return chamado

    def _log(self, tipo, nome, created):
        status = '[criado]' if created else '[existe]'
        self.stdout.write(f'  {status}  {tipo}: {nome}')
