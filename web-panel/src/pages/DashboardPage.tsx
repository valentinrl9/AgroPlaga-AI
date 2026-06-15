import { useEffect, useState } from "react";
import { exportEventsCsv, fetchDashboard } from "../api/client";
import HeatmapMap from "../components/HeatmapMap";
import type { TechDashboard } from "../types";

export default function DashboardPage() {
  const [data, setData] = useState<TechDashboard | null>(null);
  const [hours, setHours] = useState(168);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchDashboard(hours)
      .then(setData)
      .catch((e) => setError(String(e)));
  }, [hours]);

  if (error) return <p className="error">{error}</p>;
  if (!data) return <p>Cargando dashboard...</p>;

  const maxTimeline = Math.max(...data.timeline.map((p) => p.count), 1);

  return (
    <div className="dashboard">
      <div className="toolbar">
        <label>
          Ventana
          <select value={hours} onChange={(e) => setHours(Number(e.target.value))}>
            <option value={24}>24 h</option>
            <option value={168}>7 días</option>
            <option value={720}>30 días</option>
          </select>
        </label>
        <button type="button" onClick={() => exportEventsCsv(hours)}>Exportar CSV</button>
      </div>

      <section className="kpi-grid">
        <article className="kpi-card">
          <span>Eventos recientes</span>
          <strong>{data.overview.events_recent}</strong>
        </article>
        <article className="kpi-card">
          <span>Validados</span>
          <strong>{data.overview.validated_recent}</strong>
        </article>
        <article className="kpi-card">
          <span>Tasa validación</span>
          <strong>{(data.overview.validation_rate * 100).toFixed(0)}%</strong>
        </article>
        <article className="kpi-card">
          <span>Alertas activas</span>
          <strong>{data.overview.active_alerts}</strong>
        </article>
        <article className="kpi-card">
          <span>Zonas con actividad</span>
          <strong>{data.overview.active_zones}</strong>
        </article>
      </section>

      <section className="split">
        <div>
          <h2>Mapa de focos</h2>
          <HeatmapMap zones={data.zone_comparison} />
        </div>
        <div>
          <h2>Focos críticos</h2>
          <ul className="alert-list">
            {data.critical_alerts.length === 0 && <li className="muted">Sin alertas activas</li>}
            {data.critical_alerts.map((alert) => (
              <li key={alert.id}>
                <strong>{alert.plague}</strong> · {alert.zone_name ?? `Zona ${alert.zone_id}`}
                <p>{alert.description}</p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section>
        <h2>Comparativa por zona</h2>
        <table>
          <thead>
            <tr>
              <th>Zona</th>
              <th>SIGPAC</th>
              <th>Reportes</th>
              <th>Validados</th>
              <th>Severidad máx.</th>
              <th>Intensidad</th>
            </tr>
          </thead>
          <tbody>
            {data.zone_comparison.map((zone) => (
              <tr key={zone.zone_id}>
                <td>{zone.zone_name}</td>
                <td>{zone.sigpac_code}</td>
                <td>{zone.count}</td>
                <td>{zone.validated_count}</td>
                <td>{zone.max_severity}</td>
                <td>{(zone.intensity * 100).toFixed(0)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section>
        <h2>Evolución (30 días)</h2>
        <div className="timeline">
          {data.timeline.map((point) => (
            <div key={point.date} className="timeline-bar" title={`${point.date}: ${point.count}`}>
              <div style={{ height: `${(point.count / maxTimeline) * 100}%` }} />
              <small>{point.date.slice(5)}</small>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
