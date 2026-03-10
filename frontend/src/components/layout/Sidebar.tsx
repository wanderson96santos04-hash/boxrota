import { NavLink, useNavigate } from "react-router-dom";
import logo from "../../assets/logo-boxrota.svg";
import { Badge } from "../ui/Badge";

const nav = [
  { to: "/app", label: "Dashboard" },
  { to: "/app/services", label: "Serviços (OS)" },
  { to: "/app/customers", label: "Clientes" },
  { to: "/app/vehicles", label: "Veículos" },
  { to: "/app/parts", label: "Peças" },
  { to: "/app/marketplace", label: "Marketplace" },
];

const adminNav = [
  { to: "/app/admin/suppliers", label: "Fornecedores" },
  { to: "/app/admin/offers", label: "Ofertas de Peças" },
];

function clsActive(isActive: boolean) {
  return [
    "group flex items-center justify-between gap-3 rounded-2xl px-4 py-3 transition-all",
    "border border-transparent",
    isActive
      ? "bg-blue-600/15 border-blue-500/30 text-[var(--title)] shadow-sm"
      : "text-[var(--text)] hover:bg-white/5 hover:text-[var(--title)]",
  ].join(" ");
}

export default function Sidebar() {
  const navigate = useNavigate();

  function logout() {
    localStorage.removeItem("boxrota_access_token");
    localStorage.removeItem("boxrota_refresh_token");
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    navigate("/auth/login");
  }

  return (
    <div className="sticky top-0 relative h-screen w-[270px] border-r border-[var(--border)] bg-[var(--surface)]">
      <div className="flex h-full flex-col">
        {/* LOGO */}
        <div className="px-6 pt-6">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-600/15 ring-1 ring-blue-500/30 shadow-md">
              <img
                src={logo}
                alt="BoxRota"
                className="h-8 w-8 object-contain"
              />
            </div>

            <div className="leading-tight">
              <div className="text-lg font-semibold text-[var(--title)]">
                BoxRota
              </div>

              <div className="text-xs text-[var(--muted)]">
                Retorno automático
              </div>
            </div>
          </div>

          {/* PLANO */}
          <div className="mt-6 rounded-2xl border border-[var(--border)] bg-white/5 p-4">
            <div className="flex items-center justify-between">
              <div className="text-sm font-semibold text-[var(--title)]">
                Plano atual
              </div>

              <Badge tone="primary">Basic</Badge>
            </div>

            <div className="mt-2 text-xs text-[var(--muted)]">
              Marketplace com pedidos é Pro.
            </div>

            <button className="mt-4 w-full rounded-xl bg-[var(--primary)] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[var(--primaryHover)]">
              Desbloquear Pro
            </button>
          </div>
        </div>

        {/* NAV */}
        <nav className="mt-7 flex-1 overflow-y-auto px-3 pb-28">
          <div className="px-3 pb-3 text-[11px] font-semibold tracking-wide text-[var(--muted)]">
            ROTINA DA OFICINA
          </div>

          <div className="space-y-2">
            {nav.map((i) => (
              <NavLink key={i.to} to={i.to} end={i.to === "/app"}>
                {({ isActive }) => (
                  <div className={clsActive(isActive)}>
                    <span className="text-sm font-medium">{i.label}</span>

                    <span className="text-xs text-[var(--muted)] opacity-0 transition group-hover:opacity-100">
                      →
                    </span>
                  </div>
                )}
              </NavLink>
            ))}
          </div>

          <div className="mt-6 px-3 pb-3 text-[11px] font-semibold tracking-wide text-[var(--muted)]">
            ADMIN MARKETPLACE
          </div>

          <div className="space-y-2">
            {adminNav.map((i) => (
              <NavLink key={i.to} to={i.to}>
                {({ isActive }) => (
                  <div className={clsActive(isActive)}>
                    <span className="text-sm font-medium">{i.label}</span>

                    <span className="text-xs text-[var(--muted)] opacity-0 transition group-hover:opacity-100">
                      →
                    </span>
                  </div>
                )}
              </NavLink>
            ))}
          </div>
        </nav>

        {/* LOGOUT */}
        <div className="absolute bottom-0 left-0 right-0 bg-[var(--surface)] px-6 pb-6 pt-3">
          <button
            onClick={logout}
            className="w-full rounded-2xl border border-[var(--border)] bg-white/5 px-4 py-3 text-left text-sm font-medium text-[var(--text)] transition hover:bg-white/10 hover:text-[var(--title)]"
          >
            Sair
          </button>
        </div>
      </div>
    </div>
  );
}