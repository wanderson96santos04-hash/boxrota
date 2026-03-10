import React, { useCallback, useMemo, useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import BottomNav from "./BottomNav";
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

export default function AppShell() {
  const navigate = useNavigate();
  const { pathname } = useLocation();

  const [loggingOut, setLoggingOut] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

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

  return (
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text)]">
      <div className="mx-auto max-w-[1200px]">
        <div className="grid min-h-screen grid-cols-1 lg:grid-cols-[280px_1fr]">
          <aside className="hidden lg:block">
            <Sidebar />
          </aside>

          <main className="min-h-screen">
            <Topbar
              pathname={pathname}
              onOpenMenu={() => setMobileMenuOpen(true)}
            />

            <div className="px-4 pt-3 lg:px-6">
              <div className="flex items-center justify-end">
                <button
                  type="button"
                  onClick={handleLogout}
                  disabled={loggingOut}
                  className="hidden lg:inline-flex h-10 items-center justify-center rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.02)] px-4 text-sm font-semibold text-[var(--title)] hover:bg-[color:rgba(255,255,255,0.04)] disabled:opacity-60 disabled:cursor-not-allowed"
                  title={!hasRefresh ? "Sem refresh token (logout local)" : "Sair"}
                >
                  {loggingOut ? "Saindo..." : "Sair"}
                </button>
              </div>
            </div>

            <div className="px-4 pb-24 pt-4 lg:px-6 lg:pb-10">
              <Outlet />
            </div>
          </main>
        </div>
      </div>

      {mobileMenuOpen ? (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="absolute inset-0 bg-black/60"
            onClick={() => setMobileMenuOpen(false)}
          />

          <div className="absolute left-0 top-0 h-full w-[290px] max-w-[85vw] bg-[var(--surface)] shadow-2xl">
            <div className="flex items-center justify-end p-3">
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
              onClick={() => setMobileMenuOpen(false)}
              className="h-[calc(100%-64px)] overflow-y-auto"
            >
              <Sidebar />
            </div>
          </div>
        </div>
      ) : null}

      <div className="lg:hidden">
        <BottomNav />

        <div className="fixed bottom-20 left-0 right-0 px-4">
          <button
            type="button"
            onClick={handleLogout}
            disabled={loggingOut}
            className="inline-flex h-12 w-full items-center justify-center rounded-2xl border border-[var(--border)] bg-[color:rgba(255,255,255,0.04)] px-4 text-sm font-semibold text-[var(--title)] hover:bg-[color:rgba(255,255,255,0.06)] shadow-[0_18px_55px_rgba(0,0,0,0.22)] disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loggingOut ? "Saindo..." : "Sair"}
          </button>
        </div>
      </div>
    </div>
  );
}