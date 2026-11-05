# Contrato entre as 3 partes

Este documento define o formato dos dados que circulam entre o app, o backend e a análise. Enquanto ele for respeitado, cada parte pode trabalhar sozinha usando os mocks.

```
 [1] App e jogos (web/)          [3] Backend (web/app/api/ + Supabase)        [2] Análise (api/)
 navegador do celular  ── A ──▶  rotas Next.js /api/*            ── B ──▶     FastAPI /analisar/*, /comparar
```

- **Contrato A** (app ↔ backend): rotas do Next.js. Os tipos estão em `web/lib/contrato.ts`.
- **Contrato B** (backend ↔ análise): serviço Python. Os modelos estão em `api/app/modelos.py`.

Os dois arquivos de tipos precisam continuar iguais a este documento. Quem mudar um campo atualiza os três no mesmo PR.

## Convenções

- Nomes de campos em português, `snake_case`, sem acento.
- Tempos em **milissegundos** desde o início do jogo (`t_ms`). Datas em ISO 8601 UTC.
- Coordenadas de toque **normalizadas de 0 a 1** em relação à área do jogo, para que celulares diferentes sejam comparáveis.
- Os 4 jogos se chamam `vogal`, `pataka`, `espiral` e `tapping`.
- Erros seguem `{ "erro": "codigo_curto", "mensagem": "texto para humanos" }`.

## Os 4 jogos e a métrica principal de cada um

A métrica principal é a que aparece no gráfico pequeno da aba do Tuli e a que é usada para decidir se algo mudou.

| Jogo | O que a pessoa faz | Duração | Métrica principal | Quanto maior... |
|---|---|---|---|---|
| `vogal` | Segura um "aaaa" | até 15 s | `jitter_pct` (instabilidade da frequência) | pior |
| `pataka` | Repete "pa-ta-ka" o mais rápido que conseguir | 10 s | `silabas_por_s` | melhor |
| `espiral` | Traça uma espiral com o dedo por cima de um guia | até 30 s | `desvio_medio` (distância média do traço ao guia, normalizada) | pior |
| `tapping` | Toca alternando dois alvos | 15 s | `toques_por_s` | melhor |

---

## Contrato A: app ↔ backend (rotas do Next.js)

### `POST /api/jogos/vogal` e `POST /api/jogos/pataka`

`multipart/form-data`:

| Campo | Tipo | Observação |
|---|---|---|
| `audio` | arquivo | O que o `MediaRecorder` gerar (`audio/webm` ou `audio/mp4` no iPhone). |
| `duracao_ms` | número | Tempo que a pessoa segurou o botão. |

### `POST /api/jogos/espiral`

```json
{
  "mao": "direita",
  "duracao_ms": 18420,
  "pontos": [
    { "t_ms": 0, "x": 0.50, "y": 0.50 },
    { "t_ms": 16, "x": 0.51, "y": 0.50 }
  ]
}
```

O guia é uma espiral de Arquimedes centrada em (0.5, 0.5), com 3 voltas e raio final 0.45. A análise reconstrói o guia com esses mesmos números, então o app desenha exatamente essa curva:

```
θ de 0 a 6π    r = 0.45 · θ / (6π)    x = 0.5 + r·cos θ    y = 0.5 + r·sen θ
```

`y` cresce para baixo, como na tela. Se o app desenhar a versão espelhada (`y = 0.5 - r·sen θ`), a análise também aceita.

### `POST /api/jogos/tapping`

```json
{
  "mao": "direita",
  "duracao_ms": 15000,
  "alvos": { "a": { "x": 0.25, "y": 0.6 }, "b": { "x": 0.75, "y": 0.6 }, "raio": 0.12 },
  "toques": [
    { "t_ms": 312, "x": 0.26, "y": 0.61 },
    { "t_ms": 598, "x": 0.74, "y": 0.59 }
  ]
}
```

### Resposta das 4 rotas de jogo

