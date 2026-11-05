// Respostas falsas no formato do contrato, para cada parte trabalhar sem esperar as outras.
// Quando o backend real estiver pronto, as rotas em app/api/ param de usar este arquivo.

import type { Jogo, RespostaHoje, RespostaJogo, RespostaNeurologistas, RespostaResumo, PontoSerie } from "./contrato";

const METRICAS_MOCK: Record<Jogo, { metricas: Record<string, number>; principal: string }> = {
  vogal: {
    metricas: { duracao_s: 9.8, f0_medio_hz: 182, f0_desvio_hz: 3.1, jitter_pct: 0.62, shimmer_pct: 3.4, hnr_db: 21.5 },
    principal: "jitter_pct",
  },
  pataka: { metricas: { duracao_s: 10, silabas_por_s: 6.1, intervalo_cv: 0.14 }, principal: "silabas_por_s" },
  espiral: { metricas: { duracao_s: 18.4, desvio_medio: 0.021, tremor_hz: 0, velocidade_media: 0.11 }, principal: "desvio_medio" },
  tapping: { metricas: { toques_por_s: 4.8, intervalo_cv: 0.12, precisao_pct: 93, queda_ritmo_pct: 6 }, principal: "toques_por_s" },
};

export function mockRespostaJogo(jogo: Jogo): RespostaJogo {
  const m = METRICAS_MOCK[jogo];
  return {
    sessao_id: crypto.randomUUID(),
    jogo,
    criado_em: new Date().toISOString(),
    qualidade: { ok: true, motivo: null },
    metricas: m.metricas,
    metrica_principal: { nome: m.principal, valor: m.metricas[m.principal] },
    streak: { dias: 12, jogos_hoje: 2, total_jogos: 4 },
  };
}

export const mockHoje: RespostaHoje = {
  streak: { dias: 12, semana: ["feito", "feito", "feito", "hoje", "futuro", "futuro", "futuro"] },
  jogos: [
    { jogo: "vogal", status: "feito" },
    { jogo: "pataka", status: "proximo" },
    { jogo: "espiral", status: "pendente" },
    { jogo: "tapping", status: "pendente" },
  ],
  fala_do_tuli: "Bom dia! Faltam 3 jogos para manter seu streak hoje.",
};

function serie(base: number, deriva: number, inicioDeriva: number): PontoSerie[] {
  const hoje = new Date();
  return Array.from({ length: 28 }, (_, i) => {
    const d = new Date(hoje);
    d.setDate(hoje.getDate() - (27 - i));
    const ruido = Math.sin(i * 1.7) * base * 0.02;
    return { dia: d.toISOString().slice(0, 10), valor: +(base + ruido + Math.max(0, i - inicioDeriva) * deriva).toFixed(4) };
  });
}

export const mockResumo: RespostaResumo = {
  periodo_dias: 28,
  humor_do_tuli: "avisando",
  mensagem: {
    titulo: "Sua voz ficou um pouco mais instável nas últimas 2 semanas.",
    detalhe: "Isso pode ter várias causas, como cansaço ou um resfriado. Se continuar, vale conversar com seu neurologista.",
  },
  cartoes: [
    { jogo: "vogal", metrica: "jitter_pct", status: "mudou", serie: serie(0.6, 0.012, 14) },
    { jogo: "pataka", metrica: "silabas_por_s", status: "estavel", serie: serie(6.1, 0, 0) },
    { jogo: "espiral", metrica: "desvio_medio", status: "estavel", serie: serie(0.021, 0, 0) },
    { jogo: "tapping", metrica: "toques_por_s", status: "estavel", serie: serie(4.8, 0, 0) },
  ],
};

export const mockNeurologistas: RespostaNeurologistas = {
  resultados: [
    {
      nome: "[Exemplo] Ambulatório de Neurologia",
      tipo: "servico_sus",
      endereco: "[Endereço de exemplo]",
      telefone: null,
      fonte_url: "https://example.com",
      atende_sus: true,
    },
  ],
};
