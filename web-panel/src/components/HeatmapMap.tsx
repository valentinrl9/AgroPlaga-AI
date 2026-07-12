import { Circle, MapContainer, TileLayer } from "react-leaflet";
import type { ZoneCell } from "../types";

function severityColor(maxSeverity: number): string {
  if (maxSeverity >= 3) return "#c62828";
  if (maxSeverity >= 2) return "#f9a825";
  return "#2e7d32";
}

function zoneStyle(zone: ZoneCell) {
  const pending = zone.pending_count ?? 0;
  const validated = zone.validated_count ?? 0;
  const pendingOnly = pending > 0 && validated === 0;
  const validatedOnly = validated > 0 && pending === 0;

  return {
    color: pendingOnly ? "#ffb200" : validatedOnly ? "#00a86b" : severityColor(zone.max_severity),
    fillColor: pendingOnly ? "#ffb200" : severityColor(zone.max_severity),
    fillOpacity: pendingOnly ? 0.18 + zone.intensity * 0.18 : 0.25 + zone.intensity * 0.35,
    weight: validatedOnly ? 3 : pendingOnly ? 2 : 1,
    dashArray: pendingOnly ? "6 4" : undefined,
  };
}

export default function HeatmapMap({ zones }: { zones: ZoneCell[] }) {
  const center = zones.length
    ? { lat: zones[0].lat, lng: zones[0].lon }
    : { lat: 36.77, lng: -2.78 };

  return (
    <div className="map-panel">
      <MapContainer center={center} zoom={10} scrollWheelZoom className="map-container">
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {zones.map((zone) => (
          <Circle
            key={zone.zone_id}
            center={[zone.lat, zone.lon]}
            radius={800 + zone.intensity * 2000}
            pathOptions={zoneStyle(zone)}
          />
        ))}
      </MapContainer>
    </div>
  );
}
