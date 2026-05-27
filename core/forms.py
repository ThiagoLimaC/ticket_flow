from django import forms
from .models import EmpresaCliente, Equipamento, Chamado, Categoria, PecaUtilizada
from .services import TRANSICOES_PERMITIDAS
from django.contrib.auth.models import User


class EmpresaClienteForm(forms.ModelForm):
    class Meta:
        model = EmpresaCliente
        # aberto_por e criado_em são preenchidos automaticamente
        fields = ['nome', 'cnpj', 'contato', 'telefone', 'endereco']
        widgets = {
            # adiciona classe Bootstrap em todos os campos
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000/0000-00'}),
            'contato': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class EquipamentoForm(forms.ModelForm):
    class Meta:
        model = Equipamento
        fields = ['cliente', 'tipo', 'modelo', 'numero_serie', 'localizacao']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_serie': forms.TextInput(attrs={'class': 'form-control'}),
            'localizacao': forms.TextInput(attrs={'class': 'form-control'}),
        }

class AbrirChamadoForm(forms.ModelForm):

    class Meta:
        model = Chamado
        fields = ['titulo', 'descricao', 'categoria', 'prioridade', 'equipamento']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'prioridade': forms.Select(attrs={'class': 'form-select'}),
            'equipamento': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, usuario, *args, **kwargs):
        # captura o usuário antes de chamar o super().__init__()
        # porque o super() já processa os kwargs e perderia o usuário
        super().__init__(*args, **kwargs)

        perfil = usuario.perfil

        # admin vê todos os equipamentos com indicação do cliente dono
        # cliente vê apenas os equipamentos da sua empresa
        if perfil.is_admin:
            self.fields['equipamento'].queryset = Equipamento.objects.select_related('cliente').all()
        elif perfil.empresa:
            self.fields['equipamento'].queryset = Equipamento.objects.filter(cliente=perfil.empresa)
        else:
            self.fields['equipamento'].queryset = Equipamento.objects.none()

        # também precisamos passar o cliente para o chamado
        # guardamos o usuário para uso no save da view
        self.usuario = usuario

class RegistrarAtendimentoForm(forms.ModelForm):
    class Meta:
        model = Chamado
        fields = ['diagnostico', 'solucao', 'tempo_gasto']
        widgets = {
            'diagnostico': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'solucao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tempo_gasto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 1.5'}),
        }
        labels = {
            'tempo_gasto': 'Tempo gasto (horas)',
        }


class PecaUtilizadaForm(forms.ModelForm):
    class Meta:
        model = PecaUtilizada
        fields = ['descricao', 'quantidade', 'custo_unitario']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'custo_unitario': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Opcional', 'step': '0.01'}),
        }
        labels = {
            'custo_unitario': 'Custo unitário (R$)',
        }


class MudarStatusForm(forms.Form):
    novo_status = forms.ChoiceField(
        label='Novo status',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    comentario = forms.CharField(
        label='Comentário',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Opcional'}),
    )

    def __init__(self, perfil, status_atual, *args, **kwargs):
        super().__init__(*args, **kwargs)
        opcoes = TRANSICOES_PERMITIDAS.get(status_atual, [])

        # técnico não pode fechar nem reabrir — essas transições são só do admin
        if perfil.is_tecnico:
            opcoes = [s for s in opcoes if s not in (Chamado.Status.FECHADO, Chamado.Status.ABERTO)]

        label_map = dict(Chamado.Status.choices)
        self.fields['novo_status'].choices = [(s, label_map[s]) for s in opcoes]


class AtribuirTecnicoForm(forms.Form):
    # Form simples, não ModelForm — porque não estamos salvando
    # um objeto novo, estamos atualizando um campo do Chamado
    tecnico = forms.ModelChoiceField(
        queryset=User.objects.filter(perfil__tipo='tecnico'),
        label='Técnico',
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='Selecione um técnico',
    )