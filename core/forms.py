from django import forms
from .models import EmpresaCliente, Equipamento


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