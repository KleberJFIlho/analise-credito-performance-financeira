"""Simulador reprodutível de operações de crédito fictícias para fins educacionais."""
from __future__ import annotations

import calendar
import random
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

DATA_REFERENCIA = date(2026, 10, 1)
SEMENTE = 20261020


def adicionar_meses(data: date, quantidade: int) -> date:
    mes_zero = data.month - 1 + quantidade
    ano = data.year + mes_zero // 12
    mes = mes_zero % 12 + 1
    return date(ano, mes, min(data.day, calendar.monthrange(ano, mes)[1]))


def gerar_bases(pasta: Path, n_solicitacoes: int = 2400, semente: int = SEMENTE) -> dict[str, pd.DataFrame]:
    pasta.mkdir(parents=True, exist_ok=True)
    rng = random.Random(semente)
    ufs = ["MG", "SP", "RJ", "PR", "GO", "SC", "BA", "RS", "DF", "PE"]
    parceiros = []
    for i in range(1, 26):
        parceiros.append({"parceiro_id": f"PAR{i:03}",
                          "nome_parceiro": f"Imobiliária Fictícia {i:02}",
                          "uf": rng.choice(ufs),
                          "porte": rng.choices(["Pequeno", "Médio", "Grande"], weights=[5, 3, 2])[0]})

    clientes = []
    for i in range(1, 1501):
        score = rng.randint(420, 885)
        faixa = "Baixo" if score >= 740 else "Médio" if score >= 610 else "Alto"
        clientes.append({"cliente_id": f"CLI{i:05}", "uf": rng.choice(ufs),
                         "renda_mensal": round(rng.uniform(2300, 17500), 2),
                         "score_credito": score, "faixa_risco": faixa})

    inicio, fim = datetime(2025, 1, 1), datetime(2026, 9, 18)
    horizonte_horas = int((fim - inicio).total_seconds() // 3600)
    solicitacoes, contratos, parcelas = [], [], []
    clientes_por_id = {c["cliente_id"]: c for c in clientes}
    prazo_padrao = [6, 12, 18]
    for n in range(1, n_solicitacoes + 1):
        cliente = clientes_por_id[rng.choice(clientes)["cliente_id"]]
        parceiro = rng.choice(parceiros)
        data_solicitacao = inicio + timedelta(hours=rng.randrange(horizonte_horas), minutes=rng.randrange(60))
        manual = 1 if rng.random() < 0.29 else 0
        sla = round(max(0.5, rng.lognormvariate(2.65, 0.66) + manual * rng.uniform(8, 38)), 2)
        data_decisao = data_solicitacao + timedelta(hours=sla)
        prob_aprovacao = {"Baixo": 0.82, "Médio": 0.65, "Alto": 0.38}[cliente["faixa_risco"]]
        if rng.random() > prob_aprovacao:
            status = "reprovada"
        elif rng.random() < 0.83:
            status = "desembolsada"
        else:
            status = "aprovada"
        valor_pedido = round(rng.uniform(5000, 85000) / 100) * 100
        custo = round(10 + 1.18 * sla + manual * 18 + rng.uniform(0, 12), 2)
        solicitacao_id = f"SOL{n:06}"
        solicitacoes.append({
            "solicitacao_id": solicitacao_id, "cliente_id": cliente["cliente_id"],
            "parceiro_id": parceiro["parceiro_id"], "data_solicitacao": data_solicitacao.strftime("%Y-%m-%d %H:%M:%S"),
            "data_decisao": data_decisao.strftime("%Y-%m-%d %H:%M:%S"),
            "status": status, "valor_solicitado": valor_pedido,
            "sla_horas": sla, "revisao_manual": manual, "custo_operacional": custo,
        })
        if status != "desembolsada":
            continue
        id_contrato = f"CTR{len(contratos) + 1:06}"
        data_liberacao = (data_decisao + timedelta(days=rng.randint(1, 5))).date()
        principal = round(valor_pedido * rng.uniform(0.82, 1.0), 2)
        prazo = rng.choice(prazo_padrao)
        taxa_juros_anual = round(rng.uniform(12, 28), 2)
        juro_mensal = taxa_juros_anual / 1200
        parcela_fixa = round(principal * (juro_mensal / (1 - (1 + juro_mensal) ** (-prazo))), 2)
        contratos.append({
            "contrato_id": id_contrato, "solicitacao_id": solicitacao_id,
            "data_liberacao": data_liberacao.isoformat(), "valor_liberado": principal,
            "prazo_meses": prazo, "taxa_juros_anual_pct": taxa_juros_anual,
            "valor_parcela": parcela_fixa,
        })
        # Inadimplência simulada no nível do contrato: risco correlacionado por cliente.
        # Evita tratar cada parcela como uma chance independente de default e
        # produzir taxas cumulativas artificialmente altíssimas.
        prob_default = {"Baixo": 0.08, "Médio": 0.15, "Alto": 0.25}[cliente["faixa_risco"]]
        com_problema = rng.random() < prob_default
        parcela_inicio_atraso = rng.randint(2, min(prazo, 8)) if com_problema else prazo + 1
        for numero in range(1, prazo + 1):
            vencimento = adicionar_meses(data_liberacao, numero)
            pagamento = None
            valor_pago = 0.0
            if vencimento <= DATA_REFERENCIA:
                if numero < parcela_inicio_atraso:
                    # Contratos sem default podem apresentar pequenos atrasos operacionais.
                    sorte = rng.random()
                    atraso_dias = rng.randint(-5, 0) if sorte < 0.84 else rng.randint(1, 18)
                    previsto = max(data_liberacao, vencimento + timedelta(days=atraso_dias))
                    if previsto <= DATA_REFERENCIA:
                        pagamento = previsto
                        valor_pago = parcela_fixa
            parcelas.append({"parcela_id": f"PRC{len(parcelas)+1:07}",
                             "contrato_id": id_contrato, "numero_parcela": numero,
                             "vencimento": vencimento.isoformat(),
                             "pagamento": pagamento.isoformat() if pagamento else None,
                             "valor_previsto": parcela_fixa, "valor_pago": valor_pago})

    bases = {
        "parceiros": pd.DataFrame(parceiros), "clientes": pd.DataFrame(clientes),
        "solicitacoes": pd.DataFrame(solicitacoes), "contratos": pd.DataFrame(contratos),
        "parcelas": pd.DataFrame(parcelas),
    }
    for nome, tabela in bases.items():
        tabela.to_csv(pasta / f"{nome}.csv", index=False, encoding="utf-8-sig")
    return bases
