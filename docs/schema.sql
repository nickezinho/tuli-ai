-- Esquema inicial do Supabase (parte 3). Rodar no SQL Editor do projeto.

create table perfis (
  id uuid primary key references auth.users (id) on delete cascade,
  nome text not null,
  ano_nascimento int,
  ano_diagnostico int,
  mao_dominante text check (mao_dominante in ('direita', 'esquerda')),
  email_cuidador text,
  email_medico text,
  cidade text,
  uf char(2),
  criado_em timestamptz not null default now()
);

-- Calibragem: verificação do microfone e da tela feita no primeiro acesso.
create table calibragens (
  id uuid primary key default gen_random_uuid(),
  usuario_id uuid not null references perfis (id) on delete cascade,
  microfone_ok boolean not null,
  ruido_ambiente_db real,
  toque_ok boolean not null,
  criado_em timestamptz not null default now()
);

-- Uma linha por jogo jogado. metricas guarda o objeto inteiro que a análise devolveu.
create table sessoes (
  id uuid primary key default gen_random_uuid(),
  usuario_id uuid not null references perfis (id) on delete cascade,
  jogo text not null check (jogo in ('vogal', 'pataka', 'espiral', 'tapping')),
  dia date not null default (now() at time zone 'America/Sao_Paulo')::date,
  qualidade_ok boolean not null,
  metricas jsonb,
  metrica_principal_nome text,
  metrica_principal_valor real,
  audio_path text, -- caminho no Storage, só para vogal e pataka
  criado_em timestamptz not null default now()
);

create index sessoes_usuario_jogo_dia on sessoes (usuario_id, jogo, dia);

alter table perfis enable row level security;
alter table calibragens enable row level security;
alter table sessoes enable row level security;

create policy "dono le e escreve perfil" on perfis for all using (auth.uid() = id) with check (auth.uid() = id);
create policy "dono le e escreve calibragens" on calibragens for all using (auth.uid() = usuario_id) with check (auth.uid() = usuario_id);
create policy "dono le e escreve sessoes" on sessoes for all using (auth.uid() = usuario_id) with check (auth.uid() = usuario_id);
