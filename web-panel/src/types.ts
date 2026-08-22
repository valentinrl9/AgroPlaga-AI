export interface UserProfile {
  id: number;
  name: string;
  email: string;
  role: string;
  contribution_count: number;
}

export interface TechOverview {
  hours: number;
  events_recent: number;
  validated_recent: number;
  validation_rate: number;
  active_alerts: number;
  active_zones: number;
}

export interface ZoneCell {
  zone_id: number;
  sigpac_code: string;
  zone_name: string;
  lat: number;
  lon: number;
  count: number;
  max_severity: number;
  intensity: number;
  validated_count: number;
  pending_count?: number;
}

export interface TimelinePoint {
  date: string;
  count: number;
}

export interface CriticalAlert {
  id: number;
  zone_id: number;
  zone_name: string | null;
  plague: string;
  alert_type: string;
  description: string;
  priority_score: number | null;
  created_at: string;
}

export interface TechDashboard {
  overview: TechOverview;
  zone_comparison: ZoneCell[];
  timeline: TimelinePoint[];
  critical_alerts: CriticalAlert[];
}

export interface TechNotificationSummary {
  unread_count: number;
  pending_scans: number;
}

export interface TechNotification {
  id: number;
  scan_id: number;
  notification_type: string;
  title: string;
  body: string;
  is_read: boolean;
  created_at: string;
}

export interface OutbreakEvent {
  id: number;
  plague: string;
  severity: number;
  zone_id: number;
  zone_name: string | null;
  reported_at: string;
  model_version: string;
  validated: boolean;
}

export interface TechScanQueueItem {
  id: number;
  crop: string;
  plague: string;
  farmer_plague: string | null;
  effective_plague: string;
  confidence: number;
  severity: string;
  farm_id: number | null;
  farm_name: string | null;
  farmer_id: number;
  farmer_name: string;
  farmer_email: string;
  created_at: string;
  share_with_tech: boolean;
  tech_status: string | null;
  has_image: boolean;
}

export interface PilotFarmer {
  id: number;
  name: string;
  email: string;
  shared_scans: number;
  pending_scans: number;
  status: "inactive" | "ok" | "pending";
}

export interface ScanValidatePayload {
  action: "confirm" | "correct" | "reject";
  corrected_plague?: string;
  tech_notes?: string;
}

export interface PlagueCatalogResponse {
  version: string;
  region: string;
  labels: string[];
}

export interface SiexEntry {
  id: number;
  treatment_id: number;
  scan_id: number | null;
  tipo_actuacion: string;
  sigpac_code: string;
  farm_name: string | null;
  zone_name: string | null;
  crop: string;
  plague: string;
  product_name: string;
  registry_number: string | null;
  active_substance: string | null;
  dose_ml: number | null;
  surface_m2: number | null;
  safety_hours: number;
  applied_at: string;
  que_se_hizo: string;
  justificacion: string;
  climate_context: string | null;
  status: string;
  tech_notes: string | null;
  farmer_name: string | null;
  farmer_email: string | null;
  created_at: string;
}

export interface SiexEntryValidatePayload {
  action: "approve" | "reject";
  tech_notes?: string;
}

export interface SiexExportPreview {
  exported_at: string;
  count: number;
  entries: Record<string, unknown>[];
}

export interface TechIncident {
  id: number;
  scan_id: number;
  farm_id: number | null;
  farm_name: string | null;
  zone_id: number;
  zone_name: string | null;
  plague: string;
  crop: string;
  severity: number;
  stage: string;
  closure_outcome: string | null;
  notes: string | null;
  prescription_product_name: string | null;
  prescription_registry_number: string | null;
  prescription_dose_ml: number | null;
  prescription_safety_hours: number | null;
  prescription_surface_m2: number | null;
  farm_surface_m2: number | null;
  evaluation_scan_id: number | null;
  created_at: string;
  updated_at: string;
  closed_at: string | null;
  farmer_name: string;
  farmer_email: string;
}
