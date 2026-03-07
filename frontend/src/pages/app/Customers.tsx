import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../lib/api";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Badge } from "../../components/ui/Badge";

type Customer = {
  id: string;
  name: string;
  phone: string;
  created_at: string;
};

function phoneMask(v: string) {
  const d = (v || "").replace(/\D/g, "").slice(0, 11);
  if (d.length <= 10) {
    return d
      .replace(/^(\d{2})(\d)/, "($1) $2")
      .replace(/(\d{4})(\d)/, "$1-$2");
  }
  return d
    .replace(/^(\d{2})(\d)/, "($1) $2")
    .replace(/(\d{5})(\d)/, "$1-$2");
}

export default function Customers() {
  const navigate = useNavigate();

  const [q, setQ] = useState("");
  const [rows, setRows] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);

  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");

  const [saving, setSaving] = useState(false);

  async function load(term?: string) {
    setLoading(true);
    try {
      const res = await api.get("/customers", {
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

  useEffect(() => {
    load();
  }, []);

  useEffect(() => {
    const t = setTimeout(() => load(q), 250);
    return () => clearTimeout(t);
  }, [q]);

  async function create() {
    const n = name.trim();
    const p = phone.replace(/\D/g, "").trim();
    if (n.length < 2 || p.length < 6) return;

    setSaving(true);
    try {
      await api.post("/customers", { name: n, phone: p });
      setName("");
      setPhone("");
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
        title="Clientes"
        subtitle="Só 2 campos: nome e telefone. Sem enrolação."
        right={<Badge tone="primary">2 campos</Badge>}
      >
        <div className="grid gap-3 sm:grid-cols-3">
          <Input placeholder="Nome do cliente" value={name} onChange={setName} />
          <Input
            placeholder="Telefone (WhatsApp)"
            value={phone}
            onChange={(v) => setPhone(phoneMask(v))}
          />
          <button
            onClick={create}
            disabled={saving}
            className="h-12 rounded-2xl bg-[var(--primary)] px-4 text-sm font-semibold text-white hover:bg-[var(--primaryHover)] disabled:opacity-60"
          >
            {saving ? "Salvando..." : "Cadastrar"}
          </button>
        </div>

        <div className="mt-6">
          <Input
            placeholder="Buscar rápido: nome ou telefone..."
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
                Nenhum cliente cadastrado
              </div>
              <div className="mt-2 text-sm text-[var(--muted)]">
                Cadastre o primeiro — depois é só jogar a placa e abrir OS em segundos.
              </div>
            </div>
          ) : (
            list.map((c) => (
              <div
                key={c.id}
                className="rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-4"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="text-base font-semibold text-[var(--title)]">
                      {c.name}
                    </div>
                    <div className="mt-1 text-xs text-[var(--muted)]">
                      {phoneMask(c.phone)}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs font-medium text-[var(--muted)]">
                      Cliente
                    </div>
                    <button
                      type="button"
                      onClick={handleOpenOs}
                      className="mt-1 text-xs text-[var(--primary)] hover:underline"
                    >
                      Abrir OS → pela placa
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