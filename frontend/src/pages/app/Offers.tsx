import { useEffect, useMemo, useState } from "react";
import api from "../../lib/api";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Badge } from "../../components/ui/Badge";

type Supplier = {
  id: string;
  name: string;
  whatsapp?: string | null;
  city?: string | null;
  cnpj?: string | null;
};

type Part = {
  id: string;
  sku: string;
  name: string;
  brand: string;
  category: string;
  vehicle_compat?: string | null;
};

type Offer = {
  supplier_id: string;
  supplier_name: string;
  price: string;
  availability_status: string;
  lead_time_days?: number | null;
  supplier_sku?: string | null;
};

function toneAvailability(s: string) {
  if (s === "in_stock") return "success";
  if (s === "low") return "warning";
  if (s === "out") return "danger";
  return "neutral";
}

function labelAvailability(s: string) {
  if (s === "in_stock") return "Em estoque";
  if (s === "low") return "Pouco";
  if (s === "out") return "Sem";
  return "Indefinido";
}

export default function Offers() {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [suppliersLoading, setSuppliersLoading] = useState(false);

  const [partQuery, setPartQuery] = useState("");
  const [parts, setParts] = useState<Part[]>([]);
  const [partsLoading, setPartsLoading] = useState(false);

  const [selectedSupplierId, setSelectedSupplierId] = useState("");
  const [selectedPartId, setSelectedPartId] = useState("");

  const [supplierSku, setSupplierSku] = useState("");
  const [price, setPrice] = useState("");
  const [availabilityStatus, setAvailabilityStatus] = useState("in_stock");
  const [leadTimeDays, setLeadTimeDays] = useState("2");

  const [saving, setSaving] = useState(false);

  const [existingOffers, setExistingOffers] = useState<Offer[]>([]);
  const [offersLoading, setOffersLoading] = useState(false);

  async function loadSuppliers() {
    setSuppliersLoading(true);
    try {
      const res = await api.get("/marketplace/suppliers");
      setSuppliers(res.data || []);
    } catch (e) {
      console.error(e);
      setSuppliers([]);
    } finally {
      setSuppliersLoading(false);
    }
  }

  useEffect(() => {
    loadSuppliers();
  }, []);

  async function searchParts(queryText?: string) {
    const query = (queryText ?? partQuery).trim();

    if (query.length < 2) {
      setParts([]);
      return;
    }

    setPartsLoading(true);
    try {
      const res = await api.get("/marketplace/parts", {
        params: {
          query,
          limit: 20,
        },
      });
      setParts(res.data || []);
    } catch (e) {
      console.error(e);
      setParts([]);
    } finally {
      setPartsLoading(false);
    }
  }

  useEffect(() => {
    const t = setTimeout(() => {
      searchParts();
    }, 300);

    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [partQuery]);

  async function loadOffersForSelectedPart(partId: string) {
    if (!partId) {
      setExistingOffers([]);
      return;
    }

    setOffersLoading(true);
    try {
      const res = await api.get(`/marketplace/parts/${partId}/offers`);
      setExistingOffers(res.data || []);
    } catch (e) {
      console.error(e);
      setExistingOffers([]);
    } finally {
      setOffersLoading(false);
    }
  }

  useEffect(() => {
    if (selectedPartId) {
      loadOffersForSelectedPart(selectedPartId);
    } else {
      setExistingOffers([]);
    }
  }, [selectedPartId]);

  const selectedSupplier = useMemo(
    () => suppliers.find((s) => s.id === selectedSupplierId) || null,
    [suppliers, selectedSupplierId]
  );

  const selectedPart = useMemo(
    () => parts.find((p) => p.id === selectedPartId) || null,
    [parts, selectedPartId]
  );

  async function createOffer() {
    if (!selectedSupplierId) {
      alert("Selecione o fornecedor.");
      return;
    }

    if (!selectedPartId) {
      alert("Selecione a peça.");
      return;
    }

    if (!price.trim()) {
      alert("Informe o preço.");
      return;
    }

    setSaving(true);
    try {
      await api.post("/marketplace/supplier-parts", {
        supplier_id: selectedSupplierId,
        part_id: selectedPartId,
        supplier_sku: supplierSku.trim() || null,
        price: price.trim(),
        availability_status: availabilityStatus,
        lead_time_days: leadTimeDays.trim() ? Number(leadTimeDays) : null,
      });

      setSupplierSku("");
      setPrice("");
      setAvailabilityStatus("in_stock");
      setLeadTimeDays("2");

      await loadOffersForSelectedPart(selectedPartId);
      alert("Oferta cadastrada com sucesso.");
    } catch (e: any) {
      console.error(e);
      alert(e?.response?.data?.message || "Não foi possível cadastrar a oferta.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-4">
      <Card
        title="Ofertas de Peças"
        subtitle="Vincule fornecedores reais às peças do catálogo com preço, disponibilidade e prazo."
      >
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="space-y-3">
            <div className="text-sm font-semibold text-[var(--title)]">
              1. Escolha o fornecedor
            </div>

            {suppliersLoading ? (
              <div className="text-sm text-[var(--muted)]">Carregando fornecedores...</div>
            ) : suppliers.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-4 text-sm text-[var(--muted)]">
                Nenhum fornecedor cadastrado ainda. Cadastre em{" "}
                <b className="text-[var(--title)]">Fornecedores</b>.
              </div>
            ) : (
              <div className="space-y-2">
                {suppliers.map((s) => (
                  <button
                    key={s.id}
                    type="button"
                    onClick={() => setSelectedSupplierId(s.id)}
                    className={`w-full rounded-2xl border p-4 text-left transition ${
                      selectedSupplierId === s.id
                        ? "border-[var(--primary)] bg-[color:rgba(47,107,255,0.18)]"
                        : "border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] hover:bg-[color:rgba(255,255,255,0.05)]"
                    }`}
                  >
                    <div className="text-sm font-semibold text-[var(--title)]">
                      {s.name}
                    </div>
                    <div className="mt-1 text-xs text-[var(--muted)]">
                      {s.city || "Cidade não informada"} • {s.whatsapp || "WhatsApp não informado"}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="space-y-3">
            <div className="text-sm font-semibold text-[var(--title)]">
              2. Busque e selecione a peça
            </div>

            <Input
              placeholder="Buscar peça por nome, marca ou SKU"
              value={partQuery}
              onChange={setPartQuery}
            />

            {partsLoading ? (
              <div className="text-sm text-[var(--muted)]">Buscando peças...</div>
            ) : partQuery.trim().length < 2 ? (
              <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-4 text-sm text-[var(--muted)]">
                Digite pelo menos 2 caracteres para buscar.
              </div>
            ) : parts.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-4 text-sm text-[var(--muted)]">
                Nenhuma peça encontrada.
              </div>
            ) : (
              <div className="space-y-2">
                {parts.map((p) => (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => setSelectedPartId(p.id)}
                    className={`w-full rounded-2xl border p-4 text-left transition ${
                      selectedPartId === p.id
                        ? "border-[var(--primary)] bg-[color:rgba(47,107,255,0.18)]"
                        : "border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] hover:bg-[color:rgba(255,255,255,0.05)]"
                    }`}
                  >
                    <div className="text-sm font-semibold text-[var(--title)]">
                      {p.name}
                    </div>
                    <div className="mt-1 text-xs text-[var(--muted)]">
                      {p.brand || "—"} • {p.category || "—"} • SKU {p.sku}
                    </div>
                    {p.vehicle_compat ? (
                      <div className="mt-1 text-xs text-[var(--muted)] line-clamp-2">
                        Compat.: {p.vehicle_compat}
                      </div>
                    ) : null}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="mt-5 rounded-3xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-4">
          <div className="text-sm font-semibold text-[var(--title)]">
            3. Cadastre a oferta
          </div>

          <div className="mt-3 grid gap-3 md:grid-cols-2">
            <Input
              placeholder="Fornecedor selecionado"
              value={selectedSupplier ? selectedSupplier.name : ""}
              onChange={() => {}}
              disabled
            />

            <Input
              placeholder="Peça selecionada"
              value={selectedPart ? selectedPart.name : ""}
              onChange={() => {}}
              disabled
            />

            <Input
              placeholder="SKU do fornecedor"
              value={supplierSku}
              onChange={setSupplierSku}
            />

            <Input
              placeholder="Preço (ex: 89.90)"
              value={price}
              onChange={setPrice}
            />

            <div className="space-y-2">
              <div className="text-xs font-semibold text-[var(--muted)]">
                Disponibilidade
              </div>

              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => setAvailabilityStatus("in_stock")}
                  className={`h-11 rounded-2xl border text-xs font-semibold ${
                    availabilityStatus === "in_stock"
                      ? "border-[var(--primary)] bg-[color:rgba(47,107,255,0.18)] text-[var(--title)]"
                      : "border-[var(--border)] bg-[color:rgba(255,255,255,0.03)] text-[var(--muted)]"
                  }`}
                >
                  Em estoque
                </button>

                <button
                  type="button"
                  onClick={() => setAvailabilityStatus("low")}
                  className={`h-11 rounded-2xl border text-xs font-semibold ${
                    availabilityStatus === "low"
                      ? "border-[var(--primary)] bg-[color:rgba(47,107,255,0.18)] text-[var(--title)]"
                      : "border-[var(--border)] bg-[color:rgba(255,255,255,0.03)] text-[var(--muted)]"
                  }`}
                >
                  Pouco
                </button>

                <button
                  type="button"
                  onClick={() => setAvailabilityStatus("out")}
                  className={`h-11 rounded-2xl border text-xs font-semibold ${
                    availabilityStatus === "out"
                      ? "border-[var(--primary)] bg-[color:rgba(47,107,255,0.18)] text-[var(--title)]"
                      : "border-[var(--border)] bg-[color:rgba(255,255,255,0.03)] text-[var(--muted)]"
                  }`}
                >
                  Sem
                </button>
              </div>
            </div>

            <Input
              placeholder="Prazo em dias (ex: 2)"
              value={leadTimeDays}
              onChange={setLeadTimeDays}
            />
          </div>

          <div className="mt-4">
            <button
              type="button"
              onClick={createOffer}
              disabled={saving}
              className="h-11 rounded-2xl bg-[var(--primary)] px-5 text-sm font-semibold text-white hover:bg-[var(--primaryHover)] disabled:opacity-60"
            >
              {saving ? "Salvando oferta..." : "Cadastrar oferta"}
            </button>
          </div>
        </div>
      </Card>

      <Card
        title="Ofertas existentes da peça selecionada"
        subtitle="Use esta área para conferir o que já está vinculado ao catálogo."
      >
        {!selectedPartId ? (
          <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-6">
            <div className="text-sm font-semibold text-[var(--title)]">
              Nenhuma peça selecionada
            </div>
            <div className="mt-2 text-sm text-[var(--muted)]">
              Selecione uma peça acima para ver as ofertas já cadastradas.
            </div>
          </div>
        ) : offersLoading ? (
          <div className="text-sm text-[var(--muted)]">Carregando ofertas...</div>
        ) : existingOffers.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-6">
            <div className="text-sm font-semibold text-[var(--title)]">
              Sem ofertas para esta peça
            </div>
            <div className="mt-2 text-sm text-[var(--muted)]">
              Cadastre a primeira oferta real para que a oficina possa comprar.
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {existingOffers.map((o, idx) => (
              <div
                key={`${o.supplier_id}-${idx}`}
                className="rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-4"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="text-sm font-semibold text-[var(--title)]">
                      {o.supplier_name}
                    </div>

                    <div className="mt-1 text-xs text-[var(--muted)]">
                      R$ {o.price}
                      {o.lead_time_days != null ? ` • prazo ${o.lead_time_days}d` : ""}
                    </div>

                    <div className="mt-1 text-xs text-[var(--muted)]">
                      SKU fornecedor: {o.supplier_sku || "não informado"}
                    </div>
                  </div>

                  <Badge tone={toneAvailability(o.availability_status) as any}>
                    {labelAvailability(o.availability_status)}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}