```json
{
  "sessao_id": "8f2c...",
  "jogo": "tapping",
  "criado_em": "2026-11-04T22:40:00Z",
  "qualidade": { "ok": true, "motivo": null },
  "metricas": { "toques_por_s": 4.8, "intervalo_cv": 0.12, "precisao_pct": 93.0, "queda_ritmo_pct": 6.0 },
  "metrica_principal": { "nome": "toques_por_s", "valor": 4.8 },
  "streak": { "dias": 12, "jogos_hoje": 2, "total_jogos": 4 }
}
```

Quando `qualidade.ok` é `false` (áudio mudo, poucos toques, traço curto demais), a sessão **não** conta no histórico e o app pede para repetir. Valores de `motivo`: `audio_silencioso`, `audio_curto`, `poucos_toques`, `traco_incompleto`.

### `GET /api/hoje`

Alimenta a home.

```json
{
  "streak": { "dias": 12, "semana": ["feito", "feito", "feito", "hoje", "futuro", "futuro", "futuro"] },
  "jogos": [
    { "jogo": "vogal", "status": "feito" },
    { "jogo": "pataka", "status": "proximo" },
    { "jogo": "espiral", "status": "pendente" },
    { "jogo": "tapping", "status": "pendente" }
  ],
  "fala_do_tuli": "Bom dia! Faltam 3 jogos para manter seu streak hoje."
}
```

`semana` começa na segunda-feira. Valores: `feito`, `perdido`, `hoje`, `futuro`.

### `GET /api/resumo`

Alimenta a aba do Tuli.

```json
{
  "periodo_dias": 28,
  "humor_do_tuli": "avisando",
  "mensagem": {
    "titulo": "Sua voz ficou um pouco mais instável nas últimas 2 semanas.",
    "detalhe": "Isso pode ter várias causas, como cansaço ou um resfriado. Se continuar, vale conversar com seu neurologista."
  },
  "cartoes": [
    {
      "jogo": "vogal",
      "metrica": "jitter_pct",
      "status": "mudou",
      "serie": [{ "dia": "2026-10-08", "valor": 0.61 }]
    }
  ]
}
```

`humor_do_tuli`: `normal`, `comemorando`, `avisando`. `status`: `estavel`, `mudou`, `sem_dados`.

### `POST /api/relatorio` (Resend)

```json
{ "email_destino": "neuro@exemplo.com", "nome_destino": "Dra. Fulana" }
```

Resposta: `{ "enviado": true, "id": "<id do Resend>" }`.

### `GET /api/neurologistas?cidade=Recife&uf=PE` (Firecrawl)

```json
{
  "resultados": [
    { "nome": "...", "tipo": "neurologista", "endereco": "...", "telefone": "...", "fonte_url": "https://...", "atende_sus": true }
  ]
}
```

`tipo`: `neurologista`, `servico_sus`, `associacao`. `atende_sus` pode ser `null` quando a fonte não diz.

---

## Contrato B: backend ↔ análise (FastAPI)

O backend recebe o jogo do app, repassa para a análise, salva a resposta no Supabase e devolve ao app no formato do contrato A.

### `POST /analisar/vogal` e `POST /analisar/pataka`

`multipart/form-data` com `audio` (arquivo). A análise converte para WAV mono 16 kHz internamente.

Se o arquivo não for um áudio que dê para abrir, a resposta é `422` com `{ "erro": "audio_invalido", "mensagem": "..." }`. Arquivo vazio ou só ruído volta `200` com `qualidade.ok = false`.

Resposta de `vogal`:

```json
{
  "qualidade": { "ok": true, "motivo": null },
  "metricas": { "duracao_s": 9.8, "f0_medio_hz": 182.0, "f0_desvio_hz": 3.1, "jitter_pct": 0.62, "shimmer_pct": 3.4, "hnr_db": 21.5 },
  "metrica_principal": { "nome": "jitter_pct", "valor": 0.62 }
}
```

Resposta de `pataka`:

```json
{
  "qualidade": { "ok": true, "motivo": null },
  "metricas": { "duracao_s": 10.0, "silabas_por_s": 6.1, "intervalo_cv": 0.14 },
  "metrica_principal": { "nome": "silabas_por_s", "valor": 6.1 }
}
```

