"""Jogo da espiral: quão longe o traço fica do guia e se há tremor.

O guia é uma espiral de Arquimedes (docs/contrato.md):
    r(θ) = 0,45 · θ / (6π),  θ de 0 a 6π (3 voltas)
    x = 0,5 + r·cos θ,  y = 0,5 + r·sen θ   (coordenadas normalizadas, y para baixo)
Como o app pode desenhar a espiral espelhada, a análise testa as duas versões e usa a mais próxima.

Métricas:
- desvio_medio: distância média de cada ponto do traço ao ponto mais próximo do guia.
- tremor_hz: frequência dominante da oscilação do erro radial na faixa de 3 a 12 Hz
  (tremor de repouso do Parkinson costuma ficar entre 4 e 6 Hz). 0 quando não há oscilação clara.
- velocidade_media: comprimento do traço dividido pelo tempo, em unidades normalizadas por segundo.
"""

import numpy as np
from scipy.signal import butter, filtfilt, welch

from .modelos import EntradaEspiral, MetricaPrincipal, MetricasEspiral, Qualidade, RespostaEspiral

CENTRO = np.array([0.5, 0.5])
VOLTAS = 3
RAIO_FINAL = 0.45
N_GUIA = 3000

MIN_PONTOS = 30
MIN_DURACAO_S = 2.0
MIN_COBERTURA = 0.6  # o traço precisa passar por pelo menos 60% do guia

TAXA_TREMOR = 100.0  # Hz, para reamostrar o traço em passos iguais
FAIXA_TREMOR = (3.0, 12.0)
MIN_FRACAO_TREMOR = 0.35  # parte da energia de 1-20 Hz que precisa estar no pico
MIN_AMPLITUDE_TREMOR = 0.003  # ~1 mm numa tela de 350 px


def guia(espelhado: bool = False) -> tuple[np.ndarray, np.ndarray]:
    """Pontos (N, 2) e raio esperado (N,) do guia."""
    theta = np.linspace(0, 2 * np.pi * VOLTAS, N_GUIA)
    r = RAIO_FINAL * theta / theta[-1]
    sinal = -1.0 if espelhado else 1.0
    xy = np.column_stack([CENTRO[0] + r * np.cos(theta), CENTRO[1] + sinal * r * np.sin(theta)])
    return xy, r


def _mais_proximo(pontos: np.ndarray, guia_xy: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Para cada ponto, o índice do ponto do guia mais próximo e a distância até ele."""
    idx = np.empty(len(pontos), dtype=int)
    dist = np.empty(len(pontos))
    for ini in range(0, len(pontos), 500):  # em blocos para não estourar memória
        bloco = pontos[ini : ini + 500]
        d2 = ((bloco[:, None, :] - guia_xy[None, :, :]) ** 2).sum(axis=2)
        j = d2.argmin(axis=1)
        idx[ini : ini + 500] = j
        dist[ini : ini + 500] = np.sqrt(d2[np.arange(len(bloco)), j])
    return idx, dist


def frequencia_tremor(t_s: np.ndarray, erro: np.ndarray) -> float:
    """Pico de 3-12 Hz do erro radial, ou 0 se não houver oscilação clara."""
    if t_s[-1] - t_s[0] < 2.0:
        return 0.0
    grade = np.arange(t_s[0], t_s[-1], 1 / TAXA_TREMOR)
    sinal = np.interp(grade, t_s, erro)
    b, a = butter(2, [1.0, 20.0], btype="band", fs=TAXA_TREMOR)
    filtrado = filtfilt(b, a, sinal)

    freqs, pot = welch(filtrado, fs=TAXA_TREMOR, nperseg=min(256, len(filtrado)))
    larga = (freqs >= 1.0) & (freqs <= 20.0)
    faixa = (freqs >= FAIXA_TREMOR[0]) & (freqs <= FAIXA_TREMOR[1])
    if pot[larga].sum() <= 0:
        return 0.0
    i_pico = np.flatnonzero(faixa)[pot[faixa].argmax()]
    perto = (freqs >= freqs[i_pico] - 1.0) & (freqs <= freqs[i_pico] + 1.0)
    fracao = pot[perto].sum() / pot[larga].sum()

    b, a = butter(2, [max(0.5, freqs[i_pico] - 1.5), freqs[i_pico] + 1.5], btype="band", fs=TAXA_TREMOR)
    amplitude = float(np.sqrt(2) * np.std(filtfilt(b, a, sinal)))
    if fracao < MIN_FRACAO_TREMOR or amplitude < MIN_AMPLITUDE_TREMOR:
        return 0.0
    return float(freqs[i_pico])


def analisar_espiral(entrada: EntradaEspiral) -> RespostaEspiral:
    falha = RespostaEspiral(qualidade=Qualidade(ok=False, motivo="traco_incompleto"), metricas=None, metrica_principal=None)
    ordenados = sorted(entrada.pontos, key=lambda p: p.t_ms)
    if len(ordenados) < MIN_PONTOS:
        return falha
    xy = np.array([[p.x, p.y] for p in ordenados])
    t_s = np.array([p.t_ms for p in ordenados]) / 1000
    # Pointer Events às vezes repetem o mesmo instante; mantém o primeiro de cada.
    unicos = np.concatenate([[True], np.diff(t_s) > 0])
    xy, t_s = xy[unicos], t_s[unicos]
    if len(xy) < MIN_PONTOS or t_s[-1] - t_s[0] < MIN_DURACAO_S:
        return falha

    melhor = None
    for espelhado in (False, True):
        g_xy, g_r = guia(espelhado)
        idx, dist = _mais_proximo(xy, g_xy)
        if melhor is None or dist.mean() < melhor[2].mean():
            melhor = (g_r, idx, dist)
    g_r, idx, dist = melhor

    cobertura = (idx.max() - idx.min()) / (N_GUIA - 1)
    if cobertura < MIN_COBERTURA:
        return falha

    erro_radial = np.linalg.norm(xy - CENTRO, axis=1) - g_r[idx]
    comprimento = float(np.linalg.norm(np.diff(xy, axis=0), axis=1).sum())

    metricas = MetricasEspiral(
        duracao_s=round(entrada.duracao_ms / 1000, 2),
        desvio_medio=round(float(dist.mean()), 4),
        tremor_hz=round(frequencia_tremor(t_s, erro_radial), 1),
        velocidade_media=round(comprimento / float(t_s[-1] - t_s[0]), 3),
    )
    return RespostaEspiral(
        qualidade=Qualidade(ok=True),
        metricas=metricas,
        metrica_principal=MetricaPrincipal(nome="desvio_medio", valor=metricas.desvio_medio),
    )
