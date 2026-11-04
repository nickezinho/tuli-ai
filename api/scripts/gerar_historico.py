"""Gera 30 dias de histórico sintético para a demo (nada de dados reais de pacientes).

A voz começa estável e fica mais instável a partir do dia 17, como no mockup.
Uso: python scripts/gerar_historico.py [saida.json]
"""

import json
import random
import sys
from datetime import date, timedelta

DIAS = 30
INICIO_MUDANCA = 16  # índice do dia em que o jitter começa a subir

PERFIS = {
    "vogal": {"metrica": "jitter_pct", "base": 0.60, "ruido": 0.02, "deriva_por_dia": 0.012},
    "pataka": {"metrica": "silabas_por_s", "base": 6.1, "ruido": 0.15, "deriva_por_dia": 0.0},
    "espiral": {"metrica": "desvio_medio", "base": 0.021, "ruido": 0.0012, "deriva_por_dia": 0.0},
    "tapping": {"metrica": "toques_por_s", "base": 4.8, "ruido": 0.12, "deriva_por_dia": 0.0},
}


def gerar(fim: date, semente: int = 42) -> dict:
    rng = random.Random(semente)
    inicio = fim - timedelta(days=DIAS - 1)
    saida = {}
    for jogo, p in PERFIS.items():
        serie = []
        for i in range(DIAS):
            deriva = max(0, i - INICIO_MUDANCA) * p["deriva_por_dia"]
            valor = p["base"] + deriva + rng.gauss(0, p["ruido"])
            serie.append({"dia": (inicio + timedelta(days=i)).isoformat(), "valor": round(valor, 4)})
        saida[jogo] = {"metrica": p["metrica"], "serie": serie}
    return saida


if __name__ == "__main__":
    caminho = sys.argv[1] if len(sys.argv) > 1 else "historico_sintetico.json"
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(gerar(date.today()), f, ensure_ascii=False, indent=2)
    print(f"Histórico salvo em {caminho}")
