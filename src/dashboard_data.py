"""Leitura, filtros e indicadores reutilizáveis do dashboard Streamlit.

Todo o conteúdo é simulado. A inadimplência é calculada na data fixa da
simulação e pode ser segmentada pelas coortes de solicitação selecionadas.
"""
from __future__ import annotations

from contextlib import closing
from pathlib import Path
import sqlite3

import pandas as pd

from src.simulacao import DATA_REFERENCIA

BASE_DIR = Path(__file__).resolve().parents[1]
DB_FILE = BASE_DIR / "data" / "credito_simulado.sqlite"

SQL_SOLICITACOES = """
SELECT
    s.solicitacao_id, s.cliente_id, s.parceiro_id,
    s.data_solicitacao, s.data_decisao, s.status,
    s.valor_solicitado, s.sla_horas, s.revisao_manual,
    s.custo_operacional,
    p.nome_parceiro, p.uf AS uf_parceiro, p.porte,
    cl.uf AS uf_cliente, cl.faixa_risco, cl.score_credito,
    cl.renda_mensal,
    c.contrato_id, c.data_liberacao, c.valor_liberado,
    c.prazo_meses
FROM solicitacoes s
JOIN parceiros p ON p.parceiro_id = s.parceiro_id
JOIN clientes cl ON cl.cliente_id = s.cliente_id
LEFT JOIN contratos c ON c.solicitacao_id = s.solicitacao_id
"""


def carregar_dados(db_path: Path = DB_FILE) -> pd.DataFrame:
    """Carrega 1 linha por solicitação, com risco agregado no nível contrato.

    O uso de risco previamente agregado evita inflar totais devido à
    multiplicação de linhas gerada pelo JOIN direto com parcelas.
    """
    db_path = Path(db_path)
    if not db_path.exists():
        raise FileNotFoundError(f"Banco SQLite não encontrado: {db_path}")

    with closing(sqlite3.connect(db_path)) as con:
        sol = pd.read_sql_query(SQL_SOLICITACOES, con)
        if sol.empty:
            raise ValueError("A tabela de solicitações está vazia.")
        risco_sql = (BASE_DIR / "sql" / "contratos_risco.sql").read_text(encoding="utf-8")
        risco = pd.read_sql_query(
            risco_sql,
            con,
            params={"data_referencia": DATA_REFERENCIA.isoformat()},
        )

    risco = risco[[
        "contrato_id", "valor_em_atraso", "valor_vencido_30d",
        "dias_atraso_max", "inadimplente_30d",
    ]]
    df = sol.merge(risco, how="left", on="contrato_id", validate="many_to_one")
    df["data_solicitacao"] = pd.to_datetime(df["data_solicitacao"])
    df["data_decisao"] = pd.to_datetime(df["data_decisao"])
    df["data_liberacao"] = pd.to_datetime(df["data_liberacao"])
    df["mes"] = df["data_solicitacao"].dt.strftime("%Y-%m")
    df["ano"] = df["data_solicitacao"].dt.year

    for campo in ("valor_liberado", "valor_em_atraso", "valor_vencido_30d", "dias_atraso_max", "inadimplente_30d"):
        df[campo] = df[campo].fillna(0)
    df["inadimplente_30d"] = df["inadimplente_30d"].astype(int)
    df["aprovada"] = df["status"].isin(["aprovada", "desembolsada"]).astype(int)
    df["desembolsada"] = df["status"].eq("desembolsada").astype(int)
    df["revisao_manual"] = df["revisao_manual"].astype(int)
    return df


def filtrar_dados(
    df: pd.DataFrame,
    meses: tuple[str, str] | None = None,
    ufs: list[str] | None = None,
    parceiros: list[str] | None = None,
    riscos: list[str] | None = None,
    status: list[str] | None = None,
) -> pd.DataFrame:
    """Filtros cumulativos. Seleções vazias em listas significam 'todos'."""
    selecionado = pd.Series(True, index=df.index)
    if meses is not None:
        mes_inicio, mes_fim = meses
        selecionado &= df["mes"].between(mes_inicio, mes_fim)
    for coluna, valores in (
        ("uf_parceiro", ufs),
        ("nome_parceiro", parceiros),
        ("faixa_risco", riscos),
        ("status", status),
    ):
        if valores:
            selecionado &= df[coluna].isin(valores)
    return df.loc[selecionado].copy()


