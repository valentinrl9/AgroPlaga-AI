import { useEffect, useState } from "react";
import { fetchPendingEvents, validateEvent } from "../api/client";
import type { OutbreakEvent } from "../types";

export default function ValidationPage() {
  const [events, setEvents] = useState<OutbreakEvent[]>([]);
  const [error, setError] = useState("");

  function reload() {
    fetchPendingEvents()
      .then((list) => setEvents(list.filter((e) => !e.validated)))
      .catch((e) => setError(String(e)));
  }

  useEffect(() => {
    reload();
  }, []);

  async function approve(id: number) {
    await validateEvent(id, true);
    reload();
  }

  if (error) return <p className="error">{error}</p>;

  return (
    <section>
      <h2>Validación de eventos colaborativos</h2>
      <p className="muted">Vista agregada por municipio SIGPAC — sin datos de parcela.</p>
      {events.length === 0 ? (
        <p>No hay eventos pendientes.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Zona</th>
              <th>Plaga</th>
              <th>Severidad</th>
              <th>Modelo</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {events.map((event) => (
              <tr key={event.id}>
                <td>{new Date(event.reported_at).toLocaleString("es-ES")}</td>
                <td>{event.zone_name ?? event.zone_id}</td>
                <td>{event.plague}</td>
                <td>{event.severity}</td>
                <td>{event.model_version}</td>
                <td>
                  <button type="button" onClick={() => approve(event.id)}>Validar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
