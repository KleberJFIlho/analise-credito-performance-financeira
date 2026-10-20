-- Cohort de solicitação: valor liberado atribuído ao mês da SOLICITAÇÃO,
-- não necessariamente ao mês de desembolso do recurso.
SELECT SUBSTR(s.data_solicitacao,1,7) AS mes_solicitacao,
       COUNT(*) AS solicitacoes,
       SUM(CASE WHEN s.status IN ('aprovada', 'desembolsada') THEN 1 ELSE 0 END) AS aprovadas,
       COUNT(c.contrato_id) AS desembolsadas,
       ROUND(100.0 * COUNT(c.contrato_id)/NULLIF(COUNT(*),0),2) AS conversao_pct,
       ROUND(SUM(COALESCE(c.valor_liberado,0)),2) AS valor_liberado,
       ROUND(AVG(s.sla_horas),2) AS sla_medio_horas,
       ROUND(AVG(s.custo_operacional),2) AS custo_medio_operacao
FROM solicitacoes s
LEFT JOIN contratos c ON c.solicitacao_id=s.solicitacao_id
GROUP BY SUBSTR(s.data_solicitacao,1,7)
ORDER BY mes_solicitacao;
