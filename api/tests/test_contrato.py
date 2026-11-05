from datetime import date

from fastapi.testclient import TestClient

from app.main import app
from scripts.gerar_historico import gerar

cliente = TestClient(app)


def _tapping(n: int, intervalo_ms: float = 200) -> dict:
    toques = []
    for i in range(n):
        alvo = (0.25, 0.6) if i % 2 == 0 else (0.75, 0.6)
        toques.append({"t_ms": 100 + i * intervalo_ms, "x": alvo[0], "y": alvo[1]})
    return {
        "mao": "direita",
        "duracao_ms": 15000,
        "alvos": {"a": {"x": 0.25, "y": 0.6}, "b": {"x": 0.75, "y": 0.6}, "raio": 0.12},
        "toques": toques,
    }


def test_tapping_regular():
    r = cliente.post("/analisar/tapping", json=_tapping(70)).json()
    assert r["qualidade"]["ok"] is True
    assert r["metrica_principal"]["nome"] == "toques_por_s"
    assert r["metricas"]["precisao_pct"] == 100.0
    assert r["metricas"]["intervalo_cv"] == 0.0


def test_tapping_poucos_toques():
    r = cliente.post("/analisar/tapping", json=_tapping(3)).json()
    assert r["qualidade"] == {"ok": False, "motivo": "poucos_toques"}


def test_audio_vazio():
    for jogo in ("vogal", "pataka"):
        r = cliente.post(f"/analisar/{jogo}", files={"audio": ("a.webm", b"", "audio/webm")}).json()
        assert r["qualidade"] == {"ok": False, "motivo": "audio_silencioso"}


def test_audio_invalido_devolve_erro_do_contrato():
    r = cliente.post("/analisar/vogal", files={"audio": ("a.webm", b"isso nao e audio", "audio/webm")})
    assert r.status_code == 422
    assert r.json()["erro"] == "audio_invalido"


def test_comparar_detecta_mudanca_na_voz_sintetica():
    hist = gerar(date(2026, 11, 4))
    voz = cliente.post(
        "/comparar",
        json={"jogo": "vogal", "metrica": "jitter_pct", "maior_e_melhor": False, "serie": hist["vogal"]["serie"]},
    ).json()
    assert voz["status"] == "mudou"
    assert voz["direcao"] == "piorou"

    tap = cliente.post(
        "/comparar",
        json={"jogo": "tapping", "metrica": "toques_por_s", "maior_e_melhor": True, "serie": hist["tapping"]["serie"]},
    ).json()
    assert tap["status"] == "estavel"


def test_comparar_melhora_nao_vira_alerta():
    serie = [{"dia": f"2026-10-{d:02d}", "valor": 4.0 if d <= 7 else 6.0} for d in range(1, 15)]
    r = cliente.post(
        "/comparar", json={"jogo": "tapping", "metrica": "toques_por_s", "maior_e_melhor": True, "serie": serie}
    ).json()
    assert r["status"] == "estavel"
    assert r["direcao"] == "melhorou"


def test_comparar_sem_dados():
    serie = [{"dia": "2026-10-01", "valor": 1.0}]
    r = cliente.post("/comparar", json={"jogo": "vogal", "metrica": "jitter_pct", "maior_e_melhor": False, "serie": serie}).json()
    assert r["status"] == "sem_dados"
