from django import forms
from .models import EmpresaCliente, Equipamento, Chamado, Categoria


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
        else:
            # filtra equipamentos pelo usuário logado como aberto_por
            # assume que o User cliente está vinculado a uma EmpresaCliente via chamados
            # no MVP: admin cadastra o cliente e associa o User manualmente
            self.fields['equipamento'].queryset = Equipamento.objects.filter(
                cliente__chamados__aberto_por=usuario
            ).distinct()

        # também precisamos passar o cliente para o chamado
        # guardamos o usuário para uso no save da view
        self.usuario = usuario