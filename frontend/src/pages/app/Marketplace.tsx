import { useEffect, useMemo, useState } from "react";
import api from "../../lib/api";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Badge } from "../../components/ui/Badge";

type Part = {
  id: string;
  sku: string;
  name: string;
  brand: string;
  category: string;
  vehicle_compat: string;
  suggested_price?: string | null;
};

type Offer = {
  supplier_id: string;
  supplier_name: string;
  price: string;
  availability_status: string;
  lead_time_days?: number | null;
  supplier_sku?: string | null;
};

type CartItem = {
  id: string;
  part_id: string;
  sku: string;
  name: string;
  brand: string;
  category: string;
  qty: number;
  chosen_supplier_id?: string | null;
  chosen_supplier_name?: string | null;
  unit_price_snapshot: string;
};

type Cart = {
  id: string;
  status: string;
  items: CartItem[];
};

type Order = {
  id: string;
  order_number: string;
  status: string;
  supplier_id: string;
  supplier_name: string;
  total: string;
  delivery_mode: string;
  created_at: string;
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

function toneOrder(s: string) {
  if (s === "delivered") return "success";
  if (s === "shipped") return "primary";
  if (s === "confirmed") return "primary";
  if (s === "placed") return "warning";
  if (s === "canceled") return "danger";
  return "neutral";
}

function labelOrder(s: string) {
  if (s === "delivered") return "Entregue";
  if (s === "shipped") return "Enviado";
  if (s === "confirmed") return "Confirmado";
  if (s === "placed") return "Pedido feito";
  if (s === "canceled") return "Cancelado";
  return "Rascunho";
}

export default function Marketplace() {
  const [q, setQ] = useState("");
  const [parts, setParts] = useState<Part[]>([]);
  const [loading, setLoading] = useState(false);

  const [vehicleType, setVehicleType] = useState<"all" | "car" | "moto">("all");

  const [selected, setSelected] = useState<Part | null>(null);
  const [offers, setOffers] = useState<Offer[]>([]);
  const [offersLoading, setOffersLoading] = useState(false);

  const [cart, setCart] = useState<Cart | null>(null);
  const [cartLoading, setCartLoading] = useState(false);

  const [checkoutOpen, setCheckoutOpen] = useState(false);
  const [checkoutSupplierId, setCheckoutSupplierId] = useState("");
  const [deliveryMode, setDeliveryMode] = useState<"delivery" | "pickup">("delivery");
  const [deliveryAddress, setDeliveryAddress] = useState("");
  const [creatingOrder, setCreatingOrder] = useState(false);

  const [orders, setOrders] = useState<Order[]>([]);
  const [ordersLoading, setOrdersLoading] = useState(false);
  const [sendingWhatsappId, setSendingWhatsappId] = useState<string | null>(null);

  async function loadCart() {
    setCartLoading(true);
    try {
      const res = await api.get("/marketplace/cart");
      setCart(res.data);
    } catch (e) {
      console.error(e);
      setCart(null);
    } finally {
      setCartLoading(false);
    }
  }

  async function loadOrders() {
    setOrdersLoading(true);
    try {
      const res = await api.get("/marketplace/orders", { params: { limit: 20 } });
      setOrders(res.data || []);
    } catch (e) {
      console.error(e);
      setOrders([]);
    } finally {
      setOrdersLoading(false);
    }
  }

  useEffect(() => {
    loadCart();
    loadOrders();
  }, []);

  async function search() {
    setLoading(true);
    try {
      const params: Record<string, string | number> = {
        limit: 30,
      };

      if (q.trim()) {
        params.query = q.trim();
      }

      if (vehicleType !== "all") {
        params.vehicle_type = vehicleType;
      }

      const res = await api.get("/marketplace/parts", { params });
      setParts(res.data || []);
    } catch (e: any) {
      console.error(e);
      setParts([]);
    } finally {
      setLoading(false);
    }
  }

  const canSearch = useMemo(() => (q || "").trim().length >= 2, [q]);

  useEffect(() => {
    const t = setTimeout(() => {
      if (canSearch) search();
      if (!canSearch) setParts([]);
    }, 250);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q, vehicleType]);

  async function openOffers(p: Part) {
    setSelected(p);
    setOffers([]);
    setOffersLoading(true);
    try {
      const res = await api.get(`/marketplace/parts/${p.id}/offers`);
      setOffers(res.data || []);
    } catch (e: any) {
      console.error(e);
      setOffers([]);
    } finally {
      setOffersLoading(false);
    }
  }

  async function addToCart(p: Part, offer?: Offer) {
    try {
      await api.post("/marketplace/cart/items", {
        part_id: p.id,
        qty: 1,
        chosen_supplier_id: offer?.supplier_id || null,
        unit_price_snapshot: offer?.price || p.suggested_price || "0.00",
      });
      await loadCart();
    } catch (e: any) {
      console.error(e);
      alert(e?.response?.data?.message || "Não foi possível adicionar ao carrinho.");
    }
  }

  const cartSupplierHint = useMemo(() => {
    const items = cart?.items || [];
    const ids = new Set(items.map((i) => i.chosen_supplier_id || "").filter(Boolean));
    if (ids.size === 1) {
      const only =
        items.find((i) => (i.chosen_supplier_id || "") !== "")?.chosen_supplier_id || "";
      return only;
    }
    return "";
  }, [cart]);

  function openCheckout() {
    setCheckoutSupplierId(cartSupplierHint || "");
    setCheckoutOpen(true);
  }

  async function finalizeOrder() {
    const supplier = (checkoutSupplierId || "").trim();
    if (!supplier) {
      alert("Escolha o fornecedor para finalizar.");
      return;
    }
    if (deliveryMode === "delivery" && !deliveryAddress.trim()) {
      alert("Informe o endereço de entrega (ou selecione retirada).");
      return;
    }

    setCreatingOrder(true);
    try {
      await api.post("/marketplace/orders/from-cart", {
        supplier_id: supplier,
        delivery_mode: deliveryMode,
        delivery_address: deliveryMode === "delivery" ? deliveryAddress.trim() : null,
        shipping: "0.00",
        discount: "0.00",
      });
      setCheckoutOpen(false);
      setDeliveryAddress("");
      await loadCart();
      await loadOrders();
      alert("Pedido criado. Atualize status conforme o fornecedor confirmar e enviar.");
    } catch (e: any) {
      console.error(e);
      alert(e?.response?.data?.message || "Não foi possível finalizar o pedido.");
    } finally {
      setCreatingOrder(false);
    }
  }

  async function updateOrderStatus(orderId: string, status: string) {
    try {
      await api.post(`/marketplace/orders/${orderId}/status`, { status });
      await loadOrders();
    } catch (e: any) {
      console.error(e);
      alert(e?.response?.data?.message || "Não foi possível atualizar.");
    }
  }

  async function sendOrderToWhatsApp(orderId: string) {
    setSendingWhatsappId(orderId);
    try {
      const res = await api.get(`/marketplace/orders/${orderId}/whatsapp-link`);
      const url = res?.data?.whatsapp_url;

      if (!url) {
        alert("Não foi possível gerar o link do WhatsApp.");
        return;
      }

      window.open(url, "_blank", "noopener,noreferrer");
    } catch (e: any) {
      console.error(e);
      alert(
        e?.response?.data?.message ||
          "Não foi possível abrir o WhatsApp do fornecedor."
      );
    } finally {
      setSendingWhatsappId(null);
    }
  }

  return (
    <div className="space-y-4">
      <Card
        title="Marketplace de Peças"
        subtitle="Buscar, comparar e comprar sem sair do BoxRota."
        right={<Badge tone="primary">PRO</Badge>}
      >
        <div className="grid gap-3 sm:grid-cols-3">
          <Input
            placeholder="Buscar peça (nome, SKU, marca)..."
            value={q}
            onChange={setQ}
          />
          <div className="sm:col-span-2 grid grid-cols-2 gap-2">
            <button
              onClick={search}
              disabled={!canSearch || loading}
              className="h-12 rounded-2xl bg-[var(--primary)] px-4 text-sm font-semibold text-white hover:bg-[var(--primaryHover)] disabled:opacity-60"
            >
              {loading ? "Buscando..." : "Buscar"}
            </button>
            <button
              onClick={loadCart}
              className="h-12 rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.03)] px-4 text-sm font-semibold text-[var(--title)] hover:bg-[color:rgba(255,255,255,0.06)]"
            >
              {cartLoading ? "Atualizando..." : `Carrinho (${cart?.items?.length || 0})`}
            </button>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-3 gap-2 sm:max-w-md">
          <button
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

        <div className="mt-5 space-y-3">
          {!canSearch ? (
            <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-6">
              <div className="text-sm font-semibold text-[var(--title)]">
                Digite 2+ caracteres para buscar
              </div>
              <div className="mt-2 text-sm text-[var(--muted)]">
                Ex: filtro de óleo, pastilha, correia, rolamento…
              </div>
            </div>
          ) : parts.length === 0 && !loading ? (
            <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-6">
              <div className="text-sm font-semibold text-[var(--title)]">
                Nada encontrado
              </div>
              <div className="mt-2 text-sm text-[var(--muted)]">
                Tente marca + nome (ex: “Bosch vela”) ou parte do SKU.
              </div>
            </div>
          ) : (
            parts.map((p) => (
              <div
                key={p.id}
                className="rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-4"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="text-base font-semibold text-[var(--title)] truncate">
                      {p.name}
                    </div>
                    <div className="mt-1 text-xs text-[var(--muted)]">
                      {p.brand || "—"} • {p.category || "—"} • SKU {p.sku}
                    </div>
                    {p.vehicle_compat ? (
                      <div className="mt-2 text-xs text-[var(--muted)] line-clamp-2">
                        Compat.: {p.vehicle_compat}
                      </div>
                    ) : null}
                  </div>

                  <div className="flex flex-col gap-2">
                    <button
                      onClick={() => openOffers(p)}
                      className="h-10 rounded-2xl bg-[color:rgba(255,255,255,0.06)] px-4 text-xs font-semibold text-[var(--title)] hover:bg-[color:rgba(255,255,255,0.10)]"
                    >
                      Ver ofertas
                    </button>
                    <button
                      onClick={() => addToCart(p)}
                      className="h-10 rounded-2xl bg-[var(--primary)] px-4 text-xs font-semibold text-white hover:bg-[var(--primaryHover)]"
                    >
                      Add carrinho
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </Card>

      <Card
        title="Carrinho"
        subtitle="No máximo 3 passos: carrinho → entrega/retirada → finalizar."
        right={
          <button
            onClick={openCheckout}
            disabled={(cart?.items?.length || 0) === 0}
            className="h-10 rounded-2xl bg-[var(--success)] px-4 text-xs font-semibold text-white hover:bg-[var(--successHover)] disabled:opacity-60"
          >
            Finalizar pedido
          </button>
        }
      >
        {(cart?.items?.length || 0) === 0 ? (
          <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-6">
            <div className="text-sm font-semibold text-[var(--title)]">
              Carrinho vazio
            </div>
            <div className="mt-2 text-sm text-[var(--muted)]">
              Adicione peças para gerar pedido e manter histórico de compra dentro do BoxRota.
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {(cart?.items || []).map((it) => (
              <div
                key={it.id}
                className="rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-4"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="text-sm font-semibold text-[var(--title)] truncate">
                      {it.name}
                    </div>
                    <div className="mt-1 text-xs text-[var(--muted)]">
                      {it.brand || "—"} • {it.category || "—"} • {it.qty}x • R$ {it.unit_price_snapshot}
                    </div>
                    <div className="mt-1 text-xs text-[var(--muted)]">
                      Fornecedor:{" "}
                      <span className="text-[var(--title)]">
                        {it.chosen_supplier_name || "não definido"}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}

            <div className="rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-4">
              <div className="text-xs text-[var(--muted)]">
                Importante: para finalizar, o carrinho precisa ter{" "}
                <b className="text-[var(--title)]">um único fornecedor</b>.
              </div>
            </div>
          </div>
        )}
      </Card>

      <Card title="Pedidos" subtitle="Controle simples: feito → confirmado → enviado → entregue.">
        {ordersLoading ? (
          <div className="text-sm text-[var(--muted)]">Carregando...</div>
        ) : orders.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-6">
            <div className="text-sm font-semibold text-[var(--title)]">Nenhum pedido ainda</div>
            <div className="mt-2 text-sm text-[var(--muted)]">
              O histórico de compras vira vantagem: você compara preço e repete compra rápido.
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {orders.map((o) => (
              <div
                key={o.id}
                className="rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-4"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <div className="text-sm font-semibold text-[var(--title)]">
                        {o.order_number}
                      </div>
                      <Badge tone={toneOrder(o.status) as any}>{labelOrder(o.status)}</Badge>
                    </div>
                    <div className="mt-1 text-xs text-[var(--muted)]">
                      {o.supplier_name} • Total R$ {o.total} •{" "}
                      {o.delivery_mode === "pickup" ? "Retirada" : "Entrega"}
                    </div>
                  </div>

                  <div className="flex flex-col gap-2">
                    <button
                      onClick={() => sendOrderToWhatsApp(o.id)}
                      disabled={sendingWhatsappId === o.id}
                      className="h-10 rounded-2xl bg-[var(--primary)] px-4 text-xs font-semibold text-white hover:bg-[var(--primaryHover)] disabled:opacity-60"
                    >
                      {sendingWhatsappId === o.id ? "Abrindo..." : "WhatsApp"}
                    </button>
                    <button
                      onClick={() => updateOrderStatus(o.id, "confirmed")}
                      className="h-10 rounded-2xl bg-[color:rgba(255,255,255,0.06)] px-4 text-xs font-semibold text-[var(--title)] hover:bg-[color:rgba(255,255,255,0.10)]"
                    >
                      Confirmar
                    </button>
                    <button
                      onClick={() => updateOrderStatus(o.id, "shipped")}
                      className="h-10 rounded-2xl bg-[color:rgba(255,255,255,0.06)] px-4 text-xs font-semibold text-[var(--title)] hover:bg-[color:rgba(255,255,255,0.10)]"
                    >
                      Enviado
                    </button>
                    <button
                      onClick={() => updateOrderStatus(o.id, "delivered")}
                      className="h-10 rounded-2xl bg-[var(--success)] px-4 text-xs font-semibold text-white hover:bg-[var(--successHover)]"
                    >
                      Entregue
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {selected ? (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/55 p-3">
          <div className="w-full max-w-xl rounded-3xl border border-[var(--border)] bg-[var(--surface)] shadow-2xl">
            <div className="flex items-center justify-between gap-3 border-b border-[var(--border)] p-4">
              <div className="min-w-0">
                <div className="text-sm font-semibold text-[var(--title)] truncate">
                  Ofertas • {selected.name}
                </div>
                <div className="mt-1 text-xs text-[var(--muted)]">
                  Escolha o melhor preço e adicione em 1 toque.
                </div>
              </div>
              <button
                onClick={() => setSelected(null)}
                className="h-10 w-10 rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.03)] text-[var(--title)] hover:bg-[color:rgba(255,255,255,0.06)]"
              >
                ✕
              </button>
            </div>

            <div className="p-4 space-y-3">
              {offersLoading ? (
                <div className="text-sm text-[var(--muted)]">Carregando ofertas…</div>
              ) : offers.length === 0 ? (
                <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-6">
                  <div className="text-sm font-semibold text-[var(--title)]">
                    Sem ofertas para esta peça
                  </div>
                  <div className="mt-2 text-sm text-[var(--muted)]">
                    Vincule fornecedores na oficina para comparar preços aqui.
                  </div>
                </div>
              ) : (
                offers.map((o) => (
                  <div
                    key={o.supplier_id}
                    className="rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-4"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <div className="text-sm font-semibold text-[var(--title)] truncate">
                          {o.supplier_name}
                        </div>
                        <div className="mt-1 text-xs text-[var(--muted)]">
                          R$ {o.price}
                          {o.lead_time_days != null ? ` • prazo ${o.lead_time_days}d` : ""}
                        </div>
                        <div className="mt-2">
                          <Badge tone={toneAvailability(o.availability_status) as any}>
                            {labelAvailability(o.availability_status)}
                          </Badge>
                        </div>
                      </div>

                      <div className="flex flex-col gap-2">
                        <button
                          onClick={() => addToCart(selected, o)}
                          className="h-10 rounded-2xl bg-[var(--primary)] px-4 text-xs font-semibold text-white hover:bg-[var(--primaryHover)]"
                        >
                          Add carrinho
                        </button>
                        <button
                          onClick={() => {
                            setCheckoutSupplierId(o.supplier_id);
                            setSelected(null);
                            setCheckoutOpen(true);
                          }}
                          className="h-10 rounded-2xl bg-[var(--success)] px-4 text-xs font-semibold text-white hover:bg-[var(--successHover)]"
                        >
                          Comprar agora
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      ) : null}

      {checkoutOpen ? (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/55 p-3">
          <div className="w-full max-w-xl rounded-3xl border border-[var(--border)] bg-[var(--surface)] shadow-2xl">
            <div className="flex items-center justify-between gap-3 border-b border-[var(--border)] p-4">
              <div>
                <div className="text-sm font-semibold text-[var(--title)]">Finalizar pedido</div>
                <div className="mt-1 text-xs text-[var(--muted)]">
                  3 passos, sem enrolação.
                </div>
              </div>
              <button
                onClick={() => setCheckoutOpen(false)}
                className="h-10 w-10 rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.03)] text-[var(--title)] hover:bg-[color:rgba(255,255,255,0.06)]"
              >
                ✕
              </button>
            </div>

            <div className="p-4 space-y-3">
              <Input
                placeholder="Supplier ID (auto quando possível)"
                value={checkoutSupplierId}
                onChange={setCheckoutSupplierId}
              />

              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => setDeliveryMode("delivery")}
                  className={`h-12 rounded-2xl border border-[var(--border)] px-3 text-sm font-semibold ${
                    deliveryMode === "delivery"
                      ? "bg-[color:rgba(47,107,255,0.18)] text-[var(--title)]"
                      : "bg-[color:rgba(255,255,255,0.03)] text-[var(--muted)]"
                  }`}
                >
                  Entrega
                </button>
                <button
                  onClick={() => setDeliveryMode("pickup")}
                  className={`h-12 rounded-2xl border border-[var(--border)] px-3 text-sm font-semibold ${
                    deliveryMode === "pickup"
                      ? "bg-[color:rgba(47,107,255,0.18)] text-[var(--title)]"
                      : "bg-[color:rgba(255,255,255,0.03)] text-[var(--muted)]"
                  }`}
                >
                  Retirada
                </button>
              </div>

              {deliveryMode === "delivery" ? (
                <Input
                  placeholder="Endereço de entrega (rápido)"
                  value={deliveryAddress}
                  onChange={setDeliveryAddress}
                />
              ) : null}

              <button
                onClick={finalizeOrder}
                disabled={creatingOrder}
                className="h-12 w-full rounded-2xl bg-[var(--success)] px-4 text-sm font-semibold text-white hover:bg-[var(--successHover)] disabled:opacity-60"
              >
                {creatingOrder ? "Finalizando..." : "Finalizar pedido"}
              </button>

              <div className="text-xs text-[var(--muted)]">
                Dica: se der erro de “fornecedor misto”, ajuste os itens no carrinho para o mesmo fornecedor.
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}