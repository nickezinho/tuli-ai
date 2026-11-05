"""Serviço de análise (parte 2). Contrato B em docs/contrato.md.

Cada jogo tem seu módulo: vogal.py (Parselmouth), pataka.py (librosa), espiral.py e tapping.py.
"""

from fastapi import FastAPI, File, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse

from .audio import AudioInvalido, decodificar
from .comparar import comparar
from .espiral import analisar_espiral
from .modelos import (
    EntradaComparar,
    EntradaEspiral,
    EntradaTapping,
    Qualidade,
    RespostaComparar,
    RespostaEspiral,
    RespostaPataka,
    RespostaTapping,
    RespostaVogal,
)
from .pataka import analisar_pataka
from .tapping import analisar_tapping
from .vogal import analisar_vogal

app = FastAPI(title="Tuli: análise", version="0.2.0")


@app.get("/saude")
def saude() -> dict:
    return {"ok": True}


def _erro_audio(e: AudioInvalido) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"erro": "audio_invalido", "mensagem": f"Não consegui abrir o arquivo de áudio: {e}"},
    )


@app.post("/analisar/vogal", response_model=RespostaVogal, responses={422: {"description": "audio_invalido"}})
async def analisar_vogal_rota(audio: UploadFile = File(...)):
    dados = await audio.read()
    if len(dados) == 0:
        return RespostaVogal(qualidade=Qualidade(ok=False, motivo="audio_silencioso"), metricas=None, metrica_principal=None)
    try:
        amostras = await run_in_threadpool(decodificar, dados)
    except AudioInvalido as e:
        return _erro_audio(e)
    return await run_in_threadpool(analisar_vogal, amostras)


@app.post("/analisar/pataka", response_model=RespostaPataka, responses={422: {"description": "audio_invalido"}})
async def analisar_pataka_rota(audio: UploadFile = File(...)):
    dados = await audio.read()
    if len(dados) == 0:
        return RespostaPataka(qualidade=Qualidade(ok=False, motivo="audio_silencioso"), metricas=None, metrica_principal=None)
    try:
        amostras = await run_in_threadpool(decodificar, dados)
    except AudioInvalido as e:
        return _erro_audio(e)
    return await run_in_threadpool(analisar_pataka, amostras)


@app.post("/analisar/espiral", response_model=RespostaEspiral)
def analisar_espiral_rota(entrada: EntradaEspiral) -> RespostaEspiral:
    return analisar_espiral(entrada)


@app.post("/analisar/tapping", response_model=RespostaTapping)
def analisar_tapping_rota(entrada: EntradaTapping) -> RespostaTapping:
    return analisar_tapping(entrada)


@app.post("/comparar", response_model=RespostaComparar)
def comparar_rota(entrada: EntradaComparar) -> RespostaComparar:
    return comparar(entrada)
