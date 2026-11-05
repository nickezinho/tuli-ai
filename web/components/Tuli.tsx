// O mascote em pixel art (grade 14x16). Mesmo desenho dos mockups.
import type { HumorTuli } from "@/lib/contrato";

type Px = [x: number, y: number, w: number, h: number, cor: string];

const VERMELHO = "#E5484D";
const BRILHO = "#F58A8E";
const SOMBRA = "#B8323A";
const OLHO = "#1F2430";
const BOCHECHA = "#FFB3B8";

const CORPO: Px[] = [
  [2, 0, 1, 1, VERMELHO], [6, 0, 2, 1, VERMELHO], [11, 0, 1, 1, VERMELHO],
  [1, 1, 3, 1, VERMELHO], [5, 1, 4, 1, VERMELHO], [10, 1, 3, 1, VERMELHO],
  [1, 2, 12, 6, VERMELHO], [2, 2, 2, 1, BRILHO], [2, 3, 1, 1, BRILHO],
  [3, 7, 1, 1, BOCHECHA], [10, 7, 1, 1, BOCHECHA],
  [2, 8, 10, 1, SOMBRA], [3, 9, 8, 1, SOMBRA],
  [6, 10, 2, 3, "#2E7D46"],
  [3, 11, 3, 1, "#4CAF6A"], [8, 11, 3, 1, "#4CAF6A"], [2, 12, 3, 1, "#4CAF6A"], [9, 12, 3, 1, "#4CAF6A"],
  [4, 13, 6, 1, "#9E5530"], [4, 14, 6, 1, "#C2703D"], [5, 15, 4, 1, "#C2703D"],
];

const ROSTO: Record<HumorTuli, Px[]> = {
  normal: [[4, 5, 1, 2, OLHO], [9, 5, 1, 2, OLHO], [6, 7, 2, 1, OLHO]],
  comemorando: [
    [3, 6, 1, 1, OLHO], [4, 5, 1, 1, OLHO], [5, 6, 1, 1, OLHO],
    [8, 6, 1, 1, OLHO], [9, 5, 1, 1, OLHO], [10, 6, 1, 1, OLHO],
    [5, 7, 4, 1, OLHO],
  ],
  avisando: [[3, 4, 2, 1, OLHO], [9, 4, 2, 1, OLHO], [4, 5, 1, 2, OLHO], [9, 5, 1, 2, OLHO], [6, 7, 2, 1, OLHO]],
};

export function Tuli({ humor = "normal", tamanho = 84 }: { humor?: HumorTuli; tamanho?: number }) {
  const pixels = [...CORPO, ...ROSTO[humor]];
  return (
    <svg
      width={tamanho}
      height={(tamanho * 16) / 14}
      viewBox="0 0 14 16"
      shapeRendering="crispEdges"
      role="img"
      aria-label="Tuli, o mascote"
    >
      {pixels.map(([x, y, w, h, cor], i) => (
        <rect key={i} x={x} y={y} width={w} height={h} fill={cor} />
      ))}
    </svg>
  );
}
