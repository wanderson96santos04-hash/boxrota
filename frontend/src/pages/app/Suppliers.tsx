import { useEffect, useState } from "react";
import api from "../../lib/api";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";

type Supplier = {
  id: string;
  name: string;
  whatsapp?: string | null;
  city?: string | null;
  cnpj?: string | null;
};

export default function Suppliers() {
  const [items, setItems] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  const [name, setName] = useState("");
  const [whatsapp, setWhatsapp] = useState("");
  const [city, setCity] = useState("");
  const [cnpj, setCnpj] = useState("");

  async function loadSuppliers() {
    setLoading(true);
    try {
      const res = await api.get("/marketplace/suppliers");
      setItems(res.data || []);
    } catch (e) {
      console.error(e);
      setItems([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadSuppliers();
  }, []);

  async function createSupplier() {
    if (!name.trim()) {
      alert("Informe o nome do fornecedor.");
      return;
    }

    setSaving(true);
    try {
      await api.post("/marketplace/suppliers", {
        name: name.trim(),
        whatsapp: whatsapp.trim() || null,
        city: city.trim() || null,
        cnpj: cnpj.trim() || null,
      });

      setName("");
      setWhatsapp("");
      setCity("");
      setCnpj("");

      await loadSuppliers();
      alert("Fornecedor cadastrado com sucesso.");
    } catch (e: any) {
      console.error(e);
      alert(e?.response?.data?.message || "Não foi possível cadastrar o fornecedor.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-4">
      <Card
        title="Fornecedores"
        subtitle="Cadastre fornecedores reais para alimentar o Marketplace com ofertas verdadeiras."
      >
        <div className="grid gap-3 md:grid-cols-2">
          <Input
            placeholder="Nome do fornecedor"
            value={name}
            onChange={setName}
          />

          <Input
            placeholder="WhatsApp (ex: 5533999999999)"
            value={whatsapp}
            onChange={setWhatsapp}
          />

          <Input
            placeholder="Cidade"
            value={city}
            onChange={setCity}
          />

          <Input
            placeholder="CNPJ"
            value={cnpj}
            onChange={setCnpj}
          />
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          <button
            onClick={createSupplier}
            disabled={saving}
            className="h-11 rounded-2xl bg-[var(--primary)] px-5 text-sm font-semibold text-white hover:bg-[var(--primaryHover)] disabled:opacity-60"
          >
            {saving ? "Salvando..." : "Cadastrar fornecedor"}
          </button>

          <button
            onClick={loadSuppliers}
            disabled={loading}
            className="h-11 rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.03)] px-5 text-sm font-semibold text-[var(--title)] hover:bg-[color:rgba(255,255,255,0.06)] disabled:opacity-60"
          >
            {loading ? "Atualizando..." : "Atualizar lista"}
          </button>
        </div>
      </Card>

      <Card
        title="Lista de fornecedores"
        subtitle="Esses fornecedores poderão ser usados depois para cadastrar ofertas de peças."
      >
        {loading ? (
          <div className="text-sm text-[var(--muted)]">Carregando fornecedores...</div>
        ) : items.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-6">
            <div className="text-sm font-semibold text-[var(--title)]">
              Nenhum fornecedor cadastrado
            </div>
            <div className="mt-2 text-sm text-[var(--muted)]">
              Cadastre fornecedores reais com nome, WhatsApp, cidade e CNPJ.
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {items.map((s) => (
              <div
                key={s.id}
                className="rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-4"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="text-sm font-semibold text-[var(--title)] truncate">
                      {s.name}
                    </div>

                    <div className="mt-2 grid gap-1 text-xs text-[var(--muted)]">
                      <div>
                        <span className="text-[var(--title)]">WhatsApp:</span>{" "}
                        {s.whatsapp || "não informado"}
                      </div>
                      <div>
                        <span className="text-[var(--title)]">Cidade:</span>{" "}
                        {s.city || "não informada"}
                      </div>
                      <div>
                        <span className="text-[var(--title)]">CNPJ:</span>{" "}
                        {s.cnpj || "não informado"}
                      </div>
                      <div className="break-all">
                        <span className="text-[var(--title)]">ID:</span> {s.id}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}