type LatestRow = {
  id: string;
  plate: string;
  customer: string;
  service: string;
  total: number;
  status: "orçamento" | "em_andamento" | "finalizado" | "aguardando_peça";
  updatedAt: string;
};

type ReturnRow = {
  id: string;
  customer: string;
  plate: string;
  reason: string;
  when: string; // "Hoje", "Amanhã", "2d"
};

function rnd(min: number, max: number) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function pick<T>(arr: T[]): T {
  return arr[rnd(0, arr.length - 1)];
}

function plateBR() {
  // Mercosul simplificado (não perfeito, mas realista)
  const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  const L = () => letters[rnd(0, letters.length - 1)];
  const N = () => String(rnd(0, 9));
  return `${L()}${L()}${L()}${N()}${L()}${N()}${N()}`;
}

function customerName() {
  const first = [
    "Carlos", "Marcos", "Rafael", "Diego", "João", "Bruno", "Felipe",
    "Ana", "Paula", "Juliana", "Camila", "Larissa", "Renata", "Patrícia",
  ];
  const last = [
    "Silva", "Santos", "Oliveira", "Souza", "Pereira", "Costa", "Rodrigues",
    "Almeida", "Lima", "Ferreira", "Gomes", "Ribeiro",
  ];
  return `${pick(first)} ${pick(last)}`;
}

function serviceTitle() {
  return pick([
    "Troca de óleo + filtro",
    "Revisão completa",
    "Freios (pastilha + disco)",
    "Suspensão dianteira",
    "Alinhamento + balanceamento",
    "Injeção eletrônica (scanner)",
    "Arrefecimento (mangueira + aditivo)",
    "Embreagem (kit completo)",
    "Correia dentada",
    "Ar-condicionado (carga + higienização)",
  ]);
}

function updatedLabel() {
  return pick(["há 5 min", "há 18 min", "há 1 h", "há 2 h", "ontem", "hoje cedo"]);
}

function series(base: number, days: number, volatility = 0.18) {
  const out: number[] = [];
  let v = base;
  for (let i = 0; i < days; i++) {
    const drift = (Math.random() - 0.45) * volatility;
    v = Math.max(0, v + v * drift);
    out.push(Math.round(v));
  }
  return out;
}

export function demoDashboard() {
  const latest: LatestRow[] = Array.from({ length: 7 }).map((_, i) => {
    const status = pick<LatestRow["status"]>([
      "orçamento",
      "em_andamento",
      "aguardando_peça",
      "finalizado",
    ]);

    const base = status === "finalizado" ? rnd(220, 1400) : rnd(120, 900);

    return {
      id: `srv_${i}_${Date.now()}`,
      plate: plateBR(),
      customer: customerName(),
      service: serviceTitle(),
      total: base,
      status,
      updatedAt: updatedLabel(),
    };
  });

  const revenueMonth = rnd(4200, 19800);
  const revenueGoal = 25000;
  const goalProgress = Math.min(100, Math.round((revenueMonth / revenueGoal) * 100));

  const returnsPending: ReturnRow[] = Array.from({ length: rnd(5, 12) }).map((_, i) => ({
    id: `ret_${i}_${Date.now()}`,
    customer: customerName(),
    plate: plateBR(),
    reason: pick([
      "Revisão 5.000 km",
      "Retorno do freio",
      "Check-up antes de viajar",
      "Lembrete troca de óleo",
      "Barulho na suspensão",
      "Revisão do ar-condicionado",
    ]),
    when: pick(["Hoje", "Amanhã", "2d", "3d"]),
  }));

  return {
    kpis: {
      inProgress: rnd(2, 13),
      revenueMonth,
      revenueGoal,
      goalProgress,
      returnsToday: rnd(1, 9),
    },
    series: {
      inProgress14d: series(rnd(3, 8), 14, 0.22),
      revenue14d: series(rnd(350, 900), 14, 0.28),
      returns14d: series(rnd(1, 5), 14, 0.25),
    },
    latest,
    totalServices: rnd(120, 980),
    returnsPending,
  };
}