### `POST /analisar/espiral` e `POST /analisar/tapping`

Recebem o mesmo JSON do contrato A, sem mudanças. Respostas:

```json
{
  "qualidade": { "ok": true, "motivo": null },
  "metricas": { "duracao_s": 18.4, "desvio_medio": 0.021, "tremor_hz": 0.0, "velocidade_media": 0.11 },
  "metrica_principal": { "nome": "desvio_medio", "valor": 0.021 }
}
```

```json
{
  "qualidade": { "ok": true, "motivo": null },
  "metricas": { "toques_por_s": 4.8, "intervalo_cv": 0.12, "precisao_pct": 93.0, "queda_ritmo_pct": 6.0 },
  "metrica_principal": { "nome": "toques_por_s", "valor": 4.8 }
}
```

Como cada métrica é medida (detalhes nos módulos de `api/app/`):

| Jogo | Métrica | Como |
|---|---|---|
| `vogal` | `duracao_s` | Maior trecho contínuo com voz. Menos de 2 s volta `audio_curto`. |
| `vogal` | `jitter_pct`, `shimmer_pct`, `hnr_db`, `f0_*` | Praat (Parselmouth) no trecho com voz, sem os 0,25 s das pontas. Jitter e shimmer locais, HNR por autocorrelação, F0 de 75 a 500 Hz. |
| `pataka` | `silabas_por_s` | Picos de energia (librosa RMS) a pelo menos 70 ms e 6 dB de distância. `(n - 1) / (último - primeiro)`, então silêncio nas pontas não conta. |
| `pataka` | `intervalo_cv` | Desvio / média dos intervalos entre sílabas. |
| `espiral` | `desvio_medio` | Distância média de cada ponto ao ponto mais próximo do guia. O traço precisa cobrir 60% do guia, senão `traco_incompleto`. |
| `espiral` | `tremor_hz` | Pico de 3 a 12 Hz no espectro do erro radial. `0` quando não há oscilação clara (menos de ~1 mm ou energia espalhada). |
| `espiral` | `velocidade_media` | Comprimento do traço / tempo, em unidades normalizadas por segundo. |

`queda_ritmo_pct` compara os toques por segundo dos primeiros 5 s com os últimos 5 s. Um valor positivo quer dizer que a pessoa ficou mais lenta no fim.

### `POST /comparar`

O backend manda o histórico de uma métrica e recebe o status do cartão.

```json
{
  "jogo": "vogal",
  "metrica": "jitter_pct",
  "maior_e_melhor": false,
  "serie": [{ "dia": "2026-10-08", "valor": 0.61 }]
}
```

```json
{
  "status": "mudou",
  "linha_de_base": { "media": 0.60, "desvio": 0.03, "n": 7 },
  "recente": { "media": 0.74, "n": 7 },
  "z": 4.6,
  "direcao": "piorou"
}
```

Regra (simples de propósito, para dar para explicar no pitch):

1. **Linha de base**: média e desvio padrão dos **7 primeiros dias** com sessão válida.
2. **Recente**: média dos **últimos 7 dias** com sessão válida.
3. `z = (recente - base) / max(desvio, 5% da média da base)`. O piso evita alarme quando a pessoa é muito constante.
4. `status = "mudou"` se `|z| >= 2` **e** a mudança vai na direção ruim. Com menos de 10 dias de dados, `sem_dados`. No resto, `estavel`.
5. `direcao`: `piorou`, `melhorou` ou `igual`. Uma melhora nunca vira alerta.

## Regras de texto (regulamento do Hack Brasil)

O app **não faz diagnóstico**. Toda mensagem do Tuli:

- fala de **medidas da própria pessoa** ("sua voz ficou mais instável"), nunca da doença ("seu Parkinson piorou");
- cita causas comuns e inofensivas antes de sugerir o neurologista;
- nunca sugere mudar remédio ou dose;
- termina com o lembrete "O Tuli acompanha suas medidas e não faz diagnóstico." na aba de resumo.

Nada de dados reais de pacientes: a demo usa gravações do próprio time e o histórico sintético gerado por `api/scripts/gerar_historico.py`.
