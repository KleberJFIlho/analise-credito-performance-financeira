WITH risco AS (
    SELECT c.contrato_id, s.parceiro_id, c.valor_liberado,
           SUM(CASE WHEN p.pagamento IS NULL AND p.vencimento < :data_referencia
                     AND julianday(:data_referencia)-julianday(p.vencimento) >=30
                    THEN p.valor_previsto ELSE 0 END) AS valor_vencido_30d
    FROM contratos c
    JOIN solicitacoes s ON s.solicitacao_id = c.solicitacao_id
    LEFT JOIN parcelas p ON p.contrato_id=c.contrato_id
    GROUP BY c.contrato_id, s.parceiro_id, c.valor_liberado
), resumo_risco AS (
    SELECT parceiro_id, COUNT(*) AS contratos,
           SUM(valor_liberado) AS total_liberado,
           SUM(CASE WHEN valor_vencido_30d > 0 THEN 1 ELSE 0 END) AS contratos_inadimplentes_30d,
           SUM(valor_vencido_30d) AS valor_vencido_30d
    FROM risco GROUP BY parceiro_id
)
SELECT pa.parceiro_id, pa.nome_parceiro, pa.uf, pa.porte,
       COUNT(s.solicitacao_id) AS solicitacoes,
       SUM(CASE WHEN s.status IN ('aprovada','desembolsada') THEN 1 ELSE 0 END) AS aprovadas,
       COALESCE(rr.contratos,0) AS desembolsadas,
       ROUND(100.0*COALESCE(rr.contratos,0)/NULLIF(COUNT(s.solicitacao_id),0),2) AS conversao_pct,
       ROUND(COALESCE(rr.total_liberado,0),2) AS valor_liberado,
       COALESCE(rr.contratos_inadimplentes_30d,0) AS contratos_inadimplentes_30d,
       ROUND(100.0*COALESCE(rr.contratos_inadimplentes_30d,0)/NULLIF(rr.contratos,0),2) AS inadimplencia_30d_pct,
       ROUND(COALESCE(rr.valor_vencido_30d,0),2) AS valor_vencido_30d,
       ROUND(AVG(s.sla_horas),2) AS sla_medio_horas,
       ROUND(AVG(s.custo_operacional),2) AS custo_medio_operacao
FROM parceiros pa
LEFT JOIN solicitacoes s ON s.parceiro_id=pa.parceiro_id
LEFT JOIN resumo_risco rr ON rr.parceiro_id=pa.parceiro_id
GROUP BY pa.parceiro_id, pa.nome_parceiro, pa.uf, pa.porte,
         rr.contratos, rr.total_liberado, rr.contratos_inadimplentes_30d, rr.valor_vencido_30d
ORDER BY valor_liberado DESC;
