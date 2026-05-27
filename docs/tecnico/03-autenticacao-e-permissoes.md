# Documentação Técnica — Parte 3: Autenticação e Controle de Permissões

Como o sistema de autenticação do Django foi estendido para suportar três tipos de usuário com restrições diferentes de acesso.

---

## 1. Autenticação nativa do Django

O TicketFlow usa o sistema de autenticação **nativo do Django** sem modificações — `django.contrib.auth`. Isso inclui:

- `User` — model de usuário com campos `username`, `password`, `is_staff`, `is_superuser`, etc.
- `login()` / `logout()` — funções para criar e encerrar sessões
- `@login_required` — decorator que redireciona para a tela de login se o usuário não estiver autenticado
- URLs prontas via `django.contrib.auth.urls` para login e logout

A tela de login é um template customizado que usa o `AuthenticationForm` padrão do Django. Não foi necessário reimplementar a autenticação.

---

## 2. O model `Perfil` — extensão do User

O Django não oferece, por padrão, uma forma de distinguir "admin de sistema", "técnico" e "cliente" dentro do `User`. A solução adotada é o padrão **Profile** — criar um model separado com relacionamento `OneToOneField`:

```python
# usuarios/models.py
class Perfil(models.Model):
    class Tipo(models.TextChoices):
        ADMIN   = 'admin',   'Administrador'
        TECNICO = 'tecnico', 'Técnico'
        CLIENTE = 'cliente', 'Cliente'

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil'
    )
    tipo    = models.CharField(max_length=10, choices=Tipo.choices, default=Tipo.CLIENTE)
    empresa = models.ForeignKey(EmpresaCliente, null=True, blank=True, ...)
```

**`OneToOneField`** garante que cada `User` tem no máximo um `Perfil` e cada `Perfil` pertence a exatamente um `User`. É implementado como uma FK com constraint `UNIQUE` no banco.

O `related_name='perfil'` permite acessar o perfil de qualquer usuário Django como `request.user.perfil` — uma única expressão, sem query explícita (o Django faz o JOIN automaticamente quando necessário).

---

## 3. Signal `post_save` — criação automática do Perfil

Toda vez que um `User` é criado, precisamos criar o `Perfil` correspondente. Usamos um **signal** do Django para isso:

```python
# usuarios/models.py
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def criar_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)
```

**Como funciona:**
- `@receiver(post_save, sender=User)` registra a função como listener do evento "depois de salvar um User"
- O Django chama esta função automaticamente após qualquer `User.save()`
- `created=True` apenas na primeira vez — edições posteriores do usuário não criam perfis duplicados

Isso garante que **todo usuário tem um perfil**, sem precisar lembrar de criá-lo manualmente. Não há ponto do código onde se cria um `User` sem que um `Perfil` seja gerado junto.

---

## 4. Properties do Perfil — verificação semântica de tipo

O model `Perfil` tem três `@property`s que tornam as checagens de tipo legíveis:

```python
@property
def is_admin(self): return self.tipo == self.Tipo.ADMIN

@property
def is_tecnico(self): return self.tipo == self.Tipo.TECNICO

@property
def is_cliente(self): return self.tipo == self.Tipo.CLIENTE
```

**Por que properties?** Sem elas, o código das views ficaria cheio de strings literais:

```python
# sem properties — frágil, se o valor mudar no choices tudo quebra
if request.user.perfil.tipo == 'tecnico':
    ...

# com properties — semântico e seguro
if request.user.perfil.is_tecnico:
    ...
```

As properties também são usadas diretamente nos templates:

```html
{% if request.user.perfil.is_admin %}
    <a href="{% url 'atribuir_tecnico' chamado.id %}">Atribuir Técnico</a>
{% endif %}
```

---

## 5. Decorator `@requer_perfil` — fábrica de decorators

Para restringir o acesso a views por tipo de perfil, implementamos um **decorator de ordem superior** (fábrica de decorators) no arquivo `usuarios/decorators.py`:

```python
from functools import wraps
from django.shortcuts import redirect

def requer_perfil(*tipos):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.perfil.tipo not in tipos:
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
```

**Uso:**
```python
@requer_perfil('admin')
def criar_cliente(request): ...

@requer_perfil('admin', 'tecnico')
def alguma_view_compartilhada(request): ...
```

