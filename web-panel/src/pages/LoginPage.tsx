import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { clearToken, fetchProfile, login } from "../api/client";

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("admin1234");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await login(email, password);
      const profile = await fetchProfile();
      if (profile.role !== "tech" && profile.role !== "admin") {
        clearToken();
        setError("Solo usuarios técnico o administrador pueden acceder al panel.");
        return;
      }
      navigate("/");
    } catch {
      setError("No se pudo iniciar sesión. Revisa email y contraseña.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={onSubmit}>
        <h2>Panel cooperativas</h2>
        <p className="muted">Acceso para técnicos y administradores</p>
        <label>
          Email
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>
          Contraseña
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={loading}>{loading ? "Entrando..." : "Entrar"}</button>
      </form>
    </div>
  );
}
