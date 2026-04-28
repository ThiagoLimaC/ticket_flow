from django.contrib import admin
from .models import (
    EmpresaCliente,
    Categoria,
    Equipamento,
    Chamado,
    Movimentacao,
    PecaUtilizada,
)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    # colunas visíveis na listagem
    list_display = ('nome', 'sla_horas')

    # busca pelo nome da categoria
    search_fields = ('nome',)

@admin.register(EmpresaCliente)
class EmpresaClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'contato', 'telefone', 'criado_em')

    # busca por nome ou CNPJ
    search_fields = ('nome', 'cnpj')

    # filtra por data de cadastro
    list_filter = ('criado_em',)

    # data de cadastro não deve ser editada manualmente
    readonly_fields = ('criado_em',)

@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'modelo', 'numero_serie', 'cliente', 'localizacao')

    search_fields = ('tipo', 'modelo', 'numero_serie', 'cliente__nome')

    # filtra por cliente — útil quando há muitos equipamentos
    list_filter = ('cliente',)

    readonly_fields = ('criado_em',)

class MovimentacaoInline(admin.TabularInline):
    model = Movimentacao

    # campos visíveis dentro do inline
    fields = ('status_anterior', 'status_novo', 'responsavel', 'comentario', 'criado_em')

    # movimentações são imutáveis — nenhum campo editável
    readonly_fields = ('status_anterior', 'status_novo', 'responsavel', 'comentario', 'criado_em')

    # não permite adicionar nem deletar movimentações pelo Admin
    can_delete = False
    extra = 0


class PecaUtilizadaInline(admin.TabularInline):
    model = PecaUtilizada
    fields = ('descricao', 'quantidade', 'custo_unitario')

    # permite adicionar peças pelo form do chamado
    extra = 1

@admin.register(Chamado)
class ChamadoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'titulo',
        'cliente',
        'tecnico_responsavel',
        'categoria',
        'status',
        'prioridade',
        'sla_prazo',
        'esta_atrasado',
    )

    list_filter = ('status', 'prioridade', 'categoria', 'tecnico_responsavel')

    search_fields = ('titulo', 'cliente__nome', 'descricao')

    readonly_fields = ('data_abertura', 'sla_prazo', 'criado_em', 'atualizado_em')

    # inlines aparecem no final do form do chamado
    inlines = [MovimentacaoInline, PecaUtilizadaInline]

    # organiza os campos do form em seções
    fieldsets = (
        ('Identificação', {
            'fields': ('titulo', 'descricao', 'cliente', 'equipamento', 'categoria', 'prioridade')
        }),
        ('Atribuição e Status', {
            'fields': ('status', 'tecnico_responsavel', 'aberto_por')
        }),
        ('Datas e SLA', {
            'fields': ('data_abertura', 'sla_prazo', 'criado_em', 'atualizado_em')
        }),
        ('Atendimento', {
            'fields': ('diagnostico', 'solucao', 'tempo_gasto'),
            'classes': ('collapse',),  # seção recolhida por padrão
        }),
    )

@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ('chamado', 'status_anterior', 'status_novo', 'responsavel', 'criado_em')

    list_filter = ('status_novo', 'criado_em')

    search_fields = ('chamado__titulo', 'responsavel__username')

    # movimentações são completamente imutáveis
    readonly_fields = ('chamado', 'status_anterior', 'status_novo', 'responsavel', 'comentario', 'criado_em')

    # remove as ações de adicionar e deletar
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False