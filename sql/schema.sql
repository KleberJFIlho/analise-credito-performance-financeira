PRAGMA foreign_keys = ON;
DROP TABLE IF EXISTS parcelas;
DROP TABLE IF EXISTS contratos;
DROP TABLE IF EXISTS solicitacoes;
DROP TABLE IF EXISTS clientes;
DROP TABLE IF EXISTS parceiros;

CREATE TABLE parceiros (
    parceiro_id TEXT PRIMARY KEY,
    nome_parceiro TEXT NOT NULL,
    uf TEXT NOT NULL,
    porte TEXT NOT NULL
);

CREATE TABLE clientes (
    cliente_id TEXT PRIMARY KEY,
    uf TEXT NOT NULL,
    renda_mensal REAL NOT NULL CHECK (renda_mensal > 0),
    score_credito INTEGER NOT NULL CHECK (score_credito BETWEEN 300 AND 900),
    faixa_risco TEXT NOT NULL CHECK (faixa_risco IN ('Baixo', 'Médio', 'Alto'))
);

CREATE TABLE solicitacoes (
    solicitacao_id TEXT PRIMARY KEY,
    cliente_id TEXT NOT NULL REFERENCES clientes(cliente_id),
    parceiro_id TEXT NOT NULL REFERENCES parceiros(parceiro_id),
    data_solicitacao TEXT NOT NULL,
    data_decisao TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('reprovada', 'aprovada', 'desembolsada')),
    valor_solicitado REAL NOT NULL CHECK (valor_solicitado > 0),
    sla_horas REAL NOT NULL CHECK (sla_horas >= 0),
    revisao_manual INTEGER NOT NULL CHECK (revisao_manual IN (0,1)),
    custo_operacional REAL NOT NULL CHECK (custo_operacional >= 0)
);

CREATE TABLE contratos (
    contrato_id TEXT PRIMARY KEY,
    solicitacao_id TEXT NOT NULL UNIQUE REFERENCES solicitacoes(solicitacao_id),
    data_liberacao TEXT NOT NULL,
    valor_liberado REAL NOT NULL CHECK (valor_liberado > 0),
    prazo_meses INTEGER NOT NULL CHECK (prazo_meses > 0),
    taxa_juros_anual_pct REAL NOT NULL CHECK (taxa_juros_anual_pct >= 0),
    valor_parcela REAL NOT NULL CHECK (valor_parcela > 0)
);

CREATE TABLE parcelas (
    parcela_id TEXT PRIMARY KEY,
    contrato_id TEXT NOT NULL REFERENCES contratos(contrato_id),
    numero_parcela INTEGER NOT NULL CHECK (numero_parcela > 0),
    vencimento TEXT NOT NULL,
    pagamento TEXT,
    valor_previsto REAL NOT NULL CHECK (valor_previsto > 0),
    valor_pago REAL NOT NULL CHECK (valor_pago >= 0),
    UNIQUE (contrato_id, numero_parcela)
);
CREATE INDEX idx_solicitacoes_parceiro ON solicitacoes(parceiro_id);
CREATE INDEX idx_solicitacoes_data ON solicitacoes(data_solicitacao);
CREATE INDEX idx_parcelas_contrato ON parcelas(contrato_id);
CREATE INDEX idx_parcelas_vencimento ON parcelas(vencimento);
