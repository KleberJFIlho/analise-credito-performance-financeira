"""Testes automatizados com unittest, sem acesso à internet."""
import sqlite3
from contextlib import closing
import tempfile
import unittest
from pathlib import Path

from src.simulacao import DATA_REFERENCIA, gerar_bases
from src.analise import montar_banco, exportar_indicadores

ROOT = Path(__file__).resolve().parents[1]


class TestPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.temp.name)
        cls.bases = gerar_bases(cls.dir / "data", n_solicitacoes=400)
        cls.banco = cls.dir / "credito.sqlite"
        montar_banco(cls.banco, ROOT / "sql", cls.bases)
        cls.indicadores = exportar_indicadores(cls.banco, ROOT / "sql", cls.dir / "output")

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_quantidade_solicitacoes(self):
        self.assertEqual(len(self.bases["solicitacoes"]), 400)
        self.assertEqual(int(self.indicadores["kpis_gerais"].iloc[0]["solicitacoes"]), 400)
        self.assertEqual(int(self.indicadores["volume_mensal"]["solicitacoes"].sum()), 400)

    def test_integridade_referencial(self):
        with closing(sqlite3.connect(self.banco)) as con:
            self.assertEqual(con.execute("PRAGMA foreign_key_check").fetchall(), [])
            self.assertEqual(con.execute("SELECT COUNT(*) FROM contratos c LEFT JOIN solicitacoes s ON s.solicitacao_id=c.solicitacao_id WHERE s.solicitacao_id IS NULL").fetchone()[0], 0)

    def test_contratos_apenas_desembolsados(self):
        with closing(sqlite3.connect(self.banco)) as con:
            incorretos = con.execute("SELECT COUNT(*) FROM contratos c JOIN solicitacoes s ON s.solicitacao_id=c.solicitacao_id WHERE s.status != 'desembolsada'").fetchone()[0]
            self.assertEqual(incorretos, 0)
            liberados = con.execute("SELECT COUNT(*) FROM contratos").fetchone()[0]
            status = con.execute("SELECT COUNT(*) FROM solicitacoes WHERE status='desembolsada'").fetchone()[0]
            self.assertEqual(liberados, status)

    def test_parcelas_pagas_ate_data_de_referencia(self):
        with closing(sqlite3.connect(self.banco)) as con:
            problemas = con.execute(
                "SELECT COUNT(*) FROM parcelas WHERE (pagamento IS NOT NULL AND (pagamento > ? OR valor_pago <= 0)) "
                "OR (pagamento IS NULL AND valor_pago != 0)",
                (DATA_REFERENCIA.isoformat(),),
            ).fetchone()[0]
            self.assertEqual(problemas, 0)

    def test_inadimplencia_30_dias(self):
        risco = self.indicadores["contratos_risco"]
        self.assertTrue(risco["inadimplente_30d"].isin([0, 1]).all())
        self.assertTrue((risco.loc[risco["inadimplente_30d"] == 1, "dias_atraso_max"] >= 30).all())
        self.assertTrue((risco.loc[risco["inadimplente_30d"] == 0, "valor_vencido_30d"] == 0).all())

    def test_totais_consistentes_por_parceiro(self):
        parceiros = self.indicadores["desempenho_parceiros"]
        self.assertEqual(int(parceiros["solicitacoes"].sum()), 400)
        self.assertEqual(int(parceiros["desembolsadas"].sum()), len(self.bases["contratos"]))
        self.assertAlmostEqual(float(parceiros["valor_liberado"].sum()), float(self.bases["contratos"]["valor_liberado"].sum()), places=1)

    def test_reprodutibilidade(self):
        novo = gerar_bases(self.dir / "repeticao", n_solicitacoes=400)
        for nome in self.bases:
            self.assertTrue(self.bases[nome].equals(novo[nome]), nome)


if __name__ == "__main__":
    unittest.main()
