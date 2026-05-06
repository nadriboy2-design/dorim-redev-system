"use client";
import { useEffect, useState, useCallback } from "react";
import dynamic from "next/dynamic";
import {
  Box, Button, Typography, CircularProgress, Alert,
} from "@mui/material";
import WorkflowTracker from "@/components/WorkflowTracker";
import MemberGrid from "@/components/MemberGrid";
import ConsentChart from "@/components/ConsentChart";
import ProjectStats from "@/components/ProjectStats";
import HousingPlan from "@/components/HousingPlan";
import ProjectSchedule from "@/components/ProjectSchedule";
import {
  fetchMembers, fetchWorkflowStatus, generateDoc,
  Member, WorkflowStatus,
} from "@/lib/api";

// 무거운 컴포넌트 동적 임포트 (초기 번들에서 제외)
const LegalChat   = dynamic(() => import("@/components/LegalChat"),   { ssr: false, loading: () => null });
const ReceiptOcr  = dynamic(() => import("@/components/ReceiptOcr"),  { ssr: false, loading: () => null });

type View = "dashboard" | "members" | "guide" | "plan";

export default function DashboardPage() {
  const [members, setMembers]        = useState<Member[]>([]);
  const [membersLoaded, setMembersLoaded] = useState(false);
  const [status, setStatus]          = useState<WorkflowStatus | null>(null);
  const [loading, setLoading]        = useState(true);
  const [docError, setDocError]      = useState<string | null>(null);
  const [docLoading, setDocLoading]  = useState(false);
  const [view, setView]              = useState<View>("dashboard");

  // 초기 로딩: 워크플로우 상태만 가져옴 (멤버 데이터는 지연 로딩)
  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const s = await fetchWorkflowStatus();
      setStatus(s);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  // 조합원 명부 탭 전환 시에만 멤버 데이터 로딩
  const handleViewChange = useCallback((v: View) => {
    setView(v);
    if (v === "members" && !membersLoaded) {
      fetchMembers()
        .then((m) => { setMembers(m); setMembersLoaded(true); })
        .catch(console.error);
    }
  }, [membersLoaded]);

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
      <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", mt: 8 }}>
        <CircularProgress size={60} />
        <Typography sx={{ ml: 2, fontSize: "20px" }}>데이터 로딩 중...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2, bgcolor: "#0f172a", minHeight: "100vh" }}>
      <Typography variant="h5" sx={{ fontWeight: 700, mb: 2, fontSize: "22px" }}>
        🏗️ 도림사거리 역세권 재개발 통합관리
      </Typography>

      {/* 단계 진행 트래커 — 항상 표시 */}
      {status && (
        <WorkflowTracker
          currentStage={status.current_stage}
          stageName={status.stage_name}
          currentSubStage={status.current_sub_stage}
          currentSubStageDetail={status.current_sub_stage_detail}
        />
      )}

      {/* 탭 버튼 */}
      <Box sx={{ display: "flex", gap: 1, mb: 2, flexWrap: "wrap" }}>
        {(["dashboard", "members", "plan", "guide"] as View[]).map((v) => {
          const labels: Record<View, string> = {
            dashboard: "대시보드",
            members:   "조합원 명부",
            plan:      "사업 계획",
            guide:     "질의하기",
          };
          const icons: Record<View, string> = {
            dashboard: "📊",
            members:   "👥",
            plan:      "📐",
            guide:     "⚖️",
          };
          return (
            <Button
              key={v}
              variant={view === v ? "contained" : "outlined"}
              onClick={() => handleViewChange(v)}
              sx={{ fontSize: "15px", minHeight: "40px" }}
            >
              {icons[v]} {labels[v]}
            </Button>
          );
        })}

        {/* 서류 다운로드는 별도 버튼 */}
        {status && (
          <Button
            variant="outlined"
            color="success"
            disabled={docLoading}
            onClick={() => handleGenerateDoc(status.required_docs[0])}
            sx={{ fontSize: "15px", minHeight: "40px" }}
          >
            {docLoading ? "생성 중..." : "📄 서류 PDF 다운로드"}
          </Button>
        )}
      </Box>

      {docError && (
        <Alert severity="error" sx={{ mb: 2, fontSize: "15px" }}>
          오류: {docError}
        </Alert>
      )}

      {/* ── 대시보드 뷰 ── */}
      {view === "dashboard" && status && (
        <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
          <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 2 }}>
            <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
              {/* 현재 단계 필수 서류 */}
              <Box sx={{ bgcolor: "#1e293b", p: 2, borderRadius: 2 }}>
                <Typography sx={{ fontSize: "17px", fontWeight: 700, mb: 1 }}>
                  📋 현재 단계 필수 서류
                </Typography>
                {status.required_docs.map((doc) => (
                  <Typography key={doc} sx={{ fontSize: "15px", color: "#94a3b8", mb: 0.5 }}>
                    • {doc}
                  </Typography>
                ))}
              </Box>

              <LegalChat />
              <ReceiptOcr />
            </Box>

            <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
              <ConsentChart
                stats={status.consent_rate}
                threshold={status.consent_threshold}
                isThresholdMet={status.is_threshold_met}
              />
              <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 1 }}>
                <Box sx={{
                  bgcolor: "#0f172a", p: 2, borderRadius: 2,
                  textAlign: "center", border: "1px solid #1e3a5f",
                }}>
                  <Typography sx={{ fontSize: "28px", fontWeight: 700, color: "#60a5fa" }}>
                    {status.consent_rate.total}
                  </Typography>
                  <Typography sx={{ fontSize: "15px", color: "#94a3b8" }}>전체 토지등소유자</Typography>
                </Box>
                <Box sx={{
                  bgcolor: "#0f172a", p: 2, borderRadius: 2,
                  textAlign: "center", border: "1px solid #166534",
                }}>
                  <Typography sx={{ fontSize: "28px", fontWeight: 700, color: "#22c55e" }}>
                    {status.consent_rate.consented}
                  </Typography>
                  <Typography sx={{ fontSize: "15px", color: "#94a3b8" }}>동의 완료</Typography>
                </Box>
              </Box>
            </Box>
          </Box>

          {/* ── 배치도 ── */}
          <Box sx={{ bgcolor: "#1e293b", borderRadius: 2, overflow: "hidden" }}>
            <Typography sx={{ fontSize: "17px", fontWeight: 700, p: 2, pb: 1 }}>
              🗺️ 도림사거리 역세권 재개발 배치도 <span style={{ fontSize: "13px", color: "#64748b", fontWeight: 400 }}>— 정비계획 수립(안) 2023.6</span>
            </Typography>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/siteplan.jpg?v=1640"
              alt="도림사거리 역세권 재개발 배치도"
              style={{ width: "100%", objectFit: "contain", display: "block", background: "#0f172a" }}
            />
          </Box>
        </Box>
      )}

      {/* ── 조합원 명부 뷰 ── */}
      {view === "members" && (
        <MemberGrid
          members={members}
          onConsentChange={(updated) => setMembers(updated)}
        />
      )}

      {/* ── 사업 계획 뷰 (PDF 정비계획안 기반) ── */}
      {view === "plan" && (
        <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 2 }}>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <ProjectSchedule />
            <ProjectStats />
          </Box>
          <HousingPlan />
        </Box>
      )}

      {/* ── 질의하기 뷰 ── */}
      {view === "guide" && (
        <Box sx={{ maxWidth: 800 }}>
          <LegalChat />
        </Box>
      )}
    </Box>
  );
}
