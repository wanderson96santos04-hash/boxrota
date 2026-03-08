import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../lib/api";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Badge } from "../../components/ui/Badge";

type Vehicle = {
  id: string;
  plate: string;
  customer_name?: string | null;
  customer_phone?: string | null;
  created_at: string;
};

type CustomerOption = {
  id: string;
  name: string;
  phone?: string | null;
};

function normPlatePreview(v: string) {
  return (v || "").toUpperCase().replace(/[^A-Z0-9]/g, "").slice(0, 16);
}

export default function Vehicles() {
  const navigate = useNavigate();

  const [q, setQ] = useState("");
  const [rows, setRows] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);

  const [plate, setPlate] = useState("");
  const [saving, setSaving] = useState(false);

  const [customers, setCustomers] = useState<CustomerOption[]>([]);
  const [customersLoading, setCustomersLoading] = useState(false);
  const [customerId, setCustomerId] = useState("");

  async function load(term?: string) {
    setLoading(true);
    try {
      const res = await api.get("/vehicles", {
        params: { q: term || undefined, limit: 60 },
      });
      setRows(res.data || []);
    } catch (e) {
      console.error(e);
      setRows([]);
    } finally {
      setLoading(false);
    }
  }

  async function loadCustomers() {
    setCustomersLoading(true);
    try {
      const res = await api.get("/customers", {
        params: { limit: 100 },
      });

      const raw = Array.isArray(res.data) ? res.data : [];
      const mapped = raw
        .map((item: any) => ({
          id: String(item?.id ?? ""),
          name: String(item?.name ?? "").trim(),
          phone:
            typeof item?.phone === "string" && item.phone.trim()
              ? item.phone.trim()
              : null,
        }))
        .filter((item: CustomerOption) => item.id && item.name);

      setCustomers(mapped);
    } catch (e) {
      console.error(e);
      setCustomers([]);
    } finally {
      setCustomersLoading(false);
    }
  }

  useEffect(() => {
    load();
    loadCustomers();
  }, []);

  useEffect(() => {
    const t = setTimeout(() => load(q), 250);
    return () => clearTimeout(t);
  }, [q]);

  async function create() {
    const p = normPlatePreview(plate);
    if (p.length < 4) return;

    setSaving(true);
    try {
      await api.post("/vehicles", {
        plate: p,
        customer_id: customerId || null,
      });

      setPlate("");
      setCustomerId("");
      await load(q);
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  }

  function handleOpenOs() {
    navigate("/app/services");
  }

  const list = useMemo(() => rows || [], [rows]);

  return (
    <div className="space-y-4">
      <Card
        title="Veículos"
        subtitle="A placa é o centro de tudo. Histórico e OS começam aqui."
        right={<Badge tone="primary">placa</Badge>}
      >
        <div className="grid gap-3 sm:grid-cols-3">
          <Input
            placeholder="Placa (ex: ABC1234)"
            value={plate}
            onChange={(v) => setPlate(normPlatePreview(v))}
          />

          <div className="sm:col-span-2">
            <select
              value={customerId}
              onChange={(e) => setCustomerId(e.target.value)}
              className="h-12 w-full rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.03)] px-4 text-sm text-[var(--title)] outline-none focus:border-[color:rgba(47,107,255,0.55)] focus:ring-2 focus:ring-[color:rgba(47,107,255,0.18)]"
            >
              <option value="">
                {customersLoading
                  ? "Carregando clientes..."
                  : "Selecionar cliente (opcional)"}
              </option>

              {customers.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                  {c.phone ? ` • ${c.phone}` : ""}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={create}
            disabled={saving}
            className="h-12 rounded-2xl bg-[var(--primary)] px-4 text-sm font-semibold text-white hover:bg-[var(--primaryHover)] disabled:opacity-60 sm:col-span-3"
          >
            {saving ? "Salvando..." : "Cadastrar veículo"}
          </button>
        </div>

        <div className="mt-6">
          <Input
            placeholder="Buscar rápido: placa, cliente ou telefone..."
            value={q}
            onChange={setQ}
          />
        </div>

        <div className="mt-6 space-y-3">
          {loading ? (
            <div className="text-sm text-[var(--muted)]">Carregando...</div>
          ) : list.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-6">
              <div className="text-sm font-semibold text-[var(--title)]">
                Nenhum veículo cadastrado
              </div>
              <div className="mt-2 text-sm text-[var(--muted)]">
                Cadastre uma placa e vincule um cliente para abrir a OS mais
                rápido.
              </div>
            </div>
          ) : (
            list.map((v) => (
              <div
                key={v.id}
                className="rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-4"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <div className="text-base font-semibold text-[var(--title)]">
                        {v.plate}
                      </div>
                      <Badge tone="neutral">Histórico</Badge>
                    </div>

                    <div className="mt-1 text-xs text-[var(--muted)]">
                      {v.customer_name
                        ? `${v.customer_name}${v.customer_phone ? ` • ${v.customer_phone}` : ""}`
                        : "Cliente não vinculado"}
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="text-xs font-medium text-[var(--muted)]">
                      Próximo passo
                    </div>
                    <button
                      type="button"
                      onClick={handleOpenOs}
                      className="mt-1 text-xs text-[var(--primary)] hover:underline"
                    >
                      Abrir OS → por placa
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </Card>
    </div>
  );
}