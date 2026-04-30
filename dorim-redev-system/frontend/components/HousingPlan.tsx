"use client";
/**
 * HousingPlan — 형별 세대수 계획 테이블 + 분양신청 현황
 * 출처: 도림 역세권 시프트 재개발 정비사업 정비계획 수립(안) 2023.6
 */
import { useEffect, useState } from "react";
import {
  Box, Typography, Chip, CircularProgress,
  Table, TableBody, TableCell, TableHead, TableRow,
  LinearProgress, Divider,
} from "@mui/material";

interface UnitType {
  type: string;
  area_sqm: number;
  lease_units: number;
  total_units: number;
}

interface HousingData {
  total_units: number;
  long_term_lease_units: number;
  redev_rental_units: number;
  total_rental_units: number;
  general_sale_units: number;
  unit_types: UnitType[];
}

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const TYPE_COLORS: Record<string, string> = {
  "39형": "#818cf8",
  "49형": "#38bdf8",
  "59형": "#34d399",
  "74형": "#fbbf24",
  "84형": "#f97316",
  "101형": "#f87171",
};

export default function HousingPlan() {
  const [data, setData] = useState<HousingData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${BASE_URL}/api/project/housing-plan`)
      .then((r) => r.json())
      .then((j) => setData(j.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", p: 3 }}>
        <CircularProgress size={32} />
      </Box>
    );
  }

  if (!data) return null;

  return (
    <Box sx={{ bgcolor: "#1e293b", borderRadius: 2, p: 2 }}>
      {/* 헤더 */}
      <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
        <Typography sx={{ fontSize: "17px", fontWeight: 700 }}>
          🏠 세대수 공급 계획
        </Typography>
        <Chip
          label="정비계획(안) 기준"
          size="small"
          sx={{ bgcolor: "#166534", color: "#fff", fontSize: "11px" }}
        />
      </Box>

      {/* 요약 카드 */}
      <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: 1, mb: 2 }}>
        <SummaryCard label="전체 세대" value={data.total_units} color="#60a5fa" unit="세대" />
        <SummaryCard label="장기전세" value={data.long_term_lease_units} color="#a78bfa" unit="세대" />
        <SummaryCard label="재개발임대" value={data.redev_rental_units} color="#f97316" unit="세대" />
        <SummaryCard label="총 임대" value={data.total_rental_units} color="#22c55e" unit="세대" />
      </Box>

      <Divider sx={{ borderColor: "#334155", mb: 2 }} />

      {/* 형별 분양 계획 테이블 */}
      <Typography sx={{ fontSize: "14px", fontWeight: 600, color: "#94a3b8", mb: 1 }}>
        형별 공급 계획
      </Typography>

      <Box sx={{ overflowX: "auto" }}>
        <Table size="small">
          <TableHead>
            <TableRow sx={{ "& th": { bgcolor: "#0f172a", color: "#64748b", fontSize: "12px", fontWeight: 600, border: "none", py: 1 } }}>
              <TableCell>형</TableCell>
              <TableCell align="right">공급면적(㎡)</TableCell>
              <TableCell align="right">장기전세</TableCell>
              <TableCell align="right">전체 세대</TableCell>
              <TableCell align="right">비율</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data.unit_types.map((ut) => {
              const pct = Math.round((ut.total_units / data.total_units) * 100);
              const color = TYPE_COLORS[ut.type] ?? "#94a3b8";
              return (
                <TableRow
                  key={ut.type}
                  sx={{
                    "& td": { borderColor: "#1e293b", py: 0.8 },
                    "&:hover": { bgcolor: "#1e3a5f22" },
                  }}
                >
                  <TableCell>
                    <Chip
                      label={ut.type}
                      size="small"
                      sx={{ bgcolor: `${color}22`, color, fontSize: "12px", fontWeight: 700 }}
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Typography sx={{ fontSize: "13px", color: "#94a3b8" }}>
                      {ut.area_sqm.toFixed(3)}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography sx={{ fontSize: "13px", color: ut.lease_units > 0 ? "#a78bfa" : "#475569" }}>
                      {ut.lease_units > 0 ? `${ut.lease_units}세대` : "-"}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography sx={{ fontSize: "14px", fontWeight: 700, color }}>
                      {ut.total_units}세대
                    </Typography>
                  </TableCell>
                  <TableCell align="right" sx={{ minWidth: 80 }}>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 0.5, justifyContent: "flex-end" }}>
                      <Typography sx={{ fontSize: "11px", color: "#64748b" }}>
                        {pct}%
                      </Typography>
                      <Box sx={{ width: 40 }}>
                        <LinearProgress
                          variant="determinate"
                          value={pct}
                          sx={{
                            height: 4,
                            borderRadius: 2,
                            bgcolor: "#0f172a",
                            "& .MuiLinearProgress-bar": { bgcolor: color, borderRadius: 2 },
                          }}
                        />
                      </Box>
                    </Box>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </Box>

      {/* 주석 */}
      <Box sx={{
        bgcolor: "#0f172a", borderRadius: 1, p: 1, mt: 2,
        border: "1px solid #1e3a5f",
      }}>
        <Typography sx={{ fontSize: "12px", color: "#64748b" }}>
          ※ 장기전세 세대수는 시프트 공급분(용적률 증가분의 ½ 이상)이며,
          전체 세대수는 기준용적률(204.87%) 기준 계획 수치입니다.
          실제 착공 시 변경 가능.
        </Typography>
      </Box>
    </Box>
  );
}

function SummaryCard({
  label, value, color, unit,
}: { label: string; value: number; color: string; unit: string }) {
  return (
    <Box sx={{
      bgcolor: "#0f172a", p: 1.5, borderRadius: 1,
      border: `1px solid ${color}33`, textAlign: "center",
    }}>
      <Typography sx={{ fontSize: "22px", fontWeight: 700, color }}>
        {value.toLocaleString()}
      </Typography>
      <Typography sx={{ fontSize: "11px", color: "#94a3b8" }}>
        {label}<br />{unit}
      </Typography>
    </Box>
  );
}
