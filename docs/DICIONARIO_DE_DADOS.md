# Dicionário de dados — 100% simulados

**Granularidade e chaves:**

| Tabela | Grão | Chave | Ligações |
|---|---|---|---|
| `parceiros` | Uma imobiliária fictícia | `parceiro_id` | 1:N com `solicitacoes` |
| `clientes` | Um cliente fictício sem nome/CPF | `cliente_id` | 1:N com `solicitacoes` |
| `solicitacoes` | Uma solicitação de crédito | `solicitacao_id` | N:1 para parceiro e cliente; 1:0..1 com contratos |
| `contratos` | Um contrato de crédito liberado | `contrato_id` | N:1 com solicitação; 1:N com parcelas |
| `parcelas` | Uma parcela prevista | `parcela_id` | N:1 com contrato |

## Campos importantes

- **`solicitacoes.status`**: `reprovada`, `aprovada` (aprovada mas não desembolsada), `desembolsada` (aprovada e financiada).
- **`solicitacoes.sla_horas`**: tempo, em horas, entre criação e decisão, mesmo para operações reprovadas. Não é SLA contratual real.
- **`solicitacoes.custo_operacional`**: custo fictício em reais, gerado a partir de um custo-base, tempo e presença de revisão manual. Não representa despesas reais.
- **`clientes.faixa_risco`**: faixa fictícia calculada exclusivamente a partir de `score_credito`, usado apenas para simulação.
- **`contratos.valor_liberado`**: principal liberado no crédito simulado, não inclui juros futuros.
- **`contratos.valor_parcela`**: prestação simulada com tabela Price e taxa anual nominal dividida por 12. Aproximação educacional sem IOF, tarifas, CET ou demais encargos reais.
- **`parcelas.pagamento`**: data de quitação; vazia se não quitada até a data de referência.
- **`parcelas.valor_previsto`**: prestação nominal programada; **`valor_pago`**: valor recebido até a data de referência.
- **`output/contratos_risco.csv`**: grão de contrato, enriquecido com `dias_atraso_max`, `valor_em_atraso`, `valor_vencido_30d`, `inadimplente_30d`.

## Regras das métricas

Todas as métricas de inadimplência são fotografias da carteira em **01/10/2026**; as parcelas com vencimento posterior não são consideradas atrasadas.

- **Taxa de aprovação:** solicitações nos estados `aprovada` + `desembolsada` / todas as solicitações.
- **Taxa de conversão:** solicitações desembolsadas / todas as solicitações.
- **SLA médio:** média aritmética de `sla_horas` das solicitações.
- **Inadimplência 30+ (contratos):** quantidade de contratos com pelo menos uma parcela não paga há 30 dias ou mais / quantidade de contratos desembolsados.
- **Valor vencido 30+:** soma dos valores previstos das parcelas não quitadas há no mínimo 30 dias.
- **Volume mensal:** período da **solicitação**, incluindo desembolsos que ocorreram alguns dias depois. Não confundir com fluxo mensal de liberação de caixa.

**Limitação:** inadimplência por quantidade de contratos não é a mesma métrica que inadimplência por saldo devedor (NPL por EAD), e valor de parcela vencida não é saldo devedor total. Os dados servem para demonstrar SQL, integridade, indicadores e comunicação.

Os identificadores são anônimos. Não existem nomes reais, CPFs, endereços nem dados obtidos da CashGO ou de outros negócios.
