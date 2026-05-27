TicketFlow — Panorama do MVP

  O que já foi entregue

  ┌─────┬───────────────────────────────────────────────────┬─────────────┐
  │  #  │                  Funcionalidade                   │   Status    │
  ├─────┼───────────────────────────────────────────────────┼─────────────┤
  │ 1   │ Setup inicial, models e migrations                │ ✅ Completo │
  ├─────┼───────────────────────────────────────────────────┼─────────────┤
  │ 2   │ Django Admin configurado                          │ ✅ Completo │
  ├─────┼───────────────────────────────────────────────────┼─────────────┤
  │ 3   │ Autenticação e perfis (Admin / Técnico / Cliente) │ ✅ Completo │
  ├─────┼───────────────────────────────────────────────────┼─────────────┤
  │ 4   │ CRUD de clientes e equipamentos                   │ ✅ Completo │
  ├─────┼───────────────────────────────────────────────────┼─────────────┤
  │ 5   │ Abertura de chamado (cliente e admin)             │ ✅ Completo │
  ├─────┼───────────────────────────────────────────────────┼─────────────┤
  │ 6   │ Atribuição de técnico (admin)                     │ ✅ Completo │
  └─────┴───────────────────────────────────────────────────┴─────────────┘

  A DT01 (vínculo Perfil → EmpresaCliente) também foi resolvida — o campo empresa já está no model Perfil.

  ---
  O que ainda falta (em ordem de prioridade)
  
  7. Fluxo de status + movimentações — hoje só a atribuição gera movimentação. Falta:
  - View para técnico mudar status: em_andamento → aguardando → resolvido
  - View para admin fechar chamado: resolvido → fechado
  - View para admin reabrir: resolvido → aberto
  - Bloqueio de transições inválidas na view

  8. Registro de diagnóstico e peças — os campos existem no model (diagnostico, solucao, tempo_gasto, PecaUtilizada), mas não há
  view/form/template para o técnico preencher.

  9. Exibição visual do SLA — a propriedade esta_atrasado já existe no model, mas nenhum template a exibe. Falta o badge/indicador
  visual na lista e no detalhe do chamado.

  10. Painel admin — o dashboard atual é básico (lista chamados + 2 contadores). Falta filtros por técnico, cliente, categoria e status
   conforme o RF07.

  11. Histórico por cliente — não existe view/template dedicada. Seria a listagem completa de chamados de um cliente com diagnóstico,
  solução e peças de cada atendimento.

  12. ETL — a pasta etl/ nem existe ainda. São os scripts de extração e relatório de indicadores (tempo médio por categoria, chamados
  por tipo etc.).

  ---
  Bugs conhecidos (registrados em ideias-v2.md)

  - Mensagem de erro no lugar errado: quando técnico tenta acessar chamado de outro, o redirecionamento vai para o dashboard mas a
  mensagem de erro aparece no próximo chamado visitado, não no dashboard.
  - Botão "Novo Chamado" do cliente não funciona — provavelmente resíduo da DT01; vale confirmar se o form de abertura filtra
  equipamentos corretamente via request.user.perfil.empresa.

  ---
  Resumo

  Estamos no passo 6 de 12 do plano de desenvolvimento. A base de dados e o fluxo principal (abrir → atribuir) estão funcionando. O
  próximo bloco natural é o fluxo completo de status + registro de atendimento (passos 7 e 8), que desbloqueia o trabalho do técnico e
  completa o ciclo de vida do chamado.

