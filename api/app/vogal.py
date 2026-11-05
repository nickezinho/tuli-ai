"""Jogo "Segure o aaaa": estabilidade da voz numa vogal sustentada, medida com o Praat (Parselmouth).

Passos:
1. Acha o pitch (F0) quadro a quadro e pega o maior trecho contínuo com voz.
2. Corta 0,25 s do começo e do fim desse trecho, onde a voz ainda está entrando ou saindo.
3. Mede no trecho estável: F0 médio e desvio, jitter local, shimmer local e HNR.

Os parâmetros são os padrões do Praat para voz (os mesmos da literatura de voz e Parkinson).
"""

import numpy as np
import parselmouth
from parselmouth.praat import call

from .audio import TAXA, nivel_dbfs
from .modelos import MetricaPrincipal, MetricasVogal, Qualidade, RespostaVogal

F0_MIN = 75.0
F0_MAX = 500.0
PASSO_S = 0.01
MIN_VOZ_S = 2.0  # menos que isso de vogal estável não dá medida confiável
CORTE_BORDA_S = 0.25
LIMIAR_SILENCIO_DBFS = -55.0


def _falha(motivo: str) -> RespostaVogal:
    return RespostaVogal(qualidade=Qualidade(ok=False, motivo=motivo), metricas=None, metrica_principal=None)


def _maior_trecho_com_voz(f0: np.ndarray) -> tuple[int, int]:
    """Índices [ini, fim) do maior trecho de quadros com F0 > 0, tolerando buracos de até 50 ms."""
    com_voz = f0 > 0
    tolerancia = 5
    melhor = (0, 0)
    ini = None
    buraco = 0
    for i, v in enumerate(com_voz):
        if v:
            if ini is None:
                ini = i
            buraco = 0
            fim = i + 1
            if fim - ini > melhor[1] - melhor[0]:
                melhor = (ini, fim)
        elif ini is not None:
            buraco += 1
            if buraco > tolerancia:
                ini = None
    return melhor


def analisar_vogal(amostras: np.ndarray) -> RespostaVogal:
    if amostras.size < TAXA * 0.5 or nivel_dbfs(amostras) < LIMIAR_SILENCIO_DBFS:
        return _falha("audio_silencioso")

    som = parselmouth.Sound(amostras.astype(np.float64), sampling_frequency=TAXA)
    pitch = som.to_pitch(time_step=PASSO_S, pitch_floor=F0_MIN, pitch_ceiling=F0_MAX)
    f0 = pitch.selected_array["frequency"]
    tempos = pitch.xs()

    ini, fim = _maior_trecho_com_voz(f0)
    if fim - ini == 0:
        return _falha("audio_silencioso")
    t_ini, t_fim = tempos[ini], tempos[fim - 1]
    duracao_voz = t_fim - t_ini
    if duracao_voz < MIN_VOZ_S:
        return _falha("audio_curto")

    trecho = som.extract_part(from_time=t_ini + CORTE_BORDA_S, to_time=t_fim - CORTE_BORDA_S, preserve_times=False)
    pitch_t = trecho.to_pitch(time_step=PASSO_S, pitch_floor=F0_MIN, pitch_ceiling=F0_MAX)
    f0_t = pitch_t.selected_array["frequency"]
    f0_t = f0_t[f0_t > 0]
    if f0_t.size < 10:
        return _falha("audio_silencioso")

    pontos = call(trecho, "To PointProcess (periodic, cc)", F0_MIN, F0_MAX)
    jitter = call(pontos, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
    shimmer = call([trecho, pontos], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
    harm = call(trecho, "To Harmonicity (cc)", PASSO_S, F0_MIN, 0.1, 1.0)
    hnr = call(harm, "Get mean", 0, 0)

    if not all(np.isfinite(v) for v in (jitter, shimmer, hnr)):
        return _falha("audio_silencioso")

    metricas = MetricasVogal(
        duracao_s=round(float(duracao_voz), 2),
        f0_medio_hz=round(float(np.mean(f0_t)), 1),
        f0_desvio_hz=round(float(np.std(f0_t)), 2),
        jitter_pct=round(float(jitter) * 100, 3),
        shimmer_pct=round(float(shimmer) * 100, 2),
        hnr_db=round(float(hnr), 1),
    )
    return RespostaVogal(
        qualidade=Qualidade(ok=True),
        metricas=metricas,
        metrica_principal=MetricaPrincipal(nome="jitter_pct", valor=metricas.jitter_pct),
    )
