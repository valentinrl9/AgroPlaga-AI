import { Circle, MapContainer, TileLayer } from "react-leaflet";
import type { ZoneCell } from "../types";

function severityColor(maxSeverity: number): string {
  if (maxSeverity >= 3) return "#c62828";
  if (maxSeverity >= 2) return "#f9a825";
  return "#2e7d32";
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
            pathOptions={{
              color: severityColor(zone.max_severity),
              fillColor: severityColor(zone.max_severity),
              fillOpacity: 0.25 + zone.intensity * 0.35,
            }}
          />
        ))}
      </MapContainer>
    </div>
  );
}
