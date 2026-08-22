import { useEffect, useState } from "react";
import { fetchTechIncidents } from "../api/client";
import type { TechIncident } from "../types";

const STAGE_LABEL: Record<string, string> = {
  detection: "Detección",
  diagnosis: "Diagnóstico",
  prescription: "Prescripción",
  treatment: "Tratamiento",
  evaluation: "Evaluación",
  closed: "Cierre",
};

const SEVERITY_LABEL: Record<number, string> = {
  1: "Leve",
  2: "Moderado",
  3: "Alto",
};

function formatDate(value: string | null): string {
  if (!value) return "—";
  return new Date(value).toLocaleString("es-ES");
}

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<TechIncident[]>([]);
  const [activeOnly, setActiveOnly] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchTechIncidents(activeOnly)
      .then(setIncidents)
      .catch((e) => setError(String(e)));
  }, [activeOnly]);

  if (error) return <p className="error">{error}</p>;

  return (
    <section>
      <h2>Incidencias activas (CRM)</h2>
      <p className="muted">
        Seguimiento de solo lectura del ciclo fitosanitario que gestionan los agricultores en la app.
        Al cerrarse, desaparecen del mapa comunitario.
      </p>
      <label className="incidents-filter">
        <input
          type="checkbox"
          checked={activeOnly}
          onChange={(e) => setActiveOnly(e.target.checked)}
        />
        {" "}Solo incidencias abiertas
      </label>
      {incidents.length === 0 ? (
        <p>No hay incidencias {activeOnly ? "activas" : "registradas"}.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Etapa</th>
              <th>Agricultor</th>
              <th>Finca / municipio</th>
              <th>Plaga · cultivo</th>
              <th>Severidad</th>
              <th>Prescripción / tratamiento</th>
              <th>Actualizada</th>
            </tr>
          </thead>
          <tbody>
            {incidents.map((incident) => (
              <tr key={incident.id}>
                <td>{STAGE_LABEL[incident.stage] ?? incident.stage}</td>
                <td>
                  {incident.farmer_name}
                  <br />
                  <span className="muted">{incident.farmer_email}</span>
                </td>
                <td>
                  {incident.farm_name ?? "—"}
                  <br />
                  <span className="muted">{incident.zone_name ?? "—"}</span>
                </td>
                <td>
                  {incident.plague} · {incident.crop}
                </td>
                <td>{SEVERITY_LABEL[incident.severity] ?? incident.severity}</td>
                <td>
                  {incident.prescription_product_name ?? "—"}
                  {incident.prescription_dose_ml != null && (
                    <>
                      <br />
                      <span className="muted">
                        {incident.prescription_dose_ml.toFixed(0)} ml ·{" "}
                        {incident.prescription_surface_m2?.toFixed(0) ?? "—"} m²
                      </span>
                    </>
                  )}
                </td>
                <td>{formatDate(incident.updated_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
