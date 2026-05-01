"use client";
/**
 * ProjectSchedule — 정비계획 수립 절차도 (사업추진 절차도 기준)
 * 이미지: 다. 정비계획 수립 — 11단계, 현재 2단계(정비계획 입안 제안 ✓)
 */
import { useEffect, useState } from "react";
import { Box, Typography, Chip, CircularProgress } from "@mui/material";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import RadioButtonUncheckedIcon from "@mui/icons-material/RadioButtonUnchecked";
import LocationOnIcon from "@mui/icons-material/LocationOn";

interface ScheduleStep {
  step: number;
  name: string;
  actor: string;
  current: boolean;
}

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function ProjectSchedule() {
  const [steps, setSteps] = useState<ScheduleStep[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${BASE_URL}/api/project/schedule`)
      .then((r) => r.json())
      .then((j) => setSteps(j.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Box sx={{ p: 2 }}><CircularProgress size={24} /></Box>;

  const currentIdx = steps.findIndex((s) => s.current);
  const completedCount = currentIdx; // 현재 이전 단계 수

  return (
    <Box sx={{ bgcolor: "#1e293b", borderRadius: 2, p: 2 }}>
      {/* 헤더 */}
      <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
        <Typography sx={{ fontSize: "17px", fontWeight: 700 }}>
          📋 정비계획 수립 절차
        </Typography>
        <Chip
          label={`${completedCount + 1} / ${steps.length}단계`}
          size="small"
          sx={{ bgcolor: "#1d4ed8", color: "#fff", fontSize: "11px" }}
        />
        <Chip
          label="다. 정비계획 수립"
          size="small"
          sx={{ bgcolor: "#334155", color: "#94a3b8", fontSize: "11px" }}
        />
      </Box>

      {/* 전체 진행 바 */}
      <Box sx={{ mb: 2, bgcolor: "#0f172a", borderRadius: 1, overflow: "hidden", height: 6 }}>
        <Box sx={{
          height: "100%",
          width: `${((currentIdx) / (steps.length - 1)) * 100}%`,
          bgcolor: "#3b82f6",
          borderRadius: 1,
          transition: "width 0.5s ease",
        }} />
      </Box>

      {/* 단계 목록 */}
      <Box sx={{ display: "flex", flexDirection: "column", gap: 0.5 }}>
        {steps.map((step, idx) => {
          const isDone    = idx < currentIdx;
          const isCurrent = step.current;
          const isFuture  = idx > currentIdx;

          return (
            <Box
              key={step.step}
              sx={{
                display: "flex",
                alignItems: "center",
                gap: 1.5,
                p: 1,
                borderRadius: 1,
                bgcolor: isCurrent
                  ? "#1d4ed822"
                  : isDone
                  ? "#16653422"
                  : "transparent",
                border: isCurrent
                  ? "1px solid #3b82f6"
                  : isDone
                  ? "1px solid #16653444"
                  : "1px solid transparent",
                transition: "all 0.2s",
              }}
            >
              {/* 아이콘 */}
              <Box sx={{ flexShrink: 0, width: 24, display: "flex", justifyContent: "center" }}>
                {isDone ? (
                  <CheckCircleIcon sx={{ fontSize: 20, color: "#22c55e" }} />
                ) : isCurrent ? (
                  <LocationOnIcon sx={{ fontSize: 20, color: "#3b82f6" }} />
                ) : (
                  <RadioButtonUncheckedIcon sx={{ fontSize: 20, color: "#334155" }} />
                )}
              </Box>

              {/* 단계번호 */}
              <Box sx={{
                width: 24, height: 24, borderRadius: "50%",
                display: "flex", alignItems: "center", justifyContent: "center",
                bgcolor: isCurrent ? "#3b82f6" : isDone ? "#166534" : "#1e293b",
                flexShrink: 0,
              }}>
                <Typography sx={{ fontSize: "11px", fontWeight: 700, color: "#fff" }}>
                  {step.step}
                </Typography>
              </Box>

              {/* 단계명 */}
              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                  <Typography sx={{
                    fontSize: "13px",
                    fontWeight: isCurrent ? 700 : isDone ? 600 : 400,
                    color: isCurrent ? "#60a5fa" : isDone ? "#22c55e" : "#94a3b8",
                    whiteSpace: "nowrap",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                  }}>
                    {step.name}
                  </Typography>
                  {isCurrent && (
                    <Chip
                      label="현재"
                      size="small"
                      sx={{ bgcolor: "#3b82f6", color: "#fff", fontSize: "10px", height: 18 }}
                    />
                  )}
                </Box>
                <Typography sx={{ fontSize: "11px", color: "#475569" }}>
                  {step.actor}
                </Typography>
              </Box>

              {/* 연결선 (마지막 제외) */}
            </Box>
          );
        })}
      </Box>

      {/* 안내 메시지 */}
      <Box sx={{
        mt: 2, p: 1.5, bgcolor: "#0f172a", borderRadius: 1,
        border: "1px solid #1d4ed833",
      }}>
        <Typography sx={{ fontSize: "12px", color: "#64748b" }}>
          ※ 국토계획법 시행령 제46조제11항에 따른 감정평가는 市 관련 위원회 심의 이전 시행
          (비용은 제안자 부담). 사업 시행 세부 절차는 관계 법규 및 규정에 따름.
        </Typography>
      </Box>
    </Box>
  );
}
