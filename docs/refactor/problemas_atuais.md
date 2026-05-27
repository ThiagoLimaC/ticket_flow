1. atribuir.html — HTML corrompido (linha 15): tem <int:chamado_id/card-header"> no meio do HTML, o card "Resumo do Chamado" está
  completamente quebrado.
  2. AbrirChamadoForm — cliente vê lista vazia: o queryset está hardcoded como Equipamento.objects.none(). A DT01 foi resolvida no
  model (campo empresa existe no Perfil) mas o form nunca foi atualizado para usar perfil.empresa.
  3. dashboard.html — sem bloco de mensagens: o redirect com messages.error vai para o dashboard mas o template não renderiza as
  mensagens, então elas aparecem na próxima página que tiver o bloco.
  4. dashboard.html — badge com status errado: usa chamado.status == 'concluido' mas o valor correto é 'resolvido'.
  5. base.html — link "Chamados" vai para #: deveria apontar para o dashboard.