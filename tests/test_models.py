"""Testes dos modelos de domínio."""

from src.domain.models import (
    RegularizacaoState,
    ApoState,
    CenarioRegularizacao,
    TipoImovel,
    Escritura,
    TipoAPO,
    ReusoState,
)


class TestRegularizacaoState:
    def test_creation_minimal(self):
        state = RegularizacaoState(cenario=CenarioRegularizacao.EXISTENTE)
        assert state.cenario == CenarioRegularizacao.EXISTENTE
        assert state.tipo_imovel is None
        assert state.escritura is None
        assert state.cidade is None
        assert state.ultimo_checklist == ""

    def test_creation_full(self):
        state = RegularizacaoState(
            cenario=CenarioRegularizacao.PROJETO_NOVO,
            tipo_imovel=TipoImovel.CASA,
            escritura=Escritura.SIM,
            cidade="São Paulo - SP",
        )
        assert state.tipo_imovel == TipoImovel.CASA
        assert state.escritura == Escritura.SIM
        assert state.cidade == "São Paulo - SP"

    def test_resumo_dados_empty(self):
        state = RegularizacaoState(cenario=CenarioRegularizacao.CONSULTA_LIVRE)
        assert state.resumo_dados() == ""

    def test_resumo_dados_full(self):
        state = RegularizacaoState(
            cenario=CenarioRegularizacao.EXISTENTE,
            tipo_imovel=TipoImovel.APARTAMENTO,
            escritura=Escritura.NAO,
            cidade="Cuiabá - MT",
        )
        resumo = state.resumo_dados()
        assert "Apartamento" in resumo
        assert "Não" in resumo
        assert "Cuiabá" in resumo


class TestApoState:
    def test_creation_usuario(self):
        state = ApoState(tipo=TipoAPO.USUARIO)
        assert state.tipo == TipoAPO.USUARIO

    def test_creation_especialista(self):
        state = ApoState(tipo=TipoAPO.ESPECIALISTA)
        assert state.tipo == TipoAPO.ESPECIALISTA


class TestEnums:
    def test_tipo_imovel_values(self):
        assert TipoImovel.CASA.value == "Casa"
        assert TipoImovel.MISTO.value == "Misto"

    def test_escritura_values(self):
        assert Escritura.CONTRATO.value == "Só contrato de compra e venda"

    def test_cenario_members(self):
        assert len(CenarioRegularizacao) == 3


class TestReusoState:
    def test_creation_defaults(self):
        state = ReusoState()
        assert state.cidade is None
        assert state.area is None
        assert state.moradores is None

    def test_creation_with_data(self):
        state = ReusoState(cidade="Santos", area="100", moradores="4")
        assert state.cidade == "Santos"
        assert state.area == "100"
        assert state.moradores == "4"
