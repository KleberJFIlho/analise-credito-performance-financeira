-- Inadimplência 30+ por contrato: possui parcela NÃO PAGA vencida há >= 30 dias.
-- Dias de atraso são apurados na data de referência; atraso já quitado não conta.
SELECT c.contrato_id, c.solicitacao_id, s.parceiro_id, s.cliente_id,
       c.data_liberacao, c.valor_liberado, c.prazo_meses,
       ROUND(COALESCE(SUM(CASE WHEN p.pagamento IS NULL
          AND p.vencimento < :data_referencia THEN p.valor_previsto ELSE 0 END),0),2) AS valor_em_atraso,
       ROUND(COALESCE(SUM(CASE WHEN p.pagamento IS NULL
          AND p.vencimento < :data_referencia
          AND julianday(:data_referencia)-julianday(p.vencimento) >= 30
          THEN p.valor_previsto ELSE 0 END),0),2) AS valor_vencido_30d,
       COALESCE(MAX(CASE WHEN p.pagamento IS NULL AND p.vencimento < :data_referencia
          THEN CAST(julianday(:data_referencia)-julianday(p.vencimento) AS INTEGER)
          ELSE 0 END),0) AS dias_atraso_max,
       MAX(CASE WHEN p.pagamento IS NULL AND p.vencimento < :data_referencia
          AND julianday(:data_referencia)-julianday(p.vencimento) >= 30
          THEN 1 ELSE 0 END) AS inadimplente_30d
FROM contratos c
JOIN solicitacoes s ON s.solicitacao_id=c.solicitacao_id
LEFT JOIN parcelas p ON p.contrato_id=c.contrato_id
GROUP BY c.contrato_id, c.solicitacao_id, s.parceiro_id, s.cliente_id,
         c.data_liberacao, c.valor_liberado, c.prazo_meses;
