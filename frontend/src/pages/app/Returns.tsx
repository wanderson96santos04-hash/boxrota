import { useEffect, useMemo, useState } from "react";
import api from "../../lib/api";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Badge } from "../../components/ui/Badge";

type ReturnRow = {
  id: string;
  due_date: string;
  status: string;
  customer_name?: string | null;
  customer_phone?: string | null;
  vehicle_plate?: string | null;
  service_id?: string | null;
};

function formatDate(iso: string) {
  try {
    const d = new Date(iso);
    return d.toLocaleDateString("pt-BR");
  } catch {
    return iso;
  }
}

function tone(status: string) {
  if (status === "done") return "success";
  if (status === "sent") return "primary";
  return "warning";
}

function label(status: string) {
  if (status === "done") return "Concluído";
  if (status === "sent") return "Enviado";
  return "Pendente";
}

function waLink(phoneDigits: string, message: string) {
  const phone = (phoneDigits || "").replace(/\D/g, "");
  const text = encodeURIComponent(message || "");
  return `https://wa.me/55${phone}?text=${text}`;
}

function buildReturnMessage(name: string, plate: string) {
  return `Olá, ${name}! 👋

Aqui é da equipe da BoxRota.

Estamos passando para saber se ficou tudo certo com o atendimento do veículo ${plate}.

Seu feedback é muito importante para nós. Se precisar de qualquer suporte ou quiser agendar um novo retorno, estamos à disposição.

Obrigado pela confiança! 🚗🔧`;
}

