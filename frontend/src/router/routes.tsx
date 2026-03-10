import React from "react";
import { Navigate, Outlet, createBrowserRouter } from "react-router-dom";

import PublicHome from "../pages/public/Home";
import Login from "../pages/auth/Login";
import Setup from "../pages/auth/Setup";

import AppShell from "../components/layout/AppShell";
import Dashboard from "../pages/app/Dashboard";
import Services from "../pages/app/Services";
import ServiceDetail from "../pages/app/ServiceDetail";
import Customers from "../pages/app/Customers";
import Vehicles from "../pages/app/Vehicles";
import Parts from "../pages/app/Parts";
import Marketplace from "../pages/app/Marketplace";
import Returns from "../pages/app/Returns";

/* NOVAS TELAS ADMIN */
import Suppliers from "../pages/app/Suppliers";
import Offers from "../pages/app/Offers";

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
  localStorage.removeItem("boxrota_refresh_token");
  localStorage.removeItem("boxrota_workshop_id");
  localStorage.removeItem("boxrota_workshop_slug");
  localStorage.removeItem("boxrota_workshop_name");
  localStorage.removeItem("boxrota_user_email");
}

function parseJwtPayload(token: string): any | null {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;

    const base64 = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const padded = base64.padEnd(
      base64.length + ((4 - (base64.length % 4)) % 4),
      "="
    );

    const json = atob(padded);
    return JSON.parse(json);
  } catch {
    return null;
  }
}

function hasValidSession() {
  const token = getAccessToken();
  if (!token || token.length < 20) return false;

  const payload = parseJwtPayload(token);
  if (!payload) return false;

  if (typeof payload.exp === "number") {
    const nowSec = Math.floor(Date.now() / 1000);
    if (payload.exp <= nowSec) return false;
  }

  return true;
}

function Protected() {
  if (!hasValidSession()) {
    clearSession();
    return <Navigate to="/auth/login" replace />;
  }
  return <Outlet />;
}

function AuthOnlyPublic() {
  if (hasValidSession()) return <Navigate to="/app" replace />;
  return <Outlet />;
}

export const router = createBrowserRouter([
  { path: "/", element: <PublicHome /> },
  {
    path: "/auth",
    element: <AuthOnlyPublic />,
    children: [
      { path: "login", element: <Login /> },
      { path: "setup", element: <Setup /> },
    ],
  },
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

          /* ROTAS ADMIN DO MARKETPLACE */
          { path: "admin/suppliers", element: <Suppliers /> },
          { path: "admin/offers", element: <Offers /> },
        ],
      },
    ],
  },
]);