# Guia — Seed: Populando o Banco para Testes

## O que é

O comando `seed` é um atalho para popular o banco com dados realistas de teste.
Ele cria usuários, empresas, equipamentos, categorias e chamados em vários estados —
sem precisar cadastrar nada manualmente nem usar o shell do Python.

---

## Pré-requisitos

Banco rodando e migrations aplicadas. Se ainda não fez isso:

```bash
docker compose up -d postgres_ticketFlow
source .venv/bin/activate
python manage.py migrate
```

---

## Uso básico

```bash
python manage.py seed
```

Cria tudo que ainda não existe. Pode rodar várias vezes sem problema — o que já existir é ignorado.

---

## Resetar os chamados e começar do zero

```bash
python manage.py seed --reset
```

Apaga todos os chamados, movimentações e peças antes de recriar. Útil quando o banco acumulou dados de testes anteriores e você quer um estado limpo e previsível.

> Usuários, empresas, categorias e equipamentos **não são apagados** pelo `--reset` — só os chamados e seus registros relacionados.

---

## O que é criado

### Usuários

| Usuário | Senha | Perfil | Empresa vinculada |
|---|---|---|---|
| `admin` | `admin123` | Administrador | — |
| `tecnico1` | `admin123` | Técnico | — |
| `tecnico2` | `admin123` | Técnico | — |
| `cliente1` | `admin123` | Cliente | Empresa Alpha Ltda |
| `cliente2` | `admin123` | Cliente | Beta Comércio S.A. |

### Empresas e equipamentos

| Empresa | Equipamentos |
|---|---|
| Empresa Alpha Ltda | Servidor Dell PowerEdge (Sala de TI), Impressora HP LaserJet (Recepção) |
| Beta Comércio S.A. | Switch Cisco Catalyst (Rack CPD), Desktop Lenovo ThinkCentre (Financeiro) |

### Categorias

| Categoria | SLA |
|---|---|
| Hardware | 8 horas |
| Software | 4 horas |
| Rede | 2 horas |

### Chamados

Seis chamados são criados, um em cada estado relevante para testar o sistema:

| # | Título resumido | Status | Técnico | Observação |
|---|---|---|---|---|
| 1 | Servidor não responde após queda de energia | **Aberto** | — | Aguardando atribuição |
| 2 | Impressora da recepção não imprime | **Em andamento** | tecnico1 | Recém atribuído |
| 3 | Switch com porta com defeito | **Aguardando** | tecnico1 | Tem peça registrada |
| 4 | Desktop do financeiro travando | **Resolvido** | tecnico2 | Tem diagnóstico e peça |
| 5 | Configuração de VPN para acesso remoto | **Fechado** | tecnico2 | Ciclo completo encerrado |
| 6 | Sistema de backup com falha silenciosa | **Aberto** | — | **SLA vencido** — testa o indicador de atraso |

---

## Fluxos que ficam prontos para testar imediatamente

Após rodar o seed, você pode testar os principais fluxos sem nenhum cadastro manual:

- **Atribuição de técnico** — chamado #1 está Aberto sem técnico; entre como `admin` e atribua
- **Mudança de status** — chamado #2 está Em andamento; entre como `tecnico1` e mova para Aguardando ou Resolvido
- **Registro de diagnóstico/peças** — chamado #3 está Aguardando; entre como `tecnico1` e edite o atendimento
- **Fechar chamado** — chamado #4 está Resolvido; entre como `admin` e feche
- **Indicador de SLA vencido** — chamado #6 aparece com badge vermelho "Atrasado" e linha destacada no dashboard
- **Isolamento por perfil** — `cliente1` só vê chamados 1, 2, 3 e 6 (empresa Alpha); `tecnico1` só vê 2 e 3

---

## Rodando o servidor após o seed

```bash
python manage.py runserver 8080
```

Acesse `http://localhost:8080` e faça login com qualquer um dos usuários da tabela acima.