def calcular_kpis(df: pd.DataFrame) -> dict:
    total = len(df)
    aprovadas = int(df["aprovada"].sum())
    desembolsadas = int(df["desembolsada"].sum())
    inadimplentes = int(df["inadimplente_30d"].sum())
    return {
        "solicitacoes": total,
        "aprovadas": aprovadas,
        "desembolsadas": desembolsadas,
        "aprovacao_pct": aprovadas / total * 100 if total else 0.0,
        "conversao_pct": desembolsadas / total * 100 if total else 0.0,
        "inadimplentes": inadimplentes,
        "inadimplencia_30d_pct": inadimplentes / desembolsadas * 100 if desembolsadas else 0.0,
        "valor_liberado": float(df["valor_liberado"].sum()),
        "valor_vencido_30d": float(df["valor_vencido_30d"].sum()),
        "sla_medio_horas": float(df["sla_horas"].mean()) if total else 0.0,
        "custo_operacional": float(df["custo_operacional"].sum()),
        "custo_medio_operacao": float(df["custo_operacional"].mean()) if total else 0.0,
        "revisoes_manuais": int(df["revisao_manual"].sum()),
    }


def resumo_mensal(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["mes", "solicitacoes", "aprovadas", "desembolsadas", "valor_liberado", "conversao_pct"])
    resumo = df.groupby("mes", as_index=False).agg(
        solicitacoes=("solicitacao_id", "size"),
        aprovadas=("aprovada", "sum"),
        desembolsadas=("desembolsada", "sum"),
        valor_liberado=("valor_liberado", "sum"),
        sla_medio=("sla_horas", "mean"),
    )
    resumo["conversao_pct"] = resumo["desembolsadas"] / resumo["solicitacoes"] * 100
    return resumo.sort_values("mes")


def resumo_parceiros(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=[
            "parceiro_id", "nome_parceiro", "uf_parceiro", "solicitacoes", "aprovadas", "desembolsadas",
            "valor_liberado", "inadimplentes", "valor_vencido_30d", "sla_medio_horas",
            "conversao_pct", "inadimplencia_30d_pct",
        ])
    p = df.groupby(["parceiro_id", "nome_parceiro", "uf_parceiro"], as_index=False).agg(
        solicitacoes=("solicitacao_id", "size"),
        aprovadas=("aprovada", "sum"),
        desembolsadas=("desembolsada", "sum"),
        valor_liberado=("valor_liberado", "sum"),
        inadimplentes=("inadimplente_30d", "sum"),
        valor_vencido_30d=("valor_vencido_30d", "sum"),
        sla_medio_horas=("sla_horas", "mean"),
    )
    p["conversao_pct"] = p["desembolsadas"] / p["solicitacoes"] * 100
    p["inadimplencia_30d_pct"] = (
        p["inadimplentes"].div(p["desembolsadas"].replace(0, float("nan"))).fillna(0) * 100
    )
    return p.sort_values("valor_liberado", ascending=False)


def resumo_risco(df: pd.DataFrame) -> pd.DataFrame:
    liberadas = df[df["desembolsada"] == 1]
    if liberadas.empty:
        return pd.DataFrame(columns=["faixa_risco", "contratos", "inadimplentes", "valor_vencido_30d", "inadimplencia_pct"])
    tab = liberadas.groupby("faixa_risco", as_index=False).agg(
        contratos=("contrato_id", "size"),
        inadimplentes=("inadimplente_30d", "sum"),
        valor_vencido_30d=("valor_vencido_30d", "sum"),
    )
    tab["inadimplencia_pct"] = tab["inadimplentes"] / tab["contratos"] * 100
    ordem = {"Baixo": 0, "Médio": 1, "Alto": 2}
    return tab.sort_values(by="faixa_risco", key=lambda s: s.map(ordem))
