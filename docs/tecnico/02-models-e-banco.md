# Documentação Técnica — Parte 2: Models e Banco de Dados

Como o Django ORM foi utilizado no TicketFlow: relacionamentos, choices, validações automáticas e decisões de design do schema.

---

## 1. O ORM do Django

O Django vem com um **ORM (Object-Relational Mapper)** que permite trabalhar com o banco de dados usando classes e objetos Python — sem escrever SQL diretamente.

```python
# Python (Django ORM)
chamados = Chamado.objects.filter(status='aberto').order_by('-data_abertura')

# SQL equivalente gerado pelo ORM
# SELECT * FROM core_chamado WHERE status = 'aberto' ORDER BY data_abertura DESC;
```

As classes Python que mapeiam para tabelas do banco são chamadas de **models**. Cada atributo da classe vira uma coluna. O comando `python manage.py migrate` cria ou atualiza as tabelas no banco com base nesses models.

---

## 2. TextChoices — enumerações legíveis

Em vez de guardar strings mágicas no banco, usamos `TextChoices` para definir os valores válidos de um campo diretamente no model:

```python
class Chamado(models.Model):
    class Status(models.TextChoices):
        ABERTO       = 'aberto',       'Aberto'
        EM_ANDAMENTO = 'em_andamento', 'Em andamento'
        AGUARDANDO   = 'aguardando',   'Aguardando'
        RESOLVIDO    = 'resolvido',    'Resolvido'
        FECHADO      = 'fechado',      'Fechado'

    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.ABERTO,
    )
```

- **No banco**, o valor gravado é o código curto (`'aberto'`, `'em_andamento'`, etc.)
- **No template**, `chamado.get_status_display` retorna o rótulo legível (`'Em andamento'`)
- **No código**, comparamos usando a constante: `if chamado.status == Chamado.Status.ABERTO:` — sem strings soltas

O mesmo padrão é usado para `Prioridade` (`baixa`, `media`, `alta`, `critica`) e para o `Tipo` do `Perfil`.

---

## 3. ForeignKey e estratégias de deleção

Usamos `ForeignKey` para relacionamentos de N-para-1. A escolha do comportamento em caso de deleção do objeto pai é crítica:

```python
class Chamado(models.Model):
    cliente = models.ForeignKey(
        EmpresaCliente,
        on_delete=models.PROTECT,   # impede deletar cliente com chamados
    )
    tecnico_responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,  # se técnico for deletado, campo vira None
        null=True,
        blank=True,
    )
    aberto_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,   # não permite deletar usuário com chamados
    )
```

| Estratégia | Comportamento | Usado quando |
|---|---|---|
| `CASCADE` | Deleta os filhos junto com o pai | Movimentações e peças (sem sentido sem o chamado) |
| `PROTECT` | Lança erro — impede a deleção | Chamados vinculados a clientes/equipamentos |
| `SET_NULL` | Coloca `None` no campo (precisa de `null=True`) | Técnico de um chamado (pode sair da empresa) |

---

## 4. related_name — consultas reversas

O `related_name` define como acessar os objetos relacionados na direção inversa do FK:

```python
class Equipamento(models.Model):
    cliente = models.ForeignKey(
        EmpresaCliente,
        related_name='equipamentos'
    )
```

```python
# Sem related_name, seria: cliente.equipamento_set.all()
# Com related_name fica legível:
cliente.equipamentos.all()   # todos os equipamentos deste cliente
chamado.movimentacoes.all()  # todas as movimentações deste chamado
chamado.pecas.all()          # todas as peças deste chamado
```

---

## 5. auto_now_add vs auto_now vs default

Três formas de preencher automaticamente campos de data:

```python
data_abertura = models.DateTimeField(default=timezone.now)  # preenche na criação, mas pode ser sobrescrito
criado_em    = models.DateTimeField(auto_now_add=True)      # preenche na criação, readonly depois
atualizado_em = models.DateTimeField(auto_now=True)         # atualiza a cada save()
```

- `default=timezone.now` — usamos em `data_abertura` porque queremos permitir que o campo seja ajustado quando necessário
- `auto_now_add=True` — para campos que registram a criação e nunca mudam (ex: `criado_em` de qualquer model)
- `auto_now=True` — para rastrear a última modificação (ex: `atualizado_em` do `Chamado`)

---

## 6. Sobrescrita do método `save()`

Usamos a sobrescrita do `save()` do model para calcular automaticamente o prazo de SLA ao criar um chamado:

```python
class Chamado(models.Model):
    sla_prazo = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.sla_prazo and self.categoria_id:
            from datetime import timedelta
            self.sla_prazo = self.data_abertura + timedelta(hours=self.categoria.sla_horas)
        super().save(*args, **kwargs)
```

**Pontos importantes:**
- `if not self.sla_prazo` — garante que o prazo só é calculado uma vez; edições posteriores não recalculam
- `self.categoria_id` — verifica o ID (campo DB) em vez do objeto `self.categoria` para evitar uma query desnecessária
- `super().save(*args, **kwargs)` — **sempre** deve ser chamado no final para que o registro seja de fato salvo

---

## 7. Properties — lógica calculada no model

Uma `@property` Python permite que a view e o template acessem lógica calculada como se fosse um campo normal:

```python
class Chamado(models.Model):
    @property
    def esta_atrasado(self):
        if self.status in (self.Status.RESOLVIDO, self.Status.FECHADO):
            return False
        if self.sla_prazo is None:
            return False
        return timezone.now() > self.sla_prazo
```

No template:
```html
{% if chamado.esta_atrasado %}
    <span class="badge bg-danger">Atrasado</span>
{% endif %}
```

A propriedade não existe no banco — ela é calculada em memória toda vez que é acessada. Isso é adequado para lógica simples baseada em campos que já foram carregados.

---

## 8. default_permissions — controle de permissões no admin

O model `Movimentacao` é imutável por design: ninguém pode editar ou excluir um registro de movimentação. Para reforçar isso no Django Admin, usamos `default_permissions`:

```python
class Movimentacao(models.Model):
    class Meta:
        default_permissions = ('view',)  # apenas permissão de visualização
```

Por padrão, o Django cria 4 permissões para cada model: `add`, `change`, `delete`, `view`. Com `default_permissions = ('view',)`, apenas a permissão de leitura é criada — as demais não existem nem para superusuários, tornando a imutabilidade estrutural.

---

## 9. select_related — evitando N+1 queries

Ao acessar objetos relacionados dentro de um loop no template, o Django faz uma query por objeto. O `select_related` resolve isso com um JOIN:

```python
# sem select_related: 1 query para os equipamentos + 1 query por equipamento para pegar o cliente
Equipamento.objects.all()

# com select_related: 1 única query com JOIN
Equipamento.objects.select_related('cliente').all()
```

Usamos isso no formulário de abertura de chamado para que o `__str__` do `Equipamento` (que exibe o nome do cliente) não dispare queries extras.

---

## 10. Diagrama de relacionamentos

```
EmpresaCliente ──< Equipamento ──< Chamado >── Categoria
                                      │
                    User >────────────┤ (aberto_por)
                    User >────────────┤ (tecnico_responsavel)
                                      │
                                      ├──< Movimentacao >── User (responsavel)
                                      └──< PecaUtilizada
```

- `EmpresaCliente` tem muitos `Equipamento`s
- `Equipamento` tem muitos `Chamado`s
- `Chamado` tem uma `Categoria`, um `aberto_por` (User) e um `tecnico_responsavel` (User, opcional)
- `Chamado` tem muitas `Movimentacao`s e muitas `PecaUtilizada`s
