"""Serviço de análise (parte 2). Contrato B em docs/contrato.md.

vogal, pataka e espiral ainda devolvem valores fixos (mock) para o backend e o app
já poderem integrar. Cada TODO marca onde entra a análise de verdade.
"""

from fastapi import FastAPI, File, UploadFile

from .comparar import comparar
from .modelos import (
    EntradaComparar,
    EntradaEspiral,
    EntradaTapping,
    MetricaPrincipal,
    MetricasEspiral,
    MetricasPataka,
    MetricasVogal,
    Qualidade,
    RespostaComparar,
    RespostaEspiral,
    RespostaPataka,
    RespostaTapping,
    RespostaVogal,
)
from .tapping import analisar_tapping

app = FastAPI(title="Tuli: análise", version="0.1.0")


@app.get("/saude")
def saude() -> dict:
    return {"ok": True}


@app.post("/analisar/vogal", response_model=RespostaVogal)
async def analisar_vogal(audio: UploadFile = File(...)) -> RespostaVogal:
    dados = await audio.read()
    if len(dados) == 0:
        return RespostaVogal(qualidade=Qualidade(ok=False, motivo="audio_silencioso"), metricas=None, metrica_principal=None)
    # TODO(parte 2): converter para WAV 16 kHz e medir com parselmouth (pitch, jitter local, shimmer local, HNR).
    metricas = MetricasVogal(duracao_s=9.8, f0_medio_hz=182.0, f0_desvio_hz=3.1, jitter_pct=0.62, shimmer_pct=3.4, hnr_db=21.5)
    return RespostaVogal(
        qualidade=Qualidade(ok=True),
        metricas=metricas,
        metrica_principal=MetricaPrincipal(nome="jitter_pct", valor=metricas.jitter_pct),
    )


@app.post("/analisar/pataka", response_model=RespostaPataka)
async def analisar_pataka(audio: UploadFile = File(...)) -> RespostaPataka:
    dados = await audio.read()
    if len(dados) == 0:
        return RespostaPataka(qualidade=Qualidade(ok=False, motivo="audio_silencioso"), metricas=None, metrica_principal=None)
    # TODO(parte 2): detectar as sílabas com librosa (onset_detect na energia) e medir ritmo e regularidade.
    metricas = MetricasPataka(duracao_s=10.0, silabas_por_s=6.1, intervalo_cv=0.14)
    return RespostaPataka(
        qualidade=Qualidade(ok=True),
        metricas=metricas,
        metrica_principal=MetricaPrincipal(nome="silabas_por_s", valor=metricas.silabas_por_s),
    )


@app.post("/analisar/espiral", response_model=RespostaEspiral)
def analisar_espiral(entrada: EntradaEspiral) -> RespostaEspiral:
    if len(entrada.pontos) < 30:
        return RespostaEspiral(qualidade=Qualidade(ok=False, motivo="traco_incompleto"), metricas=None, metrica_principal=None)
    # TODO(parte 2): reconstruir o guia (Arquimedes, centro 0.5/0.5, 3 voltas, raio 0.45),
    # medir a distância de cada ponto ao guia e o tremor pela FFT do erro radial.
    metricas = MetricasEspiral(duracao_s=entrada.duracao_ms / 1000, desvio_medio=0.021, tremor_hz=0.0, velocidade_media=0.11)
    return RespostaEspiral(
        qualidade=Qualidade(ok=True),
        metricas=metricas,
        metrica_principal=MetricaPrincipal(nome="desvio_medio", valor=metricas.desvio_medio),
    )


@app.post("/analisar/tapping", response_model=RespostaTapping)
def analisar_tapping_rota(entrada: EntradaTapping) -> RespostaTapping:
    return analisar_tapping(entrada)


@app.post("/comparar", response_model=RespostaComparar)
def comparar_rota(entrada: EntradaComparar) -> RespostaComparar:
    return comparar(entrada)
