import { NextResponse } from "next/server";
import type { EntradaRelatorio, Erro, RespostaRelatorio } from "@/lib/contrato";

// Parte 3: montar o email com o resumo e enviar pelo Resend (RESEND_API_KEY).
export async function POST(req: Request) {
  const corpo = (await req.json()) as Partial<EntradaRelatorio>;
  if (!corpo.email_destino) {
    return NextResponse.json<Erro>({ erro: "email_obrigatorio", mensagem: "Informe o email de destino." }, { status: 400 });
  }
  return NextResponse.json<RespostaRelatorio>({ enviado: false, id: null });
}
