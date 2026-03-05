import React from "react";
import { Navigate, Outlet, createBrowserRouter } from "react-router-dom";

import PublicHome from "../pages/public/Home";
import Login from "../pages/auth/Login";

import AppShell from "../components/layout/AppShell";
import Dashboard from "../pages/app/Dashboard";
import Services from "../pages/app/Services";
import ServiceDetail from "../pages/app/ServiceDetail";
import Customers from "../pages/app/Customers";
import Vehicles from "../pages/app/Vehicles";
import Parts from "../pages/app/Parts";
import Marketplace from "../pages/app/Marketplace";
import Returns from "../pages/app/Returns";

function getAccessToken() {
  return (
    localStorage.getItem("boxrota_access_token") ||
    localStorage.getItem("access_token") ||
    ""
  );
}

function clearSession() {
  localStorage.removeItem("boxrota_access_token");
  localStorage.removeItem("access_token");
}

function parseJwtPayload(token: string): any | null {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;

    // base64url -> base64
    const base64 = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const padded = base64.padEnd(base64.length + (4 - (base64.length % 4)) % 4, "=");

    const json = atob(padded);
    return JSON.parse(json);
  } catch {
    return null;
  }
}

/**
 * Regra de sessão:
 * - token existe
 * - token parece JWT
 * - se tiver "exp", não pode estar expirado
 *
 * Não valida assinatura (isso é papel do backend), mas evita UX ruim de token expirado.
 */
function hasValidSession() {
  const token = getAccessToken();
  if (!token || token.length < 20) return false;

  const payload = parseJwtPayload(token);
  if (!payload) return false;

  // Se o token tiver exp, valida expiração
  if (typeof payload.exp === "number") {
    const nowSec = Math.floor(Date.now() / 1000);
    if (payload.exp <= nowSec) return false;
  }

  return true;
}

function Protected() {
  if (!hasValidSession()) {
    // evita “meia sessão” quebrada em produção
    clearSession();
    return <Navigate to="/auth/login" replace />;
  }
  return <Outlet />;
}

function AuthOnlyPublicLogin() {
  // Se já está logado, não deixa ficar na tela de login
  if (hasValidSession()) return <Navigate to="/app" replace />;
  return <Login />;
}

export const router = createBrowserRouter([
  { path: "/", element: <PublicHome /> },
  { path: "/auth/login", element: <AuthOnlyPublicLogin /> },
  {
    path: "/app",
    element: <Protected />,
    children: [
      {
        element: <AppShell />,
        children: [
          { index: true, element: <Dashboard /> },
          { path: "services", element: <Services /> },
          { path: "services/:id", element: <ServiceDetail /> },
          { path: "returns", element: <Returns /> },
          { path: "customers", element: <Customers /> },
          { path: "vehicles", element: <Vehicles /> },
          { path: "parts", element: <Parts /> },
          { path: "marketplace", element: <Marketplace /> },
        ],
      },
    ],
  },
]);