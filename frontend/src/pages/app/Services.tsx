import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import api from "../../lib/api";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Badge } from "../../components/ui/Badge";

interface Service {
  id: string;
  status: string;
  total_amount: number;
  vehicle_plate: string;
  customer_name?: string;
  created_at: string;
}

function money(v: number) {
  try {
    return (Number(v || 0)).toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
    });
  } catch {
    return `R$ ${v}`;
  }
}

function toneFromStatus(status: string) {
  return status === "finalized" ? "success" : "primary";
}

function labelFromStatus(status: string) {
  return status === "finalized" ? "Finalizada" : "Em andamento";
}

export default function Services() {
  const [services, setServices] = useState<Service[]>([]);
  const [search, setSearch] = useState("");
  const [plate, setPlate] = useState("");
  const [customer, setCustomer] = useState("");
  const [phone, setPhone] = useState("");
  const [loading, setLoading] = useState(false);

  async function loadServices() {
    try {
      const res = await api.get("/services", {
        params: { q: search || undefined, limit: 60 },
      });
      setServices(res.data || []);
    } catch (err) {
      console.error(err);
    }
  }

  useEffect(() => {
    loadServices();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const t = setTimeout(() => loadServices(), 250);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search]);

  async function createService() {
    const p = plate.trim();
    if (!p) return;

    setLoading(true);
    try {
      await api.post("/services", {
        plate: p,
        customer_name: customer.trim() || null,
        customer_phone: phone.trim() || null,
      });

      setPlate("");
      setCustomer("");
      setPhone("");
      await loadServices();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const list = useMemo(() => services || [], [services]);

  return (
    <div className="space-y-4">
      <Card
        title="Ordens de Serviço"
        subtitle="Placa no centro. Total automático. Histórico garantido."
      >
        <div className="grid gap-3 md:grid-cols-4">
          <Input placeholder="Placa" value={plate} onChange={setPlate} />
          <Input placeholder="Cliente (opcional)" value={customer} onChange={setCustomer} />
          <Input placeholder="Telefone (opcional)" value={phone} onChange={setPhone} />
          <button
            onClick={createService}
            className="h-12 rounded-2xl bg-[var(--primary)] px-4 text-sm font-semibold text-white hover:bg-[var(--primaryHover)] disabled:opacity-60"
            disabled={loading}
          >
            {loading ? "Criando..." : "Nova OS"}
          </button>
        </div>

        <div className="mt-6">
          <Input
            placeholder="Buscar rápido: placa, cliente, telefone..."
            value={search}
            onChange={setSearch}
          />
        </div>

        <div className="mt-6 space-y-3">
          {list.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-6">
              <div className="text-sm font-semibold text-[var(--title)]">
                Nenhuma OS ainda
              </div>
              <div className="mt-2 text-sm text-[var(--muted)]">
                Crie a primeira OS com a placa — o BoxRota organiza o resto.
              </div>
            </div>
          ) : (
            list.map((s) => (
              <Link
                key={s.id}
                to={`/app/services/${s.id}`}
                className="block rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-4 hover:bg-[color:rgba(255,255,255,0.04)]"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <div className="text-base font-semibold text-[var(--title)]">
                        {s.vehicle_plate}
                      </div>
                      <Badge tone={toneFromStatus(s.status) as any}>
                        {labelFromStatus(s.status)}
                      </Badge>
                    </div>
                    <div className="mt-1 truncate text-xs text-[var(--muted)]">
                      {s.customer_name ? s.customer_name : "Cliente não informado"}
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="text-base font-semibold text-[var(--title)]">
                      {money(Number(s.total_amount || 0))}
                    </div>
                    <div className="mt-1 text-xs text-[var(--muted)]">Abrir →</div>
                  </div>
                </div>
              </Link>
            ))
          )}
        </div>
      </Card>
    </div>
  );
}