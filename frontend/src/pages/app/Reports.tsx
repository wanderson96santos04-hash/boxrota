import { useEffect, useState } from "react";
import api from "../../lib/api";
import { Card } from "../../components/ui/Card";

type ReportStats = {
  revenue: number;
  open_value: number;
  finished_orders: number;
  average_ticket: number;
};

function money(v: number) {
  try {
    return Number(v || 0).toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  } catch {
    return `R$ ${Number(v || 0).toFixed(2).replace(".", ",")}`;
  }
}

export default function Reports() {
  const [stats, setStats] = useState<ReportStats | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const res = await api.get("/reports/month");
        setStats(res.data);
      } catch (e) {
        console.error(e);
      }
    }

    load();
  }, []);

  return (
    <div className="space-y-4">
      <Card className="p-4">
        <div className="text-sm text-[var(--muted)]">
          Faturamento do mês
        </div>
        <div className="text-2xl font-semibold">
          {money(stats?.revenue ?? 0)}
        </div>
      </Card>

      <Card className="p-4">
        <div className="text-sm text-[var(--muted)]">
          Valor em aberto
        </div>
        <div className="text-2xl font-semibold">
          {money(stats?.open_value ?? 0)}
        </div>
      </Card>

      <Card className="p-4">
        <div className="text-sm text-[var(--muted)]">
          OS finalizadas
        </div>
        <div className="text-2xl font-semibold">
          {stats?.finished_orders ?? 0}
        </div>
      </Card>

      <Card className="p-4">
        <div className="text-sm text-[var(--muted)]">
          Ticket médio
        </div>
        <div className="text-2xl font-semibold">
          {money(stats?.average_ticket ?? 0)}
        </div>
      </Card>
    </div>
  );
}