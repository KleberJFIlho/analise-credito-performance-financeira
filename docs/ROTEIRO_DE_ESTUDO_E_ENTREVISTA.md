# Roteiro de estudo e apresentação do projeto

**Objetivo:** demonstrar que você compreende a análise, as consultas e as decisões. O código pode servir como ponto de partida, mas você deve executar, modificar e conseguir explicar os resultados antes de anunciar esse trabalho como seu portfólio.

## Primeiro dia — SQL e dados (1 a 2 horas)

1. Execute `python run_pipeline.py` e abra `data/credito_simulado.sqlite` no SQLite/VS Code.
2. Leia `sql/schema.sql`, desenhe as relações entre solicitações, parceiros, contratos e parcelas.
3. Execute cada consulta SQL e confira os arquivos `output/*.csv`.
4. Reescreva sem copiar a consulta de taxa de conversão por parceiro.

## Segundo dia — Python e qualidade de dados (1 a 2 horas)

1. Abra `src/simulacao.py`: onde são criados os dados? Onde está definida a data de referência?
2. Explique por que parcelas futuras não são classificadas como inadimplentes.
3. Altere a quantidade de solicitações para 3.000 e gere novamente. Depois reverta se quiser preservar as métricas originais.
4. Rode `python -m unittest discover -s tests -v` e explique o propósito de dois testes.

## Terceiro dia — análise e Power BI (2 a 4 horas)

1. Importe os CSVs no Power BI Desktop seguindo `docs/POWER_BI_GUIA.md`.
2. Configure as relações e valide a contagem total de solicitações.
3. Crie três cartões: conversão, total liberado e inadimplência 30+.
4. Construa uma tabela de performance por parceiro.
5. Salve imagens **do painel que você efetivamente construiu**.

## Perguntas para praticar antes da entrevista

- Qual a diferença entre taxa de aprovação e taxa de conversão?
- O que ocorre se eu fizer um `INNER JOIN` entre solicitações e contratos para contar todas as solicitações?
- Como garantir que um contrato apareça apenas uma vez no cálculo da inadimplência?
- Como você identificaria duplicidades, IDs órfãos e pagamentos posteriores à data de referência?
- Por que inadimplência de **contratos** é diferente de inadimplência de **saldo**?
- Qual seria sua hipótese para reduzir o SLA e o custo de casos com revisão manual?
- O que significaria a queda de volume em setembro de 2026 no gráfico? (*Dica:* os dados foram gerados só até 18 de setembro; o mês está incompleto.)

## Exemplo de apresentação honesta (aprox. 30 segundos)

“Desenvolvi e estudei um projeto educacional de análise de crédito com base simulada. Usei Python para geração e tratamento, SQLite/SQL para modelagem e consultas, e montei indicadores de aprovação, conversão, tempo de decisão, inadimplência e performance por parceiro. Incluí verificações automatizadas da consistência dos dados. Estou usando essa base para desenvolver minha prática com Power BI.”

Se o Power BI já estiver concluído, substitua a última frase por uma descrição exata do painel que construiu e sabe demonstrar.
