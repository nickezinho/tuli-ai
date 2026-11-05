"""Decodifica o áudio que o app manda (webm/opus, mp4/aac, wav...) para mono 16 kHz.

Usa o ffmpeg do sistema quando existe e, se não, o binário que vem no pacote
imageio-ffmpeg. Assim o serviço sobe em Render/Railway sem instalar nada a mais.
"""

import shutil
import subprocess

import numpy as np

TAXA = 16000


class AudioInvalido(Exception):
    """O arquivo não é um áudio que o ffmpeg consiga abrir."""


def _ffmpeg() -> str:
    caminho = shutil.which("ffmpeg")
    if caminho:
        return caminho
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def decodificar(dados: bytes) -> np.ndarray:
    """Devolve as amostras em float32, mono, 16 kHz, entre -1 e 1."""
    proc = subprocess.run(
        [_ffmpeg(), "-hide_banner", "-loglevel", "error", "-i", "pipe:0",
         "-ac", "1", "-ar", str(TAXA), "-f", "f32le", "pipe:1"],
        input=dados,
        capture_output=True,
        timeout=30,
    )
    if proc.returncode != 0:
        raise AudioInvalido(proc.stderr.decode(errors="ignore").strip()[:200])
    return np.frombuffer(proc.stdout, dtype=np.float32).copy()


def nivel_dbfs(amostras: np.ndarray) -> float:
    """Volume RMS em dB relativo ao máximo digital (0 dBFS)."""
    if amostras.size == 0:
        return -120.0
    rms = float(np.sqrt(np.mean(amostras.astype(np.float64) ** 2)))
    return 20 * np.log10(max(rms, 1e-6))
