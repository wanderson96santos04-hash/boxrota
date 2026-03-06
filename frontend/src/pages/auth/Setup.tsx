import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Logo from "../../assets/logo-boxrota.svg";
import { Input } from "../../components/ui/Input";
import api from "../../lib/api";

type SetupResponse = {
  workshop: {
    id: string;
    name: string;
    slug?: string;
  };
  user: {
    id: string;
    name: string;
    email: string;
  };
  tokens: {
    access_token: string;
    refresh_token: string;
    token_type?: string;
  };
};

function extractErrorMessage(err: any): string {
  const data = err?.response?.data;

  if (!data) {
    return err?.message || "Erro ao criar conta.";
  }

  if (typeof data.message === "string" && data.message.trim()) {
    return data.message;
  }

  if (typeof data.detail === "string" && data.detail.trim()) {
    return data.detail;
  }

  if (Array.isArray(data.detail) && data.detail.length > 0) {
    const first = data.detail[0];
    if (typeof first?.msg === "string") {
      return first.msg;
    }
  }

  if (typeof data.code === "string" && data.code.trim()) {
    return data.code;
  }

  return "Erro ao criar conta.";
}

export default function Setup() {
  const navigate = useNavigate();

  const [workshopName, setWorkshopName] = useState("");
  const [phone, setPhone] = useState("");
  const [city, setCity] = useState("");

  const [adminName, setAdminName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    const payload = {
      workshop: {
        name: workshopName.trim(),
        phone: phone.trim(),
        city: city.trim(),
      },
      admin: {
        name: adminName.trim(),
        email: email.trim().toLowerCase(),
        password,
      },
    };

    try {
      setLoading(true);

      const res = await api.post<SetupResponse>("/auth/setup", payload);

      const access = res.data?.tokens?.access_token;
      const refresh = res.data?.tokens?.refresh_token;
      const workshop = res.data?.workshop;
      const user = res.data?.user;

      if (!access || !refresh || !workshop?.id) {
        throw new Error("Resposta inválida ao criar conta.");
      }

      localStorage.setItem("boxrota_access_token", access);
      localStorage.setItem("boxrota_refresh_token", refresh);
      localStorage.setItem("boxrota_workshop_id", workshop.id);

      if (workshop.slug) {
        localStorage.setItem("boxrota_workshop_slug", workshop.slug);
      }

      if (workshop.name) {
        localStorage.setItem("boxrota_workshop_name", workshop.name);
      }

      if (user?.email) {
        localStorage.setItem("boxrota_user_email", user.email);
      }

      navigate("/app", { replace: true });
    } catch (err: any) {
      setError(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[var(--bg,#0b1020)] text-[var(--text,#e5e7eb)] flex items-center justify-center px-6">
      <div className="w-full max-w-[560px] rounded-[22px] border border-[var(--border,#1f2937)] bg-[var(--surface,#111827)] p-8 shadow-[0_20px_60px_rgba(0,0,0,0.35)]">
        <div className="flex items-center gap-4">
          <div className="grid h-11 w-11 place-items-center rounded-2xl bg-blue-600/20 ring-1 ring-[var(--border,#1f2937)]">
            <img src={Logo} alt="BoxRota" className="h-7 w-7" />
          </div>

          <div className="flex items-center gap-8">
            <div className="text-2xl font-bold text-[var(--title,#fff)]">
              BoxRota
            </div>
            <div className="text-2xl font-bold text-[var(--title,#fff)]">
              Criar oficina
            </div>
          </div>
        </div>

        {error && (
          <div className="mt-5 rounded-2xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-200">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-8 grid gap-4">
          <Input
            placeholder="Nome da oficina"
            value={workshopName}
            onChange={setWorkshopName}
          />

          <Input
            placeholder="Telefone"
            value={phone}
            onChange={setPhone}
          />

          <Input
            placeholder="Cidade"
            value={city}
            onChange={setCity}
          />

          <Input
            placeholder="Seu nome"
            value={adminName}
            onChange={setAdminName}
          />

          <Input
            placeholder="Email"
            value={email}
            onChange={setEmail}
          />

          <Input
            placeholder="Senha"
            value={password}
            onChange={setPassword}
          />

          <button
            type="submit"
            disabled={loading}
            className="mt-2 h-14 w-full rounded-2xl bg-[var(--primary,#3b82f6)] text-white font-semibold text-sm hover:opacity-95 disabled:opacity-60"
          >
            {loading ? "Criando..." : "Criar conta"}
          </button>
        </form>

        <div className="mt-6 text-center">
          <Link
            to="/"
            className="text-sm font-semibold text-[var(--muted,#9ca3af)] hover:text-white"
          >
            Voltar para a landing
          </Link>
        </div>
      </div>
    </div>
  );
}