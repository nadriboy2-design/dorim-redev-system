"use client";
import { Box, Chip, Typography } from "@mui/material";

const STAGES = [
  { key: "STAGE_1_PRELIMINARY", label: "① 정비구역 입안" },
  { key: "STAGE_2_COMMITTEE",   label: "② 추진위 구성" },
  { key: "STAGE_3_ASSOCIATION", label: "③ 조합 설립" },
  { key: "STAGE_4_CONTRACTOR",  label: "④ 시공사 선정" },
  { key: "STAGE_5_DISPOSAL",    label: "⑤ 관리처분" },
];

interface Props {
  currentStage: string;
  stageName: string;
}

export default function WorkflowTracker({ currentStage, stageName }: Props) {
  const currentIdx = STAGES.findIndex((s) => s.key === currentStage);

  return (
    <Box sx={{ bgcolor: "#1e293b", p: 2, borderRadius: 2, mb: 2 }}>
      <Typography sx={{ fontSize: "16px", color: "#94a3b8", mb: 1 }}>
        현재 사업 단계: <strong style={{ color: "#fff" }}>{stageName}</strong>
      </Typography>
      <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
        {STAGES.map((stage, idx) => (
          <Chip
            key={stage.key}
            label={stage.label}
            size="small"
            sx={{
              fontSize: "13px",
              fontWeight: idx === currentIdx ? 700 : 400,
              bgcolor: idx === currentIdx ? "#3b82f6" : idx < currentIdx ? "#166534" : "#334155",
              color: idx <= currentIdx ? "#fff" : "#94a3b8",
              border: idx === currentIdx ? "2px solid #60a5fa" : "none",
            }}
          />
        ))}
      </Box>
    </Box>
  );
}
