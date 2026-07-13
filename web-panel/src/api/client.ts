import type { OutbreakEvent, PilotFarmer, ScanValidatePayload, SiexEntry, SiexEntryValidatePayload, SiexExportPreview, TechDashboard, TechScanQueueItem, UserProfile } from "../types";

const TOKEN_KEY = "agroplaga_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(path, { ...init, headers });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export async function login(email: string, password: string): Promise<void> {
  const body = new URLSearchParams({ username: email, password });
  const response = await fetch("/api/v1/auth/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!response.ok) throw new Error("Credenciales inválidas");
  const data = (await response.json()) as { access_token: string };
  setToken(data.access_token);
}

export function fetchProfile(): Promise<UserProfile> {
  return request<UserProfile>("/api/v1/users/me");
}

export function fetchDashboard(hours = 168): Promise<TechDashboard> {
  return request<TechDashboard>(`/api/v1/tech/dashboard?hours=${hours}`);
}

export function fetchPendingEvents(): Promise<OutbreakEvent[]> {
  return request<OutbreakEvent[]>("/api/v1/outbreak-events?hours=168");
}

export function fetchPendingScans(): Promise<TechScanQueueItem[]> {
  return request<TechScanQueueItem[]>("/api/v1/tech/pending-scans");
}

export function fetchPilotFarmers(): Promise<PilotFarmer[]> {
  return request<PilotFarmer[]>("/api/v1/tech/farmers");
}

export function validateScan(scanId: number, payload: ScanValidatePayload): Promise<void> {
  return request(`/api/v1/scans/${scanId}/validate`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function fetchScanImageBlobUrl(scanId: number): Promise<string> {
  const token = getToken();
  const response = await fetch(`/api/v1/scans/${scanId}/image`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!response.ok) throw new Error("No se pudo cargar la imagen");
  const blob = await response.blob();
  return URL.createObjectURL(blob);
}

export function validateEvent(eventId: number, validated: boolean): Promise<OutbreakEvent> {
  return request<OutbreakEvent>(`/api/v1/outbreak-events/${eventId}/validate`, {
    method: "PATCH",
    body: JSON.stringify({ validated }),
  });
}

export function exportEventsCsv(hours = 720): void {
  const token = getToken();
  const url = `/api/v1/tech/export/events.csv?hours=${hours}`;
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", "eventos_agroplaga.csv");
  if (token) {
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.blob())
      .then((blob) => {
        link.href = URL.createObjectURL(blob);
        link.click();
      });
    return;
  }
  link.click();
}

export function fetchPendingSiexEntries(): Promise<SiexEntry[]> {
  return request<SiexEntry[]>("/api/v1/siex/entries/pending");
}

export function validateSiexEntry(entryId: number, payload: SiexEntryValidatePayload): Promise<SiexEntry> {
  return request<SiexEntry>(`/api/v1/siex/entries/${entryId}/validate`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function fetchSiexExportPreview(): Promise<SiexExportPreview> {
  return request<SiexExportPreview>("/api/v1/siex/entries/export");
}
