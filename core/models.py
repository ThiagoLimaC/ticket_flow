from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class EmpresaCliente(models.Model):
    nome = models.CharField(max_length=200)

    cnpj = models.CharField(max_length=18, unique=True)

    contato = models.CharField(max_length=100)

    telefone = models.CharField(max_length=20, blank=True)

    endereco = models.TextField(blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Empresa Cliente'
        verbose_name_plural = 'Empresas Clientes'
        ordering = ['nome']

    def __str__(self):
        return self.nome

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    sla_horas = models.PositiveIntegerField(default=24)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome} (SLA: {self.sla_horas}h)'

class Equipamento(models.Model):
    cliente = models.ForeignKey(
        EmpresaCliente,
        on_delete=models.CASCADE,
        related_name='equipamentos'
    )

    tipo = models.CharField(max_length=100)      
    modelo = models.CharField(max_length=100)    
    numero_serie = models.CharField(max_length=100, blank=True)
    localizacao = models.CharField(max_length=200, blank=True)  

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Equipamento'
        verbose_name_plural = 'Equipamentos'
        ordering = ['cliente', 'tipo']

    def __str__(self):
        return f'{self.tipo} — {self.modelo} ({self.cliente.nome})' 

class Chamado(models.Model):

    class Status(models.TextChoices):
        ABERTO = 'aberto', 'Aberto'
        EM_ANDAMENTO = 'em_andamento', 'Em andamento'
        AGUARDANDO = 'aguardando', 'Aguardando'
        RESOLVIDO = 'resolvido', 'Resolvido'
        FECHADO = 'fechado', 'Fechado'

    class Prioridade(models.TextChoices):
        BAIXA = 'baixa', 'Baixa'
        MEDIA = 'media', 'Média'
        ALTA = 'alta', 'Alta'
        CRITICA = 'critica', 'Crítica'

    cliente = models.ForeignKey(
        EmpresaCliente,
        on_delete=models.PROTECT,   # PROTECT: não deixa deletar cliente com chamados
        related_name='chamados'
    )
    equipamento = models.ForeignKey(
        Equipamento,
        on_delete=models.PROTECT,
        related_name='chamados'
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='chamados'
    )
    tecnico_responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chamados_atribuidos'
    )
    aberto_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='chamados_abertos'
    )

    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    prioridade = models.CharField(
        max_length=10,
        choices=Prioridade.choices,
        default=Prioridade.MEDIA
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.ABERTO
    )

    data_abertura = models.DateTimeField(default=timezone.now)
    sla_prazo = models.DateTimeField(null=True, blank=True)

    diagnostico = models.TextField(blank=True)
    solucao = models.TextField(blank=True)
    tempo_gasto = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Chamado'
        verbose_name_plural = 'Chamados'
        ordering = ['-data_abertura']

    def save(self, *args, **kwargs):
        # calcula sla_prazo automaticamente na primeira vez que o chamado é salvo
        # se já existe sla_prazo, não recalcula — evita alterar o prazo original
        if not self.sla_prazo and self.categoria_id:
            from datetime import timedelta
            self.sla_prazo = self.data_abertura + timedelta(hours=self.categoria.sla_horas)
        super().save(*args, **kwargs)

    @property
    def esta_atrasado(self):
        # chamado está atrasado quando passou do prazo e ainda não foi resolvido/fechado
        if self.status in (self.Status.RESOLVIDO, self.Status.FECHADO):
            return False
        if self.sla_prazo is None:
            return False
        return timezone.now() > self.sla_prazo

    def __str__(self):
        return f'#{self.pk} — {self.titulo} ({self.get_status_display()})'

class Movimentacao(models.Model):
    chamado = models.ForeignKey(
        Chamado,
        on_delete=models.CASCADE,
        related_name='movimentacoes'
    )
    responsavel = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='movimentacoes'
    )

    status_anterior = models.CharField(max_length=15, choices=Chamado.Status.choices)
    status_novo = models.CharField(max_length=15, choices=Chamado.Status.choices)
    comentario = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Movimentação'
        verbose_name_plural = 'Movimentações'
        ordering = ['criado_em']
        # movimentações são imutáveis — sem permissão de alteração no admin
        default_permissions = ('view',)

    def __str__(self):
        return f'#{self.chamado.pk} — {self.status_anterior} → {self.status_novo}'


class PecaUtilizada(models.Model):
    chamado = models.ForeignKey(
        Chamado,
        on_delete=models.CASCADE,
        related_name='pecas'
    )
    descricao = models.CharField(max_length=200)
    quantidade = models.PositiveIntegerField(default=1)

    custo_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Peça Utilizada'
        verbose_name_plural = 'Peças Utilizadas'

    def __str__(self):
        return f'{self.descricao} (x{self.quantidade})'