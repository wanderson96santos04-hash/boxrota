import React from "react";
import { Link } from "react-router-dom";
import Logo from "../../assets/logo-boxrota.svg";

const CHECKOUT_PRO = "https://pay.kiwify.com.br/zZJN9Oj";
const DASH_PREVIEW_SRC = "/dashboard-preview.png";

function Container({ children }: { children: React.ReactNode }) {
  return <div className="mx-auto w-full max-w-7xl px-6">{children}</div>;
}

function Badge({ children }: { children: React.ReactNode }) {
  return (
    <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[color:rgba(255,255,255,0.03)] px-4 py-2 text-xs font-semibold text-[var(--text)]">
      <span className="h-2 w-2 rounded-full bg-[var(--success)]" />
      {children}
    </div>
  );
}

function Card({
  title,
  desc,
  icon,
}: {
  title: string;
  desc: string;
  icon: React.ReactNode;
}) {
  return (
    <div className="group rounded-[18px] border border-[var(--border)] bg-[var(--surface)] p-6 shadow-[0_18px_55px_rgba(0,0,0,0.22)] transition hover:-translate-y-0.5 hover:shadow-[0_24px_70px_rgba(0,0,0,0.28)]">
      <div className="flex items-start gap-3">
        <div className="grid h-10 w-10 place-items-center rounded-2xl bg-[color:rgba(47,107,255,0.14)] ring-1 ring-[var(--border)]">
          {icon}
        </div>
        <div>
          <div className="text-base font-semibold text-[var(--title)]">
            {title}
          </div>
          <div className="mt-2 text-sm text-[var(--muted)]">{desc}</div>
        </div>
      </div>
    </div>
  );
}

