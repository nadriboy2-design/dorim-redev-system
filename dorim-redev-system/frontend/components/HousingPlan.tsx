"use client";
/**
 * HousingPlan — 형별 세대수 계획 테이블 (임대/분양 구분)
 * 최신 건축계획 기준: 전체 1,640세대 (임대 514 + 분양 1,126)
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
  rental_units: number;
  sale_units: number;
  total_units: number;
  ratio_pct: number;
  // legacy fields
  lease_units?: number;
}

interface HousingData {
  total_units: number;
  rental_units: number;
  sale_units: number;
  total_rental_units: number;
  general_sale_units: number;
  unit_types: UnitType[];
}

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const TYPE_COLORS: Record<string, string> = {
  "39형":  "#818cf8",
  "49형":  "#38bdf8",
  "59형":  "#34d399",
  "74형":  "#fbbf24",
  "84형":  "#f97316",
  "103형": "#f87171",
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

  const rentalUnits = data.rental_units ?? data.total_rental_units ?? 514;
  const saleUnits   = data.sale_units   ?? data.general_sale_units ?? 1126;
  const total       = data.total_units ?? 1640;
  const rentalRatio = Math.round((rentalUnits / total) * 100);

  return (
    <Box sx={{ bgcolor: "#1e293b", borderRadius: 2, p: 2 }}>
      {/* 헤더 */}
      <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
        <Typography sx={{ fontSize: "17px", fontWeight: 700 }}>
          🏠 세대수 공급 계획
        </Typography>
        <Chip
          label="최신 건축계획 기준"
          size="small"
          sx={{ bgcolor: "#1d4ed8", color: "#fff", fontSize: "11px" }}
        />
      </Box>

      {/* 요약 카드 */}
      <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 1, mb: 2 }}>
        <Box sx={{ bgcolor: "#0f172a", p: 1.5, borderRadius: 1, border: "1px solid #60a5fa33", textAlign: "center" }}>
          <Typography sx={{ fontSize: "26px", fontWeight: 700, color: "#60a5fa" }}>
            {total.toLocaleString()}
          </Typography>
          <Typography sx={{ fontSize: "12px", color: "#94a3b8" }}>전체 세대</Typography>
        </Box>
        <Box sx={{ bgcolor: "#0f172a", p: 1.5, borderRadius: 1, border: "1px solid #a78bfa33", textAlign: "center" }}>
          <Typography sx={{ fontSize: "26px", fontWeight: 700, color: "#a78bfa" }}>
            {rentalUnits.toLocaleString()}
          </Typography>
          <Typography sx={{ fontSize: "12px", color: "#94a3b8" }}>임대</Typography>
          <Typography sx={{ fontSize: "11px", color: "#475569" }}>{rentalRatio}%</Typography>
        </Box>
        <Box sx={{ bgcolor: "#0f172a", p: 1.5, borderRadius: 1, border: "1px solid #22c55e33", textAlign: "center" }}>
          <Typography sx={{ fontSize: "26px", fontWeight: 700, color: "#22c55e" }}>
            {saleUnits.toLocaleString()}
          </Typography>
          <Typography sx={{ fontSize: "12px", color: "#94a3b8" }}>분양</Typography>
          <Typography sx={{ fontSize: "11px", color: "#475569" }}>{100 - rentalRatio}%</Typography>
        </Box>
      </Box>

      {/* 임대/분양 비율 게이지 */}
      <Box sx={{ mb: 2 }}>
        <Box sx={{ display: "flex", mb: 0.5 }}>
          <Box sx={{ flex: rentalUnits, bgcolor: "#a78bfa", height: 10, borderRadius: "4px 0 0 4px" }} />
          <Box sx={{ flex: saleUnits, bgcolor: "#22c55e", height: 10, borderRadius: "0 4px 4px 0" }} />
        </Box>
        <Box sx={{ display: "flex", justifyContent: "space-between" }}>
          <Typography sx={{ fontSize: "11px", color: "#a78bfa" }}>임대 {rentalUnits}세대</Typography>
          <Typography sx={{ fontSize: "11px", color: "#22c55e" }}>분양 {saleUnits}세대</Typography>
        </Box>
      </Box>

      <Divider sx={{ borderColor: "#334155", mb: 2 }} />

      {/* 형별 분양 계획 테이블 */}
      <Typography sx={{ fontSize: "14px", fontWeight: 600, color: "#94a3b8", mb: 1 }}>
        형별 세대수 현황
      </Typography>

      <Box sx={{ overflowX: "auto" }}>
        <Table size="small">
          <TableHead>
            <TableRow sx={{ "& th": { bgcolor: "#0f172a", color: "#64748b", fontSize: "12px", fontWeight: 600, border: "none", py: 1 } }}>
              <TableCell>TYPE</TableCell>
              <TableCell align="right">전용(㎡)</TableCell>
              <TableCell align="right" sx={{ color: "#a78bfa !important" }}>임대</TableCell>
              <TableCell align="right" sx={{ color: "#22c55e !important" }}>분양</TableCell>
              <TableCell align="right">소계</TableCell>
              <TableCell align="right">비율</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data.unit_types.map((ut) => {
              const color = TYPE_COLORS[ut.type] ?? "#94a3b8";
              const rentalU = ut.rental_units ?? ut.lease_units ?? 0;
              const saleU   = ut.sale_units ?? 0;
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
                    <Typography sx={{ fontSize: "12px", color: "#94a3b8" }}>
                      {ut.area_sqm.toFixed(1)}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography sx={{ fontSize: "13px", color: rentalU > 0 ? "#a78bfa" : "#475569" }}>
                      {rentalU > 0 ? rentalU : "-"}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography sx={{ fontSize: "13px", color: saleU > 0 ? "#22c55e" : "#475569" }}>
                      {saleU > 0 ? saleU : "-"}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography sx={{ fontSize: "14px", fontWeight: 700, color }}>
                      {ut.total_units}
                    </Typography>
                  </TableCell>
                  <TableCell align="right" sx={{ minWidth: 80 }}>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 0.5, justifyContent: "flex-end" }}>
                      <Typography sx={{ fontSize: "11px", color: "#64748b" }}>
                        {ut.ratio_pct}%
                      </Typography>
                      <Box sx={{ width: 40 }}>
                        <LinearProgress
                          variant="determinate"
                          value={ut.ratio_pct}
                          sx={{
                            height: 4, borderRadius: 2, bgcolor: "#0f172a",
                            "& .MuiLinearProgress-bar": { bgcolor: color, borderRadius: 2 },
                          }}
                        />
                      </Box>
                    </Box>
                  </TableCell>
                </TableRow>
              );
            })}

            {/* 합계 행 */}
            <TableRow sx={{ "& td": { borderTop: "1px solid #334155", pt: 1 } }}>
              <TableCell>
                <Typography sx={{ fontSize: "13px", fontWeight: 700, color: "#e2e8f0" }}>합 계</Typography>
              </TableCell>
              <TableCell />
              <TableCell align="right">
                <Typography sx={{ fontSize: "13px", fontWeight: 700, color: "#a78bfa" }}>{rentalUnits}</Typography>
              </TableCell>
              <TableCell align="right">
                <Typography sx={{ fontSize: "13px", fontWeight: 700, color: "#22c55e" }}>{saleUnits}</Typography>
              </TableCell>
              <TableCell align="right">
                <Typography sx={{ fontSize: "15px", fontWeight: 700, color: "#60a5fa" }}>{total.toLocaleString()}</Typography>
              </TableCell>
              <TableCell align="right">
                <Typography sx={{ fontSize: "13px", fontWeight: 700, color: "#94a3b8" }}>100%</Typography>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </Box>

      <Box sx={{ bgcolor: "#0f172a", borderRadius: 1, p: 1, mt: 2, border: "1px solid #1e3a5f" }}>
        <Typography sx={{ fontSize: "12px", color: "#64748b" }}>
          ※ 임대: 장기전세주택 + 재개발공공임대주택 합산 / 분양: 일반분양 세대수
          (최신 건축계획 기준, 정비계획 확정 후 변경 가능)
        </Typography>
      </Box>
    </Box>
  );
}
