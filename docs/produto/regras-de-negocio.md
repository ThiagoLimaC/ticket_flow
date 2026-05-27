# Regras de Negócio — TicketFlow

Descrição completa do funcionamento do sistema do ponto de vista do produto.
Documento de referência para a equipe entender o que o sistema faz, quem pode fazer o quê e como os fluxos funcionam.

---

## 1. O que é o TicketFlow

O TicketFlow é um sistema web de controle de chamados de suporte técnico desenvolvido para a **TechFix Soluções**, uma empresa prestadora de serviços de manutenção de TI. A TechFix atende outras empresas (suas clientes) via contratos de suporte. O sistema substitui o controle feito por WhatsApp + planilha Excel.

O ciclo de atendimento é simples: um chamado é aberto, atribuído a um técnico, trabalhado, resolvido e fechado. Cada passo gera um registro de histórico imutável.

---

## 2. Perfis de usuário

O sistema tem três tipos de usuário. O tipo é definido pelo campo `tipo` no `Perfil` vinculado a cada usuário cadastrado.

### Admin
Representa o gestor da TechFix. Tem acesso total ao sistema.

- Cadastra e edita clientes (EmpresaCliente) e seus equipamentos
- Abre chamados em nome de qualquer cliente
- Atribui técnicos a chamados abertos
- Visualiza todos os chamados do sistema
- Fecha chamados resolvidos (`Resolvido → Fechado`)
- Reabre chamados para revisão (`Resolvido → Aberto`)
- Acessa o painel administrativo do Django (`/admin/`)

### Técnico
Representa um técnico de campo da TechFix.

- Visualiza apenas os chamados atribuídos a ele
- Altera o status dos seus chamados entre: `Em andamento`, `Aguardando` e `Resolvido`
- Registra diagnóstico, solução e tempo gasto no chamado
- Adiciona peças utilizadas durante o atendimento
- **Não pode** abrir chamados, atribuir técnicos, fechar ou reabrir chamados

### Cliente
Representa um usuário de uma empresa cliente da TechFix.

- Abre chamados para os equipamentos da sua empresa
- Acompanha o status dos seus próprios chamados
- **Não pode** ver chamados de outras empresas, alterar status ou registrar atendimento

> Todo usuário recém-criado recebe automaticamente o perfil `Cliente` por padrão. O admin muda o tipo via painel de administração.

---

## 3. Clientes e Equipamentos

**EmpresaCliente** representa as empresas que contratam os serviços da TechFix. Cada empresa tem nome, CNPJ (único), contato, telefone e endereço.

**Equipamento** representa um ativo de TI pertencente a uma empresa cliente. Um equipamento tem tipo (ex: Servidor), modelo, número de série e localização física. Um equipamento pertence a exatamente uma empresa e não pode ser transferido.

Todo chamado está vinculado a um equipamento — e por consequência a um cliente. Ao abrir um chamado, o sistema identifica automaticamente o cliente pela empresa dona do equipamento selecionado.

O **Cliente** só enxerga equipamentos da sua própria empresa ao abrir um chamado. Se a empresa do cliente não tiver equipamentos cadastrados, o admin precisa cadastrá-los antes.

---

## 4. Ciclo de vida de um chamado

### 4.1 Abertura

Um chamado pode ser aberto pelo **Admin** ou pelo **Cliente**. O **Técnico não pode abrir chamados**.

Ao abrir, o formulário coleta:
- **Título** — descrição curta do problema
- **Descrição** — detalhamento do problema
- **Categoria** — tipo de problema (ex: Hardware, Software, Rede); define o SLA
- **Prioridade** — Baixa, Média, Alta ou Crítica
- **Equipamento** — o ativo que apresenta o problema

O sistema preenche automaticamente:
- Status inicial: `Aberto`
- Data de abertura: momento atual
- Prazo de SLA: data de abertura + horas da categoria
- Primeira movimentação: `Aberto → Aberto — Chamado aberto.`

### 4.2 Atribuição de técnico

Apenas o **Admin** pode atribuir um técnico. Um chamado `Aberto` sem técnico apresenta o botão **Atribuir Técnico** para o admin.

Ao atribuir:
- O campo `tecnico_responsavel` do chamado é preenchido
- O status muda automaticamente de `Aberto` para `Em andamento`
- Uma movimentação é registrada: `Aberto → Em andamento — Chamado atribuído ao técnico [nome].`

Um chamado já com técnico atribuído não pode ser reatribuído no MVP. Para atribuir outro técnico, o admin deve reabrir o chamado (o que desvincula o técnico automaticamente).

### 4.3 Fluxo de status

```
Aberto
  └──► Em andamento ──► Aguardando ──► Resolvido ──► Fechado
              └───────────────────────► Resolvido ──► Fechado
                                              └──► Aberto (admin reabre)
```

