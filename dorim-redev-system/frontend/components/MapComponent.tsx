"use client";
import { useEffect, useState } from "react";
import { Box, Typography } from "@mui/material";

interface Marker {
  member_id: number;
  address: string;
  lat: number;
  lng: number;
  consent: boolean;
  color: string;
}

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function MapComponent() {
  const [markers, setMarkers] = useState<Marker[]>([]);
  const [MapReady, setMapReady] = useState(false);

  useEffect(() => {
    // Fetch markers
    fetch(`${BASE_URL}/api/gis/markers`)
      .then((r) => r.json())
      .then((json) => setMarkers(json.data ?? []));

    // Mark as ready for dynamic import
    setMapReady(true);
  }, []);

  if (!MapReady) {
    return (
      <Box sx={{ height: 300, display: "flex", alignItems: "center",
                 justifyContent: "center", bgcolor: "#1e293b", borderRadius: 2 }}>
        <Typography sx={{ color: "#94a3b8" }}>지도 로딩 중...</Typography>
      </Box>
    );
  }

  return (
    <DynamicMap markers={markers} />
  );
}

// Separate component for the actual Leaflet map (prevents SSR issues)
import dynamic from "next/dynamic";

const DynamicMap = dynamic(
  () => import("./LeafletMap"),
  {
    ssr: false,
    loading: () => (
      <Box sx={{ height: 300, display: "flex", alignItems: "center",
                 justifyContent: "center", bgcolor: "#1e293b", borderRadius: 2 }}>
        <Typography sx={{ color: "#94a3b8" }}>지도 초기화 중...</Typography>
      </Box>
    )
  }
);
