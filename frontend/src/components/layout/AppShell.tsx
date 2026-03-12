import React, { useCallback, useMemo, useRef, useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import api from "../../lib/api";

function getRefreshToken() {
  return localStorage.getItem("boxrota_refresh_token") || "";
}

function clearSession() {
  localStorage.removeItem("boxrota_access_token");
  localStorage.removeItem("access_token");
  localStorage.removeItem("boxrota_refresh_token");
  localStorage.removeItem("boxrota_workshop_id");
}

export type AppShellOutletContext = {
  quickSearchValue: string;
  setQuickSearchValue: (value: string) => void;
  runQuickSearch: () => void;
  focusQuickSearch: () => void;
};

export default function AppShell() {
  const navigate = useNavigate();
  const { pathname } = useLocation();

  const [loggingOut, setLoggingOut] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [quickSearchValue, setQuickSearchValue] = useState("");

  const quickSearchInputRef = useRef<HTMLInputElement | null>(null);

  const hasRefresh = useMemo(() => {
    const rt = getRefreshToken();
    return Boolean(rt && rt.length > 20);
  }, []);

  const handleLogout = useCallback(async () => {
    if (loggingOut) return;

    try {
      setLoggingOut(true);

      const refresh_token = getRefreshToken();

      if (refresh_token) {
        await api.post("/auth/logout", { refresh_token });
      }
    } catch {
    } finally {
      clearSession();
      setLoggingOut(false);
      navigate("/auth/login", { replace: true });
    }
  }, [loggingOut, navigate]);

  const focusQuickSearch = useCallback(() => {
    const input = quickSearchInputRef.current;
    if (input) {
      input.focus();
      input.select();
    }
  }, []);

  const runQuickSearch = useCallback(() => {
    const term = (quickSearchValue || "").trim();

    if (!term) {
      focusQuickSearch();
      return;
    }

    navigate(`/app/services?q=${encodeURIComponent(term)}`);
  }, [focusQuickSearch, navigate, quickSearchValue]);

  const outletContext: AppShellOutletContext = {
    quickSearchValue,
    setQuickSearchValue,
    runQuickSearch,
    focusQuickSearch,
  };

  return (
    <div className="min-h-screen overflow-x-hidden bg-[var(--bg)] text-[var(--text)]">
      <div className="mx-auto max-w-[1200px]">
        <div className="grid min-h-screen grid-cols-1 lg:grid-cols-[280px_1fr]">
          <aside className="hidden lg:block">
            <Sidebar />
          </aside>

          <main className="min-h-screen min-w-0 overflow-x-hidden">
            <Topbar
              pathname={pathname}
              onOpenMenu={() => setMobileMenuOpen(true)}
              quickSearchValue={quickSearchValue}
              setQuickSearchValue={setQuickSearchValue}
              runQuickSearch={runQuickSearch}
              quickSearchInputRef={quickSearchInputRef}
            />

            <div className="px-4 pt-3 lg:px-6">
              <div className="flex items-center justify-end">
                <button
                  type="button"
                  onClick={handleLogout}
                  disabled={loggingOut}
                  className="hidden lg:inline-flex h-10 items-center justify-center rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] px-4 text-sm font-semibold text-[var(--title)] hover:bg-[color:rgba(255,255,255,0.04)] disabled:cursor-not-allowed disabled:opacity-60"
                  title={!hasRefresh ? "Sem refresh token (logout local)" : "Sair"}
                >
                  {loggingOut ? "Saindo..." : "Sair"}
                </button>
              </div>
            </div>

            <div className="min-w-0 overflow-x-hidden px-4 pb-8 pt-4 lg:px-6 lg:pb-10">
              <Outlet context={outletContext} />
            </div>
          </main>
        </div>
      </div>

      {mobileMenuOpen ? (
        <div className="fixed inset-0 z-50 lg:hidden">
          <button
            type="button"
            className="absolute inset-0 bg-black/60"
            onClick={() => setMobileMenuOpen(false)}
            aria-label="Fechar menu"
          />

          <div className="absolute left-0 top-0 h-full w-[290px] max-w-[85vw] overflow-hidden bg-[var(--surface)] shadow-2xl">
            <div className="flex items-center justify-end border-b border-[var(--border)] p-3">
              <button
                type="button"
                onClick={() => setMobileMenuOpen(false)}
                className="inline-flex h-10 w-10 items-center justify-center rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.04)] text-[var(--title)] hover:bg-[color:rgba(255,255,255,0.08)]"
                aria-label="Fechar menu"
              >
                ✕
              </button>
            </div>

            <div
              className="h-[calc(100%-73px)] overflow-y-auto"
              onClick={() => setMobileMenuOpen(false)}
            >
              <Sidebar />
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}