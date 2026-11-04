# Tuli

App web para pessoas com Parkinson fazerem 4 jogos rápidos por dia (voz e toque na tela) e acompanharem as próprias medidas ao longo do tempo. Quando uma medida muda em relação à linha de base da pessoa, o mascote Tuli avisa que vale conversar com o neurologista. **O app não faz diagnóstico.**

Projeto do Hack Brasil, tema Saúde e bem-estar.

## Os 4 jogos

| Jogo | O que mede |
|---|---|
| Segure o "aaaa" | estabilidade da voz (jitter, shimmer, HNR) |
| Pa-ta-ka | agilidade da fala (sílabas por segundo) |
| Espiral | tremor e precisão do traço |
| Tapping | velocidade, ritmo e queda de ritmo dos toques |

## Estrutura

```
docs/contrato.md   formato dos dados entre as 3 partes (leia primeiro)
docs/schema.sql    tabelas do Supabase
web/               Next.js: telas, jogos e rotas /api/* (partes 1 e 3)
api/               FastAPI: análise de voz e toque (parte 2)
```

## Divisão do trabalho

1. **App e jogos** (`web/app`, `web/components`): telas, Tuli, streak, captura de áudio com `MediaRecorder` e dos toques com Pointer Events.
2. **Análise** (`api/`): um endpoint por jogo, a comparação com a linha de base (`/comparar`) e o histórico sintético da demo.
3. **Backend e integrações** (`web/app/api`, Supabase): login, perfil, salvar sessões, streak, Resend (lembretes e relatório semanal), Firecrawl (busca de neurologistas e serviços do SUS), cron e deploy.

Todas as rotas já respondem com dados falsos no formato do contrato (`web/lib/mocks.ts` e os `TODO` em `api/app/main.py`), então cada parte começa sem esperar as outras.

## Rodando

**App (web/):**

```bash
cd web
cp .env.example .env.local
npm install
npm run dev        # http://localhost:3000
```

**Análise (api/):**

```bash
cd api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload   # http://localhost:8000/docs
pytest
python scripts/gerar_historico.py   # histórico sintético de 30 dias
```

## Stack

Next.js 15 + React 19 + TypeScript + Tailwind 4 (Vercel) · FastAPI + Parselmouth + librosa (Render ou Railway) · Supabase (Postgres, auth, storage) · Resend · Firecrawl · Devin.

## Regras do regulamento

- Nada de diagnóstico ou prescrição: o Tuli fala das medidas da pessoa, nunca da doença.
- Nada de dados reais de pacientes: a demo usa gravações do time e o histórico sintético.
