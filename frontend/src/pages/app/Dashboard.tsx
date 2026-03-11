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
      aria-hidden="true"
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
          <TrendBlock
            spark={
              spark ?? [8, 10, 9, 12, 11, 14, 16, 13, 15, 18, 16, 17, 20, 21]
            }
          />
        </div>
      </div>
    </div>
  );
}

function StatusPill({ s }: { s: ServiceRow["status"] }) {
  const cls =
    s === "Finalizado"
      ? "bg-emerald-500/10 text-emerald-700 ring-emerald-400/30"
      : s === "Aguardando peça"
      ? "bg-amber-500/10 text-amber-700 ring-amber-400/30"
      : "bg-[color:rgba(47,107,255,0.10)] text-[var(--title)] ring-[color:rgba(47,107,255,0.25)]";

  return (
    <span
      className={cx(
        "inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ring-1 whitespace-nowrap",
        cls
      )}
    >
      {s}
    </span>
  );
}

function mapStatusToLabel(status: string): ServiceRow["status"] {
  switch (status) {
    case "waiting_parts":
      return "Aguardando peça";
    case "completed":
    case "delivered":
      return "Finalizado";
    case "draft":
    case "open":
    case "in_progress":
    case "canceled":
    default:
      return "Em andamento";
  }
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;

    (async () => {
      try {
        setLoading(true);
        setError(null);

        const res = await api.get<DashboardStats>("/dashboard");
        if (!alive) return;

        setStats(res.data);
      } catch (e: any) {
        if (!alive) return;

        const msg =
          e?.response?.data?.detail ||
          e?.message ||
          "Falha ao carregar o dashboard.";
        setError(String(msg));
      } finally {
        if (!alive) return;
        setLoading(false);
      }
    })();

    return () => {
      alive = false;
    };
  }, []);

  const monthGoal = 25000;
  const monthRevenue = stats?.revenue_month ?? 0;

  const pct = useMemo(() => {
    return Math.round((monthRevenue / Math.max(1, monthGoal)) * 100);
  }, [monthRevenue, monthGoal]);

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
  const returnsTodayValue = "—";

  return (
    <div className="w-full overflow-x-hidden">
      <div className="mx-auto w-full max-w-6xl px-4 py-6 sm:px-6 sm:py-7">
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-start">
          <div className="min-w-0">
            <div className="text-2xl font-semibold text-[var(--title)]">
              Dashboard
            </div>
            <div className="mt-1 text-sm text-[var(--muted)]">
              Visão rápida do que está rodando hoje — e onde você ganha mais.
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 min-w-0">
            <Pill tone={error ? "neutral" : "success"}>
              <span
                className={cx(
                  "inline-block h-1.5 w-1.5 rounded-full",
                  error ? "bg-amber-500" : "bg-emerald-500"
                )}
              />
              {error ? "Atenção" : "Online"}
            </Pill>
            <button className="inline-flex max-w-full items-center gap-2 rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] px-4 py-2 text-sm font-semibold text-[var(--title)] hover:bg-[color:rgba(255,255,255,0.04)]">
              Ctrl K • Buscar
            </button>
          </div>
        </div>

        {error && (
          <div className="mt-4 rounded-2xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-[var(--title)]">
            {error}
          </div>
        )}

        <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <KpiCard
            label="Serviços em andamento"
            value={openServicesValue}
            hint="Inclui aguardando peça e em execução."
            spark={[8, 10, 9, 12, 11, 14, 16, 13, 15, 18, 16, 17, 20, 21]}
          />

          <div className="rounded-[18px] border border-[var(--border)] bg-[var(--surface)] p-5 shadow-[0_18px_55px_rgba(0,0,0,0.14)] min-w-0">
            <div className="grid gap-4 md:grid-cols-[1fr_140px] md:items-start">
              <div className="min-w-0">
                <div className="text-xs font-semibold uppercase tracking-wide text-[var(--muted)]">
                  Faturamento do mês
                </div>
                <div className="mt-2 text-3xl font-semibold text-[var(--title)] md:whitespace-nowrap">
                  {loading ? "—" : formatBRL(monthRevenue)}
                </div>
                <div className="mt-2 text-sm text-[var(--muted)]">
                  Meta:{" "}
                  <span className="font-semibold">{formatBRL(monthGoal)}</span>{" "}
                  •{" "}
                  <span className="font-semibold">
                    {loading ? "—" : `${pct}%`}
                  </span>
                </div>
              </div>

              <div className="min-w-0 md:justify-self-end">
                <TrendBlock
                  spark={[
                    10, 12, 15, 14, 16, 18, 20, 19, 22, 24, 23, 25, 28, 30,
                  ]}
                />
              </div>
            </div>

            <div className="mt-4">
              <div className="h-2 w-full rounded-full bg-black/5">
                <div
                  className="h-2 rounded-full bg-[var(--primary)]"
                  style={{ width: `${Math.min(100, loading ? 0 : pct)}%` }}
                />
              </div>
              <div className="mt-2 text-xs text-[var(--muted)]">
                Projeção: se mantiver o ritmo, fecha a meta em ~9 dias úteis.
              </div>
            </div>
          </div>

          <KpiCard
            label="Retornos para hoje"
            value={returnsTodayValue}
            hint="Vamos ligar isso ao módulo de retornos."
            spark={[3, 4, 4, 5, 4, 6, 5, 5, 6, 7, 6, 6, 7, 8]}
          />
        </div>

        <div className="mt-6 grid gap-4 xl:grid-cols-3">
          <div className="min-w-0 xl:col-span-2">
            <Card
              title="Últimos serviços"
              right={
                <span className="text-xs font-semibold text-[var(--muted)]">
                  Foco: orçamento, execução e finalização
                </span>
              }
            >
              {!loading && rows.length === 0 ? (
                <div className="py-2 text-center text-sm text-[var(--muted)]">
                  Nenhum serviço encontrado ainda.
                </div>
              ) : (
                <>
                  <div className="space-y-3 md:hidden">
                    {rows.map((r, idx) => (
                      <div
                        key={`${r.plate}-${idx}`}
                        className="rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-4"
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div className="min-w-0">
                            <div className="text-sm font-semibold text-[var(--title)]">
                              {r.plate}
                            </div>
                            <div className="mt-1 text-xs text-[var(--muted)]">
                              {r.customer}
                            </div>
                            <div className="mt-3 text-sm font-medium text-[var(--title)]">
                              {r.service}
                            </div>
                            {r.updated ? (
                              <div className="mt-1 text-xs text-[var(--muted)]">
                                {r.updated}
                              </div>
                            ) : null}
                            <div className="mt-3 text-sm font-semibold text-[var(--title)]">
                              {formatBRL(r.total)}
                            </div>
                          </div>

                          <div className="shrink-0">
                            <StatusPill s={r.status} />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="hidden md:block">
                    <table className="w-full border-separate border-spacing-0">
                      <thead>
                        <tr className="text-left text-[11px] font-semibold uppercase tracking-wide text-[var(--muted)]">
                          <th className="border-b border-[var(--border)] pb-3">
                            Placa / Cliente
                          </th>
                          <th className="border-b border-[var(--border)] pb-3">
                            Serviço
                          </th>
                          <th className="border-b border-[var(--border)] pb-3">
                            Total
                          </th>
                          <th className="border-b border-[var(--border)] pb-3">
                            Status
                          </th>
                        </tr>
                      </thead>

                      <tbody>
                        {rows.map((r, idx) => (
                          <tr key={`${r.plate}-${idx}`} className="align-top">
                            <td className="border-b border-[var(--border)] py-4">
                              <div className="text-sm font-semibold text-[var(--title)]">
                                {r.plate}
                              </div>
                              <div className="text-xs text-[var(--muted)]">
                                {r.customer}
                              </div>
                            </td>

                            <td className="border-b border-[var(--border)] py-4">
                              <div className="text-sm font-medium text-[var(--title)]">
                                {r.service}
                              </div>
                              <div className="text-xs text-[var(--muted)]">
                                {r.updated}
                              </div>
                            </td>

                            <td className="border-b border-[var(--border)] py-4">
                              <div className="text-sm font-semibold text-[var(--title)]">
                                {formatBRL(r.total)}
                              </div>
                            </td>

                            <td className="border-b border-[var(--border)] py-4">
                              <StatusPill s={r.status} />
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}

              <div className="mt-4 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div className="text-xs text-[var(--muted)]">
                  Dica: priorize “Aguardando peça” para não travar caixa.
                </div>
                <button className="inline-flex h-10 items-center justify-center rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] px-4 text-sm font-semibold text-[var(--title)] hover:bg-[color:rgba(255,255,255,0.04)]">
                  Ver tudo
                </button>
              </div>
            </Card>
          </div>

          <div className="min-w-0 xl:col-span-1">
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

        <div className="mt-6 text-center text-xs text-[var(--muted)]">
          BoxRota • Dados reais via API • Atualiza ao abrir
        </div>
      </div>
    </div>
  );
}
