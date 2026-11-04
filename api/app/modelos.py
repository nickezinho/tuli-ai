"""Modelos do contrato B (backend <-> análise). Espelham docs/contrato.md."""

from typing import Literal, Optional

from pydantic import BaseModel, Field

Jogo = Literal["vogal", "pataka", "espiral", "tapping"]
Mao = Literal["direita", "esquerda"]
MotivoQualidade = Literal["audio_silencioso", "audio_curto", "poucos_toques", "traco_incompleto"]


class Qualidade(BaseModel):
    ok: bool
    motivo: Optional[MotivoQualidade] = None


class MetricaPrincipal(BaseModel):
    nome: str
    valor: float


# ---------- Entradas dos jogos de toque ----------


class Ponto(BaseModel):
    t_ms: float
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)


class EntradaEspiral(BaseModel):
    mao: Mao
    duracao_ms: float
    pontos: list[Ponto]


class Alvo(BaseModel):
    x: float
    y: float


class Alvos(BaseModel):
    a: Alvo
    b: Alvo
    raio: float


class EntradaTapping(BaseModel):
    mao: Mao
    duracao_ms: float
    alvos: Alvos
    toques: list[Ponto]


# ---------- Respostas ----------


class MetricasVogal(BaseModel):
    duracao_s: float
    f0_medio_hz: float
    f0_desvio_hz: float
    jitter_pct: float
    shimmer_pct: float
    hnr_db: float


class MetricasPataka(BaseModel):
    duracao_s: float
    silabas_por_s: float
    intervalo_cv: float


class MetricasEspiral(BaseModel):
    duracao_s: float
    desvio_medio: float
    tremor_hz: float
    velocidade_media: float


class MetricasTapping(BaseModel):
    toques_por_s: float
    intervalo_cv: float
    precisao_pct: float
    queda_ritmo_pct: float


class RespostaVogal(BaseModel):
    qualidade: Qualidade
    metricas: Optional[MetricasVogal]
    metrica_principal: Optional[MetricaPrincipal]


class RespostaPataka(BaseModel):
    qualidade: Qualidade
    metricas: Optional[MetricasPataka]
    metrica_principal: Optional[MetricaPrincipal]


class RespostaEspiral(BaseModel):
    qualidade: Qualidade
    metricas: Optional[MetricasEspiral]
    metrica_principal: Optional[MetricaPrincipal]


class RespostaTapping(BaseModel):
    qualidade: Qualidade
    metricas: Optional[MetricasTapping]
    metrica_principal: Optional[MetricaPrincipal]


# ---------- Comparação com a linha de base ----------


class PontoSerie(BaseModel):
    dia: str  # YYYY-MM-DD
    valor: float


class EntradaComparar(BaseModel):
    jogo: Jogo
    metrica: str
    maior_e_melhor: bool
    serie: list[PontoSerie]


class LinhaDeBase(BaseModel):
    media: float
    desvio: float
    n: int


class Recente(BaseModel):
    media: float
    n: int


class RespostaComparar(BaseModel):
    status: Literal["estavel", "mudou", "sem_dados"]
    linha_de_base: Optional[LinhaDeBase]
    recente: Optional[Recente]
    z: Optional[float]
    direcao: Optional[Literal["piorou", "melhorou", "igual"]]
