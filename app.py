"""Dashboard interativo — Análise de Crédito e Performance Financeira.

Para executar no terminal, na pasta do projeto:
    python -m streamlit run app.py

DADOS 100% FICTÍCIOS — não são resultados reais de nenhuma empresa.
"""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.dashboard_data import (
    DB_FILE,
    carregar_dados,
    calcular_kpis,
    filtrar_dados,
    resumo_mensal,
    resumo_parceiros,
    resumo_risco,
)
from src.simulacao import DATA_REFERENCIA

st.set_page_config(
    page_title="Atlas Credit | Painel de análise",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

CORES = {
    "verde": "#4ADFC0",
    "azul": "#62A7FF",
    "violeta": "#AD9FFF",
    "amarelo": "#F8C470",
    "vermelho": "#FF8090",
    "cinza": "#8DA2BD",
    "branco": "#EAF2FA",
}

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.5rem; padding-bottom: 3.5rem; max-width: 1500px;}
      [data-testid="stSidebar"] {border-right: 1px solid #27354B;}
      [data-testid="stMetric"] {background: #132036; padding: 19px 20px; border-radius: 15px; border: 1px solid #27364B;}
      [data-testid="stMetricLabel"] {color: #A4B6CA;}
      [data-testid="stMetricValue"] {font-weight: 740; letter-spacing: -0.025em;}
      .badge {display:inline-block; padding:6px 10px; border: 1px solid #33546A; border-radius:50px;
              color: #92E8D6; font-size: 11px; font-weight: 760; letter-spacing: .11em;}
      .hero-title {font-size: clamp(2.1rem, 4.3vw, 3.35rem); font-weight: 820; letter-spacing: -.055em;
                   line-height: 1.12; margin: .55rem 0 .45rem; color: #F2F6FD;}
      .hero-lead {font-size: 1.02rem; color: #A9B8CE; max-width: 850px; line-height: 1.6;}
      .eyebrow {font-size: 12px; text-transform: uppercase; font-weight: 750; letter-spacing: .14em; color: #81DCC7;}
      .aside {font-size: 12px; color: #9DB1C5; line-height: 1.6;}
      .subtle {border-top: 1px solid #263951; margin: 1.15rem 0;}
      div[data-testid="stTabs"] button {font-weight: 650;}
      h2, h3 {letter-spacing: -.025em;}
      a {text-decoration:none;}
    </style>
    """,
    unsafe_allow_html=True,
)


def n(v: float, casas: int = 0) -> str:
    return f"{v:,.{casas}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def real(v: float, compacto: bool = False) -> str:
    if compacto:
        if abs(v) >= 1_000_000:
            return f"R$ {n(v / 1_000_000, 2)} mi"
        if abs(v) >= 1_000:
            return f"R$ {n(v / 1_000, 1)} mil"
    return f"R$ {n(v, 2)}"


def pct(v: float) -> str:
    return f"{n(v, 2)}%"


def grafico_base(fig: go.Figure, altura: int = 370, horizontal: bool = False) -> go.Figure:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=CORES["branco"], family="Arial"),
        margin=dict(l=5, r=10, t=26, b=16),
        height=altura,
        legend=dict(orientation="h", y=1.1, x=0, font=dict(size=11)),
        hovermode="closest" if horizontal else "x unified",
    )
    fig.update_xaxes(showgrid=False, zeroline=False, tickfont=dict(color=CORES["cinza"], size=11))
    fig.update_yaxes(showgrid=True, gridcolor="rgba(140,164,190,.12)", zeroline=False,
                     tickfont=dict(color=CORES["cinza"], size=11))
    return fig


@st.cache_data(show_spinner="Carregando dados do SQLite...")
def ler_sqlite(caminho: str, mtime: float) -> pd.DataFrame:
    return carregar_dados(Path(caminho))


if not DB_FILE.exists():
    st.error("O banco de dados ainda não foi encontrado.")
    st.code("python run_pipeline.py", language="powershell")
    st.info("Execute esse comando na pasta do projeto e depois abra o dashboard novamente.")
    st.stop()

try:
    dados = ler_sqlite(str(DB_FILE), DB_FILE.stat().st_mtime)
except Exception as erro:
    st.error("Não foi possível carregar o banco SQLite do projeto.")
    st.exception(erro)
    st.stop()

meses = sorted(dados["mes"].unique())

with st.sidebar:
    st.markdown('<span class="eyebrow">ATLAS / CREDIT LAB</span>', unsafe_allow_html=True)
    st.markdown("## Painel financeiro")
    st.caption("PROJETO EDUCACIONAL · SQL + PYTHON")
    st.divider()
    st.markdown("### Filtros de análise")
    periodo = st.select_slider("Período das solicitações", options=meses, value=(meses[0], meses[-1]))
    uf = st.multiselect("UF da imobiliária", sorted(dados["uf_parceiro"].unique()),
                        placeholder="Todas as UFs")
    alternativas = dados[dados["uf_parceiro"].isin(uf)] if uf else dados
    parceiro = st.multiselect("Imobiliária parceira", sorted(alternativas["nome_parceiro"].unique()),
                              placeholder="Todas as imobiliárias")
    risco = st.multiselect("Faixa de risco do cliente", ["Baixo", "Médio", "Alto"],
                          placeholder="Todas as faixas")
    status = st.multiselect("Status da solicitação", ["reprovada", "aprovada", "desembolsada"],
                            placeholder="Todos os status")
    st.divider()
    st.markdown(
        f'<div class="aside">• Dados integralmente fictícios.<br>• Risco 30+ medido em '
        f'{DATA_REFERENCIA.strftime("%d/%m/%Y")}.<br>• Filtros aplicados a todas as abas.</div>',
        unsafe_allow_html=True,
    )
    if st.button("Atualizar dados do banco", use_container_width=True, type="secondary"):
        st.cache_data.clear()
        st.rerun()

filtrados = filtrar_dados(
    dados, meses=periodo, ufs=uf, parceiros=parceiro, riscos=risco, status=status
)

st.markdown('<span class="badge">● DADOS SIMULADOS · PORTFÓLIO</span>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">Análise de Crédito<br>& Performance Financeira</div>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-lead">Da solicitação à liberação: acompanhe conversão, volume financeiro, '
    'eficiência operacional e inadimplência da carteira por parceiro e perfil de risco.</p>',
    unsafe_allow_html=True,
)
st.caption(
    f"Coortes de solicitação: {periodo[0]} a {periodo[1]}  ·  "
    f"Posição fixa da carteira: {DATA_REFERENCIA.strftime('%d/%m/%Y')}  ·  "
    f"{n(len(filtrados))} solicitações no filtro"
)

if filtrados.empty:
    st.warning("Nenhum registro encontrado para a combinação de filtros. Remova um filtro na barra lateral.")
    st.stop()

k = calcular_kpis(filtrados)
linha1 = st.columns(4, gap="medium")
with linha1[0]:
    st.metric("Solicitações recebidas", n(k["solicitacoes"]))
with linha1[1]:
    st.metric("Aprovação", pct(k["aprovacao_pct"]), help="Aprovadas + desembolsadas / solicitações")
with linha1[2]:
    st.metric("Créditos liberados", n(k["desembolsadas"]))
with linha1[3]:
    st.metric("Valor liberado", real(k["valor_liberado"], compacto=True))
linha2 = st.columns(4, gap="medium")
with linha2[0]:
    st.metric("Conversão em desembolso", pct(k["conversao_pct"]))
with linha2[1]:
    st.metric("Inadimplência 30+", pct(k["inadimplencia_30d_pct"]),
              help="Contratos com ao menos uma parcela não paga há 30+ dias / contratos liberados do filtro")
with linha2[2]:
    st.metric("Tempo médio de decisão", f"{n(k['sla_medio_horas'], 1)} h")
with linha2[3]:
    st.metric("Valor vencido 30+", real(k["valor_vencido_30d"], compacto=True))

st.write("")
t1, t2, t3, t4 = st.tabs(["📊 Visão geral", "🏢 Parceiros", "💳 Crédito & risco", "🗃️ Dados & SQL"])

with t1:
    mensal = resumo_mensal(filtrados)
    a, b = st.columns([1.7, 1], gap="large")
    with a:
        st.subheader("Evolução da operação")
        st.caption("Solicitações e contratos liberados por mês da solicitação")
        fig = go.Figure()
        fig.add_bar(x=mensal["mes"], y=mensal["solicitacoes"], name="Solicitações",
                    marker_color=CORES["azul"], opacity=.86)
        fig.add_bar(x=mensal["mes"], y=mensal["desembolsadas"], name="Liberados",
                    marker_color=CORES["verde"], opacity=.92)
        fig.update_layout(barmode="group", bargap=.32)
        st.plotly_chart(grafico_base(fig, 380), use_container_width=True, config={"displaylogo": False})
    with b:
        st.subheader("Etapas do funil")
        st.caption("Distribuição exclusiva do status final das solicitações")
        etapas = filtrados["status"].value_counts()
        ordem = ["desembolsada", "aprovada", "reprovada"]
        valores = [int(etapas.get(x, 0)) for x in ordem]
        fig = go.Figure(go.Pie(
            labels=["Liberadas", "Aprovadas, não liberadas", "Reprovadas"],
            values=valores, hole=.73,
            marker_colors=[CORES["verde"], CORES["amarelo"], CORES["vermelho"]],
            textinfo="percent", hovertemplate="%{label}<br>%{value} solicitações<extra></extra>",
        ))
        fig.update_layout(showlegend=True,
                          annotations=[dict(text=n(k["solicitacoes"]), x=.5, y=.53,
                                            showarrow=False, font=dict(size=28, color="#EEF6FD")),
                                       dict(text="solicitações", x=.5, y=.43,
                                            showarrow=False, font=dict(size=12, color="#A4B6CA"))])
        st.plotly_chart(grafico_base(fig, 380), use_container_width=True, config={"displaylogo": False})

    a, b = st.columns([1.25, 1], gap="large")
    with a:
        st.subheader("Volume financeiro por coorte")
        st.caption("Valor liberado vinculado ao mês da solicitação, não ao caixa do mês")
        fig = go.Figure(go.Scatter(
            x=mensal["mes"], y=mensal["valor_liberado"],
            mode="lines+markers", fill="tozeroy", name="Valor liberado",
            line=dict(color=CORES["verde"], width=3),
            fillcolor="rgba(74,223,192,0.09)",
            hovertemplate="%{x}<br>R$ %{y:,.2f}<extra></extra>",
        ))
        fig.update_yaxes(tickprefix="R$ ", tickformat="~s")
        st.plotly_chart(grafico_base(fig, 335), use_container_width=True, config={"displaylogo": False})
    with b:
        st.subheader("Conversão mensal")
        st.caption("Percentual de solicitações que viraram créditos liberados")
        fig = go.Figure(go.Scatter(
            x=mensal["mes"], y=mensal["conversao_pct"],
            mode="lines+markers", name="Conversão",
            line=dict(color=CORES["violeta"], width=3),
            marker=dict(size=7),
            hovertemplate="%{x}<br>%{y:.2f}%<extra></extra>",
        ))
        fig.update_yaxes(ticksuffix="%", range=[0, max(75, float(mensal["conversao_pct"].max()) + 10)])
        st.plotly_chart(grafico_base(fig, 335), use_container_width=True, config={"displaylogo": False})

with t2:
    parceiros = resumo_parceiros(filtrados)
    st.subheader("Performance das imobiliárias")
    st.caption("Ranking por principal liberado, com conversão e risco apurados para o mesmo grupo filtrado")
    a, b = st.columns([1.2, 1], gap="large")
    with a:
        top = parceiros.nlargest(10, "valor_liberado").sort_values("valor_liberado")
        fig = go.Figure(go.Bar(
            x=top["valor_liberado"], y=top["nome_parceiro"], orientation="h",
            marker_color=CORES["azul"], name="Valor liberado",
            hovertemplate="%{y}<br>R$ %{x:,.2f}<extra></extra>",
        ))
        fig.update_xaxes(tickprefix="R$ ", tickformat="~s")
        st.plotly_chart(grafico_base(fig, 460, horizontal=True), use_container_width=True, config={"displaylogo": False})
    with b:
        st.markdown("#### Comparativo de conversão e risco")
        st.caption("Tamanho da bolha = quantidade de contratos liberados")
        fig = go.Figure(go.Scatter(
            x=parceiros["conversao_pct"], y=parceiros["inadimplencia_30d_pct"],
            text=parceiros["nome_parceiro"],
            mode="markers", name="Parceiros",
            marker=dict(size=parceiros["desembolsadas"].clip(lower=1).pow(.5) * 3.2,
                        color=CORES["verde"], opacity=.78, line=dict(color="#0B1320", width=1)),
            hovertemplate="%{text}<br>Conversão: %{x:.1f}%<br>Inadimplência: %{y:.1f}%<extra></extra>",
        ))
        fig.update_xaxes(title_text="Conversão (%)", ticksuffix="%")
        fig.update_yaxes(title_text="Inadimplência 30+ (%)", ticksuffix="%")
        st.plotly_chart(grafico_base(fig, 460), use_container_width=True, config={"displaylogo": False})
    st.markdown("#### Tabela comparativa")
    exibir = parceiros[[
        "nome_parceiro", "uf_parceiro", "solicitacoes", "desembolsadas",
        "conversao_pct", "valor_liberado", "inadimplentes",
        "inadimplencia_30d_pct", "sla_medio_horas",
    ]].rename(columns={
        "nome_parceiro": "Imobiliária", "uf_parceiro": "UF", "solicitacoes": "Solicitações",
        "desembolsadas": "Liberadas", "conversao_pct": "Conversão (%)",
        "valor_liberado": "Valor liberado (R$)", "inadimplentes": "Contratos 30+",
        "inadimplencia_30d_pct": "Inadimplência (%)", "sla_medio_horas": "SLA (h)",
    }).round(2)
    st.dataframe(exibir, hide_index=True, use_container_width=True, height=380)
    st.download_button("⬇ Exportar desempenho por parceiro", exibir.to_csv(index=False, sep=";").encode("utf-8-sig"),
                       "performance_parceiros_filtrada.csv", mime="text/csv")

with t3:
    a, b, c = st.columns(3)
    with a:
        st.metric("Contratos com atraso 30+", n(k["inadimplentes"]))
    with b:
        st.metric("Total de custo operacional", real(k["custo_operacional"], compacto=True))
    with c:
        st.metric("Revisões manuais", n(k["revisoes_manuais"]))
    a, b = st.columns([1, 1.1], gap="large")
    with a:
        st.subheader("Risco por faixa de score")
        st.caption("% de contratos com parcelas abertas e atraso mínimo de 30 dias")
        tab_risco = resumo_risco(filtrados)
        if not tab_risco.empty:
            fig = go.Figure(go.Bar(
                x=tab_risco["faixa_risco"], y=tab_risco["inadimplencia_pct"],
                marker_color=[CORES["verde"] if x == "Baixo" else
                              CORES["amarelo"] if x == "Médio" else CORES["vermelho"]
                              for x in tab_risco["faixa_risco"]],
                text=[pct(v) for v in tab_risco["inadimplencia_pct"]], textposition="outside",
                hovertemplate="%{x}<br>Inadimplência: %{y:.2f}%<extra></extra>",
            ))
            fig.update_yaxes(ticksuffix="%", range=[0, max(15, float(tab_risco["inadimplencia_pct"].max()) * 1.3)])
            st.plotly_chart(grafico_base(fig, 370), use_container_width=True, config={"displaylogo": False})
        else:
            st.info("Este filtro não contém contratos liberados.")
    with b:
        st.subheader("Eficiência da revisão manual")
        st.caption("SLA médio da decisão e custo operacional por tipo de processo")
        revisoes = filtrados.groupby("revisao_manual").agg(
            solicitacoes=("solicitacao_id", "size"),
            sla=("sla_horas", "mean"),
            custo=("custo_operacional", "mean"),
        )
        revisoes.index = revisoes.index.map({0: "Sem revisão", 1: "Com revisão"})
        fig = go.Figure()
        fig.add_bar(x=revisoes.index, y=revisoes["sla"], name="SLA médio (h)", marker_color=CORES["violeta"])
        fig.add_bar(x=revisoes.index, y=revisoes["custo"], name="Custo médio (R$)", marker_color=CORES["amarelo"])
        fig.update_layout(barmode="group")
        st.plotly_chart(grafico_base(fig, 370), use_container_width=True, config={"displaylogo": False})
    st.info(
        "**Como ler a inadimplência:** o indicador é uma fotografia de "
        f"{DATA_REFERENCIA.strftime('%d/%m/%Y')}, mesmo que você filtre meses anteriores. "
        "Não é uma série histórica de inadimplência, e não equivale ao saldo devedor em risco (EAD)."
    )

with t4:
    st.subheader("Explorador de solicitações")
    st.caption("Dados anônimos e fictícios. A tabela abaixo respeita todos os filtros da barra lateral.")
    busca = st.text_input("Localizar solicitação ou contrato", placeholder="Ex.: SOL000001 ou CTR000001")
    base = filtrados.copy()
    if busca.strip():
        termo = busca.strip().upper()
        base = base.loc[
            base["solicitacao_id"].str.contains(termo, regex=False, case=False) |
            base["contrato_id"].fillna("").str.contains(termo, regex=False, case=False)
        ]
    cols = ["solicitacao_id", "data_solicitacao", "nome_parceiro", "status", "faixa_risco",
            "valor_solicitado", "valor_liberado", "sla_horas", "inadimplente_30d", "contrato_id"]
    visao = base[cols].rename(columns={
        "solicitacao_id": "Solicitação", "data_solicitacao": "Data", "nome_parceiro": "Imobiliária",
        "status": "Status", "faixa_risco": "Risco", "valor_solicitado": "Solicitado (R$)",
        "valor_liberado": "Liberado (R$)", "sla_horas": "SLA (h)",
        "inadimplente_30d": "Atraso 30+", "contrato_id": "Contrato",
    })
    st.dataframe(visao, hide_index=True, use_container_width=True, height=420)
    st.caption(f"{n(len(visao))} registros encontrados")
    st.download_button(
        "⬇ Exportar dados filtrados (CSV)",
        base.to_csv(index=False, sep=";").encode("utf-8-sig"),
        "solicitacoes_analise_credito.csv", mime="text/csv",
    )
    st.markdown("#### SQL que alimenta a análise")
    st.caption("Exemplo de consulta SQL do projeto; os indicadores do painel são recalculados a partir do SQLite após aplicar os filtros.")
    st.code(
        """SELECT p.nome_parceiro,
       COUNT(*) AS solicitacoes,
       SUM(CASE WHEN s.status = 'desembolsada' THEN 1 ELSE 0 END) AS liberadas,
       ROUND(100.0 * SUM(CASE WHEN s.status = 'desembolsada' THEN 1 ELSE 0 END)
             / NULLIF(COUNT(*), 0), 2) AS conversao_pct
FROM solicitacoes s
JOIN parceiros p ON p.parceiro_id = s.parceiro_id
GROUP BY p.nome_parceiro
ORDER BY conversao_pct DESC;""",
        language="sql",
    )

st.markdown('<div class="subtle"></div>', unsafe_allow_html=True)
st.caption(
    "ATLAS CREDIT LAB  ·  Protótipo de análise financeira para portfólio  ·  "
    "Sem dados pessoais reais  ·  Sem vínculo com a CashGO ou qualquer instituição financeira"
)
