import React, { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Logo from "../../assets/logo-boxrota.svg";
import { Input } from "../../components/ui/Input";
import api from "../../lib/api";

type LoginResponse = {
  user: any;
  workshop?: {
    id: string;
    slug: string;
    name: string;
  };
  tokens: {
    access_token: string;
    refresh_token: string;
  };
};

export default function Login() {
  const navigate = useNavigate();

  const [slug, setSlug] = useState(
    localStorage.getItem("boxrota_workshop_slug") || ""
  );
  const [email, setEmail] = useState(
    localStorage.getItem("boxrota_user_email") || ""
  );
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSubmit = useMemo(() => {
    return (
      !loading &&
      slug.trim().length >= 2 &&
      email.trim().length >= 3 &&
      password.length >= 1
    );
  }, [loading, slug, email, password]);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    const slugValue = slug.trim().toLowerCase();
    const emailValue = email.trim().toLowerCase();

    if (!slugValue) return setError("Informe o identificador da oficina.");
    if (!emailValue) return setError("Informe o e-mail.");
    if (!password) return setError("Informe a senha.");

    try {
      setLoading(true);

      const res = await api.post<LoginResponse>(
        `/auth/login?slug=${encodeURIComponent(slugValue)}`,
        {
          email: emailValue,
          password,
        }
      );

      const access = res.data?.tokens?.access_token;
      const refresh = res.data?.tokens?.refresh_token;
      const workshop = res.data?.workshop;
      const user = res.data?.user;

      if (!access || !refresh) {
        throw new Error("Resposta inválida do servidor (tokens ausentes).");
      }

      localStorage.setItem("boxrota_access_token", access);
      localStorage.setItem("boxrota_refresh_token", refresh);
      localStorage.setItem("boxrota_workshop_slug", slugValue);

      if (workshop?.id) {
        localStorage.setItem("boxrota_workshop_id", workshop.id);
      }

      if (workshop?.name) {
        localStorage.setItem("boxrota_workshop_name", workshop.name);
      }

      if (user?.email) {
        localStorage.setItem("boxrota_user_email", user.email);
      }

      navigate("/app", { replace: true });
    } catch (err: any) {
      const apiMessage =
        err?.response?.data?.message ||
        err?.response?.data?.detail ||
        err?.message ||
        "Falha ao entrar. Verifique oficina, e-mail e senha.";

      setError(apiMessage);

      localStorage.removeItem("boxrota_access_token");
      localStorage.removeItem("boxrota_refresh_token");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[var(--bg,#0f172a)] text-[var(--text,#e5e7eb)] flex items-center justify-center px-6">
      <div className="w-full max-w-[560px] rounded-[18px] border border-[var(--border,#1f2937)] bg-[var(--surface,#111827)] p-7 shadow-[0_18px_55px_rgba(0,0,0,0.35)]">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-2xl bg-blue-600/20 ring-1 ring-[var(--border,#1f2937)]">
            <img src={Logo} alt="BoxRota" className="h-6 w-6" />
          </div>

          <div>
            <div className="text-base font-semibold text-[var(--title,#fff)]">
              Entrar no BoxRota
            </div>

            <div className="text-xs text-[var(--muted,#9ca3af)]">
              Retorno automático. Oficina organizada.
            </div>
          </div>
        </div>

        {error && (
          <div className="mt-5 rounded-2xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-[var(--title,#fff)]">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="mt-6 grid gap-4">
          <Input
            placeholder="Identificador da oficina — ex: minha-oficina"
            required
            value={slug}
            onChange={(e: any) => setSlug(e.target.value)}
          />

          <Input
            placeholder="E-mail"
            type="email"
            required
            value={email}
            onChange={(e: any) => setEmail(e.target.value)}
          />

          <Input
            placeholder="Senha"
            type="password"
            required
            value={password}
            onChange={(e: any) => setPassword(e.target.value)}
          />

          <button
            type="submit"
            disabled={!canSubmit}
            className="mt-2 h-12 w-full rounded-2xl bg-blue-600 text-white font-semibold text-sm shadow-lg hover:bg-blue-700 transition disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? "Entrando..." : "Entrar no painel"}
          </button>

          <div className="mt-2 rounded-2xl border border-[var(--border,#1f2937)] bg-white/5 p-4 text-xs text-[var(--muted,#9ca3af)]">
            Use o identificador da sua oficina, por exemplo:
            <span className="ml-1 font-semibold">minha-oficina</span>
          </div>

          <Link
            to="/"
            className="text-center text-sm font-semibold text-[var(--muted,#9ca3af)] hover:text-white transition"
          >
            Voltar para a landing
          </Link>
        </form>
      </div>
    </div>
  );
}