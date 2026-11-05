"""Sinais sintéticos com propriedades conhecidas, para testar a análise sem gravações reais."""

import io
import wave

import numpy as np

TAXA = 16000


def para_wav(amostras: np.ndarray, taxa: int = TAXA) -> bytes:
    pcm = (np.clip(amostras, -1, 1) * 32767).astype("<i2")
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(taxa)
        w.writeframes(pcm.tobytes())
    return buf.getvalue()


def _ressonador(x: np.ndarray, freq: float, banda: float) -> np.ndarray:
    from scipy.signal import lfilter

    r = np.exp(-np.pi * banda / TAXA)
    a = [1, -2 * r * np.cos(2 * np.pi * freq / TAXA), r * r]
    return lfilter([1 - r], a, x)


def vogal(dur_s: float = 5.0, f0: float = 150.0, jitter: float = 0.003, shimmer: float = 0.02,
          ruido: float = 0.002, silencio_s: float = 0.5, semente: int = 0) -> np.ndarray:
    """Um "aaaa" feito de pulsos glotais com jitter e shimmer controlados, filtrado por formantes de /a/."""
    rng = np.random.default_rng(semente)
    n = int(dur_s * TAXA)
    # Início contínuo de cada ciclo glotal (sem arredondar para a amostra, para não criar jitter falso).
    periodos = (1 / f0) * (1 + jitter * rng.standard_normal(int(dur_s * f0 * 1.5) + 10))
    inicios = np.concatenate([[0.0], np.cumsum(periodos)])
    amplitudes = 1 + shimmer * rng.standard_normal(len(inicios))
    t = np.arange(n) / TAXA
    k = np.searchsorted(inicios, t, side="right") - 1
    fase = (t - inicios[k]) / periodos[k]
    # Pulso de Rosenberg: abre em 40% do ciclo, fecha em 16%, fica fechado no resto.
    pulso = np.where(fase < 0.4, 0.5 * (1 - np.cos(np.pi * fase / 0.4)),
                     np.where(fase < 0.56, np.cos(np.pi * (fase - 0.4) / 0.32), 0.0))
    fonte = np.diff(amplitudes[k] * pulso, prepend=0)
    som = sum(_ressonador(fonte, f, b) * g for f, b, g in [(700, 80, 1.0), (1220, 90, 0.5), (2600, 120, 0.25)])
    som = 0.3 * som / np.max(np.abs(som))
    som = som + ruido * rng.standard_normal(n)
    pausa = np.zeros(int(silencio_s * TAXA))
    return np.concatenate([pausa, som, pausa]).astype(np.float32)


def pataka(silabas_por_s: float = 6.0, dur_s: float = 8.0, irregularidade: float = 0.0,
           silencio_s: float = 0.7, semente: int = 0) -> tuple[np.ndarray, int]:
    """Sílabas sintéticas: estouro de ruído (consoante) + vogal curta. Devolve o áudio e o nº de sílabas."""
    rng = np.random.default_rng(semente)
    total = int((dur_s + 2 * silencio_s) * TAXA)
    audio = 0.0005 * rng.standard_normal(total)
    periodo = 1 / silabas_por_s
    t = silencio_s
    n = 0
    while t < silencio_s + dur_s - periodo:
        i = int(t * TAXA)
        conso = 0.1 * rng.standard_normal(int(0.015 * TAXA))
        dv = int(0.6 * periodo * TAXA)
        tt = np.arange(dv) / TAXA
        env = np.sin(np.pi * np.arange(dv) / dv) ** 2
        vog = 0.4 * env * (np.sin(2 * np.pi * 140 * tt) + 0.5 * np.sin(2 * np.pi * 280 * tt) + 0.3 * np.sin(2 * np.pi * 700 * tt))
        seg = np.concatenate([conso, vog])
        audio[i : i + len(seg)] += seg[: total - i]
        n += 1
        t += periodo * (1 + irregularidade * rng.standard_normal())
    return audio.astype(np.float32), n


def espiral(dur_s: float = 15.0, taxa_hz: float = 60.0, ruido: float = 0.002, tremor_hz: float = 0.0,
            tremor_amp: float = 0.0, deslocamento: float = 0.0, fracao: float = 1.0,
            espelhado: bool = False, semente: int = 0) -> dict:
    """Pontos de uma espiral traçada por cima do guia, com ruído, tremor e desvio controlados."""
    rng = np.random.default_rng(semente)
    n = int(dur_s * taxa_hz)
    t = np.arange(n) / taxa_hz
    theta = np.sqrt(np.linspace(0, 1, n)) * 6 * np.pi * fracao  # velocidade linear mais ou menos constante
    r = 0.45 * theta / (6 * np.pi) + deslocamento
    r = r + tremor_amp * np.sin(2 * np.pi * tremor_hz * t) + ruido * rng.standard_normal(n)
    sinal = -1 if espelhado else 1
    x = np.clip(0.5 + r * np.cos(theta), 0, 1)
    y = np.clip(0.5 + sinal * r * np.sin(theta), 0, 1)
    pontos = [{"t_ms": float(ti * 1000), "x": float(xi), "y": float(yi)} for ti, xi, yi in zip(t, x, y)]
    return {"mao": "direita", "duracao_ms": dur_s * 1000, "pontos": pontos}
