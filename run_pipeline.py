"""Execute: python run_pipeline.py"""
from pathlib import Path

from src.simulacao import DATA_REFERENCIA, gerar_bases
from src.analise import montar_banco, exportar_indicadores
from src.visualizacao import criar_graficos

RAIZ = Path(__file__).resolve().parent


def main() -> None:
    print("1/4 - Gerando dados 100% fictícios...")
    bases = gerar_bases(RAIZ / "data" / "raw")
    print("2/4 - Criando SQLite com chaves e integridade...")
    banco = RAIZ / "data" / "credito_simulado.sqlite"
    montar_banco(banco, RAIZ / "sql", bases)
    print("3/4 - Executando consultas SQL e exportando indicadores...")
    tabelas = exportar_indicadores(banco, RAIZ / "sql", RAIZ / "output")
    print("4/4 - Gerando imagens para o portfólio...")
    criar_graficos(tabelas, RAIZ / "imagens")
    resumo = tabelas["kpis_gerais"].iloc[0]
    linhas = [
        "# Resumo executivo — dados fictícios",
        f"Data de referência: {DATA_REFERENCIA.isoformat()}",
        "", "Este material demonstra as métricas de um negócio hipotético, e não contém dados reais da CashGO.", "",
        f"- Solicitações: {int(resumo['solicitacoes']):,}".replace(",", "."),
        f"- Aprovação: {resumo['taxa_aprovacao_pct']:.2f}%",
        f"- Conversão em desembolso: {resumo['conversao_pct']:.2f}%",
        f"- SLA médio de decisão: {resumo['sla_medio_horas']:.2f} h",
        f"- Custo operacional médio por solicitação: R$ {resumo['custo_medio_operacao']:.2f}", "",
        "## Oportunidades de análise", "",
        "1. Comparar SLA e custo operacional por casos com e sem revisão manual.",
        "2. Verificar quais parceiros apresentam maior conversão com menor inadimplência 30+.",
        "3. Separar o volume por coorte de solicitação do caixa efetivamente desembolsado por data.",
        "4. Não usar scores simulados para decisões reais de crédito.", "",
        "**Atenção:** as métricas não representam resultados de nenhuma empresa real.",
    ]
    (RAIZ / "output" / "resumo_executivo.md").write_text("\n".join(linhas)+"\n", encoding="utf-8")
    print(f"Concluído. CSVs em data/raw e output; imagens em imagens; banco: {banco.name}")


if __name__ == "__main__":
    main()
