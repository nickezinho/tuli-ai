"""Compara o período recente com a linha de base da própria pessoa (regra em docs/contrato.md)."""

from statistics import mean, pstdev

from .modelos import EntradaComparar, LinhaDeBase, Recente, RespostaComparar

DIAS_BASE = 7
DIAS_RECENTE = 7
MIN_DIAS = 10
LIMIAR_Z = 2.0
PISO_DESVIO = 0.05  # 5% da média da base


def comparar(entrada: EntradaComparar) -> RespostaComparar:
    serie = sorted(entrada.serie, key=lambda p: p.dia)
    if len(serie) < MIN_DIAS:
        return RespostaComparar(status="sem_dados", linha_de_base=None, recente=None, z=None, direcao=None)

    base = [p.valor for p in serie[:DIAS_BASE]]
    recente = [p.valor for p in serie[-DIAS_RECENTE:]]
    media_base = mean(base)
    desvio_base = pstdev(base)
    media_recente = mean(recente)

    denominador = max(desvio_base, abs(media_base) * PISO_DESVIO, 1e-9)
    z = (media_recente - media_base) / denominador

    if abs(z) < LIMIAR_Z:
        direcao = "igual"
    else:
        subiu = z > 0
        direcao = "melhorou" if subiu == entrada.maior_e_melhor else "piorou"

    return RespostaComparar(
        status="mudou" if direcao == "piorou" else "estavel",
        linha_de_base=LinhaDeBase(media=round(media_base, 4), desvio=round(desvio_base, 4), n=len(base)),
        recente=Recente(media=round(media_recente, 4), n=len(recente)),
        z=round(z, 2),
        direcao=direcao,
    )
