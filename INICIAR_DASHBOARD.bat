@echo off
setlocal
cd /d "%~dp0"
title Dashboard - Analise de Credito e Performance Financeira

echo =============================================================
echo    ANALISE DE CREDITO - DASHBOARD STREAMLIT
echo =============================================================
echo.
if exist ".venv\Scripts\python.exe" (
  set "PYTHON=.venv\Scripts\python.exe"
) else (
  set "PYTHON=python"
)

"%PYTHON%" --version >nul 2>&1
if errorlevel 1 (
  echo ERRO: Python nao foi encontrado. Instale o Python e tente novamente.
  pause
  exit /b 1
)

"%PYTHON%" -c "import streamlit, pandas, plotly, matplotlib" >nul 2>&1
if errorlevel 1 (
  echo Instalando dependencias do projeto pela primeira vez...
  "%PYTHON%" -m pip install -r requirements.txt
  if errorlevel 1 (
    echo ERRO na instalacao. Consulte a mensagem acima.
    pause
    exit /b 1
  )
)

if not exist "data\credito_simulado.sqlite" (
  echo Criando banco e dados ficticios...
  "%PYTHON%" run_pipeline.py
  if errorlevel 1 (
    echo ERRO ao preparar o banco.
    pause
    exit /b 1
  )
)

echo.
echo Abrindo o painel. Caso a guia nao abra, visite:
echo http://localhost:8501
echo.
echo Para encerrar, volte a esta janela e pressione CTRL+C.
"%PYTHON%" -m streamlit run app.py
pause
