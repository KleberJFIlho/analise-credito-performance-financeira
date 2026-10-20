# Power BI — guia de aprendizagem para montar o painel

Este repositório inclui o **modelo de dados, consultas SQL, CSVs e medidas DAX sugeridas**. **Não inclui um arquivo `.pbix` pronto**: o painel deve ser montado no Power BI Desktop, o que também permite aprender a ferramenta. Não descreva o painel como concluído enquanto não fizer essa etapa.

## 1. Importar dados

Abra o Power BI Desktop (Windows) → **Obter dados > Texto/CSV**. Importe os arquivos abaixo:

1. `data/raw/parceiros.csv` → dimensão `parceiros`.
2. `data/raw/clientes.csv` → dimensão `clientes`.
3. `data/raw/solicitacoes.csv` → fato `solicitacoes`.
4. `output/contratos_risco.csv` → fato `contratos_risco` (com a fotografia 30+ pronta em SQL).
5. `data/raw/parcelas.csv` → fato `parcelas` (opcional para análises de vencimentos e recebimentos).

Configure `valor_*`, `sla_horas` e `custo_operacional` como decimal; campos de datas como Data ou Data/Hora. IDs são Texto. Atenção aos separadores decimais ao importar conforme a regionalização do Power BI.

## 2. Criar relacionamentos (modelo estrela simplificado)

- `parceiros[parceiro_id]` **1 → N** `solicitacoes[parceiro_id]`.
- `clientes[cliente_id]` **1 → N** `solicitacoes[cliente_id]`.
- `solicitacoes[solicitacao_id]` **1 → 0..1** `contratos_risco[solicitacao_id]` (na interface pode aparecer como 1:N).
- `contratos_risco[contrato_id]` **1 → N** `parcelas[contrato_id]`.

Deixe o filtro em direção única, do lado 1 para o lado N. **Não** importe também `data/raw/contratos.csv` no mesmo modelo a menos que saiba como resolver relações duplicadas.

## 3. Criar medidas (Modelagem > Nova medida)

Cada bloco abaixo é uma medida separada:

```dax
Total Solicitações = COUNTROWS(solicitacoes)
```

```dax
Total Aprovadas =
CALCULATE(
    COUNTROWS(solicitacoes),
    solicitacoes[status] IN {"aprovada", "desembolsada"}
)
```

```dax
Contratos Liberados = COUNTROWS(contratos_risco)
```

```dax
Taxa Aprovação = DIVIDE([Total Aprovadas], [Total Solicitações], 0)
```

```dax
Taxa Conversão = DIVIDE([Contratos Liberados], [Total Solicitações], 0)
```

```dax
Valor Liberado = SUM(contratos_risco[valor_liberado])
```

```dax
SLA Médio Horas = AVERAGE(solicitacoes[sla_horas])
```

```dax
Custo Médio Operacional = AVERAGE(solicitacoes[custo_operacional])
```

```dax
Contratos Inadimplentes 30d =
CALCULATE(
    COUNTROWS(contratos_risco),
    contratos_risco[inadimplente_30d] = 1
)
```

```dax
Inadimplência 30d = DIVIDE([Contratos Inadimplentes 30d], [Contratos Liberados], 0)
```

```dax
Valor Vencido 30d = SUM(contratos_risco[valor_vencido_30d])
```

Formate `[Taxa Aprovação]`, `[Taxa Conversão]` e `[Inadimplência 30d]` como percentual. Formate `[Valor Liberado]`, `[Valor Vencido 30d]` e `[Custo Médio Operacional]` como moeda R$.

**Atenção ao filtro de datas:** o dado de inadimplência é uma fotografia fixa em 01/10/2026, e não uma série histórica de inadimplência mês a mês. A relação por solicitação filtra por **coortes de origem**, não pelo momento de vencimento da parcela.

## 4. Montar três páginas

**Página 1 — Visão executiva**: cartões de solicitações, aprovação, conversão, valor liberado e custo médio; linha de solicitações por mês; filtros de parceiro, UF e faixa de risco.

**Página 2 — Parceiros**: tabela com parceiro, volume, conversão, valor liberado, inadimplência 30+ e SLA; gráfico de barras ordenando por valor liberado.

**Página 3 — Eficiência e risco**: comparação do SLA e custo por revisão manual (`solicitacoes[revisao_manual]`), tabelas de contratos com atraso e distribuição por `clientes[faixa_risco]`.

## 5. Conferir resultados

Compare os totais com `output/kpis_gerais.csv`, `output/desempenho_parceiros.csv` e `output/contratos_risco.csv`. Se houver divergência, confira tipo de dados, cardinalidade e direção dos filtros antes de alterar medidas.

Ao finalizar, tire **prints do painel real que você construiu** e coloque-os em `imagens/`. Você também pode adicionar o `.pbix` ao GitHub caso queira disponibilizá-lo, verificando o tamanho e a ausência de dados sigilosos.
