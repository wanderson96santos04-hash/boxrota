import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import api from "../../lib/api";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Badge } from "../../components/ui/Badge";

type ServiceItem = {
  id: string;
  part_id?: string | null;
  description: string;
  qty: number;
  unit_price: number;
  total_price: number;
};

type Service = {
  id: string;
  status: string;
  notes?: string | null;
  labor_amount: number;
  subtotal_amount: number;
  total_amount: number;
  vehicle: { id: string; plate: string };
  customer?: { id: string; name: string; phone: string } | null;
  items: ServiceItem[];
};

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

export default function ServiceDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [service, setService] = useState<Service | null>(null);
  const [loading, setLoading] = useState(true);

  const [desc, setDesc] = useState("");
  const [qty, setQty] = useState("1");
  const [unit, setUnit] = useState("0");

  const [labor, setLabor] = useState("0");
  const [notes, setNotes] = useState("");

  const [saving, setSaving] = useState(false);

  async function load() {
    if (!id) return;
    setLoading(true);
    try {
      const res = await api.get(`/services/${id}`);
      const s: Service = res.data;
      setService(s);
      setLabor(String(s.labor_amount ?? 0));
      setNotes(s.notes ?? "");
    } catch (e) {
      console.error(e);
      navigate("/app/services");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const canEdit = useMemo(() => (service?.status !== "finalized"), [service?.status]);

  async function addItem() {
    if (!service || !id) return;
    const d = desc.trim();
    if (!d) return;

    const q = Math.max(1, Math.min(999, parseInt(qty || "1", 10) || 1));
    const u = Number(String(unit || "0").replace(",", ".")) || 0;

    setSaving(true);
    try {
      await api.post(`/services/${id}/items`, {
        description: d,
        qty: q,
        unit_price: u,
      });
      setDesc("");
      setQty("1");
      setUnit("0");
      await load();
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  }

  async function saveBasics() {
    if (!service || !id) return;

    const l = Number(String(labor || "0").replace(",", ".")) || 0;

    setSaving(true);
    try {
      await api.patch(`/services/${id}`, {
        labor_amount: l,
        notes: notes.trim() || null,
      });
      await load();
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  }

  async function finalize() {
    if (!service || !id) return;
    setSaving(true);
    try {
      await api.patch(`/services/${id}`, { status: "finalized" });
      await load();
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  }

  if (loading || !service) {
    return (
      <div className="space-y-4">
        <Card title="Carregando OS..." subtitle="Só um instante." />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <Card
        title={`OS • ${service.vehicle.plate}`}
        subtitle={service.customer?.name ? service.customer.name : "Cliente não informado"}
        right={<Badge tone={toneFromStatus(service.status) as any}>{labelFromStatus(service.status)}</Badge>}
      >
        <div className="grid gap-3 sm:grid-cols-3">
          <div className="rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-4">
            <div className="text-xs font-medium text-[var(--muted)]">Subtotal (itens)</div>
            <div className="mt-2 text-xl font-semibold text-[var(--title)]">
              {money(Number(service.subtotal_amount || 0))}
            </div>
          </div>

          <div className="rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-4">
            <div className="text-xs font-medium text-[var(--muted)]">Mão de obra</div>
            <div className="mt-2 text-xl font-semibold text-[var(--title)]">
              {money(Number(service.labor_amount || 0))}
            </div>
          </div>

          <div className="rounded-2xl border border-[var(--border)] bg-[color:rgba(47,107,255,0.12)] p-4">
            <div className="text-xs font-medium text-[var(--muted)]">Total</div>
            <div className="mt-2 text-2xl font-semibold text-[var(--title)]">
              {money(Number(service.total_amount || 0))}
            </div>
          </div>
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          <Link
            to="/app/services"
            className="h-12 inline-flex items-center justify-center rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] px-4 text-sm font-semibold text-[var(--title)] hover:bg-[color:rgba(255,255,255,0.05)]"
          >
            Voltar
          </Link>

          <button
            onClick={finalize}
            disabled={!canEdit || saving}
            className="h-12 rounded-2xl bg-[var(--success)] px-4 text-sm font-semibold text-white hover:bg-[var(--successHover)] disabled:opacity-60"
          >
            Finalizar OS (gera retorno automático depois)
          </button>
        </div>
      </Card>

      <Card title="Itens da OS" subtitle="Peças e serviços (um toque para adicionar)">
        <div className="grid gap-3 sm:grid-cols-4">
          <Input
            placeholder="Descrição (ex: Pastilha de freio)"
            value={desc}
            onChange={setDesc}
          />
          <Input placeholder="Qtd" value={qty} onChange={setQty} />
          <Input placeholder="Valor unit." value={unit} onChange={setUnit} />
          <button
            onClick={addItem}
            disabled={!canEdit || saving}
            className="h-12 rounded-2xl bg-[var(--primary)] px-4 text-sm font-semibold text-white hover:bg-[var(--primaryHover)] disabled:opacity-60"
          >
            {saving ? "Salvando..." : "Adicionar"}
          </button>
        </div>

        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          <Link
            to="/app/marketplace"
            className="h-12 inline-flex items-center justify-center rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] px-4 text-sm font-semibold text-[var(--title)] hover:bg-[color:rgba(255,255,255,0.05)]"
          >
            Adicionar do Marketplace
          </Link>
          <div className="rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] px-4 py-3 text-xs text-[var(--muted)]">
            Fluxo: OS → Marketplace → Selecionar → Adicionar
          </div>
        </div>

        <div className="mt-5 space-y-3">
          {(service.items || []).length === 0 ? (
            <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-6">
              <div className="text-sm font-semibold text-[var(--title)]">
                Nenhum item ainda
              </div>
              <div className="mt-2 text-sm text-[var(--muted)]">
                Adicione a primeira peça/serviço e o total fica automático.
              </div>
            </div>
          ) : (
            (service.items || []).map((it) => (
              <div
                key={it.id}
                className="rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-4"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="text-sm font-semibold text-[var(--title)]">
                      {it.description}
                    </div>
                    <div className="mt-1 text-xs text-[var(--muted)]">
                      {it.qty} × {money(Number(it.unit_price || 0))}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold text-[var(--title)]">
                      {money(Number(it.total_price || 0))}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </Card>

      <Card title="Mão de obra e observações" subtitle="Poucos campos. Direto ao ponto.">
        <div className="grid gap-3 sm:grid-cols-3">
          <Input placeholder="Mão de obra (R$)" value={labor} onChange={setLabor} />
          <div className="sm:col-span-2">
            <div className="relative">
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Observações (opcional)"
                className="min-h-[48px] w-full rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.03)] px-4 py-3 text-sm text-[var(--title)] placeholder:text-[var(--muted)] outline-none focus:border-[color:rgba(47,107,255,0.55)] focus:ring-2 focus:ring-[color:rgba(47,107,255,0.18)]"
              />
            </div>
          </div>
        </div>

        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          <button
            onClick={saveBasics}
            disabled={saving || !canEdit}
            className="h-12 rounded-2xl bg-[color:rgba(255,255,255,0.06)] px-4 text-sm font-semibold text-[var(--title)] hover:bg-[color:rgba(255,255,255,0.10)] disabled:opacity-60"
          >
            Salvar
          </button>
          <div className="rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] px-4 py-3 text-xs text-[var(--muted)]">
            Total recalcula automaticamente ao salvar e ao adicionar itens.
          </div>
        </div>
      </Card>
    </div>
  );
}