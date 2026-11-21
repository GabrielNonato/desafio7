from typing import Literal, Optional
from pydantic import BaseModel, Field


class Verificacao(BaseModel):
    criterio: Literal[
        "cadastro",
        "dados_completos",
        "antecedencia",
        "prestacao_contas",
        "limite_mensal",
        "saldo_orcamentario",
    ]
    situacao: Literal["atende", "nao_atende", "nao_verificado"]
    detalhe: str


class Instrucao(BaseModel):
    numero_pedido: str
    matricula: str
    quantidade_diarias: Optional[float] = None
    valor_total: Optional[float] = None
    verificacoes: list[Verificacao]
    recomendacao: Literal["apto_para_autorizacao", "diligencia", "nao_recomendado"]
    exige_autorizacao_superior: bool
    pendencias: list[str] = Field(default_factory=list)
    alertas: list[str] = Field(default_factory=list)
    minuta_despacho: str
