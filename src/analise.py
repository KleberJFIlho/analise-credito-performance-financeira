"""Indicadores calculados via consultas SQL em SQLite."""
from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

from src.simulacao import DATA_REFERENCIA


def montar_banco(caminho: Path, sql_dir: Path, bases: dict[str, pd.DataFrame]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    if caminho.exists():
        caminho.unlink()
    with closing(sqlite3.connect(caminho)) as con, con:
        con.execute("PRAGMA foreign_keys=ON")
        con.executescript((sql_dir / "schema.sql").read_text(encoding="utf-8"))
        for nome in ("parceiros", "clientes", "solicitacoes", "contratos", "parcelas"):
            bases[nome].to_sql(nome, con, if_exists="append", index=False)
        problemas = con.execute("PRAGMA foreign_key_check").fetchall()
        if problemas:
            raise ValueError(f"Erros de integridade referencial: {problemas[:5]}")


def executar_consulta(con: sqlite3.Connection, caminho: Path) -> pd.DataFrame:
    query = caminho.read_text(encoding="utf-8")
    return pd.read_sql_query(query, con, params={"data_referencia": DATA_REFERENCIA.isoformat()})


def exportar_indicadores(banco: Path, sql_dir: Path, pasta_saida: Path) -> dict[str, pd.DataFrame]:
    pasta_saida.mkdir(parents=True, exist_ok=True)
    consultas = ["kpis_gerais", "volume_mensal", "contratos_risco", "desempenho_parceiros"]
    with closing(sqlite3.connect(banco)) as con:
        tabelas = {nome: executar_consulta(con, sql_dir / f"{nome}.sql") for nome in consultas}
    for nome, tabela in tabelas.items():
        tabela.to_csv(pasta_saida / f"{nome}.csv", index=False, encoding="utf-8-sig")
    return tabelas
