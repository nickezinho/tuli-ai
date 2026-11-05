// Home (parte 1). Lê o mock direto; troque por fetch("/api/hoje") quando quiser.
import { Tuli } from "@/components/Tuli";
import type { Jogo } from "@/lib/contrato";
import { mockHoje } from "@/lib/mocks";

const NOME_JOGO: Record<Jogo, string> = {
  vogal: "Segure o “aaaa”",
  pataka: "Pa-ta-ka",
  espiral: "Espiral",
  tapping: "Tapping",
};

const DIAS = ["S", "T", "Q", "Q", "S", "S", "D"];

export default function Home() {
  const hoje = mockHoje;
  return (
    <div className="flex min-h-dvh flex-col px-5 pt-6 pb-8">
      <header className="flex items-center justify-between">
        <span className="font-pixel text-3xl font-bold text-tulipa">tuli</span>
        <span className="rounded-full border-2 border-[#FFD9A0] bg-[#FFF4E0] px-3 py-1 font-pixel text-lg font-bold text-[#A34F00]">
          {hoje.streak.dias} dias
        </span>
      </header>

      <ol className="mt-4 grid grid-cols-7 gap-1.5">
        {hoje.streak.semana.map((s, i) => (
          <li key={i} className="flex flex-col items-center gap-1.5 text-xs font-bold text-texto-suave">
            {DIAS[i]}
            <span
              className={
                s === "feito"
                  ? "size-7 rounded-lg bg-streak"
                  : s === "hoje"
                    ? "size-7 rounded-lg border-2 border-dashed border-streak"
                    : "size-7 rounded-lg bg-[#EEF0F3]"
              }
            />
          </li>
        ))}
      </ol>

      <div className="mt-5 flex items-end gap-3">
        <Tuli />
        <p className="flex-1 rounded-2xl rounded-bl border-2 border-borda bg-fundo-suave px-4 py-3 font-bold">
          {hoje.fala_do_tuli}
        </p>
      </div>

      <ul className="mt-6 flex flex-col gap-2.5">
        {hoje.jogos.map(({ jogo, status }) => (
          <li
            key={jogo}
            className={`rounded-2xl border-2 px-4 py-3 font-extrabold ${
              status === "proximo" ? "border-tulipa border-b-[5px]" : status === "feito" ? "border-borda bg-[#F4FBF6]" : "border-borda"
            }`}
          >
            {NOME_JOGO[jogo]}
            {status === "feito" && <span className="ml-2 text-sm text-folha-escura">Feito</span>}
          </li>
        ))}
      </ul>

      <button
        type="button"
        className="mt-auto h-14 rounded-2xl bg-tulipa text-lg font-extrabold tracking-wide text-white uppercase shadow-[0_5px_0_var(--color-tulipa-escura)]"
      >
        Continuar
      </button>
    </div>
  );
}
