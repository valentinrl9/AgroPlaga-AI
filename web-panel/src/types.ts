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
