import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";

export default function Parts() {
  return (
    <div className="space-y-4">
      <Card title="Peças" subtitle="Catálogo rápido para adicionar na OS.">
        <div className="grid gap-3">
          <Input placeholder="Buscar peça por nome ou SKU..." />
          <div className="grid gap-3 sm:grid-cols-2">
            <button className="h-12 rounded-2xl bg-[color:rgba(255,255,255,0.06)] px-4 text-sm font-semibold text-[var(--title)] hover:bg-[color:rgba(255,255,255,0.10)]">
              Adicionar peça manual
            </button>
            <button className="h-12 rounded-2xl bg-[var(--primary)] px-4 text-sm font-semibold text-white hover:bg-[var(--primaryHover)]">
              Buscar no Marketplace
            </button>
          </div>

          <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-6">
            <div className="text-sm font-semibold text-[var(--title)]">
              Sem itens no catálogo
            </div>
            <div className="mt-2 text-sm text-[var(--muted)]">
              No Basic você registra manual. No Pro você compra e já adiciona na OS.
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}