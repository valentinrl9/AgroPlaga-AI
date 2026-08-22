import { useEffect, useState } from "react";
import {
  fetchPendingScans,
  fetchPlagueCatalog,
  fetchScanImageBlobUrl,
  markAllTechNotificationsRead,
  validateScan,
} from "../api/client";
import type { TechScanQueueItem } from "../types";

const FALLBACK_PLAGUE_LABELS = [
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

function plagueSuggestionsFor(
  scan: TechScanQueueItem,
  catalogLabels: string[],
): string[] {
  const seen = new Set<string>();
  const options: string[] = [];
  for (const raw of [...catalogLabels, scan.plague, scan.farmer_plague, scan.effective_plague]) {
    const normalized = raw?.trim().toLowerCase();
    if (!normalized || seen.has(normalized)) continue;
    seen.add(normalized);
    options.push(normalized);
  }
  return options;
}

function selectedPlague(
  scan: TechScanQueueItem,
  overrides: Record<number, string>,
): string {
  return (overrides[scan.id] ?? scan.effective_plague).trim().toLowerCase();
}

export default function ValidationPage() {
  const [scans, setScans] = useState<TechScanQueueItem[]>([]);
  const [catalogLabels, setCatalogLabels] = useState<string[]>(FALLBACK_PLAGUE_LABELS);
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
    void markAllTechNotificationsRead();
    fetchPlagueCatalog()
      .then((catalog) => setCatalogLabels(catalog.labels))
      .catch(() => {
        /* fallback local list */
      });
    return () => {
      Object.values(imageUrls).forEach((url) => URL.revokeObjectURL(url));
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function act(scanId: number, action: "confirm" | "correct" | "reject") {
    const scan = scans.find((row) => row.id === scanId);
    if (!scan) return;

    const corrected = selectedPlague(scan, correctPlague);
    if (action === "correct" && !corrected) {
      setError("Indica la plaga corregida");
      return;
    }

    setBusyId(scanId);
    setError("");
    try {
      await validateScan(scanId, {
        action,
        corrected_plague: action === "correct" ? corrected : undefined,
        tech_notes: notes[scanId]?.trim() || undefined,
      });
      reload();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusyId(null);
    }
  }

  if (error && scans.length === 0) return <p className="error">{error}</p>;

  return (
    <section>
      <h2>Validación de escaneos (perito)</h2>
      <p className="muted">
        Escaneos compartidos por agricultores con foto. El mapa comunitario sigue siendo anónimo.
      </p>
      {error && <p className="error">{error}</p>}
      {scans.length === 0 ? (
        <p>No hay escaneos pendientes de validar.</p>
      ) : (
        <div className="validation-grid">
          {scans.map((scan) => {
            const suggestions = plagueSuggestionsFor(scan, catalogLabels);
            return (
              <article key={scan.id} className="validation-card">
                <div className="validation-photo">
                  {imageUrls[scan.id] ? (
                    <img src={imageUrls[scan.id]} alt={`Escaneo ${scan.id}`} />
                  ) : (
                    <div className="photo-placeholder">Cargando foto…</div>
                  )}
                </div>
                <div className="validation-body">
                  <h3>{scan.effective_plague}</h3>
                  {scan.farmer_plague && scan.farmer_plague.toLowerCase() !== scan.plague.toLowerCase() ? (
                    <p className="validation-plague-note">
                      <strong>IA sugirió:</strong> {scan.plague} ({(scan.confidence * 100).toFixed(0)}%) ·{" "}
                      <strong>Agricultor indica:</strong> {scan.farmer_plague}
                    </p>
                  ) : (
                    <p>
                      <strong>Confianza IA:</strong> {(scan.confidence * 100).toFixed(0)}%
                    </p>
                  )}
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
                    Plaga corregida
                    <input
                      type="text"
                      list={`plague-suggestions-${scan.id}`}
                      maxLength={50}
                      value={selectedPlague(scan, correctPlague)}
                      placeholder="Escribe o elige del catálogo"
                      onChange={(e) =>
                        setCorrectPlague({
                          ...correctPlague,
                          [scan.id]: e.target.value.trim().toLowerCase(),
                        })
                      }
                    />
                    <datalist id={`plague-suggestions-${scan.id}`}>
                      {suggestions.map((p) => (
                        <option key={p} value={p} />
                      ))}
                    </datalist>
                    <span className="muted validation-field-hint">
                      Catálogo ({catalogLabels.length} sugeridas) u otra plaga libre (máx. 50 caracteres).
                    </span>
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
            );
          })}
        </div>
      )}
    </section>
  );
}
