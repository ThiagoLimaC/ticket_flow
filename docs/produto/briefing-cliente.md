Briefing do Cliente — TechFix Soluções

    Documento gerado na fase de levantamento de requisitos.
    Simula a entrevista inicial com o cliente fictício do projeto TicketFlow.

1. Identificação do cliente
Campo 	Informação
Empresa 	TechFix Soluções
Segmento 	Suporte técnico e manutenção de TI
Porte 	Pequena empresa — 8 técnicos, 1 gestor
Público atendido 	Pequenas e médias empresas com contrato de suporte
Controle atual 	WhatsApp + planilha Excel
2. Contexto do negócio

A TechFix presta serviços de suporte técnico e manutenção corretiva/preventiva de equipamentos de TI para empresas clientes via contrato mensal. Os técnicos atendem chamados presencialmente ou de forma remota.

Hoje o fluxo de trabalho é: 1. Cliente entra em contato via WhatsApp 2. Gestor anota em planilha e encaminha para um técnico via mensagem 3. Técnico resolve e informa o gestor informalmente 4. Gestor atualiza a planilha manualmente

Esse processo gera perda de informação, falta de rastreabilidade e dificuldade de cobrança.
3. Dores relatadas pelo cliente

    Frases coletadas durante a entrevista de levantamento de requisitos.

Visibilidade:

    "Não sei quantos chamados estão abertos agora nem quem está atendendo o quê."

Histórico:

    "Quando um técnico sai de férias, o substituto não sabe nada do histórico do cliente."

Controle financeiro:

    "Não consigo cobrar direito porque não sei quanto tempo cada serviço levou nem quais peças foram usadas."

Prazo:

    "Já perdi cliente por esquecer de retornar um chamado. Não tenho nenhum controle de prazo."

Relatórios:

    "Quero saber quais tipos de problema aparecem mais, pra poder oferecer contratos preventivos."

4. Requisitos funcionais levantados
RF01 — Gestão de clientes e equipamentos

    Cadastrar empresas clientes com CNPJ, contato e endereço
    Associar equipamentos a cada cliente (tipo, modelo, número de série, localização)

RF02 — Abertura de chamados

    Cliente ou admin pode abrir um chamado
    Chamado deve ter: título, descrição, categoria, prioridade e equipamento relacionado
    Ao abrir, o sistema registra data/hora automaticamente

RF03 — Atribuição de técnico

    Admin atribui um técnico responsável ao chamado
    Técnico recebe o chamado com status "Em andamento"

RF04 — Fluxo de status

    Chamado percorre os estados: Aberto → Em andamento → Aguardando → Resolvido → Fechado
    Cada mudança de status gera um registro de movimentação com data, responsável e comentário

RF05 — Registro de atendimento

    Técnico registra diagnóstico, solução aplicada, peças utilizadas (descrição, quantidade, custo) e tempo gasto

RF06 — SLA por categoria

    Cada categoria de chamado tem um prazo em horas definido pelo admin
    Sistema indica visualmente se o chamado está dentro ou fora do SLA

RF07 — Painel administrativo

    Admin visualiza todos os chamados abertos, em andamento e atrasados
    Filtros por técnico, cliente, categoria e status

RF08 — Histórico por cliente

    Listagem completa de chamados anteriores de um cliente
    Inclui diagnóstico, solução e peças de cada atendimento

RF09 — Perfis de acesso

    Admin: acesso total — gerencia clientes, técnicos, chamados e configurações
    Técnico: visualiza chamados atribuídos, atualiza status e registra atendimento
    Cliente: abre chamados e acompanha o status dos seus próprios chamados

5. Requisitos não funcionais
ID 	Requisito
RNF01 	Sistema web acessível via navegador, sem necessidade de app
RNF02 	Autenticação obrigatória para todos os perfis
RNF03 	Interface responsiva para uso em tablet e desktop
RNF04 	Dados armazenados em banco relacional (SQLite no desenvolvimento, PostgreSQL em produção)
RNF05 	Código versionado em Git com padrão de commits definido
6. O que está fora do escopo (v1)

    Notificações por e-mail ou SMS
    Aplicativo mobile
    Integração com sistemas de cobrança ou ERP
    Chat em tempo real entre técnico e cliente
    Assinatura digital de OS
    Geolocalização de técnicos

7. Critérios de aceite do MVP

O sistema será considerado entregue quando:

    [ ] Admin consegue cadastrar clientes, equipamentos e técnicos
    [ ] Cliente consegue abrir um chamado e acompanhar o status
    [ ] Admin consegue atribuir chamado a um técnico
    [ ] Técnico consegue registrar diagnóstico, peças e resolução
    [ ] Sistema exibe indicação visual de chamados fora do SLA
    [ ] Admin visualiza painel com chamados abertos e atrasados
    [ ] Histórico completo de chamados por cliente está acessível
    [ ] Script ETL gera relatório com os principais indicadores

8. Cronograma estimado
Semana 	Entrega
1 	Setup do projeto, models, migrations, admin Django
2 	Autenticação, perfis, CRUD de clientes e equipamentos
3 	Fluxo de chamados — abertura, atribuição, status
4 	Registro de atendimento, SLA, painel admin
5 	ETL, ajustes finais, testes e documentação

Documento elaborado pelo time de desenvolvimento como parte da simulação do ciclo completo de desenvolvimento de software.
