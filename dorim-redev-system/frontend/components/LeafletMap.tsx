"use client";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { Box } from "@mui/material";

interface Marker {
  member_id: number;
  address: string;
  lat: number;
  lng: number;
  consent: boolean;
  color: string;
}

interface Props {
  markers: Marker[];
}

export default function LeafletMap({ markers }: Props) {
  return (
    <Box sx={{ height: 300, borderRadius: 2, overflow: "hidden" }}>
      <MapContainer
        center={[37.5134, 126.8986]}
        zoom={17}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {markers.map((m) => (
          <CircleMarker
            key={m.member_id}
            center={[m.lat, m.lng]}
            radius={2}
            pathOptions={{ color: m.color, fillColor: m.color, fillOpacity: 0.8 }}
          >
            <Popup>
              <strong>조합원 {m.member_id}</strong><br />
              {m.address}<br />
              동의여부: {m.consent ? "✅ 동의" : "❌ 미동의"}
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </Box>
  );
}