**Por que `@wraps(view_func)`?** O decorator substitui a função original pela função `wrapper`. O `@wraps` copia os metadados da função original (`__name__`, `__doc__`) para o wrapper — necessário para que o Django consiga identificar e nomear a view corretamente no sistema de URLs.

**Por que uma fábrica em vez de um decorator simples?** Para tornar o decorator parametrizável. `@requer_perfil('admin')` e `@requer_perfil('admin', 'tecnico')` são o mesmo decorator chamado com argumentos diferentes. O nível extra de função (`def requer_perfil(*tipos)`) captura esses argumentos antes de retornar o decorator real.

---

## 6. Formulários com comportamento dinâmico

O `AbrirChamadoForm` filtra os equipamentos disponíveis com base em quem está logado. Para isso, o formulário recebe o usuário no `__init__`:

```python
class AbrirChamadoForm(forms.ModelForm):

    def __init__(self, usuario, *args, **kwargs):
        super().__init__(*args, **kwargs)  # super() ANTES de usar self.fields
        perfil = usuario.perfil

        if perfil.is_admin:
            self.fields['equipamento'].queryset = Equipamento.objects.select_related('cliente').all()
        elif perfil.empresa:
            self.fields['equipamento'].queryset = Equipamento.objects.filter(cliente=perfil.empresa)
        else:
            self.fields['equipamento'].queryset = Equipamento.objects.none()
```

**Como instanciar:**
```python
# GET — form vazio
form = AbrirChamadoForm(request.user)

# POST — form com dados
form = AbrirChamadoForm(request.user, request.POST)
```

O usuário é o **primeiro argumento posicional** extra, antes dos `*args` — por isso ele é passado diretamente, não como keyword argument.

---

## 7. `MudarStatusForm` — choices dinâmicos por perfil

O formulário de mudança de status calcula as opções disponíveis com base no status atual do chamado e no tipo de perfil do usuário:

```python
class MudarStatusForm(forms.Form):
    novo_status = forms.ChoiceField(...)
    comentario  = forms.CharField(required=False, ...)

    def __init__(self, perfil, status_atual, *args, **kwargs):
        super().__init__(*args, **kwargs)
        opcoes = TRANSICOES_PERMITIDAS.get(status_atual, [])

        # técnico não pode fechar nem reabrir
        if perfil.is_tecnico:
            opcoes = [s for s in opcoes if s not in (Chamado.Status.FECHADO, Chamado.Status.ABERTO)]

        label_map = dict(Chamado.Status.choices)
        self.fields['novo_status'].choices = [(s, label_map[s]) for s in opcoes]
```

O dicionário `TRANSICOES_PERMITIDAS` (definido em `services.py`) mapeia cada status para a lista de status para os quais ele pode transicionar:

```python
TRANSICOES_PERMITIDAS = {
    Chamado.Status.EM_ANDAMENTO: [Chamado.Status.AGUARDANDO, Chamado.Status.RESOLVIDO],
    Chamado.Status.AGUARDANDO:   [Chamado.Status.EM_ANDAMENTO, Chamado.Status.RESOLVIDO],
    Chamado.Status.RESOLVIDO:    [Chamado.Status.FECHADO, Chamado.Status.ABERTO],
}
```

**Decisão de design:** a validação das transições vive em `services.py` (não nas views nem nos forms), porque é lógica de negócio pura — independente do HTTP.

---

## 8. Checklist para a apresentação

Conceitos Django que o projeto demonstra e que vale estudar antes da apresentação:

- [ ] MVT: como request flui de `urls.py` → view → template
- [ ] ORM: `filter()`, `exclude()`, `get_or_404()`, `select_related()`
- [ ] Models: `TextChoices`, `ForeignKey` com `on_delete`, `OneToOneField`, `auto_now_add`
- [ ] `save()` sobrescrito e quando chamar `super().save()`
- [ ] `@property` em models e como o template acessa
- [ ] Signals: `post_save`, `@receiver`, parâmetro `created`
- [ ] `@login_required` vs decorator customizado (`@requer_perfil`)
- [ ] `functools.wraps` e por que é necessário em decorators
- [ ] ModelForm: `commit=False`, `instance=`, `fields`, `widgets`
- [ ] `__init__` customizado em forms para queryset dinâmico
- [ ] Messages framework: `messages.success()`, `messages.error()`, padrão PRG
- [ ] Template inheritance: `{% extends %}`, `{% block %}`, `{% url %}`
- [ ] `django-environ`: separação de configuração e código
