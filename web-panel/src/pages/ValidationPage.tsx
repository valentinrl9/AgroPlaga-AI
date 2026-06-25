import { useEffect, useState } from "react";
import {
  fetchPendingScans,
  fetchScanImageBlobUrl,
  validateScan,
} from "../api/client";
import type { TechScanQueueItem } from "../types";

const PLAGUE_OPTIONS = [
  "sana",
  "tuta absoluta",
  "trips",
  "mosca blanca",
  "pulgón",
  "arañuela roja",
  "minador",
  "piojo harinoso",
  "oruga",
  "mildiu",
  "oídio",
  "botritis",
  "mancha bacteriana",
  "fusarium",
  "clorosis viral",
];

export default function ValidationPage() {
  const [scans, setScans] = useState<TechScanQueueItem[]>([]);
  const [imageUrls, setImageUrls] = useState<Record<number, string>>({});
  const [error, setError] = useState("");
  const [correctPlague, setCorrectPlague] = useState<Record<number, string>>({});
  const [notes, setNotes] = useState<Record<number, string>>({});
  const [busyId, setBusyId] = useState<number | null>(null);

  function reload() {
    fetchPendingScans()
      .then(async (list) => {
        setScans(list);
        const urls: Record<number, string> = {};
        await Promise.all(
          list.map(async (scan) => {
            urls[scan.id] = await fetchScanImageBlobUrl(scan.id);
          }),
        );
        setImageUrls((prev) => {
          Object.values(prev).forEach((url) => URL.revokeObjectURL(url));
          return urls;
        });
      })
      .catch((e) => setError(String(e)));
  }

  useEffect(() => {
    reload();
    return () => {
      Object.values(imageUrls).forEach((url) => URL.revokeObjectURL(url));
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function act(scanId: number, action: "confirm" | "correct" | "reject") {
    setBusyId(scanId);
    setError("");
    try {
      await validateScan(scanId, {
        action,
        corrected_plague: action === "correct" ? correctPlague[scanId] : undefined,
        tech_notes: notes[scanId] || undefined,
      });
      reload();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusyId(null);
    }
  }

  if (error) return <p className="error">{error}</p>;

  return (
    <section>
      <h2>Validación de escaneos (perito)</h2>
      <p className="muted">
        Escaneos compartidos por agricultores con foto. El mapa comunitario sigue siendo anónimo.
      </p>
      {scans.length === 0 ? (
        <p>No hay escaneos pendientes de validar.</p>
      ) : (
        <div className="validation-grid">
          {scans.map((scan) => (
            <article key={scan.id} className="validation-card">
              <div className="validation-photo">
                {imageUrls[scan.id] ? (
                  <img src={imageUrls[scan.id]} alt={`Escaneo ${scan.id}`} />
                ) : (
                  <div className="photo-placeholder">Cargando foto…</div>
                )}
              </div>
              <div className="validation-body">
                <h3>{scan.plague}</h3>
                <p>
                  <strong>Confianza IA:</strong> {(scan.confidence * 100).toFixed(0)}%
                </p>
                <p>
                  <strong>Cultivo:</strong> {scan.crop} · <strong>Severidad:</strong> {scan.severity}
                </p>
                <p>
                  <strong>Agricultor:</strong> {scan.farmer_name} ({scan.farmer_email})
                </p>
                {scan.farm_name && (
                  <p>
                    <strong>Finca:</strong> {scan.farm_name}
                  </p>
                )}
                <p className="muted">
                  {new Date(scan.created_at).toLocaleString("es-ES")}
                </p>
                <label>
                  Notas (opcional)
                  <textarea
                    rows={2}
                    value={notes[scan.id] ?? ""}
                    onChange={(e) => setNotes({ ...notes, [scan.id]: e.target.value })}
                  />
                </label>
                <label>
                  Plaga corregida (si aplica)
                  <select
                    value={correctPlague[scan.id] ?? scan.plague}
                    onChange={(e) => setCorrectPlague({ ...correctPlague, [scan.id]: e.target.value })}
                  >
                    {PLAGUE_OPTIONS.map((p) => (
                      <option key={p} value={p}>
                        {p}
                      </option>
                    ))}
                  </select>
                </label>
                <div className="validation-actions">
                  <button
                    type="button"
                    disabled={busyId === scan.id}
                    onClick={() => act(scan.id, "confirm")}
                  >
                    Confirmar
                  </button>
                  <button
                    type="button"
                    className="secondary"
                    disabled={busyId === scan.id}
                    onClick={() => act(scan.id, "correct")}
                  >
                    Corregir
                  </button>
                  <button
                    type="button"
                    className="danger"
                    disabled={busyId === scan.id}
                    onClick={() => act(scan.id, "reject")}
                  >
                    Descartar
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
