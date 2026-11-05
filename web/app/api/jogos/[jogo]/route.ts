import { NextResponse } from "next/server";
import { JOGOS, type Jogo, type Erro } from "@/lib/contrato";
import { mockRespostaJogo } from "@/lib/mocks";

// Parte 3: repassar para a análise (ANALISE_URL + /analisar/{jogo}), salvar no Supabase,
// atualizar o streak e devolver no formato RespostaJogo. Por enquanto devolve o mock.
export async function POST(_req: Request, { params }: { params: Promise<{ jogo: string }> }) {
  const { jogo } = await params;
  if (!JOGOS.includes(jogo as Jogo)) {
    return NextResponse.json<Erro>({ erro: "jogo_invalido", mensagem: `Jogo desconhecido: ${jogo}` }, { status: 404 });
  }
  return NextResponse.json(mockRespostaJogo(jogo as Jogo));
}
