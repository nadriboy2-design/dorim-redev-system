"use client";
import { Box, Typography, LinearProgress, Alert } from "@mui/material";
import { ConsentRate } from "@/lib/api";

interface Props {
  stats: ConsentRate;
  threshold: number;
  isThresholdMet: boolean;
}

export default function ConsentChart({ stats, threshold, isThresholdMet }: Props) {
  const needed = Math.ceil(stats.total * threshold) - stats.consented;

  return (
    <Box sx={{ bgcolor: "#0f172a", p: 2, borderRadius: 2, border: "1px solid #334155" }}>
      <Typography sx={{ fontSize: "14px", color: "#94a3b8", mb: 1, fontWeight: 600 }}>
        동의율 현황 (기준: {(threshold * 100).toFixed(0)}%)
      </Typography>

      <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 1 }}>
        <LinearProgress
          variant="determinate"
          value={Math.min(stats.rate, 100)}
          sx={{
            flex: 1,
            height: 14,
            borderRadius: 7,
            "& .MuiLinearProgress-bar": {
              bgcolor: isThresholdMet ? "#22c55e" : "#3b82f6",
            },
          }}
        />
        <Typography
          sx={{
            fontSize: "24px",
            fontWeight: 700,
            color: isThresholdMet ? "#22c55e" : "#fbbf24",
            minWidth: "60px",
          }}
        >
          {stats.rate}%
        </Typography>
      </Box>

      <Typography sx={{ fontSize: "14px", color: "#64748b" }}>
        동의 완료 {stats.consented}명 / 전체 {stats.total}명
      </Typography>

      {!isThresholdMet && (
        <Alert severity="warning" sx={{ mt: 1, fontSize: "14px" }}>
          다음 단계 진입까지 <strong>{needed}명</strong> 더 필요합니다
        </Alert>
      )}
      {isThresholdMet && (
        <Alert severity="success" sx={{ mt: 1, fontSize: "14px" }}>
          동의율 기준({(threshold * 100).toFixed(0)}%) 달성 ✅
        </Alert>
      )}
    </Box>
  );
}
