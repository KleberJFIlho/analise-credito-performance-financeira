"""Valida métricas e filtros do dashboard sem precisar instalar Streamlit."""
import unittest

from src.dashboard_data import (
    carregar_dados, calcular_kpis, filtrar_dados,
    resumo_mensal, resumo_parceiros, resumo_risco,
)


class TestDashboardData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dados = carregar_dados()

    def test_base_sem_duplicacao(self):
        self.assertEqual(len(self.dados), 2400)
        self.assertTrue(self.dados["solicitacao_id"].is_unique)
        self.assertEqual(int(self.dados["contrato_id"].notna().sum()), 1213)

    def test_kpis_coerentes(self):
        k = calcular_kpis(self.dados)
        self.assertEqual(k["solicitacoes"], 2400)
        self.assertEqual(k["aprovadas"], 1446)
        self.assertEqual(k["desembolsadas"], 1213)
        self.assertAlmostEqual(k["aprovacao_pct"], 60.25, places=2)
        self.assertEqual(k["inadimplentes"], 126)
        self.assertAlmostEqual(k["inadimplencia_30d_pct"], 100 * 126 / 1213)

    def test_total_por_mes_e_parceiro(self):
        self.assertEqual(int(resumo_mensal(self.dados)["solicitacoes"].sum()), 2400)
        p = resumo_parceiros(self.dados)
        self.assertEqual(int(p["solicitacoes"].sum()), 2400)
        self.assertEqual(int(p["desembolsadas"].sum()), 1213)
        self.assertEqual(int(p["inadimplentes"].sum()), 126)

    def test_filtros_combinados(self):
        f = filtrar_dados(self.dados, meses=("2026-01", "2026-06"),
                          ufs=["MG"], riscos=["Baixo"], status=["desembolsada"])
        self.assertFalse(f.empty)
        self.assertTrue(f["mes"].between("2026-01", "2026-06").all())
        self.assertTrue((f["uf_parceiro"] == "MG").all())
        self.assertTrue((f["faixa_risco"] == "Baixo").all())
        self.assertTrue((f["status"] == "desembolsada").all())
        self.assertEqual(calcular_kpis(f)["desembolsadas"], len(f))

    def test_filtro_sem_contratos(self):
        f = filtrar_dados(self.dados, status=["reprovada"])
        k = calcular_kpis(f)
        self.assertEqual(k["desembolsadas"], 0)
        self.assertEqual(k["inadimplentes"], 0)
        self.assertEqual(k["inadimplencia_30d_pct"], 0)
        self.assertTrue(resumo_risco(f).empty)

    def test_filtro_vazio(self):
        f = filtrar_dados(self.dados, ufs=["XX"])
        self.assertTrue(f.empty)
        self.assertEqual(calcular_kpis(f)["solicitacoes"], 0)


if __name__ == "__main__":
    unittest.main()