function CheckIcon() {
  return (
    <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M20 6L9 17l-5-5"
        stroke="currentColor"
        strokeWidth="2.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function BoltIcon() {
  return (
    <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M13 2L3 14h7l-1 8 12-14h-7l-1-6z"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function CarIcon() {
  return (
    <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M3 13l2-6a2 2 0 0 1 2-1h10a2 2 0 0 1 2 1l2 6"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <path
        d="M5 13h14v6H5v-6z"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinejoin="round"
      />
      <path
        d="M7.5 19a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3zM16.5 19a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3z"
        fill="currentColor"
      />
    </svg>
  );
}

function BoxIcon() {
  return (
    <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M21 8l-9-5-9 5 9 5 9-5z"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinejoin="round"
      />
      <path
        d="M3 8v8l9 5 9-5V8"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinejoin="round"
      />
      <path
        d="M12 13v8"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}

function Divider() {
  return <div className="my-14 h-px w-full bg-[var(--border)]/80" />;
}

export default function Home() {
  return (
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text)]">
      <div className="pointer-events-none fixed inset-0 -z-10">
        <div className="absolute left-1/2 top-[-220px] h-[520px] w-[520px] -translate-x-1/2 rounded-full bg-[color:rgba(47,107,255,0.18)] blur-[90px]" />
        <div className="absolute right-[-160px] top-[120px] h-[460px] w-[460px] rounded-full bg-[color:rgba(45,212,191,0.10)] blur-[90px]" />
        <div className="absolute bottom-[-220px] left-[-180px] h-[520px] w-[520px] rounded-full bg-[color:rgba(168,85,247,0.10)] blur-[95px]" />
      </div>

      <header className="sticky top-0 z-30 border-b border-[var(--border)] bg-[color:rgba(11,16,32,0.72)] backdrop-blur">
        <Container>
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center gap-3">
              <div className="grid h-11 w-11 place-items-center rounded-2xl bg-[color:rgba(47,107,255,0.18)] ring-1 ring-[var(--border)] shadow-[0_10px_28px_rgba(0,0,0,0.25)]">
                <img src={Logo} alt="BoxRota" className="h-7 w-7" />
              </div>
              <div className="leading-tight">
                <div className="flex items-center gap-2">
                  <div className="text-base font-extrabold tracking-tight text-[var(--title)]">
                    BoxRota
                  </div>
                  <div className="rounded-full border border-[var(--border)] bg-[color:rgba(255,255,255,0.05)] px-2 py-0.5 text-[10px] font-semibold text-[var(--text)]">
                    SaaS
                  </div>
                </div>
                <div className="text-sm font-medium text-[var(--muted)]">
                  Retorno automático. Oficina organizada.
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Link
                to="/auth/login"
                className="rounded-xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.03)] px-4 py-2 text-sm font-semibold text-[var(--text)] hover:bg-[color:rgba(255,255,255,0.06)] hover:text-[var(--title)]"
              >
                Entrar
              </Link>

              <a
                href={CHECKOUT_PRO}
                target="_blank"
                rel="noreferrer"
                className="rounded-xl bg-[var(--primary)] px-4 py-2 text-sm font-semibold text-white hover:bg-[var(--primaryHover)]"
              >
                Assinar Pro
              </a>
            </div>
          </div>
        </Container>
      </header>

      <main>
        <section className="pt-14">
          <Container>
            <div className="mx-auto max-w-3xl text-center">
              <Badge>Feito para oficina na correria • Mobile-first real</Badge>

              <h1 className="mt-6 text-4xl font-semibold leading-tight text-[var(--title)] md:text-6xl">
                Pare de perder serviços por falta de organização.
                <span className="text-[var(--muted)]">
                  {" "}
                  Feche mais com um sistema profissional.
                </span>
              </h1>

              <p className="mx-auto mt-6 max-w-2xl text-base text-[var(--text)]/90 md:text-lg">
                Crie OS em segundos, registre peças e mão de obra, gere orçamento
                profissional e acompanhe retornos — sem planilha, sem papel, sem
                “procura aí”.
              </p>

              <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
                <Link
                  to="/auth/setup"
                  className="inline-flex h-12 items-center justify-center rounded-2xl bg-[var(--primary)] px-8 text-sm font-semibold text-white hover:bg-[var(--primaryHover)]"
                >
                  Criar conta grátis
                </Link>

                <Link
                  to="/app"
                  className="inline-flex h-12 items-center justify-center rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.03)] px-8 text-sm font-semibold text-[var(--title)] hover:bg-[color:rgba(255,255,255,0.06)]"
                >
                  Ver painel (preview)
                </Link>
              </div>

              <div className="mt-3 text-xs text-[var(--muted)]">
                Sem cartão • Comece em menos de 30 segundos
              </div>
            </div>

            <div className="mt-10">
              <div className="mx-auto max-w-6xl rounded-[22px] border border-[var(--border)] bg-[var(--surface)] p-3 shadow-[0_30px_100px_rgba(0,0,0,0.28)]">
                <div className="flex items-center gap-2 px-3 py-2">
                  <span className="h-2.5 w-2.5 rounded-full bg-[color:rgba(255,255,255,0.18)]" />
                  <span className="h-2.5 w-2.5 rounded-full bg-[color:rgba(255,255,255,0.12)]" />
                  <span className="h-2.5 w-2.5 rounded-full bg-[color:rgba(255,255,255,0.10)]" />
                  <div className="ml-2 text-xs font-medium text-[var(--muted)]">
                    Prévia do painel
                  </div>
                </div>

                <img
                  src={DASH_PREVIEW_SRC}
                  alt="Dashboard BoxRota"
                  className="w-full rounded-[16px] border border-[var(--border)] shadow-[0_40px_120px_rgba(0,0,0,0.5)]"
                />
              </div>
            </div>

            <div className="mt-10 grid gap-4 md:grid-cols-3">
              <Card
                title="Retorno automático"
                desc="Finalize a OS e o BoxRota sugere o retorno. Você só confirma e manda no WhatsApp."
                icon={<BoltIcon />}
              />
              <Card
                title="Histórico por placa"
                desc="Atendimento rápido: veja tudo que já foi feito no carro e evite retrabalho."
                icon={<CarIcon />}
              />
              <Card
                title="Peças no fluxo da OS"
                desc="Registre peças e custos. No Pro você compara ofertas e controla pedidos."
                icon={<BoxIcon />}
              />
            </div>
          </Container>
        </section>

        <section className="pt-16">
          <Container>
            <div className="mx-auto max-w-6xl">
              <h2 className="text-center text-3xl font-semibold text-[var(--title)]">
                A maioria das oficinas perde dinheiro por um motivo simples
              </h2>

              <div className="mt-10 grid gap-4 md:grid-cols-3">
                <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-[0_18px_55px_rgba(0,0,0,0.14)]">
                  <div className="text-base font-semibold text-[var(--title)]">
                    ❌ Esquece de cobrar resposta
                  </div>
                  <p className="mt-2 text-sm text-[var(--muted)]">
                    O cliente pede orçamento e ninguém acompanha depois.
                  </p>
                </div>

                <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-[0_18px_55px_rgba(0,0,0,0.14)]">
                  <div className="text-base font-semibold text-[var(--title)]">
                    ❌ Não sabe quem está aguardando
                  </div>
                  <p className="mt-2 text-sm text-[var(--muted)]">
                    Sem organização, serviços ficam perdidos no WhatsApp.
                  </p>
                </div>

                <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-[0_18px_55px_rgba(0,0,0,0.14)]">
                  <div className="text-base font-semibold text-[var(--title)]">
                    ❌ Histórico do carro perdido
                  </div>
                  <p className="mt-2 text-sm text-[var(--muted)]">
                    Quando o cliente volta, ninguém lembra o que foi feito.
                  </p>
                </div>
              </div>

              <p className="mt-8 text-center text-sm font-medium text-[var(--muted)]">
                O cliente esfria e fecha com outra oficina.
              </p>
            </div>
          </Container>
        </section>

        <Divider />

        <section>
          <Container>
            <div className="grid gap-4 rounded-[18px] border border-[var(--border)] bg-[var(--surface)] p-6 shadow-[0_18px_55px_rgba(0,0,0,0.20)] md:grid-cols-3">
              <div className="rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-5">
                <div className="text-2xl font-semibold text-[var(--title)]">
                  OS em 3 cliques
                </div>
                <div className="mt-2 text-sm text-[var(--muted)]">
                  Criação, itens e orçamento sem bagunça.
                </div>
              </div>
              <div className="rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-5">
                <div className="text-2xl font-semibold text-[var(--title)]">
                  Histórico sempre
                </div>
                <div className="mt-2 text-sm text-[var(--muted)]">
                  Placa = tudo que já foi feito no carro.
                </div>
              </div>
              <div className="rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] p-5">
                <div className="text-2xl font-semibold text-[var(--title)]">
                  Mais retorno
                </div>
                <div className="mt-2 text-sm text-[var(--muted)]">
                  Você vira a oficina que chama na hora certa.
                </div>
              </div>
            </div>
          </Container>
        </section>

        <Divider />

        <section>
          <Container>
            <div className="mx-auto max-w-3xl text-center">
              <div className="text-3xl font-semibold text-[var(--title)]">
                Planos simples. Cresce com você.
              </div>
              <div className="mt-3 text-sm text-[var(--muted)]">
                Comece no Basic para organizar. Suba para Pro para vender mais e
                automatizar tudo.
              </div>
            </div>

            <div className="mt-10 grid gap-4 md:grid-cols-2">
              <div className="rounded-[18px] border border-[var(--border)] bg-[var(--surface)] p-7 shadow-[0_18px_55px_rgba(0,0,0,0.20)]">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="text-lg font-semibold text-[var(--title)]">
                      Basic
                    </div>
                    <div className="mt-1 text-sm text-[var(--muted)]">
                      Para organizar a rotina sem dor de cabeça.
                    </div>
                  </div>
                  <div className="rounded-full border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] px-3 py-1 text-xs font-semibold text-[var(--text)]">
                    Começar
                  </div>
                </div>

                <div className="mt-5 text-3xl font-semibold text-[var(--title)]">
                  R$ 39,90
                  <span className="text-sm font-medium text-[var(--muted)]">
                    {" "}
                    / mês
                  </span>
                </div>

                <ul className="mt-6 space-y-3 text-sm text-[var(--text)]/90">
                  {[
                    "Dashboard da oficina",
                    "OS / Serviços",
                    "Clientes e veículos",
                    "Histórico por placa",
                    "Registro de peças e mão de obra",
                  ].map((t) => (
                    <li key={t} className="flex items-center gap-2">
                      <span className="text-[var(--success)]">
                        <CheckIcon />
                      </span>
                      {t}
                    </li>
                  ))}
                </ul>

                <Link
                  to="/auth/setup"
                  className="mt-7 inline-flex h-12 w-full items-center justify-center rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.03)] px-6 text-sm font-semibold text-[var(--title)] hover:bg-[color:rgba(255,255,255,0.06)]"
                >
                  Criar conta (setup)
                </Link>

                <div className="mt-3 text-xs text-[var(--muted)]">
                  Ideal para começar a operar e parar a bagunça.
                </div>
              </div>

              <div className="relative rounded-[18px] border border-[var(--border)] bg-[var(--surface)] p-7 shadow-[0_22px_70px_rgba(0,0,0,0.26)]">
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-[var(--primary)] px-4 py-1 text-xs font-semibold text-white shadow-[0_10px_30px_rgba(0,0,0,0.20)]">
                  Mais escolhido
                </div>

                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="text-lg font-semibold text-[var(--title)]">
                      Pro
                    </div>
                    <div className="mt-1 text-sm text-[var(--muted)]">
                      Para fechar mais e automatizar retorno + pedidos.
                    </div>
                  </div>
                  <div className="rounded-full border border-[var(--border)] bg-[color:rgba(47,107,255,0.14)] px-3 py-1 text-xs font-semibold text-[var(--title)]">
                    Pro
                  </div>
                </div>

                <div className="mt-5 text-3xl font-semibold text-[var(--title)]">
                  R$ 49,90
                  <span className="text-sm font-medium text-[var(--muted)]">
                    {" "}
                    / mês
                  </span>
                </div>

                <ul className="mt-6 space-y-3 text-sm text-[var(--text)]/90">
                  {[
                    "Tudo do Basic",
                    "Marketplace de peças e fornecedores",
                    "Pedidos e controle de compras",
                    "Retorno automático + prioridade no dashboard",
                    "Recursos premium do painel",
                  ].map((t) => (
                    <li key={t} className="flex items-center gap-2">
                      <span className="text-[var(--success)]">
                        <CheckIcon />
                      </span>
                      {t}
                    </li>
                  ))}
                </ul>

                <a
                  href={CHECKOUT_PRO}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-7 inline-flex h-12 w-full items-center justify-center rounded-2xl bg-[var(--primary)] px-6 text-sm font-semibold text-white hover:bg-[var(--primaryHover)]"
                >
                  Assinar Pro agora
                </a>

                <div className="mt-3 text-xs text-[var(--muted)]">
                  Checkout seguro (Kiwify). Ativa na hora.
                </div>
              </div>
            </div>
          </Container>
        </section>

        <Divider />

        <section className="pb-16">
          <Container>
            <div className="rounded-[18px] border border-[var(--border)] bg-[var(--surface)] p-8 shadow-[0_22px_70px_rgba(0,0,0,0.22)]">
              <div className="flex flex-col items-start justify-between gap-6 md:flex-row md:items-center">
                <div>
                  <div className="text-2xl font-semibold text-[var(--title)]">
                    Organize a oficina hoje.
                  </div>
                  <div className="mt-2 text-sm text-[var(--muted)]">
                    Menos bagunça. Mais retorno. Mais previsibilidade.
                  </div>
                </div>

                <div className="flex w-full flex-col gap-3 sm:w-auto sm:flex-row">
                  <Link
                    to="/auth/setup"
                    className="inline-flex h-12 items-center justify-center rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.03)] px-7 text-sm font-semibold text-[var(--title)] hover:bg-[color:rgba(255,255,255,0.06)]"
                  >
                    Criar conta grátis
                  </Link>
                  <a
                    href={CHECKOUT_PRO}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex h-12 items-center justify-center rounded-2xl bg-[var(--primary)] px-7 text-sm font-semibold text-white hover:bg-[var(--primaryHover)]"
                  >
                    Assinar Pro
                  </a>
                </div>
              </div>
            </div>

            <div className="mt-10 text-center text-sm text-[var(--muted)]">
              BoxRota • Sistema de gestão para oficinas (Brasil)
            </div>
          </Container>
        </section>
      </main>
    </div>
  );
}