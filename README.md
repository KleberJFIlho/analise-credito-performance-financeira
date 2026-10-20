## 🌐 Dashboard online

[🚀 Acessar Atlas Credit — Dashboard Interativo](https://c8lka6o86egxm5woxtgm8j.streamlit.app/)

Projeto educacional de análise de crédito e performance
financeira desenvolvido com Python, SQL, SQLite e Streamlit.

Todos os dados utilizados são fictícios.

# Análise de Crédito e Performance Financeira

**Projeto de portfólio | Python • SQL • SQLite • Streamlit (dashboard interativo) • Power BI (roteiro)**

Projeto educacional de analytics para simular a operação de crédito de uma rede de imobiliárias parceiras. Foi inspirado nos **tipos de indicadores** solicitados em vagas de dados do setor de crédito, incluindo a vaga de Analista de Dados Júnior da CashGO, mas **não é um projeto oficial da empresa** e **não usa dados reais**.

> **Importante:** todos os registros são **100% fictícios e gerados por simulação**, com semente fixa, para uso didático. O roteiro de Power BI foi preparado, mas um dashboard `.pbix` ainda precisa ser construído no Power BI Desktop.

## Perguntas de negócio

1. Quantas solicitações de crédito são recebidas e qual o percentual aprovado?
2. Qual parcela das solicitações vira crédito efetivamente liberado?
3. Quais imobiliárias parceiras geram mais volume, e quais têm maior inadimplência?
4. Quantos contratos possuem parcelas abertas com **30+ dias de atraso**?
5. Qual o tempo médio da decisão e o custo operacional por solicitação?
6. Como a revisão manual altera o SLA e o custo médio?

## Dashboard interativo (NOVO)

A versão atual já inclui um **dashboard funcional em Streamlit**. O painel abre no navegador, com filtros por mês, UF, parceiro, faixa de risco e status; gráficos de volume, funil, conversão, inadimplência e eficiência; tabelas e exportação CSV.

**Windows: entre na pasta e dê dois cliques em `INICIAR_DASHBOARD.bat`.** Na primeira execução é necessária conexão à internet para instalar bibliotecas que ainda não estejam presentes. Mantenha o terminal aberto para o servidor continuar funcionando.

Ou utilize o terminal na pasta do projeto:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Abra `http://localhost:8501` se o navegador não abrir sozinho. O comando `python run_pipeline.py` apenas regenera dados, consultas e imagens: **não abre a interface**.

Passo a passo completo: [Guia do dashboard Streamlit](docs/DASHBOARD_STREAMLIT.md).

## Prévia dos resultados simulados

![Solicitações e desembolsos por mês](imagens/volume_mensal.png)

![Ranking das imobiliárias fictícias](imagens/ranking_parceiros.png)

![Inadimplência dos parceiros](imagens/inadimplencia_parceiros.png)

Leia o [resumo executivo gerado](output/resumo_executivo.md). **Nenhum resultado representa métricas da CashGO.**

## Arquitetura

```text
Gerador Python (seed fixa)
        |
        v
5 CSVs em data/raw
        |
        v
SQLite (5 tabelas, PKs, FKs e índices)
        |
        v
Consultas SQL: KPIs, coortes mensais,
risco por contrato e comparação por parceiro
        |
        +--> CSVs de análise em output/
        +--> Gráficos PNG em imagens/
        +--> Interface Streamlit (app.py; filtros e gráficos)
        +--> Insumo para Power BI Desktop (passo manual)
```

## Como executar no Windows (PowerShell)

```powershell
# 1. Na pasta descompactada do projeto
py -m venv .venv

# 2. Ative o ambiente virtual
.\.venv\Scripts\Activate.ps1

# 3. Instale as dependências
python -m pip install -r requirements.txt

# 4. Execute a carga e a análise
python run_pipeline.py

# 5. Valide a integridade e os indicadores
python -m unittest discover -s tests -v
```

Se o Windows bloquear a ativação do PowerShell, use os comandos do executável diretamente (sem alterar políticas de execução):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run_pipeline.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

No Linux/macOS, use `python3 -m venv .venv`, `source .venv/bin/activate` e depois os mesmos comandos `python ...`.

## Arquivos principais

```text
analise-credito-performance-financeira/
├── run_pipeline.py             # Execução completa
├── requirements.txt            # pandas, matplotlib, streamlit, plotly
├── app.py                      # Painel web Streamlit
├── INICIAR_DASHBOARD.bat       # Atalho Windows (duplo clique)
├── .streamlit/config.toml      # Tema escuro
├── src/
│   ├── simulacao.py            # Dados fictícios e parcelas
│   ├── analise.py              # Carga SQLite + consultas
│   └── visualizacao.py         # Gráficos para portfólio
├── sql/
│   ├── schema.sql              # Modelo relacional e integridade
│   ├── kpis_gerais.sql
│   ├── volume_mensal.sql
│   ├── contratos_risco.sql
│   ├── desempenho_parceiros.sql
│   └── exemplos_avancados.sql # CTE, agregações, window function
├── data/
│   ├── raw/                    # Cinco CSVs sintéticos
│   └── credito_simulado.sqlite # Base SQLite já gerada
├── output/                     # Consultas exportadas e resumo
├── imagens/                    # Gráficos gerados por Python
├── docs/
│   ├── DICIONARIO_DE_DADOS.md
│   ├── POWER_BI_GUIA.md
│   └── DASHBOARD_STREAMLIT.md
└── tests/                     # Pipeline e dados do dashboard
```

## Exemplo SQL — volume e conversão por parceiro

```sql
SELECT p.nome_parceiro,
       COUNT(*) AS solicitacoes,
       SUM(CASE WHEN s.status='desembolsada' THEN 1 ELSE 0 END) AS desembolsadas,
       ROUND(100.0*SUM(CASE WHEN s.status='desembolsada' THEN 1 ELSE 0 END)
             / NULLIF(COUNT(*),0),2) AS conversao_pct
FROM solicitacoes s
JOIN parceiros p ON p.parceiro_id=s.parceiro_id
GROUP BY p.nome_parceiro
ORDER BY conversao_pct DESC;
```

Abra `data/credito_simulado.sqlite` em um cliente SQLite ou extensão SQLite do VS Code e rode as consultas de `sql/`.

## Modelagem e qualidade

- **Chaves primárias e estrangeiras** no banco para evitar registros órfãos.
- **Testes automatizados** de consistência: total de solicitações, desembolsos, pagamentos, integridade e reprodutibilidade.
- **Métrica 30+ com data de referência explícita**: parcela não paga com atraso ≥30 dias em 01/10/2026.
- **Limites claros**: os valores de contratos, custos, atrasos e taxas são inventados; o projeto não tenta inferir a performance de um negócio real.

Documentação: [dicionário e regras](docs/DICIONARIO_DE_DADOS.md) · [guia Power BI com DAX](docs/POWER_BI_GUIA.md).

## Evoluções sugeridas

- Construir o **Power BI Desktop real** e adicionar o `.pbix` e screenshots ao repositório.
- Elaborar análises mensais históricas de inadimplência usando múltiplas datas de corte.
- Publicar o **dashboard Streamlit existente** online (deploy) com os dados 100% fictícios.
- Implementar CI no GitHub Actions para executar os testes a cada `push`.

## Publicar no GitHub

Crie um repositório público chamado `analise-credito-performance-financeira`. Extraia este projeto, abra o terminal na pasta e execute:

```bash
git init
git add .
git commit -m "Projeto de portfolio: analise de credito com SQL e Python"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/analise-credito-performance-financeira.git
git push -u origin main
```

Crie primeiro o repositório **vazio** na interface do GitHub, sem README inicial, e substitua `SEU_USUARIO` pelo seu usuário. A publicação no GitHub é uma etapa manual, não realizada automaticamente neste pacote.

---

**Como apresentar no currículo (após estudar e executar):** “Projeto educacional de análise de crédito com Python, SQL e Streamlit: banco relacional SQLite, indicadores de conversão, inadimplência 30+, SLA, análise de parceiros e dashboard web interativo com filtros e exportação CSV.”

**Atenção:** apresentar uma prática guiada como projeto educacional é adequado; não a declare experiência profissional real, nem declare domínio de Power BI sem construí-lo e conseguir explicar o painel.
