import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../lib/api";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Badge } from "../../components/ui/Badge";

type VehicleFilter = "all" | "car" | "moto";

type Part = {
  id: string;
  name: string;
  sku?: string | null;
  price?: number | string | null;
  suggested_price?: number | string | null;
  stock_qty?: number | null;
  vehicle_type?: string | null;
  created_at?: string;
};

function extractErrorMessage(err: any): string {
  const data = err?.response?.data;

  if (!data) {
    return err?.message || "Erro ao salvar peça.";
  }

  if (typeof data.message === "string" && data.message.trim()) {
    return data.message;
  }

  if (typeof data.detail === "string" && data.detail.trim()) {
    return data.detail;
  }

  if (Array.isArray(data.detail) && data.detail.length > 0) {
    const first = data.detail[0];
    if (typeof first?.msg === "string") {
      return first.msg;
    }
  }

  return "Erro ao salvar peça.";
}

export default function Parts() {
  const navigate = useNavigate();

  const [q, setQ] = useState("");
  const [rows, setRows] = useState<Part[]>([]);
  const [loading, setLoading] = useState(true);

  const [vehicleType, setVehicleType] = useState<VehicleFilter>("all");

  const [showManualForm, setShowManualForm] = useState(false);
  const [saving, setSaving] = useState(false);

  const [name, setName] = useState("");
  const [sku, setSku] = useState("");
  const [price, setPrice] = useState("");
  const [stockQty, setStockQty] = useState("");

  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function load(term?: string) {
    setLoading(true);
    try {
      const params: Record<string, string | number> = {
        limit: 60,
      };

      if (term && term.trim()) {
        params.q = term.trim();
      }

      if (vehicleType !== "all") {
        params.vehicle_type = vehicleType;
      }

      const res = await api.get("/parts", { params });
      setRows(Array.isArray(res.data) ? res.data : []);
    } catch (e) {
      console.error(e);
      setRows([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vehicleType]);

  useEffect(() => {
    const t = setTimeout(() => load(q), 250);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q, vehicleType]);

  async function createManualPart() {
    const cleanName = name.trim();
    if (!cleanName) return;

    const parsedPrice = Number(String(price || "0").replace(",", ".")) || 0;
    const parsedStockQty = parseInt(String(stockQty || "0"), 10) || 0;

    setError(null);
    setSuccess(null);
    setSaving(true);

    try {
      await api.post("/parts", {
        name: cleanName,
        sku: sku.trim() || null,
        price: parsedPrice,
        stock_qty: parsedStockQty,
      });

      setName("");
      setSku("");
      setPrice("");
      setStockQty("");
      setShowManualForm(false);
      setSuccess("Peça salva com sucesso.");

      await load(q);
    } catch (e: any) {
      console.error(e);
      setError(extractErrorMessage(e));
    } finally {
      setSaving(false);
    }
  }

  function handleOpenServices() {
    navigate("/app/services");
  }

  const list = useMemo(() => rows || [], [rows]);

  return (
    <div className="space-y-4">
      <Card title="Peças" subtitle="Catálogo rápido para adicionar na OS.">
        <div className="grid gap-3">
          <Input
            placeholder="Buscar peça por nome ou SKU..."
            value={q}
            onChange={setQ}
          />

          <div className="grid grid-cols-3 gap-2 sm:max-w-md">
            <button
              type="button"
              onClick={() => setVehicleType("all")}
              className={`h-11 rounded-2xl border px-3 text-sm font-semibold transition ${
                vehicleType === "all"
                  ? "border-[var(--primary)] bg-[color:rgba(47,107,255,0.18)] text-[var(--title)]"
                  : "border-[var(--border)] bg-[color:rgba(255,255,255,0.03)] text-[var(--muted)] hover:bg-[color:rgba(255,255,255,0.06)]"
              }`}
            >
              Todos
            </button>

            <button
              type="button"
              onClick={() => setVehicleType("car")}
              className={`h-11 rounded-2xl border px-3 text-sm font-semibold transition ${
                vehicleType === "car"
                  ? "border-[var(--primary)] bg-[color:rgba(47,107,255,0.18)] text-[var(--title)]"
                  : "border-[var(--border)] bg-[color:rgba(255,255,255,0.03)] text-[var(--muted)] hover:bg-[color:rgba(255,255,255,0.06)]"
              }`}
            >
              Carro
            </button>

            <button
              type="button"
              onClick={() => setVehicleType("moto")}
              className={`h-11 rounded-2xl border px-3 text-sm font-semibold transition ${
                vehicleType === "moto"
                  ? "border-[var(--primary)] bg-[color:rgba(47,107,255,0.18)] text-[var(--title)]"
                  : "border-[var(--border)] bg-[color:rgba(255,255,255,0.03)] text-[var(--muted)] hover:bg-[color:rgba(255,255,255,0.06)]"
              }`}
            >
              Moto
            </button>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <button
              type="button"
              onClick={() => {
                setError(null);
                setSuccess(null);
                setShowManualForm((v) => !v);
              }}
              className="h-12 rounded-2xl bg-[color:rgba(255,255,255,0.06)] px-4 text-sm font-semibold text-[var(--title)] hover:bg-[color:rgba(255,255,255,0.10)]"
            >
              {showManualForm ? "Fechar cadastro manual" : "Adicionar peça manual"}
            </button>

            <button
              type="button"
              onClick={() => navigate("/app/marketplace")}
              className="h-12 rounded-2xl bg-[var(--primary)] px-4 text-sm font-semibold text-white hover:bg-[var(--primaryHover)]"
            >
              Buscar no Marketplace
            </button>
          </div>

          {error ? (
            <div className="rounded-2xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-200">
              {error}
            </div>
          ) : null}

          {success ? (
            <div className="rounded-2xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-200">
              {success}
            </div>
          ) : null}

          {showManualForm && (
            <div className="rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-4">
              <div className="mb-4 text-sm font-semibold text-[var(--title)]">
                Cadastro manual de peça
              </div>

              <div className="grid gap-3 sm:grid-cols-2">
                <Input
                  placeholder="Nome da peça"
                  value={name}
                  onChange={setName}
                />

                <Input
                  placeholder="SKU (opcional)"
                  value={sku}
                  onChange={setSku}
                />

                <Input
                  placeholder="Preço interno (ex: 200)"
                  value={price}
                  onChange={setPrice}
                />

                <Input
                  placeholder="Estoque (ex: 10)"
                  value={stockQty}
                  onChange={setStockQty}
                />
              </div>

              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <button
                  type="button"
                  onClick={createManualPart}
                  disabled={saving}
                  className="h-12 rounded-2xl bg-[var(--success)] px-4 text-sm font-semibold text-white hover:opacity-90 disabled:opacity-60"
                >
                  {saving ? "Salvando..." : "Salvar peça"}
                </button>

                <div className="rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] px-4 py-3 text-xs text-[var(--muted)]">
                  Use cadastro manual para montar seu catálogo básico da oficina.
                </div>
              </div>
            </div>
          )}

          <div className="space-y-3">
            {loading ? (
              <div className="text-sm text-[var(--muted)]">Carregando peças...</div>
            ) : list.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-6">
                <div className="text-sm font-semibold text-[var(--title)]">
                  Sem itens no catálogo
                </div>
                <div className="mt-2 text-sm text-[var(--muted)]">
                  No Basic você registra manual. No Pro você compra e já adiciona na
                  OS.
                </div>
              </div>
            ) : (
              list.map((part) => {
                return (
                  <div
                    key={part.id}
                    role="button"
                    tabIndex={0}
                    onClick={handleOpenServices}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        handleOpenServices();
                      }
                    }}
                    className="cursor-pointer rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-4 transition hover:border-[var(--primary)] hover:bg-[color:rgba(255,255,255,0.04)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <div className="text-base font-semibold text-[var(--title)]">
                            {part.name}
                          </div>

                          {part.sku ? (
                            <Badge tone="neutral">{part.sku}</Badge>
                          ) : null}
                        </div>

                        <div className="mt-1 text-xs text-[var(--muted)]">
                          Estoque: {Number(part.stock_qty || 0)}
                        </div>
                      </div>

                      <div className="text-right">
                        <div className="text-xs text-[var(--muted)]">
                          Catálogo interno
                        </div>

                        <div className="mt-2 text-xs font-medium text-[var(--primary)]">
                          Abrir OS →
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}