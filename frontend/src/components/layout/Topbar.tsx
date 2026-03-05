import { useLocation, useNavigate } from "react-router-dom";
import { Input } from "../ui/Input";
import { Badge } from "../ui/Badge";

function titleFromPath(pathname: string) {
  if (pathname === "/app") return "Dashboard";
  if (pathname.includes("/services")) return "Serviços (OS)";
  if (pathname.includes("/customers")) return "Clientes";
  if (pathname.includes("/vehicles")) return "Veículos";
  if (pathname.includes("/parts")) return "Peças";
  if (pathname.includes("/marketplace")) return "Marketplace";
  return "BoxRota";
}

export default function Topbar() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const title = titleFromPath(pathname);

  function logout() {
    localStorage.removeItem("boxrota_access_token");
    localStorage.removeItem("boxrota_refresh_token");
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    navigate("/auth/login");
  }

  return (
    <div className="sticky top-0 z-30 border-b border-[var(--border)] bg-[color:rgba(11,16,32,0.72)] backdrop-blur">
      <div className="px-4 py-4 lg:px-6">
        <div className="flex items-center gap-3">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <h1 className="truncate text-lg font-semibold text-[var(--title)]">
                {title}
              </h1>
              <div className="hidden sm:block">
                <Badge tone="success">Online</Badge>
              </div>
            </div>
            <div className="mt-1 hidden text-xs text-[var(--muted)] sm:block">
              Busca global por placa, cliente, telefone ou OS.
            </div>
          </div>

          <div className="hidden w-[420px] lg:block">
            <Input
              placeholder="Buscar rápido: placa, cliente, telefone, OS..."
              rightHint="Ctrl K"
            />
          </div>

          <div className="flex items-center gap-2">
            <button className="hidden rounded-xl border border-[var(--border)] px-4 py-2 text-sm font-medium text-[var(--text)] hover:bg-[color:rgba(255,255,255,0.04)] hover:text-[var(--title)] sm:inline-flex">
              Novo serviço
            </button>
            <button
              onClick={logout}
              className="rounded-xl bg-[color:rgba(255,255,255,0.06)] px-4 py-2 text-sm font-medium text-[var(--text)] hover:bg-[color:rgba(255,255,255,0.10)] hover:text-[var(--title)]"
            >
              Sair
            </button>
          </div>
        </div>

        <div className="mt-3 lg:hidden">
          <Input placeholder="Buscar: placa, cliente, telefone, OS..." />
        </div>
      </div>
    </div>
  );
}