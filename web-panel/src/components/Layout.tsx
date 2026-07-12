import { useEffect, useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { clearToken, fetchProfile } from "../api/client";
import type { UserProfile } from "../types";
import BrandWordmark from "./BrandWordmark";

export default function Layout() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<UserProfile | null>(null);

  useEffect(() => {
    fetchProfile()
      .then((p) => {
        if (p.role !== "tech" && p.role !== "admin") {
          clearToken();
          navigate("/login");
          return;
        }
        setProfile(p);
      })
      .catch(() => {
        clearToken();
        navigate("/login");
      });
  }, [navigate]);

  function logout() {
    clearToken();
    navigate("/login");
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar-brand">
          <img src={`${import.meta.env.BASE_URL}app_logo.png`} alt="NEXO Agro" className="brand-logo" />
          <div>
            <BrandWordmark />
            <p className="muted">Panel Enterprise — cooperativas y SAT</p>
          </div>
        </div>
        <div className="topbar-right">
          {profile && <span>{profile.name} ({profile.role})</span>}
          <button type="button" onClick={logout}>Salir</button>
        </div>
      </header>
      <nav className="nav">
        <NavLink to="/" end>Dashboard</NavLink>
        <NavLink to="/validacion">Validar escaneos</NavLink>
        <NavLink to="/agricultores">Agricultores</NavLink>
      </nav>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