export default function Returns() {
  const [rows, setRows] = useState<ReturnRow[]>([]);
  const [loading, setLoading] = useState(true);

  const [q, setQ] = useState("");
  const [status, setStatus] = useState<"" | "pending" | "sent" | "done">("");

  const [ruleDays, setRuleDays] = useState("180");
  const [ruleActive, setRuleActive] = useState(true);
  const [savingRule, setSavingRule] = useState(false);

  async function loadRule() {
    try {
      const res = await api.get("/returns/rule");
      setRuleDays(String(res.data.days_after ?? 180));
      setRuleActive(Boolean(res.data.active ?? true));
    } catch (e) {
      console.error(e);
    }
  }

  async function saveRule() {
    const parsedDays = parseInt(ruleDays ?? "180", 10);
    const days = Number.isNaN(parsedDays)
      ? 180
      : Math.max(0, Math.min(3650, parsedDays));

    setSavingRule(true);
    try {
      await api.post("/returns/rule", {
        name: "Retorno",
        days_after: days,
        active: Boolean(ruleActive),
      });
      await loadRule();
      await loadReturns();
    } catch (e) {
      console.error(e);
    } finally {
      setSavingRule(false);
    }
  }

  async function loadReturns() {
    setLoading(true);
    try {
      const res = await api.get("/returns", {
        params: { status: status || undefined, limit: 120 },
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
    loadRule();
    loadReturns();
  }, []);

  useEffect(() => {
    loadReturns();
  }, [status]);

  const filtered = useMemo(() => {
    const term = (q || "").trim().toLowerCase();
    if (!term) return rows;
    return (rows || []).filter((r) => {
      const plate = (r.vehicle_plate || "").toLowerCase();
      const name = (r.customer_name || "").toLowerCase();
      const phone = (r.customer_phone || "").toLowerCase();
      return plate.includes(term) || name.includes(term) || phone.includes(term);
    });
  }, [q, rows]);

  async function setRowStatus(id: string, next: "sent" | "done" | "pending") {
    try {
      await api.post(`/returns/${id}/status`, { status: next });
      await loadReturns();
    } catch (e) {
      console.error(e);
    }
  }

  return (
    <div className="space-y-4">
      <Card
        title="Retornos"
        subtitle="O BoxRota te lembra. Você só clica e manda."
        right={<Badge tone="primary">retenção</Badge>}
      >
        <div className="grid gap-3 sm:grid-cols-3">
          <Input
            placeholder="Buscar: placa, cliente, telefone..."
            value={q}
            onChange={setQ}
          />
          <div className="grid grid-cols-3 gap-2 sm:col-span-2">
            <button
              onClick={() => setStatus("")}
              className={`h-12 rounded-2xl border border-[var(--border)] px-3 text-sm font-semibold ${
                status === ""
                  ? "bg-[color:rgba(47,107,255,0.18)] text-[var(--title)]"
                  : "bg-[color:rgba(255,255,255,0.03)] text-[var(--muted)]"
              }`}
            >
              Todos
            </button>
            <button
              onClick={() => setStatus("pending")}
              className={`h-12 rounded-2xl border border-[var(--border)] px-3 text-sm font-semibold ${
                status === "pending"
                  ? "bg-[color:rgba(255,176,32,0.18)] text-[var(--title)]"
                  : "bg-[color:rgba(255,255,255,0.03)] text-[var(--muted)]"
              }`}
            >
              Pendentes
            </button>
            <button
              onClick={() => setStatus("sent")}
              className={`h-12 rounded-2xl border border-[var(--border)] px-3 text-sm font-semibold ${
                status === "sent"
                  ? "bg-[color:rgba(47,107,255,0.18)] text-[var(--title)]"
                  : "bg-[color:rgba(255,255,255,0.03)] text-[var(--muted)]"
              }`}
            >
              Enviados
            </button>
          </div>
        </div>

        <div className="mt-6 rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-4">
          <div className="flex items-center justify-between gap-3">
            <div>
              <div className="text-sm font-semibold text-[var(--title)]">
                Regra de retorno
              </div>
              <div className="mt-1 text-xs text-[var(--muted)]">
                Ao finalizar OS, agenda automaticamente.
              </div>
            </div>
            <Badge tone={ruleActive ? "success" : "neutral"}>
              {ruleActive ? "Ativo" : "Desativado"}
            </Badge>
          </div>

          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <Input
              placeholder="Dias após (ex: 180)"
              value={ruleDays}
              onChange={setRuleDays}
            />
            <button
              onClick={() => setRuleActive((v) => !v)}
              className="h-12 rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.03)] px-4 text-sm font-semibold text-[var(--title)] hover:bg-[color:rgba(255,255,255,0.06)]"
            >
              {ruleActive ? "Desativar regra" : "Ativar regra"}
            </button>
            <button
              onClick={saveRule}
              disabled={savingRule}
              className="h-12 rounded-2xl bg-[var(--primary)] px-4 text-sm font-semibold text-white hover:bg-[var(--primaryHover)] disabled:opacity-60"
            >
              {savingRule ? "Salvando..." : "Salvar regra"}
            </button>
          </div>
        </div>

        <div className="mt-6 space-y-3">
          {loading ? (
            <div className="text-sm text-[var(--muted)]">Carregando...</div>
          ) : filtered.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-6">
              <div className="text-sm font-semibold text-[var(--title)]">
                Nenhum retorno ainda
              </div>
              <div className="mt-2 text-sm text-[var(--muted)]">
                Finalize uma OS e o BoxRota agenda o retorno com mensagem pronta.
              </div>
            </div>
          ) : (
            filtered.map((r) => {
              const phone = (r.customer_phone || "").replace(/\D/g, "");
              const plate = (r.vehicle_plate || "-").toUpperCase();
              const name = r.customer_name || "Cliente";
              const msg = buildReturnMessage(name, plate);

              return (
                <div
                  key={r.id}
                  className="rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-4"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <div className="text-base font-semibold text-[var(--title)]">
                          {plate}
                        </div>
                        <Badge tone={tone(r.status) as any}>
                          {label(r.status)}
                        </Badge>
                      </div>
                      <div className="mt-1 text-xs text-[var(--muted)]">
                        {name}
                        {r.customer_phone ? ` • ${r.customer_phone}` : ""}
                      </div>
                      <div className="mt-2 text-xs text-[var(--muted)]">
                        Previsto:{" "}
                        <span className="text-[var(--title)]">
                          {formatDate(r.due_date)}
                        </span>
                      </div>
                    </div>

                    <div className="flex flex-col gap-2">
                      <a
                        href={phone ? waLink(phone, msg) : undefined}
                        target="_blank"
                        rel="noreferrer"
                        className={`h-10 inline-flex items-center justify-center rounded-2xl px-4 text-xs font-semibold ${
                          phone
                            ? "bg-[var(--success)] text-white hover:bg-[var(--successHover)]"
                            : "bg-[color:rgba(255,255,255,0.06)] text-[var(--muted)] cursor-not-allowed"
                        }`}
                      >
                        WhatsApp
                      </a>

                      <button
                        onClick={() =>
                          setRowStatus(
                            r.id,
                            r.status === "sent" ? "done" : "sent"
                          )
                        }
                        className="h-10 rounded-2xl bg-[color:rgba(255,255,255,0.06)] px-4 text-xs font-semibold text-[var(--title)] hover:bg-[color:rgba(255,255,255,0.10)]"
                      >
                        {r.status === "sent"
                          ? "Marcar concluído"
                          : "Marcar enviado"}
                      </button>

                      <button
                        onClick={() => setRowStatus(r.id, "pending")}
                        className="h-10 rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] px-4 text-xs font-semibold text-[var(--muted)] hover:bg-[color:rgba(255,255,255,0.05)]"
                      >
                        Voltar p/ pendente
                      </button>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </Card>
    </div>
  );
}