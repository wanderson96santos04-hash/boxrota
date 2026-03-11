import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../lib/api";

type ServiceRow = {
  plate: string;
  customer: string;
  service: string;
  updated: string;
  total: number;
  status: "Em andamento" | "Aguardando peça" | "Finalizado";
};

type DashboardLastService = {
  id: string;
  plate: string;
  total: number;
  status: string;
};

type DashboardStats = {
  open_services: number;
  revenue_month: number;
  last_services: DashboardLastService[];
};

function cx(...s: Array<string | false | undefined | null>) {
  return s.filter(Boolean).join(" ");
}

function formatBRL(v: number) {
  return v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function Pill({
  children,
  tone = "neutral",
}: {
  children: React.ReactNode;
  tone?: "neutral" | "success" | "primary";
}) {
  const toneCls =
    tone === "success"
      ? "bg-emerald-500/10 text-emerald-700 ring-emerald-400/30"
      : tone === "primary"
      ? "bg-[color:rgba(47,107,255,0.12)] text-[var(--title)] ring-[color:rgba(47,107,255,0.25)]"
      : "bg-black/5 text-[var(--text)] ring-black/10";

  return (
    <span
      className={cx(
        "inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold ring-1 whitespace-nowrap",
        toneCls
      )}
    >
      {children}
    </span>
  );
}

function Card({
  title,
  right,
  children,
}: {
  title: string;
  right?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-[18px] border border-[var(--border)] bg-[var(--surface)] shadow-[0_18px_55px_rgba(0,0,0,0.14)] min-w-0">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--border)] px-5 py-4 min-w-0">
        <div className="text-sm font-semibold text-[var(--title)]">{title}</div>
        {right}
      </div>
      <div className="p-5 min-w-0">{children}</div>
    </div>
  );
}

function Sparkline({
  values,
  className,
}: {
  values: number[];
  className?: string;
}) {
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = Math.max(1e-6, max - min);

  const pts = values
    .map((v, i) => {
      const x = (i / Math.max(1, values.length - 1)) * 100;
      const y = 100 - ((v - min) / span) * 100;
      return `${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(" ");

  return (
    <svg
      viewBox="0 0 100 100"
      className={cx("h-10 w-full overflow-hidden", className)}
      preserveAspectRatio="none"
    >
      <polyline
        fill="none"
        stroke="currentColor"
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
        points={pts}
        opacity="0.85"
      />
    </svg>
  );
}

function TrendBlock({
  trendLabel = "Últimos 14 dias",
  trendPill = "em alta",
  spark = [12, 14, 13, 17, 16, 18, 22, 19, 21, 26, 24, 27, 29, 31],
}: {
  trendLabel?: string;
  trendPill?: string;
  spark?: number[];
}) {
  return (
    <div className="flex flex-col items-start gap-2 md:items-end">
      <div className="flex flex-wrap items-center gap-2 md:justify-end">
        <span className="text-[11px] font-semibold text-[var(--muted)] whitespace-nowrap">
          {trendLabel}
        </span>
        <Pill tone="success">
          <span className="inline-block h-1.5 w-1.5 rounded-full bg-emerald-500" />
          {trendPill}
        </Pill>
      </div>

      <div className="w-full max-w-[120px] text-[var(--title)]">
        <Sparkline values={spark} className="text-[var(--title)]/80" />
      </div>
    </div>
  );
}

function KpiCard({
  label,
  value,
  hint,
  spark,
}: {
  label: string;
  value: string;
  hint: string;
  spark?: number[];
}) {
  return (
    <div className="rounded-[18px] border border-[var(--border)] bg-[var(--surface)] p-5 shadow-[0_18px_55px_rgba(0,0,0,0.14)] min-w-0">
      <div className="grid gap-4 md:grid-cols-[1fr_140px] md:items-start">
        <div className="min-w-0">
          <div className="text-xs font-semibold uppercase tracking-wide text-[var(--muted)]">
            {label}
          </div>

          <div className="mt-2 text-3xl font-semibold text-[var(--title)] md:whitespace-nowrap">
            {value}
          </div>

          <div className="mt-2 text-sm text-[var(--muted)]">{hint}</div>
        </div>

        <div className="min-w-0 md:justify-self-end">
          <TrendBlock spark={spark} />
        </div>
      </div>
    </div>
  );
}

function mapStatusToLabel(status: string): ServiceRow["status"] {
  switch (status) {
    case "waiting_parts":
      return "Aguardando peça";
    case "completed":
    case "delivered":
      return "Finalizado";
    default:
      return "Em andamento";
  }
}

export default function Dashboard() {

  const navigate = useNavigate();

  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get("/dashboard");
        setStats(res.data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const monthGoal = 25000;
  const monthRevenue = stats?.revenue_month ?? 0;

  const pct = useMemo(() => {
    return Math.round((monthRevenue / Math.max(1, monthGoal)) * 100);
  }, [monthRevenue]);

  const rows: ServiceRow[] = useMemo(() => {
    const last = stats?.last_services ?? [];
    return last.map((s) => ({
      plate: s.plate || "-",
      customer: "—",
      service: "—",
      updated: "",
      total: Number(s.total ?? 0),
      status: mapStatusToLabel(s.status),
    }));
  }, [stats]);

  const openServicesValue = loading ? "—" : String(stats?.open_services ?? 0);

  return (
    <div className="w-full overflow-x-hidden">
      <div className="mx-auto w-full max-w-6xl px-4 py-6 sm:px-6 sm:py-7">

        <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">

          <KpiCard
            label="Serviços em andamento"
            value={openServicesValue}
            hint="Inclui aguardando peça e em execução."
            spark={[8,10,9,12,11,14,16,13,15,18,16,17,20,21]}
          />

          <div className="rounded-[18px] border border-[var(--border)] bg-[var(--surface)] p-5 shadow-[0_18px_55px_rgba(0,0,0,0.14)]">

            <div className="text-xs font-semibold uppercase tracking-wide text-[var(--muted)]">
              Faturamento do mês
            </div>

            <div className="mt-2 text-3xl font-semibold text-[var(--title)] md:whitespace-nowrap">
              {loading ? "—" : formatBRL(monthRevenue)}
            </div>

            <div className="mt-2 text-sm text-[var(--muted)]">
              Meta: {formatBRL(monthGoal)} • {pct}%
            </div>

          </div>

        </div>

        {/* AÇÃO RÁPIDA */}

        <div className="mt-6 grid gap-4 xl:grid-cols-3">

          <div className="xl:col-span-2"></div>

          <div className="xl:col-span-1">

            <Card title="Ação rápida" right={<Pill tone="primary">Atalhos</Pill>}>

              <div className="space-y-3">

                <div className="rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-4">
                  <div className="text-sm font-semibold text-[var(--title)]">
                    Criar OS em 10 segundos
                  </div>

                  <div className="mt-1 text-sm text-[var(--muted)]">
                    Comece pela placa e puxe histórico + cliente.
                  </div>

                  <button
                    onClick={() => navigate("/app/services")}
                    className="mt-3 inline-flex h-10 w-full items-center justify-center rounded-2xl bg-[var(--primary)] px-4 text-sm font-semibold text-white hover:bg-[var(--primaryHover)]"
                  >
                    Nova OS
                  </button>
                </div>

                <div className="rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-4">

                  <div className="text-sm font-semibold text-[var(--title)]">
                    Enviar retornos do dia
                  </div>

                  <div className="mt-1 text-sm text-[var(--muted)]">
                    Mensagens prontas no WhatsApp, 1 clique por cliente.
                  </div>

                  <button
                    onClick={() => navigate("/app/returns")}
                    className="mt-3 inline-flex h-10 w-full items-center justify-center rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.03)] px-4 text-sm font-semibold text-[var(--title)] hover:bg-[color:rgba(255,255,255,0.06)]"
                  >
                    Abrir retornos
                  </button>
                </div>

                <div className="rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-4">

                  <div className="text-sm font-semibold text-[var(--title)]">
                    Caixa do mês
                  </div>

                  <div className="mt-1 text-sm text-[var(--muted)]">
                    Veja o que entrou, o que está em aberto e o que está parado.
                  </div>

                  <button
                    onClick={() => navigate("/app")}
                    className="mt-3 inline-flex h-10 w-full items-center justify-center rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.03)] px-4 text-sm font-semibold text-[var(--title)] hover:bg-[color:rgba(255,255,255,0.06)]"
                  >
                    Ver relatório
                  </button>

                </div>

              </div>

            </Card>

          </div>

        </div>

      </div>
    </div>
  );
}