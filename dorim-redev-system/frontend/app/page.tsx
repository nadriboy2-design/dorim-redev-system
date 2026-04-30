"use client";
import { useEffect, useState, useCallback } from "react";
import {
  Box,
  Button,
  Typography,
  CircularProgress,
  Alert,
} from "@mui/material";
import WorkflowTracker from "@/components/WorkflowTracker";
import MemberGrid from "@/components/MemberGrid";
import ConsentChart from "@/components/ConsentChart";
import LegalChat from "@/components/LegalChat";
import MapComponent from "@/components/MapComponent";
import ReceiptOcr from "@/components/ReceiptOcr";
import {
  fetchMembers,
  fetchWorkflowStatus,
  generateDoc,
  Member,
  WorkflowStatus,
} from "@/lib/api";

export default function DashboardPage() {
  const [members, setMembers] = useState<Member[]>([]);
  const [status, setStatus] = useState<WorkflowStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [docError, setDocError] = useState<string | null>(null);
  const [docLoading, setDocLoading] = useState(false);
  const [view, setView] = useState<"dashboard" | "members">("dashboard");

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [m, s] = await Promise.all([fetchMembers(), fetchWorkflowStatus()]);
      setMembers(m);
      setStatus(s);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleGenerateDoc = async (docType: string) => {
    setDocError(null);
    setDocLoading(true);
    try {
      const blob = await generateDoc(docType);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${docType}.pdf`;
      a.click();
    } catch (e: unknown) {
      setDocError(e instanceof Error ? e.message : "문서 생성 실패");
    } finally {
      setDocLoading(false);
    }
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          mt: 8,
        }}
      >
        <CircularProgress size={60} />
        <Typography sx={{ ml: 2, fontSize: "20px" }}>
          데이터 로딩 중...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2, bgcolor: "#0f172a", minHeight: "100vh" }}>
      <Typography variant="h5" sx={{ fontWeight: 700, mb: 2, fontSize: "22px" }}>
        🏗️ 도림사거리 역세권 재개발 통합관리
      </Typography>

      {status && (
        <WorkflowTracker
          currentStage={status.current_stage}
          stageName={status.stage_name}
        />
      )}

      <Box sx={{ display: "flex", gap: 1, mb: 2 }}>
        <Button
          variant={view === "dashboard" ? "contained" : "outlined"}
          onClick={() => setView("dashboard")}
        >
          대시보드
        </Button>
        <Button
          variant={view === "members" ? "contained" : "outlined"}
          onClick={() => setView("members")}
        >
          조합원 명부
        </Button>
      </Box>

      {view === "dashboard" && status && (
        <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 2 }}>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <LegalChat />

            <Box sx={{ bgcolor: "#1e293b", p: 2, borderRadius: 2 }}>
              <Typography sx={{ fontSize: "18px", fontWeight: 700, mb: 1 }}>
                📋 현재 단계 필수 서류 뽑기
              </Typography>
              {status.required_docs.map((doc) => (
                <Typography
                  key={doc}
                  sx={{ fontSize: "16px", color: "#94a3b8", mb: 0.5 }}
                >
                  • {doc}
                </Typography>
              ))}
              {docError && (
                <Alert severity="error" sx={{ mt: 1, fontSize: "16px" }}>
                  오류: {docError}
                </Alert>
              )}
              <Button
                fullWidth
                variant="contained"
                color="success"
                size="large"
                sx={{ mt: 1 }}
                disabled={docLoading}
                onClick={() => handleGenerateDoc(status.required_docs[0])}
              >
                {docLoading ? "생성 중..." : "서류 PDF 다운로드"}
              </Button>
            </Box>

            <ReceiptOcr />
          </Box>

          <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <ConsentChart
              stats={status.consent_rate}
              threshold={status.consent_threshold}
              isThresholdMet={status.is_threshold_met}
            />
            <Box sx={{ bgcolor: "#1e293b", borderRadius: 2, p: 1, minHeight: 300 }}>
              <MapComponent />
            </Box>
            <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 1 }}>
              <Box
                sx={{
                  bgcolor: "#0f172a",
                  p: 2,
                  borderRadius: 2,
                  textAlign: "center",
                  border: "1px solid #1e3a5f",
                }}
              >
                <Typography sx={{ fontSize: "28px", fontWeight: 700, color: "#60a5fa" }}>
                  {status.consent_rate.total}
                </Typography>
                <Typography sx={{ fontSize: "16px", color: "#94a3b8" }}>
                  전체 토지등소유자
                </Typography>
              </Box>
              <Box
                sx={{
                  bgcolor: "#0f172a",
                  p: 2,
                  borderRadius: 2,
                  textAlign: "center",
                  border: "1px solid #166534",
                }}
              >
                <Typography sx={{ fontSize: "28px", fontWeight: 700, color: "#22c55e" }}>
                  {status.consent_rate.consented}
                </Typography>
                <Typography sx={{ fontSize: "16px", color: "#94a3b8" }}>
                  동의 완료
                </Typography>
              </Box>
            </Box>
          </Box>
        </Box>
      )}

      {view === "members" && (
        <MemberGrid
          members={members}
          onConsentChange={(updated) => setMembers(updated)}
        />
      )}
    </Box>
  );
}
