-- Status 'aprovada' significa aprovada mas não liberada;
-- 'desembolsada' significa aprovada e liberada.
SELECT COUNT(*) AS solicitacoes,
       SUM(CASE WHEN status IN ('aprovada','desembolsada') THEN 1 ELSE 0 END) AS aprovadas,
       SUM(CASE WHEN status = 'desembolsada' THEN 1 ELSE 0 END) AS desembolsadas,
       ROUND(100.0 * SUM(CASE WHEN status IN ('aprovada','desembolsada') THEN 1 ELSE 0 END)/NULLIF(COUNT(*),0),2) AS taxa_aprovacao_pct,
       ROUND(100.0 * SUM(CASE WHEN status='desembolsada' THEN 1 ELSE 0 END)/NULLIF(COUNT(*),0),2) AS conversao_pct,
       ROUND(AVG(sla_horas),2) AS sla_medio_horas,
       ROUND(AVG(custo_operacional),2) AS custo_medio_operacao,
       ROUND(SUM(custo_operacional),2) AS custo_total_operacoes
FROM solicitacoes;
