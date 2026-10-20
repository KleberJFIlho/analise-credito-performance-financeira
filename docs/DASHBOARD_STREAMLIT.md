# Como usar o dashboard Streamlit no Windows

A aplicação visual já está implementada no **`app.py`**. `run_pipeline.py` prepara os dados e **não abre uma tela**. O comando que abre a interface é `python -m streamlit run app.py`.

## Opção mais simples — dois cliques

1. Extraia o ZIP completo; não execute nada diretamente de dentro do ZIP.
2. Entre na pasta `analise-credito-performance-financeira`.
3. Dê **dois cliques** em `INICIAR_DASHBOARD.bat`.
4. A primeira execução instala bibliotecas faltantes (requer internet).
5. O navegador deve abrir em **http://localhost:8501**. Se não abrir automaticamente, digite esse endereço manualmente.
6. **Não feche a janela preta do terminal** enquanto estiver usando o dashboard. Para encerrar, pressione `Ctrl + C` nela.

## Opção via VS Code / PowerShell

Abra no VS Code a pasta que contém `app.py` e `requirements.txt` e execute:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Se o banco não existir ainda, primeiro:

```powershell
python run_pipeline.py
```

### Usando um ambiente virtual (recomendado)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Esse formato funciona sem ativar o ambiente virtual e evita problemas de política de execução do PowerShell.

## O que o dashboard mostra

- **Visão geral:** KPIs dinâmicos, funil de aprovações, volume e conversão mensal.
- **Parceiros:** ranking, comparação de conversão e inadimplência, CSV exportável.
- **Crédito & risco:** atraso 30+, eficiência da revisão manual e faixas de risco.
- **Dados & SQL:** pesquisa de solicitações, tabela detalhada, exportação dos dados filtrados e exemplo de consulta.
- **Barra lateral:** filtros combináveis por mês, UF, parceiro, faixa de risco e status.

### Notas importantes para interpretar os números

- Os dados são **inteiramente simulados** e **não refletem o desempenho real da CashGO**.
- Os indicadores do gráfico mensal são atribuídos ao **mês da solicitação**, não à data de efetivo desembolso do dinheiro.
- A inadimplência é avaliada **sempre em 01/10/2026**, mesmo quando você filtra coortes mais antigas. Ela é uma fotografia da carteira, **não uma série histórica**.
- Uma solicitação com status `aprovada` ainda não foi liberada; `desembolsada` significa aprovada e liberada.
- Ao filtrar apenas solicitações `reprovada`, a carteira liberada fica vazia e a taxa de inadimplência é apresentada como zero por convenção da visualização (não é taxa observável naquele subconjunto).
- A tabela aplica os filtros em memória após carregar as informações do SQLite. O código-fonte de consulta SQL fica em `sql/`.

## Resolver problemas comuns

**`No module named streamlit`**: instale com `python -m pip install -r requirements.txt` no mesmo Python que executa o painel.

**`File does not exist: app.py`**: você está na pasta errada ou usando o ZIP anterior sem a nova interface. Abra a pasta que contém `INICIAR_DASHBOARD.bat` e `app.py`.

**`localhost:8501` não abre**: deixe o terminal em execução e confirme a porta indicada nele. Se estiver em uso, o Streamlit poderá oferecer outra porta, por exemplo `8502`.

**Python não encontrado**: execute `python --version` para conferir a instalação e o PATH.

**PowerShell bloqueou a ativação `.ps1`**: use o executável `.venv\Scripts\python.exe` conforme os exemplos acima.

**O painel está em branco, mas o pipeline funcionou**: abra `http://localhost:8501`, confira mensagens de erro no terminal e veja se `data/credito_simulado.sqlite` está presente.

## Estrutura acrescentada nesta versão

```text
app.py                      # Interface visual Streamlit
INICIAR_DASHBOARD.bat       # Inicialização por dois cliques no Windows
.streamlit/config.toml      # Tema visual
src/dashboard_data.py       # Camada de dados, filtros e KPIs
checks: tests/test_dashboard_data.py
```
