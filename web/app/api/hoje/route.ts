import { NextResponse } from "next/server";
import type { RespostaHoje } from "@/lib/contrato";
import { mockHoje } from "@/lib/mocks";

// Parte 3: montar a partir das sessões do usuário no Supabase.
export async function GET() {
  return NextResponse.json<RespostaHoje>(mockHoje);
}
