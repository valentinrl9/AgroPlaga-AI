import { useEffect, useRef, useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { clearToken, fetchProfile, fetchTechNotificationSummary } from "../api/client";
import type { TechNotificationSummary, UserProfile } from "../types";
import BrandWordmark from "./BrandWordmark";

export default function Layout() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [pendingScans, setPendingScans] = useState(0);
  const lastPendingRef = useRef(0);

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

  useEffect(() => {
    if (!profile) return;

    if ("Notification" in window && Notification.permission === "default") {
      void Notification.requestPermission();
    }

    const poll = async () => {
      try {
        const summary: TechNotificationSummary = await fetchTechNotificationSummary();
        if (
          summary.pending_scans > lastPendingRef.current &&
          lastPendingRef.current > 0 &&
          typeof Notification !== "undefined" &&
          Notification.permission === "granted"
        ) {
          new Notification("NEXO Agro — validación pendiente", {
            body: `${summary.pending_scans} escaneo(s) esperan revisión del perito.`,
            tag: "nexo-pending-scans",
          });
        }
        lastPendingRef.current = summary.pending_scans;
        setPendingScans(summary.pending_scans);
      } catch {
        /* ignore poll errors */
      }
    };

    void poll();
    const timer = window.setInterval(poll, 30000);
    return () => window.clearInterval(timer);
  }, [profile]);

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
        <NavLink to="/validacion">
          Validar escaneos
          {pendingScans > 0 ? <span className="nav-badge">{pendingScans}</span> : null}
        </NavLink>
        <NavLink to="/siex">Cuaderno SIEX</NavLink>
        <NavLink to="/incidencias">Incidencias</NavLink>
        <NavLink to="/agricultores">Agricultores</NavLink>
      </nav>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
