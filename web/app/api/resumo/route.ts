import { NextResponse } from "next/server";
import type { RespostaResumo } from "@/lib/contrato";
import { mockResumo } from "@/lib/mocks";

// Parte 3: para cada jogo, buscar a série no Supabase, chamar ANALISE_URL + /comparar
// e escolher a mensagem do Tuli (regras de texto em docs/contrato.md).
export async function GET() {
  return NextResponse.json<RespostaResumo>(mockResumo);
}
