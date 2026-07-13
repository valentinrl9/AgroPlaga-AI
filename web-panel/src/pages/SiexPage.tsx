import { useEffect, useState } from "react";
import {
  fetchPendingSiexEntries,
  fetchSiexExportPreview,
  validateSiexEntry,
} from "../api/client";
import type { SiexEntry, SiexExportPreview } from "../types";

export default function SiexPage() {
  const [entries, setEntries] = useState<SiexEntry[]>([]);
  const [exportPreview, setExportPreview] = useState<SiexExportPreview | null>(null);
  const [notes, setNotes] = useState<Record<number, string>>({});
  const [error, setError] = useState("");
  const [busyId, setBusyId] = useState<number | null>(null);
  const [loadingExport, setLoadingExport] = useState(false);

  function reload() {
    fetchPendingSiexEntries()
      .then(setEntries)
      .catch((e) => setError(String(e)));
  }

  useEffect(() => {
    reload();
  }, []);

  async function act(entryId: number, action: "approve" | "reject") {
    setBusyId(entryId);
    setError("");
    try {
      await validateSiexEntry(entryId, {
        action,
        tech_notes: notes[entryId] || undefined,
      });
      reload();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusyId(null);
    }
  }

  async function loadExport() {
    setLoadingExport(true);
    setError("");
    try {
      const data = await fetchSiexExportPreview();
      setExportPreview(data);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoadingExport(false);
    }
  }

  function downloadExport() {
    if (!exportPreview) return;
    const blob = new Blob([JSON.stringify(exportPreview, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `siex_export_${new Date().toISOString().slice(0, 10)}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <section>
      <h2>Cuaderno SIEX — validación perito</h2>
      <p className="muted">
        Actuaciones fitosanitarias generadas desde Field con SIGPAC. Aprueba o rechaza antes del
        export ministerial.
      </p>

      {error && <p className="error">{error}</p>}

      <div className="siex-toolbar">
        <button type="button" className="secondary" onClick={reload}>
          Actualizar cola
        </button>
        <button type="button" disabled={loadingExport} onClick={loadExport}>
          {loadingExport ? "Cargando export…" : "Vista previa export JSON"}
        </button>
        {exportPreview && (
          <button type="button" className="secondary" onClick={downloadExport}>
            Descargar JSON ({exportPreview.count} validadas)
          </button>
        )}
      </div>

      {exportPreview && (
        <details className="siex-export-preview">
          <summary>
            Export validado — {exportPreview.count} entradas ·{" "}
            {new Date(exportPreview.exported_at).toLocaleString("es-ES")}
          </summary>
          <pre>{JSON.stringify(exportPreview.entries, null, 2)}</pre>
        </details>
      )}

      {entries.length === 0 ? (
        <p>No hay entradas SIEX pendientes de validar.</p>
      ) : (
        <div className="validation-grid">
          {entries.map((entry) => (
            <article key={entry.id} className="validation-card">
              <div className="validation-body">
                <h3>{entry.product_name}</h3>
                <p>
                  <strong>Agricultor:</strong> {entry.farmer_name} ({entry.farmer_email})
                </p>
                <p>
                  <strong>SIGPAC:</strong> {entry.sigpac_code}
                  {entry.farm_name && <> · <strong>Finca:</strong> {entry.farm_name}</>}
                </p>
                <p>
                  <strong>Cultivo:</strong> {entry.crop} · <strong>Plaga:</strong> {entry.plague}
                </p>
                <p>
                  <strong>MAPA:</strong> {entry.registry_number ?? "—"} ·{" "}
                  <strong>Dosis:</strong> {entry.dose_ml ?? "—"} ml ·{" "}
                  <strong>Carencia:</strong> {entry.safety_hours} h
                </p>
                <p className="muted">
                  Aplicado: {new Date(entry.applied_at).toLocaleString("es-ES")}
                </p>
                <div className="siex-text-block">
                  <strong>Qué se hizo</strong>
                  <p>{entry.que_se_hizo}</p>
                </div>
                <div className="siex-text-block">
                  <strong>Justificación</strong>
                  <p>{entry.justificacion}</p>
                </div>
                {entry.climate_context && (
                  <div className="siex-text-block">
                    <strong>Contexto Climate</strong>
                    <p>{entry.climate_context}</p>
                  </div>
                )}
                <label>
                  Notas perito (opcional)
                  <textarea
                    rows={2}
                    value={notes[entry.id] ?? ""}
                    onChange={(e) => setNotes({ ...notes, [entry.id]: e.target.value })}
                  />
                </label>
                <div className="validation-actions">
                  <button
                    type="button"
                    disabled={busyId === entry.id}
                    onClick={() => act(entry.id, "approve")}
                  >
                    Validar
                  </button>
                  <button
                    type="button"
                    className="danger"
                    disabled={busyId === entry.id}
                    onClick={() => act(entry.id, "reject")}
                  >
                    Rechazar
                  </button>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
