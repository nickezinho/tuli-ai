// Tipos do contrato A (app <-> backend). Espelham docs/contrato.md.

export type Jogo = "vogal" | "pataka" | "espiral" | "tapping";
export type Mao = "direita" | "esquerda";
export type MotivoQualidade = "audio_silencioso" | "audio_curto" | "poucos_toques" | "traco_incompleto";

export interface Qualidade {
  ok: boolean;
  motivo: MotivoQualidade | null;
}

export interface MetricaPrincipal {
  nome: string;
  valor: number;
}

// ---------- Entradas ----------

/** Coordenadas normalizadas de 0 a 1 em relação à área do jogo. */
export interface Ponto {
  t_ms: number;
  x: number;
  y: number;
}

export interface EntradaEspiral {
  mao: Mao;
  duracao_ms: number;
  pontos: Ponto[];
}

export interface EntradaTapping {
  mao: Mao;
  duracao_ms: number;
  alvos: { a: { x: number; y: number }; b: { x: number; y: number }; raio: number };
  toques: Ponto[];
}

/**
 * Guia da espiral: o app desenha exatamente esta curva e a análise a reconstrói.
 * θ de 0 a 2π·voltas, r = raio_final · θ / (2π·voltas), x = centro.x + r·cos θ, y = centro.y + r·sen θ.
 */
export const GUIA_ESPIRAL = { centro: { x: 0.5, y: 0.5 }, voltas: 3, raio_final: 0.45 } as const;

// ---------- Respostas ----------

export interface Streak {
  dias: number;
  jogos_hoje: number;
  total_jogos: number;
}

export interface RespostaJogo {
  sessao_id: string;
  jogo: Jogo;
  criado_em: string;
  qualidade: Qualidade;
  metricas: Record<string, number> | null;
  metrica_principal: MetricaPrincipal | null;
  streak: Streak;
}

export type StatusDia = "feito" | "perdido" | "hoje" | "futuro";
export type StatusJogo = "feito" | "proximo" | "pendente";

export interface RespostaHoje {
  streak: { dias: number; semana: StatusDia[] };
  jogos: { jogo: Jogo; status: StatusJogo }[];
  fala_do_tuli: string;
}

export type HumorTuli = "normal" | "comemorando" | "avisando";
export type StatusCartao = "estavel" | "mudou" | "sem_dados";

export interface PontoSerie {
  dia: string;
  valor: number;
}

export interface RespostaResumo {
  periodo_dias: number;
  humor_do_tuli: HumorTuli;
  mensagem: { titulo: string; detalhe: string };
  cartoes: { jogo: Jogo; metrica: string; status: StatusCartao; serie: PontoSerie[] }[];
}

export interface EntradaRelatorio {
  email_destino: string;
  nome_destino?: string;
}

export interface RespostaRelatorio {
  enviado: boolean;
  id: string | null;
}

export interface ResultadoNeurologista {
  nome: string;
  tipo: "neurologista" | "servico_sus" | "associacao";
  endereco: string;
  telefone: string | null;
  fonte_url: string;
  atende_sus: boolean | null;
}

export interface RespostaNeurologistas {
  resultados: ResultadoNeurologista[];
}

export interface Erro {
  erro: string;
  mensagem: string;
}

export const JOGOS: Jogo[] = ["vogal", "pataka", "espiral", "tapping"];

export const METRICA_PRINCIPAL: Record<Jogo, { nome: string; maior_e_melhor: boolean }> = {
  vogal: { nome: "jitter_pct", maior_e_melhor: false },
  pataka: { nome: "silabas_por_s", maior_e_melhor: true },
  espiral: { nome: "desvio_medio", maior_e_melhor: false },
  tapping: { nome: "toques_por_s", maior_e_melhor: true },
};
