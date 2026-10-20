"""Geração de gráficos estáticos para pré-visualização do projeto."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def criar_graficos(tabelas: dict[str, pd.DataFrame], pasta: Path) -> None:
    pasta.mkdir(parents=True, exist_ok=True)
    meses = tabelas["volume_mensal"]
    parceiros = tabelas["desempenho_parceiros"]

    fig, ax = plt.subplots(figsize=(13, 5))
    indices = range(len(meses))
    ax.plot(indices, meses["solicitacoes"], marker="o", label="Solicitações")
    ax.plot(indices, meses["desembolsadas"], marker="o", label="Desembolsadas")
    ax.set_xticks(list(indices)[::2], meses["mes_solicitacao"].iloc[::2], rotation=45, ha="right")
    ax.set_ylabel("Quantidade")
    ax.set_title("Volume por mês de solicitação (dados simulados)")
    ax.legend()
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(pasta / "volume_mensal.png", dpi=160)
    plt.close(fig)

    top = parceiros.nlargest(10, "valor_liberado").sort_values("valor_liberado")
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.barh(top["nome_parceiro"], top["valor_liberado"] / 1_000_000)
    ax.set_xlabel("Valor liberado (R$ milhões)")
    ax.set_title("10 maiores parceiros por volume financiado (dados simulados)")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(pasta / "ranking_parceiros.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 5))
    base = parceiros.nlargest(10, "desembolsadas").sort_values("inadimplencia_30d_pct")
    ax.barh(base["nome_parceiro"], base["inadimplencia_30d_pct"])
    ax.set_xlabel("Contratos com parcelas 30+ dias em atraso (%)")
    ax.set_title("Inadimplência 30+ dos 10 parceiros com mais contratos (simulação)")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(pasta / "inadimplencia_parceiros.png", dpi=160)
    plt.close(fig)
