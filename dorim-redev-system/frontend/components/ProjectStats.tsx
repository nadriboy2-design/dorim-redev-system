"use client";
/**
 * ProjectStats — 사업 핵심 지표 카드 (PDF 정비계획 수립안 2023.6 기준)
 * 도림2동 역세권 장기전세주택사업 핵심 수치 시각화
 */
import { useEffect, useState } from "react";
import {
  Box, Typography, Chip, CircularProgress, Divider,
  LinearProgress, Tooltip,
} from "@mui/material";

interface FarInfo {
  base_far_pct: number;
  base_far_after_donation_pct: number;
  legal_max_far_pct: number;
  planned_far_pct: number;
  far_increase_pct: number;
  public_rental_ratio_pct: number;
  far_formula: string;
}

interface HousingInfo {
  total_units: number;
  long_term_lease_units: number;
  redev_rental_units: number;
  total_rental_units: number;
  general_sale_units: number;
  unit_types: Array<{
    type: string;
    area_sqm: number;
    lease_units: number;
    total_units: number;
  }>;
}

interface ProjectInfo {
  project_name: string;
  zone: string;
  area_sqm: number;
  land_area_sqm: number;
  lot_area_sqm: number;
  station_zone_1_m: number;
  station_zone_2_m: number;
  far: FarInfo;
  housing_plan: HousingInfo;
}

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function ProjectStats() {
  const [info, setInfo] = useState<ProjectInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${BASE_URL}/api/project/info`)
      .then((r) => r.json())
      .then((j) => setInfo(j.data))
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

  if (!info) return null;

  const farProgress = (info.far.planned_far_pct / info.far.legal_max_far_pct) * 100;
  const rentalRatio = Math.round((info.housing_plan.total_rental_units / info.housing_plan.total_units) * 100);

  return (
    <Box sx={{ bgcolor: "#1e293b", borderRadius: 2, p: 2 }}>
      {/* 헤더 */}
      <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
        <Typography sx={{ fontSize: "17px", fontWeight: 700 }}>
          📐 사업 기본 계획 지표
        </Typography>
        <Chip
          label="2023.6 정비계획(안)"
          size="small"
          sx={{ bgcolor: "#1d4ed8", color: "#fff", fontSize: "11px" }}
        />
      </Box>

      {/* 구역 정보 */}
      <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 1, mb: 2 }}>
        <StatCard label="사업구역 면적" value={`${info.land_area_sqm.toLocaleString()}㎡`} color="#60a5fa" />
        <StatCard label="획지 면적" value={`${info.lot_area_sqm.toLocaleString()}㎡`} color="#94a3b8" />
        <StatCard label="1차 역세권" value={`반경 ${info.station_zone_1_m}m`} color="#f59e0b" />
      </Box>

      <Divider sx={{ borderColor: "#334155", mb: 2 }} />

      {/* 용적률 계획 */}
      <Typography sx={{ fontSize: "14px", fontWeight: 600, color: "#94a3b8", mb: 1 }}>
        용적률 계획
      </Typography>
      <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 1, mb: 1.5 }}>
        <FarRow label="기준용적률" value={`${info.far.base_far_pct}%`} sub="가중평균" color="#94a3b8" />
        <FarRow label="공공기여 후" value={`${info.far.base_far_after_donation_pct}%`} sub="순부담 0.86%" color="#60a5fa" />
        <FarRow label="법적상한용적률" value={`${info.far.legal_max_far_pct}%`} sub="가중평균 상한" color="#f59e0b" />
        <FarRow label="계획 용적률" value={`${info.far.planned_far_pct}%`} sub="최종 계획" color="#22c55e" />
      </Box>

      {/* 용적률 게이지 */}
      <Tooltip title={`계획 ${info.far.planned_far_pct}% / 법적상한 ${info.far.legal_max_far_pct}%`}>
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: "flex", justifyContent: "space-between", mb: 0.5 }}>
            <Typography sx={{ fontSize: "12px", color: "#64748b" }}>계획 용적률 달성도</Typography>
            <Typography sx={{ fontSize: "12px", color: "#22c55e" }}>
              {farProgress.toFixed(1)}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={Math.min(farProgress, 100)}
            sx={{
              height: 8,
              borderRadius: 4,
              bgcolor: "#0f172a",
              "& .MuiLinearProgress-bar": { bgcolor: "#22c55e", borderRadius: 4 },
            }}
          />
          <Box sx={{ display: "flex", justifyContent: "space-between", mt: 0.5 }}>
            <Typography sx={{ fontSize: "11px", color: "#475569" }}>0%</Typography>
            <Typography sx={{ fontSize: "11px", color: "#475569" }}>
              상한 {info.far.legal_max_far_pct}%
            </Typography>
          </Box>
        </Box>
      </Tooltip>

      <Divider sx={{ borderColor: "#334155", mb: 2 }} />

      {/* 세대수 계획 */}
      <Typography sx={{ fontSize: "14px", fontWeight: 600, color: "#94a3b8", mb: 1 }}>
        세대수 계획
      </Typography>
      <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 1, mb: 1.5 }}>
        <StatCard label="전체 세대" value={`${info.housing_plan.total_units.toLocaleString()}세대`} color="#60a5fa" />
        <StatCard
          label="장기전세"
          value={`${info.housing_plan.long_term_lease_units}세대`}
          color="#a78bfa"
          sub={`용적률 증가분 ${info.far.far_increase_pct}%의 ½`}
        />
        <StatCard label="재개발임대" value={`${info.housing_plan.redev_rental_units}세대`} color="#f97316" />
      </Box>

      {/* 임대 비율 게이지 */}
      <Box sx={{ mb: 1 }}>
        <Box sx={{ display: "flex", justifyContent: "space-between", mb: 0.5 }}>
          <Typography sx={{ fontSize: "12px", color: "#64748b" }}>임대주택 비율</Typography>
          <Typography sx={{ fontSize: "12px", color: "#a78bfa" }}>
            {info.housing_plan.total_rental_units}세대 ({rentalRatio}%)
          </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={rentalRatio}
          sx={{
            height: 8,
            borderRadius: 4,
            bgcolor: "#0f172a",
            "& .MuiLinearProgress-bar": { bgcolor: "#a78bfa", borderRadius: 4 },
          }}
        />
      </Box>

      {/* 공공임대 의무비율 안내 */}
      <Box sx={{
        bgcolor: "#0f172a", borderRadius: 1, p: 1,
        border: "1px solid #1e3a5f", mt: 1,
      }}>
        <Typography sx={{ fontSize: "12px", color: "#64748b" }}>
          💡 장기전세 확보 의무: 용적률 증가분(172.99%)의 ½ = 86.47% 이상
          (연면적 43,180㎡ / 획지 49,908㎡)
        </Typography>
      </Box>
    </Box>
  );
}

/* ─── 서브 컴포넌트 ─────────────────────────────────────────────────────── */

function StatCard({
  label, value, color, sub,
}: { label: string; value: string; color: string; sub?: string }) {
  return (
    <Box sx={{
      bgcolor: "#0f172a", p: 1.5, borderRadius: 1,
      border: `1px solid ${color}33`, textAlign: "center",
    }}>
      <Typography sx={{ fontSize: "18px", fontWeight: 700, color }}>
        {value}
      </Typography>
      <Typography sx={{ fontSize: "12px", color: "#94a3b8", mt: 0.3 }}>
        {label}
      </Typography>
      {sub && (
        <Typography sx={{ fontSize: "11px", color: "#475569", mt: 0.2 }}>
          {sub}
        </Typography>
      )}
    </Box>
  );
}

function FarRow({
  label, value, sub, color,
}: { label: string; value: string; sub: string; color: string }) {
  return (
    <Box sx={{
      display: "flex", justifyContent: "space-between", alignItems: "center",
      bgcolor: "#0f172a", px: 1.5, py: 0.8, borderRadius: 1,
    }}>
      <Box>
        <Typography sx={{ fontSize: "13px", color: "#94a3b8" }}>{label}</Typography>
        <Typography sx={{ fontSize: "11px", color: "#475569" }}>{sub}</Typography>
      </Box>
      <Typography sx={{ fontSize: "15px", fontWeight: 700, color }}>{value}</Typography>
    </Box>
  );
}
