"""Testes da análise de verdade com sinais de propriedades conhecidas.

tests/audios/*.webm são vozes sintéticas do espeak-ng ("pá tá cá" 8 vezes e um "ááá" longo),
codificadas em opus como o MediaRecorder do Chrome faz. Nenhuma gravação de paciente.
"""

from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.audio import decodificar
from app.espiral import analisar_espiral
from app.main import app
from app.modelos import EntradaEspiral
from app.pataka import analisar_pataka
from app.vogal import analisar_vogal
from tests import sinais

cliente = TestClient(app)
AUDIOS = Path(__file__).parent / "audios"


# ---------- vogal ----------


def test_vogal_rota_com_webm_de_verdade():
    with open(AUDIOS / "aaaa_voz_sintetica.webm", "rb") as f:
        r = cliente.post("/analisar/vogal", files={"audio": ("a.webm", f, "audio/webm")}).json()
    assert r["qualidade"]["ok"] is True
    assert r["metrica_principal"]["nome"] == "jitter_pct"
    m = r["metricas"]
    assert 3.5 < m["duracao_s"] < 5.0
    assert 80 < m["f0_medio_hz"] < 130
    assert m["hnr_db"] > 10


def test_vogal_mede_f0_e_jitter_baixo_numa_voz_estavel():
    m = analisar_vogal(sinais.vogal(f0=150, jitter=0.002)).metricas
    assert m.f0_medio_hz == pytest.approx(150, abs=1)
    assert m.jitter_pct < 0.3
    assert m.hnr_db > 25
    assert m.duracao_s == pytest.approx(5.0, abs=0.1)


def test_vogal_jitter_sobe_com_a_instabilidade():
    jitters = [analisar_vogal(sinais.vogal(jitter=j)).metricas.jitter_pct for j in (0.002, 0.005, 0.01, 0.02)]
    assert jitters == sorted(jitters)
    assert jitters[-1] > 3 * jitters[0]


def test_vogal_shimmer_sobe_com_a_variacao_de_volume():
    shimmers = [analisar_vogal(sinais.vogal(shimmer=s)).metricas.shimmer_pct for s in (0.0, 0.05, 0.1)]
    assert shimmers == sorted(shimmers)


def test_vogal_hnr_cai_com_ruido():
    limpo = analisar_vogal(sinais.vogal(ruido=0.002)).metricas.hnr_db
    ruidoso = analisar_vogal(sinais.vogal(ruido=0.03)).metricas.hnr_db
    assert ruidoso < limpo - 10


def test_vogal_curta_e_silencio():
    assert analisar_vogal(sinais.vogal(dur_s=1.0)).qualidade.motivo == "audio_curto"
    assert analisar_vogal(np.zeros(16000 * 3, dtype=np.float32)).qualidade.motivo == "audio_silencioso"
    ruido = (0.05 * np.random.default_rng(0).standard_normal(16000 * 5)).astype(np.float32)
    assert analisar_vogal(ruido).qualidade.motivo == "audio_silencioso"


# ---------- pataka ----------


def test_pataka_rota_com_webm_de_verdade():
    with open(AUDIOS / "pataka_voz_sintetica.webm", "rb") as f:
        r = cliente.post("/analisar/pataka", files={"audio": ("p.webm", f, "audio/webm")}).json()
    assert r["qualidade"]["ok"] is True
    assert r["metrica_principal"]["nome"] == "silabas_por_s"
    assert r["metricas"]["silabas_por_s"] == pytest.approx(6.1, abs=0.3)  # 24 sílabas em ~3,8 s


@pytest.mark.parametrize("ritmo", [3, 5, 6, 8, 10])
def test_pataka_conta_o_ritmo_certo(ritmo):
    audio, _ = sinais.pataka(silabas_por_s=ritmo)
    m = analisar_pataka(audio).metricas
    assert m.silabas_por_s == pytest.approx(ritmo, rel=0.05)
    assert m.intervalo_cv < 0.08


def test_pataka_irregular_tem_cv_maior():
    regular = analisar_pataka(sinais.pataka(irregularidade=0.0)[0]).metricas.intervalo_cv
    irregular = analisar_pataka(sinais.pataka(irregularidade=0.2)[0]).metricas.intervalo_cv
    assert irregular > regular + 0.1


def test_pataka_aguenta_ruido_de_fundo_e_volume_baixo():
    audio = decodificar((AUDIOS / "pataka_voz_sintetica.webm").read_bytes())
    ruido = 0.02 * np.random.default_rng(0).standard_normal(audio.size).astype(np.float32)
    assert analisar_pataka(audio + ruido).metricas.silabas_por_s == pytest.approx(6.1, abs=0.3)
    assert analisar_pataka(audio * 0.05).metricas.silabas_por_s == pytest.approx(6.1, abs=0.3)


def test_pataka_silencio_e_ruido_nao_contam():
    assert analisar_pataka(np.zeros(16000 * 5, dtype=np.float32)).qualidade.motivo == "audio_silencioso"
    ruido = (0.05 * np.random.default_rng(0).standard_normal(16000 * 8)).astype(np.float32)
    assert analisar_pataka(ruido).qualidade.motivo == "audio_silencioso"


# ---------- espiral ----------


def _espiral(**kw):
    return analisar_espiral(EntradaEspiral(**sinais.espiral(**kw)))


def test_espiral_rota():
    r = cliente.post("/analisar/espiral", json=sinais.espiral()).json()
    assert r["qualidade"]["ok"] is True
    assert r["metrica_principal"]["nome"] == "desvio_medio"


def test_espiral_traco_bom_tem_desvio_pequeno_e_sem_tremor():
    m = _espiral(ruido=0.002).metricas
    assert m.desvio_medio < 0.004
    assert m.tremor_hz == 0.0
    assert m.duracao_s == 15.0


def test_espiral_desvio_acompanha_o_erro():
    m = _espiral(deslocamento=0.03).metricas
    assert m.desvio_medio == pytest.approx(0.03, abs=0.004)


@pytest.mark.parametrize("freq", [4.0, 5.0, 6.0, 9.0])
def test_espiral_acha_a_frequencia_do_tremor(freq):
    m = _espiral(tremor_hz=freq, tremor_amp=0.008).metricas
    assert m.tremor_hz == pytest.approx(freq, abs=0.6)


def test_espiral_tremor_com_toques_a_120_hz():
    m = _espiral(tremor_hz=5.0, tremor_amp=0.006, taxa_hz=120).metricas
    assert m.tremor_hz == pytest.approx(5.0, abs=0.6)


def test_espiral_ruido_aleatorio_nao_vira_tremor():
    for semente in range(5):
        assert _espiral(ruido=0.006, semente=semente).metricas.tremor_hz == 0.0


def test_espiral_espelhada_tambem_vale():
    assert _espiral(espelhado=True).metricas.desvio_medio < 0.004


def test_espiral_incompleta():
    assert _espiral(fracao=0.4).qualidade.motivo == "traco_incompleto"
    assert _espiral(dur_s=0.3).qualidade.motivo == "traco_incompleto"
