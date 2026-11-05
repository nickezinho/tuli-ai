"""Jogo "Pa-ta-ka" (diadococinesia): quantas sílabas por segundo e com que regularidade.

Cada sílaba tem um núcleo de vogal, que é um pico de energia. Então:
1. Calcula a energia (RMS) do áudio com librosa em janelas de 10 ms e suaviza.
2. Acha os picos com distância mínima de 70 ms (ninguém passa de ~14 sílabas/s)
   e proeminência mínima relativa ao volume da gravação, para ignorar ruído de fundo.
3. silabas_por_s = (n - 1) / (tempo do último pico - tempo do primeiro), ou seja,
   o ritmo enquanto a pessoa está falando, sem contar silêncio no começo e no fim.
4. intervalo_cv = desvio / média dos intervalos entre sílabas (quanto menor, mais regular).
"""

import librosa
import numpy as np
from scipy.signal import find_peaks

from .audio import TAXA, nivel_dbfs
from .modelos import MetricaPrincipal, MetricasPataka, Qualidade, RespostaPataka

SALTO = 160  # 10 ms a 16 kHz
JANELA = 512
DIST_MIN_S = 0.07
MIN_SILABAS = 6
MIN_FALA_S = 2.0
LIMIAR_SILENCIO_DBFS = -55.0


def _falha(motivo: str) -> RespostaPataka:
    return RespostaPataka(qualidade=Qualidade(ok=False, motivo=motivo), metricas=None, metrica_principal=None)


def detectar_silabas(amostras: np.ndarray) -> np.ndarray:
    """Tempos (s) dos núcleos de sílaba."""
    rms = librosa.feature.rms(y=amostras, frame_length=JANELA, hop_length=SALTO, center=True)[0]
    rms_db = librosa.amplitude_to_db(rms, ref=np.max, top_db=60)  # 0 dB no pico, piso em -60
    suave = np.convolve(rms_db, np.ones(3) / 3, mode="same")
    picos, _ = find_peaks(
        suave,
        distance=max(1, int(DIST_MIN_S * TAXA / SALTO)),
        prominence=6.0,  # o vale entre duas sílabas tem que cair pelo menos 6 dB
        height=-35.0,  # e o pico tem que estar a no máximo 35 dB do mais alto
    )
    return librosa.frames_to_time(picos, sr=TAXA, hop_length=SALTO)


def analisar_pataka(amostras: np.ndarray) -> RespostaPataka:
    if amostras.size < TAXA * 0.5 or nivel_dbfs(amostras) < LIMIAR_SILENCIO_DBFS:
        return _falha("audio_silencioso")

    tempos = detectar_silabas(amostras)
    if tempos.size < MIN_SILABAS:
        return _falha("audio_silencioso")
    fala_s = float(tempos[-1] - tempos[0])
    if fala_s < MIN_FALA_S:
        return _falha("audio_curto")

    intervalos = np.diff(tempos)
    metricas = MetricasPataka(
        duracao_s=round(amostras.size / TAXA, 2),
        silabas_por_s=round((tempos.size - 1) / fala_s, 2),
        intervalo_cv=round(float(np.std(intervalos) / np.mean(intervalos)), 3),
    )
    return RespostaPataka(
        qualidade=Qualidade(ok=True),
        metricas=metricas,
        metrica_principal=MetricaPrincipal(nome="silabas_por_s", valor=metricas.silabas_por_s),
    )
