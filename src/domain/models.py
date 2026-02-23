from dataclasses import dataclass, field
from enum import Enum, auto


class TipoImovel(Enum):
    CASA = "Casa"
    APARTAMENTO = "Apartamento"
    COMERCIO = "Comércio"
    MISTO = "Misto"


class Escritura(Enum):
    SIM = "Sim"
    NAO = "Não"
    CONTRATO = "Só contrato de compra e venda"


class CenarioRegularizacao(Enum):
    EXISTENTE = auto()
    PROJETO_NOVO = auto()
    CONSULTA_LIVRE = auto()


class TipoAPO(Enum):
    USUARIO = auto()
    ESPECIALISTA = auto()


@dataclass
class RegularizacaoState:
    cenario: CenarioRegularizacao
    tipo_imovel: TipoImovel | None = None
    escritura: Escritura | None = None
    cidade: str | None = None
    ultimo_checklist: str = ""

    def resumo_dados(self) -> str:
        partes = []
        if self.tipo_imovel:
            partes.append(f"Tipo de imóvel: {self.tipo_imovel.value}")
        if self.escritura:
            partes.append(f"Possui escritura/matrícula: {self.escritura.value}")
        if self.cidade:
            partes.append(f"Localização: {self.cidade}")
        return ". ".join(partes) + "." if partes else ""


@dataclass
class ApoState:
    tipo: TipoAPO

@dataclass
class ReusoState:
    cidade: str | None = None
    area: str | None = None
    moradores: str | None = None

