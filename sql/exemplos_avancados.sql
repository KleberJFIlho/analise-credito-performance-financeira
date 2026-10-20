-- EXEMPLO 1: ranking de parceiros por valor liberado (window function).
WITH totais AS (
  SELECT s.parceiro_id, ROUND(SUM(c.valor_liberado),2) AS total_liberado
  FROM solicitacoes s JOIN contratos c ON c.solicitacao_id=s.solicitacao_id
  GROUP BY s.parceiro_id
)
SELECT parceiro_id, total_liberado,
       DENSE_RANK() OVER (ORDER BY total_liberado DESC) AS posicao
FROM totais;

-- EXEMPLO 2: SLA e custo médio com revisão manual vs. sem revisão.
SELECT revisao_manual, COUNT(*) AS quantidade,
       ROUND(AVG(sla_horas),2) AS sla_medio_horas,
       ROUND(AVG(custo_operacional),2) AS custo_medio_reais
FROM solicitacoes GROUP BY revisao_manual;

-- EXEMPLO 3: índice de reprovação por faixa de risco de crédito.
SELECT cl.faixa_risco, COUNT(*) AS total,
       SUM(CASE WHEN s.status='reprovada' THEN 1 ELSE 0 END) AS reprovadas,
       ROUND(100.0*SUM(CASE WHEN s.status='reprovada' THEN 1 ELSE 0 END)/COUNT(*),2) AS reprovacao_pct
FROM solicitacoes s JOIN clientes cl ON cl.cliente_id=s.cliente_id
GROUP BY cl.faixa_risco;
