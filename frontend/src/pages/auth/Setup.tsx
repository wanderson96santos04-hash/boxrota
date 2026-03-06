import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Input } from "../../components/ui/Input";
import api from "../../lib/api";
import Logo from "../../assets/logo-boxrota.svg";

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

    try {
      setLoading(true);

      const res = await api.post("/auth/setup", {
        workshop_name: workshopName,
        phone,
        city,
        admin_name: adminName,
        email,
        password,
      });

      const tokens = res.data?.tokens;

      if (!tokens?.access_token) {
        throw new Error("Erro ao criar conta.");
      }

      localStorage.setItem("boxrota_access_token", tokens.access_token);
      localStorage.setItem("boxrota_refresh_token", tokens.refresh_token);

      navigate("/app", { replace: true });
    } catch (err: any) {
      const msg =
        err?.response?.data?.detail ||
        err?.message ||
        "Erro ao criar conta.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[var(--bg)] flex items-center justify-center px-6">
      <div className="w-full max-w-md rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-8">

        <div className="flex items-center gap-3 mb-6">
          <img src={Logo} className="h-8" />
          <div className="font-semibold text-lg text-[var(--title)]">
            Criar oficina
          </div>
        </div>

        {error && (
          <div className="mb-4 text-sm text-red-400">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">

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
            className="w-full h-12 rounded-xl bg-[var(--primary)] text-white font-semibold"
          >
            {loading ? "Criando..." : "Criar conta"}
          </button>

        </form>
      </div>
    </div>
  );
}