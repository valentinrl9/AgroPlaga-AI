import { useEffect, useState } from "react";
import { fetchPilotFarmers } from "../api/client";
import type { PilotFarmer } from "../types";

const STATUS_LABEL: Record<PilotFarmer["status"], string> = {
  inactive: "Sin escaneos compartidos",
  ok: "Al día",
  pending: "Pendientes de validar",
};

export default function FarmersPage() {
  const [farmers, setFarmers] = useState<PilotFarmer[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchPilotFarmers()
      .then(setFarmers)
      .catch((e) => setError(String(e)));
  }, []);

  if (error) return <p className="error">{error}</p>;

  return (
    <section>
      <h2>Agricultores del piloto</h2>
      <p className="muted">Semáforo según escaneos compartidos con el técnico.</p>
      <table>
        <thead>
          <tr>
            <th>Estado</th>
            <th>Nombre</th>
            <th>Email</th>
            <th>Compartidos</th>
            <th>Pendientes</th>
          </tr>
        </thead>
        <tbody>
          {farmers.map((farmer) => (
            <tr key={farmer.id}>
              <td>
                <span className={`status-dot status-${farmer.status}`} />
                {STATUS_LABEL[farmer.status]}
              </td>
              <td>{farmer.name}</td>
              <td>{farmer.email}</td>
              <td>{farmer.shared_scans}</td>
              <td>{farmer.pending_scans}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
