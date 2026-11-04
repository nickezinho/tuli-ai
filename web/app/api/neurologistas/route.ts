import { NextResponse } from "next/server";
import type { RespostaNeurologistas } from "@/lib/contrato";
import { mockNeurologistas } from "@/lib/mocks";

// Parte 3: buscar com o Firecrawl (FIRECRAWL_API_KEY) usando ?cidade=&uf=
// e normalizar para ResultadoNeurologista.
export async function GET() {
  return NextResponse.json<RespostaNeurologistas>(mockNeurologistas);
}
