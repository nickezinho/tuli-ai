"""Métricas do jogo de tapping. Implementação inicial, pronta para a parte 2 refinar."""

from math import hypot
from statistics import mean, pstdev

from .modelos import EntradaTapping, MetricaPrincipal, MetricasTapping, Qualidade, RespostaTapping

MIN_TOQUES = 10
JANELA_MS = 5000


def analisar_tapping(entrada: EntradaTapping) -> RespostaTapping:
    toques = sorted(entrada.toques, key=lambda t: t.t_ms)
    if len(toques) < MIN_TOQUES:
        return RespostaTapping(
            qualidade=Qualidade(ok=False, motivo="poucos_toques"), metricas=None, metrica_principal=None
        )

    duracao_s = entrada.duracao_ms / 1000
    toques_por_s = len(toques) / duracao_s

    intervalos = [b.t_ms - a.t_ms for a, b in zip(toques, toques[1:])]
    media_int = mean(intervalos)
    intervalo_cv = pstdev(intervalos) / media_int if media_int > 0 else 0.0

    alvos = entrada.alvos
    acertos = sum(
        1
        for t in toques
        if min(hypot(t.x - alvos.a.x, t.y - alvos.a.y), hypot(t.x - alvos.b.x, t.y - alvos.b.y)) <= alvos.raio
    )
    precisao_pct = 100 * acertos / len(toques)

    inicio = sum(1 for t in toques if t.t_ms < JANELA_MS)
    fim = sum(1 for t in toques if t.t_ms >= entrada.duracao_ms - JANELA_MS)
    queda_ritmo_pct = 100 * (inicio - fim) / inicio if inicio else 0.0

    metricas = MetricasTapping(
        toques_por_s=round(toques_por_s, 2),
        intervalo_cv=round(intervalo_cv, 3),
        precisao_pct=round(precisao_pct, 1),
        queda_ritmo_pct=round(queda_ritmo_pct, 1),
    )
    return RespostaTapping(
        qualidade=Qualidade(ok=True),
        metricas=metricas,
        metrica_principal=MetricaPrincipal(nome="toques_por_s", valor=metricas.toques_por_s),
    )