**Transições válidas por perfil:**

| Status atual | Técnico pode ir para | Admin pode ir para |
|---|---|---|
| Em andamento | Aguardando, Resolvido | Aguardando, Resolvido |
| Aguardando | Em andamento, Resolvido | Em andamento, Resolvido |
| Resolvido | — | Fechado, Aberto |
| Fechado | — | — |
| Aberto | — | — |

> O status `Aberto` não tem transições disponíveis via card de status — ele só sai de Aberto via atribuição de técnico (que move para Em andamento) ou via reabertura pelo admin.

**Ao reabrir um chamado (Resolvido → Aberto):**
- O técnico responsável é desvinculado automaticamente
- O botão Atribuir Técnico reaparece para o admin fazer nova atribuição

**Chamado Fechado é imutável:** nenhum campo pode ser alterado, nenhuma transição é permitida.

### 4.4 Registro de atendimento

O técnico pode registrar o atendimento em chamados com status `Em andamento` ou `Aguardando`. Isso inclui:

- **Diagnóstico** — o que foi identificado como causa do problema
- **Solução** — o que foi feito para resolver
- **Tempo gasto** — horas decimais (ex: 1.5 = 1h30min)

O registro de atendimento não muda o status do chamado — é uma atualização dos campos informativos. O técnico salva o diagnóstico independente de quando vai resolver.

### 4.5 Peças utilizadas

Durante um chamado ativo (`Em andamento` ou `Aguardando`), o técnico pode registrar peças consumidas. Cada peça tem:

- **Descrição** — nome da peça
- **Quantidade** — número de unidades utilizadas
- **Custo unitário** — valor opcional em reais

Não há controle de estoque — as peças são apenas informativas para fins de registro e eventual cobrança. Um chamado pode ter zero ou mais peças.

---

## 5. SLA (Acordo de Nível de Serviço)

Cada **Categoria** tem um prazo configurado em horas (`sla_horas`). Ao abrir um chamado, o sistema calcula o prazo automaticamente:

```
sla_prazo = data_abertura + categoria.sla_horas
```

Uma vez calculado, o `sla_prazo` nunca é recalculado — mesmo que o chamado seja editado.

**Um chamado está "Atrasado" quando:**
- O momento atual já passou do `sla_prazo`
- **E** o chamado ainda não está nos status `Resolvido` ou `Fechado`

Chamados resolvidos ou fechados não são considerados atrasados independentemente do prazo. O atraso é visual — não há bloqueio de ações por SLA vencido.

**Como aparece na interface:**
- No detalhe do chamado: badge `No prazo` (verde) ou `Atrasado` (vermelho) com data/hora do prazo
- No dashboard: badge por chamado na coluna SLA + card contador de chamados atrasados + linha vermelha (`table-danger`) para chamados com prazo vencido

---

## 6. Movimentações (histórico imutável)

Toda ação que muda o status de um chamado gera automaticamente uma **Movimentação**. Movimentações nunca são editadas ou excluídas — são o registro oficial do que aconteceu com o chamado.

Cada movimentação registra:
- Data e hora exata
- Usuário responsável pela ação
- Status anterior e status novo
- Comentário opcional (preenchido pelo técnico ou admin)

**Movimentações geradas automaticamente:**
- Abertura do chamado: `Aberto → Aberto — Chamado aberto.`
- Atribuição de técnico: `Aberto → Em andamento — Chamado atribuído ao técnico [nome].`
- Qualquer mudança de status via card "Alterar Status"

O histórico completo aparece no detalhe do chamado em ordem cronológica.

---

## 7. Tabela de permissões completa

| Ação | Admin | Técnico | Cliente |
|---|:---:|:---:|:---:|
| Abrir chamado | ✅ | ❌ | ✅ |
| Ver todos os chamados | ✅ | ❌ (só os seus) | ❌ (só os seus) |
| Atribuir técnico | ✅ | ❌ | ❌ |
| Alterar status (Em andamento/Aguardando/Resolvido) | ✅ | ✅ (só os seus) | ❌ |
| Fechar chamado (Resolvido → Fechado) | ✅ | ❌ | ❌ |
| Reabrir chamado (Resolvido → Aberto) | ✅ | ❌ | ❌ |
| Registrar diagnóstico e solução | ✅ | ✅ (só os seus, status ativo) | ❌ |
| Adicionar peças utilizadas | ✅ | ✅ (só os seus, status ativo) | ❌ |
| Cadastrar/editar clientes e equipamentos | ✅ | ❌ | ❌ |
| Acessar painel admin Django | ✅ | ❌ | ❌ |

> **Status ativo** = `Em andamento` ou `Aguardando`. Chamados `Abertos`, `Resolvidos` e `Fechados` não permitem registro de atendimento.
