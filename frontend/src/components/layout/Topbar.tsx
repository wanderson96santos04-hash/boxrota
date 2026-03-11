import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
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

type TopbarProps = {
  pathname: string;
  onOpenMenu?: () => void;
};

export default function Topbar({ pathname, onOpenMenu }: TopbarProps) {
  const title = titleFromPath(pathname);
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const desktopInputRef = useRef<HTMLInputElement | null>(null);

  function focusSearch() {
    const input =
      desktopInputRef.current ||
      (document.getElementById("topbar-quick-search") as HTMLInputElement | null);

    if (input) {
      input.focus();
      input.select();
    }
  }

  function runSearch() {
    const term = (search || "").trim();

    if (!term) {
      focusSearch();
      return;
    }

    navigate(`/app/services?q=${encodeURIComponent(term)}`);
  }

  function handleInputKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") {
      e.preventDefault();
      runSearch();
    }
  }

  function handleInputKeyUp(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") {
      e.preventDefault();
      runSearch();
    }
  }

  useEffect(() => {
    function onGlobalKeyDown(e: KeyboardEvent) {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        focusSearch();
      }
    }

    function onQuickSearchRun() {
      runSearch();
    }

    function onQuickSearchFocus() {
      focusSearch();
    }

    window.addEventListener("keydown", onGlobalKeyDown);
    window.addEventListener("boxrota:quick-search-run", onQuickSearchRun as EventListener);
    window.addEventListener("boxrota:quick-search-focus", onQuickSearchFocus as EventListener);

    return () => {
      window.removeEventListener("keydown", onGlobalKeyDown);
      window.removeEventListener("boxrota:quick-search-run", onQuickSearchRun as EventListener);
      window.removeEventListener("boxrota:quick-search-focus", onQuickSearchFocus as EventListener);
    };
  }, [search]);

  return (
    <div className="sticky top-0 z-30 border-b border-[var(--border)] bg-[color:rgba(11,16,32,0.72)] backdrop-blur">
      <div className="px-4 py-4 lg:px-6">
        <div className="flex items-center gap-3">
          <div className="lg:hidden">
            <button
              type="button"
              onClick={onOpenMenu}
              className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.04)] text-[var(--title)] hover:bg-[color:rgba(255,255,255,0.08)]"
              aria-label="Abrir menu"
            >
              ☰
            </button>
          </div>

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
              id="topbar-quick-search"
              inputRef={desktopInputRef}
              placeholder="Buscar rápido: placa, cliente, telefone, OS..."
              rightHint="Ctrl K"
              value={search}
              onChange={setSearch}
              onKeyDown={handleInputKeyDown}
              onKeyUp={handleInputKeyUp}
            />
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => navigate("/app/services")}
              className="hidden rounded-xl border border-[var(--border)] px-4 py-2 text-sm font-medium text-[var(--text)] hover:bg-[color:rgba(255,255,255,0.04)] hover:text-[var(--title)] sm:inline-flex"
            >
              Novo serviço
            </button>
          </div>
        </div>

        <div className="mt-3 lg:hidden">
          <Input
            placeholder="Buscar: placa, cliente, telefone, OS..."
            value={search}
            onChange={setSearch}
            onKeyDown={handleInputKeyDown}
            onKeyUp={handleInputKeyUp}
          />
        </div>
      </div>
    </div>
  );
}