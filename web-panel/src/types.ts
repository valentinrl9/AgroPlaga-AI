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
