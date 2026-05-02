"use client";
import { useState } from "react";
import {
  Box, Chip, Typography, Collapse, Divider,
  List, ListItem, ListItemIcon, ListItemText,
  Accordion, AccordionSummary, AccordionDetails,
  Alert, Paper
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import GavelIcon from "@mui/icons-material/Gavel";
import CalculateIcon from "@mui/icons-material/Calculate";
import HomeWorkIcon from "@mui/icons-material/HomeWork";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutlineOutlined";

// ── 9단계 정의 ──────────────────────────────────────────────────────────────
const STAGES = [
  { key: "STAGE_1_PRELIMINARY", short: "① 구역입안" },
  { key: "STAGE_2_COMMITTEE",   short: "② 추진위" },
  { key: "STAGE_3_ASSOCIATION", short: "③ 조합설립" },
  { key: "STAGE_4_BUSINESS",    short: "④ 사업시행" },
  { key: "STAGE_5_CONTRACTOR",  short: "⑤ 시공사" },
  { key: "STAGE_6_DISPOSAL",    short: "⑥ 관리처분" },
  { key: "STAGE_7_RELOCATION",  short: "⑦ 이주·철거" },
  { key: "STAGE_8_CONSTRUCTION",short: "⑧ 착공·준공" },
  { key: "STAGE_9_MOVEIN",      short: "⑨ 입주·청산" },
];

// ── 단계별 상세 가이드 데이터 ────────────────────────────────────────────────
const STAGE_GUIDE: Record<string, {
  subStages: string[];
  cautions: string[];
  contractCautions: string[];
  proportionalInfo: { title: string; formula: string; notes: string[] } | null;
  relocationInfo: { title: string; items: string[]; caution?: string } | null;
}> = {
  STAGE_1_PRELIMINARY: {
    subStages: [
      "사전검토 신청서 제출 (동의율 40% 필요)",
      "서울시 사전검토회의 심의",
      "주민공람·공고 (14일 이상)",
      "정비구역 지정 고시",
    ],
    cautions: [
      "도림동 133-1 구역 좌표·소유자 혼입 절대 금지 (인허가 무효 위험)",
      "【2026.3.6. 개정】 사전검토 동의 3가지 요건 모두 필수 충족",
      "  ① 토지등소유자 40% 이상",
      "  ② 토지면적 40% 이상",
      "  ③ 폭 20m 이상 도로변 접한 대지의 토지등소유자·토지면적 각 50% 이상 (신설)",
      "【2026.3.6. 개정】 사전검토 통과 후 2년 이내 입안 신청 의무 — 미이행 시 후보지 자동 제외",
      "【2026.3.6. 경과조치】 이미 사전검토 통과한 경우 → 계획검토로 재신청 의무",
      "1차 역세권: 승강장 경계 기준 250m 이내 (지역중심 이상 환승역세권은 위원회 인정 시 350m)",
      "노후도 기준: 건축물 2/3 이상이 준공 후 20년 이상이어야 함",
      "동의서는 토지등소유자 기준 — 세입자 동의 불인정",
    ],
    contractCautions: [
      "【동의서】 서명·날인 전 토지등기사항증명서와 성명·주소 일치 확인",
      "【동의서】 공유자가 있는 경우 공유자 전원 동의 필요 (일부만 동의 무효)",
      "【동의서】 유효기간 명시 필수 — 통상 2년, 기간 내 철회 시 동의율 재계산",
      "【위임장】 대리인 동의 시 인감증명서(3개월 이내) 반드시 첨부",
      "【개인정보】 주민번호 수집 시 개인정보보호법 동의서 별도 징구",
    ],
    proportionalInfo: null,
    relocationInfo: null,
  },
  STAGE_2_COMMITTEE: {
    subStages: [
      "추진위원장 및 위원 선출 (총회)",
      "추진위원회 운영규정 작성",
      "서울시 승인 신청 (동의율 50% 필요)",
      "추진위원회 운영 개시",
    ],
    cautions: [
      "추진위원은 반드시 해당 구역 토지등소유자이어야 함 (세입자 불가)",
      "위원장은 선출직 — 총회 의사록에 선출 과정 명확히 기재",
      "추진위 운영비 지출은 추후 조합 설립 후 정산 대상 → 영수증 전산관리 필수",
      "서울시 승인 후 추진위원 변경 시 별도 변경 승인 필요",
      "이 단계에서 시공사와 어떠한 약정·MOU도 법적 효력 없음",
    ],
    contractCautions: [
      "【업무대행 계약】 용역업체 선정 시 추진위원회 의결 필수, 단독 계약 무효",
      "【업무대행 계약】 계약기간·보수·해지조건 명확히 기재, 조합 설립 전 자동 만료 조항 삽입",
      "【설계용역 계약】 기본설계 단계임을 명시, 실시설계 자동 전환 조항 금지",
      "【감정평가 계약】 감정평가법인 2개소 이상 선정, 평균값 적용 조건 명시",
      "【회계감사 계약】 독립 공인회계사 감사 의무 — 내부 감사만으로 불충분",
    ],
    proportionalInfo: null,
    relocationInfo: null,
  },
  STAGE_3_ASSOCIATION: {
    subStages: [
      "창립총회 개최 (토지등소유자 75%·토지면적 1/2 이상)",
      "조합 설립 인가 신청 (영등포구청)",
      "조합설립 인가 고시",
      "조합원 명부 확정 및 통보",
    ],
    cautions: [
      "토지등소유자 3/4 이상 + 토지면적 1/2 이상 두 요건 모두 충족 (도정법 제35조)",
      "무허가 건물 소유자 조합원 포함 여부 별도 검토 (1989.1.24. 이전 건축물 기준)",
      "조합 정관 필수 기재사항 누락 시 인가 반려 — 서울시 표준 정관 사용 권장",
      "조합설립 인가 후 30일 이내 법인 등기 의무",
      "조합원 확정 후 탈퇴 원칙적 불가 → 이후 현금청산으로 처리",
    ],
    contractCautions: [
      "【정관】 '비례율 산정 방법' 조항 반드시 명시 (종전/종후 자산 산정 기준 포함)",
      "【정관】 이주비 지급 기준·한도·시기 명확히 기재",
      "【정관】 분양신청 기간·철회 조건·미신청자 현금청산 조건 구체적으로 규정",
      "【임원계약】 임기·해임 요건·보수 상한액 명확히 설정 (총회 의결 사항)",
      "【계약 전환】 추진위 시절 계약을 조합명의로 전환 시 이사회 의결 필수",
    ],
    proportionalInfo: {
      title: "예비 비례율 산출 — 조합원 권리 보호의 기준선",
      formula: "비례율(%) = (종후자산총가액 − 총사업비) ÷ 종전자산총가액 × 100",
      notes: [
        "종전자산총가액: 감정평가법인 2개소 평균값 적용",
        "역세권 고밀개발의 경우 통상 105~120% 범위",
        "비례율 100% 이하 시 사업성 재검토 필요",
        "권리가액 = 종전자산평가액 × 비례율 ÷ 100",
      ],
    },
    relocationInfo: null,
  },
  STAGE_4_BUSINESS: {
    subStages: [
      "건축 기본설계 완료",
      "환경영향·교통영향 평가",
      "건축심의 (서울시 건축위원회)",
      "사업시행계획 인가 신청",
      "사업시행 인가 고시",
    ],
    cautions: [
      "건축심의는 평균 3~6개월 소요 예상",
      "1차 역세권 법정 용적률 상한 700% 초과 시 하드락 A 자동 발동",
      "【2026.3.6.】 700% 달성 필수요건: ①간선도로변(구역둘레 1/8이상 접함) 또는 역사인접부 + ②진입도로 8m이상",
      "【2026.3.6.】 활성화항목 누적 가산(최대+200%p): 장기전세추가(+70%p) · 역세권환경개선(+50%p) · 열린공간(+50%p) · 서울형정책상향(+30%p)",
      "【2026.3.6.】 친환경 건축물 필수: 환경성능·에너지성능·에너지관리·신재생에너지 4개 부문 중 2개 이상 상향 등급",
      "소형주택(전용 60㎡ 이하) 용적률 20% 이상 추가 공급 시 기준용적률 20% 추가 완화 혜택",
      "사업시행인가 후 3년 이내 착공하지 않으면 인가 효력 상실",
    ],
    contractCautions: [
      "【설계계약】 기본설계·실시설계 별도 계약, 기본설계 완료 후 발주처 승인 절차 삽입",
      "【설계계약】 설계변경 범위·절차·추가비용 기준 명확히 규정",
      "【환경평가 계약】 주민설명회 개최 의무 및 이의신청 처리 절차 명시",
      "【전문관리업자】 업무 범위·보고 주기·성과지표(KPI) 명확히 정의",
      "【감리계약】 건설기술진흥법상 감리 자격 보유 여부 확인",
    ],
    proportionalInfo: {
      title: "사업시행 인가 후 비례율 정밀 산출",
      formula: "비례율(%) = (분양수입 + 임대수입 − 총사업비) ÷ 종전자산총가액 × 100",
      notes: [
        "분양수입: 일반분양 세대 × 분양단가 (건축심의 확정 후 산출)",
        "임대수입: 역세권 장기전세 환산 임대료",
        "총사업비: 공사비(기본설계 기준) + 부대비용",
        "이 단계 비례율로 각 조합원 권리가액 잠정 확정",
      ],
    },
    relocationInfo: null,
  },
  STAGE_5_CONTRACTOR: {
    subStages: [
      "입찰공고 (30일 이상)",
      "현장설명회 개최",
      "입찰서류 접수 (기본설계도서·성능요구서·내역서)",
      "총회 의결로 시공사 선정",
      "공사도급 계약 체결",
    ],
    cautions: [
      "【하드락 B】 조합설립인가 이전 시공사 선정 시도 → 자동 차단",
      "최소 3개사 이상 경쟁 입찰, 단독 입찰 시 유찰 처리",
      "시공사 재무건전성: 최근 3년 감사보고서, 신용등급 BBB+ 이상",
      "하도급 비율 상한 50%, 주요 공종 직접 시공 의무화",
      "분양공고 전 공사비 검증(국토부 고시) 의무 — 미이행 시 분양 불가",
    ],
    contractCautions: [
      "【도급계약】 공사비 조정 기준 명확히 — 물가변동 연동 조항 적용 범위 한정",
      "【도급계약】 이주비 대여 조건(금리·한도·상환방식) 별도 특약으로 규정",
      "【도급계약】 공사 지연 시 지체보상금 기준 명시 (공사비 × 지연일수 × 비율)",
      "【도급계약】 하자담보책임: 내력구조부 10년, 방수 5년, 기타 1~2년",
      "【도급계약】 분양 미달 시 미분양 처리 방법·조합 부담 한도 명확히 기재",
    ],
    proportionalInfo: {
      title: "공사비 확정 → 비례율 최종 확정",
      formula: "비례율(%) = (종후자산총가액 − 확정 총사업비) ÷ 종전자산총가액 × 100",
      notes: [
        "확정 공사비: 도급계약금액 (부가세 별도)",
        "이주비 이자: 이주비 × 대출금리 × 이주기간",
        "예비비: 총사업비의 3~5% 반영",
        "권리가액 = 종전자산평가액 × 확정비례율 ÷ 100",
      ],
    },
    relocationInfo: {
      title: "이주비 지급 기준 확정",
      items: [
        "이주비 한도: 권리가액의 60% (서울시 기준)",
        "대출 금리: 시중은행 협약 금리 (CD금리 + 1.0~1.5%)",
        "이주비 이자는 총사업비에 포함 → 비례율에 영향",
        "무허가건물 소유자: 이주비 지급 기준 별도 심의 필요",
      ],
    },
  },
  STAGE_6_DISPOSAL: {
    subStages: [
      "분양신청 공고 및 접수 (30일 이상)",
      "분양신청 결과 집계·분석",
      "관리처분계획 수립 (비례율 확정)",
      "한국부동산원 타당성 검토",
      "총회 의결 (출석 2/3 이상)",
      "관리처분계획 인가 신청 및 고시",
    ],
    cautions: [
      "【하드락 C】 공사비 검증 결과서 미첨부 시 분양공고 자동 차단",
      "분양신청 기간 종료 후 철회 불가",
      "미분양 신청자(현금청산자) 청산금은 현재 감정평가액 기준",
      "관리처분 총회: 분양신청자 과반수 출석 + 출석 2/3 이상 찬성",
      "사업비 증가로 비례율 5% 이상 변동 시 조합원 2/3 동의로 재의결",
    ],
    contractCautions: [
      "【분양계약】 청약 자격·면적·금액·납부일정 명확히 기재",
      "【분양계약】 분양가 상한제 적용 여부 확인 (역세권 고밀개발 해당 가능)",
      "【현금청산 계약】 청산금 지급 시기·이자 여부·지급방법 구체적으로 명시",
      "【이주 합의서】 이주비 지급 조건·명도 기한·지체 시 손해배상 규정",
      "【세입자 이주비】 주거이전비·이사비 지급 기준은 공익사업보상법 준용",
    ],
    proportionalInfo: {
      title: "최종 확정 비례율 및 개인별 청산금",
      formula: "비례율(%) = (종후자산총가액 − 총사업비) ÷ 종전자산총가액 × 100",
      notes: [
        "권리가액 = 종전자산평가액 × 최종비례율 ÷ 100",
        "청산금(납부) = 분양예정가액 − 권리가액 > 0 → 조합원이 납부",
        "청산금(환급) = 분양예정가액 − 권리가액 < 0 → 조합이 지급",
        "비례율은 소수점 둘째 자리까지, 청산금은 1원 단위 확정",
      ],
    },
    relocationInfo: {
      title: "이주비 집행 기준",
      items: [
        "이주비 대출: 시중은행 협약대출 (조합이 담보 제공)",
        "주거이전비: 가구원 수 기준 3개월 가계지출비 (통계청 고시)",
        "이사비: 40㎡ 미만→60만원, 60㎡ 미만→80만원, 이상→100만원",
        "영업손실 보상: 사업자등록 영업자 4개월분 영업이익",
      ],
    },
  },
  STAGE_7_RELOCATION: {
    subStages: [
      "이주비 지급 개시",
      "세입자 이주 완료",
      "조합원 이주 완료",
      "건물 철거 공사",
      "지장물 이설 (가스·전기·통신)",
    ],
    cautions: [
      "석면 함유 건축물은 전문업체 석면 해체 선행 (산안법 의무)",
      "지하매설물 파악 후 철거 — 가스관 손상 시 형사 책임",
      "이주 완료 전 조합원에게 철거 유예 기간(30일) 부여",
      "철거 공사 시 소음·분진·진동 민원 대응 계획 수립",
    ],
    contractCautions: [
      "【이주비 대출 약정】 상환 시기: 입주 후 잔금 납부 시 일괄 상환 조건 명시",
      "【명도합의서】 이주 거부 세대에 대한 강제 집행 근거 조항 삽입",
      "【철거계약】 철거 범위·안전관리·사후 정리 의무 명확히 기재",
      "【보상계약】 영업 손실 보상은 실 영업 기간만 인정",
    ],
    proportionalInfo: null,
    relocationInfo: {
      title: "이주비 집행 현황",
      items: [
        "이주비 지급 대상: 분양신청 조합원 전원",
        "지급 시기: 이주개시일로부터 30일 이내",
        "이주비 대출금리 동결 조건 확인 필요",
        "현금청산 조합원: 사업시행인가일 기준 감정가로 보상",
      ],
    },
  },
  STAGE_8_CONSTRUCTION: {
    subStages: [
      "착공신고 (착공 전 7일 이내)",
      "골조 공사",
      "마감 공사",
      "사용승인 신청",
      "준공 및 입주자 사전점검",
    ],
    cautions: [
      "착공 후 공사비 증가(토질불량·설계변경) 시 비례율 변동 가능",
      "공사비 10% 이상 증가 시 조합원 총회 재의결 필요",
      "중도금 대출 실행 타이밍: 골조 완료율 50% 이상 기준",
      "준공 지연 시 이주비 이자 추가 발생 → 사업비 증가",
    ],
    contractCautions: [
      "【중도금 대출 약정】 분양금액의 60%까지, 금리·납부일정 명확히",
      "【입주자 특약】 입주 전 자체 점검 및 하자 목록 제출 기한 명시",
      "【하자보증】 입주 후 의무 하자보수 기간 공종별 명세 첨부",
    ],
    proportionalInfo: {
      title: "공사비 변동 모니터링",
      formula: "실제비례율 재산출 기준",
      notes: [
        "공사비가 확정 도급금액의 ±5% 초과 시 비례율 수정 검토",
        "설계변경 내역서 조합 이사회 보고 의무",
      ],
    },
    relocationInfo: null,
  },
  STAGE_9_MOVEIN: {
    subStages: [
      "입주 개시",
      "잔금 납부 및 소유권 이전 등기",
      "청산금 정산 (납부 또는 환급)",
      "조합 해산 총회",
      "조합 청산 완료",
    ],
    cautions: [
      "잔금 미납 조합원은 소유권 이전 불가 → 경매 처리 가능",
      "청산금 납부 기한 초과 시 연 6% 이자 부과 (도정법 규정)",
      "조합 해산 전 모든 소송·분쟁 완결 필요",
      "조합원 사망 시 상속인 확인 후 이전 등기 진행",
    ],
    contractCautions: [
      "【소유권이전 계약】 등기 이전 전 근저당·가압류 전부 해제 확인",
      "【청산계약】 추가 청산금 발생 시 지급 시기·이자 조건 명확히",
      "【조합 해산 결의】 잔여재산 처분 방법 정관에 따라 처리",
    ],
    proportionalInfo: {
      title: "최종 비례율 vs 확정 비례율 차액 정산",
      formula: "실제비례율 = (실제 종후자산총가액 − 실제 총사업비) ÷ 종전자산총가액 × 100",
      notes: [
        "비례율 차이만큼 개인별 청산금 증감 재계산",
        "과수령 조합원: 추가 납부",
        "과소수령 조합원: 추가 환급",
      ],
    },
    relocationInfo: {
      title: "이주비 대출 최종 상환",
      items: [
        "이주비 대출 상환: 입주 시 잔금에서 일괄 공제",
        "이자 정산: 이주 시작~입주 완료까지 실 발생 이자 정산",
        "이주비 반환 불이행 시 분양권 담보 실행",
      ],
    },
  },
};

// ── Props ────────────────────────────────────────────────────────────────────
interface Props {
  currentStage: string;
  stageName: string;
  currentSubStage?: string;
  currentSubStageDetail?: string;
}

// ── 컬러 팔레트 ──────────────────────────────────────────────────────────────
const COLORS = {
  done:    "#166534",
  current: "#1d4ed8",
  pending: "#1e293b",
  text:    "#94a3b8",
};

export default function WorkflowTracker({ currentStage, stageName, currentSubStage, currentSubStageDetail }: Props) {
  const currentIdx = STAGES.findIndex((s) => s.key === currentStage);
  const [expanded, setExpanded] = useState<string | false>(currentStage);

  const guide = STAGE_GUIDE[expanded || currentStage];
  const expandedIdx = STAGES.findIndex((s) => s.key === expanded);

  return (
    <Box sx={{ mb: 2 }}>
      {/* ── 진행 바 ── */}
      <Box sx={{ bgcolor: "#1e293b", p: 2, borderRadius: 2, mb: 1 }}>
        <Typography sx={{ fontSize: "15px", color: "#94a3b8", mb: currentSubStage ? 0.5 : 1.5 }}>
          현재 사업 단계:{" "}
          <strong style={{ color: "#fff", fontSize: "17px" }}>{stageName}</strong>
        </Typography>
        {currentSubStage && (
          <Typography sx={{ fontSize: "14px", color: "#60a5fa", mb: 0.3, fontWeight: 600 }}>
            📍 {currentSubStage}
          </Typography>
        )}
        {currentSubStageDetail && (
          <Typography sx={{ fontSize: "13px", color: "#94a3b8", mb: 1.5 }}>
            {currentSubStageDetail}
          </Typography>
        )}
        <Box sx={{ display: "flex", gap: 0.8, flexWrap: "wrap" }}>
          {STAGES.map((stage, idx) => {
            const isDone    = idx < currentIdx;
            const isCurrent = idx === currentIdx;
            const isExpanded= stage.key === expanded;
            return (
              <Chip
                key={stage.key}
                label={stage.short}
                size="small"
                onClick={() => setExpanded(isExpanded ? false : stage.key)}
                sx={{
                  fontSize: "12px",
                  fontWeight: isCurrent ? 700 : 400,
                  bgcolor: isCurrent
                    ? COLORS.current
                    : isDone
                    ? COLORS.done
                    : COLORS.pending,
                  color: idx <= currentIdx ? "#fff" : COLORS.text,
                  border: isExpanded
                    ? "2px solid #f59e0b"
                    : isCurrent
                    ? "2px solid #60a5fa"
                    : "none",
                  cursor: "pointer",
                  "&:hover": { opacity: 0.85 },
                }}
              />
            );
          })}
        </Box>
      </Box>

      {/* ── 단계 상세 가이드 ── */}
      <Collapse in={!!expanded && !!guide}>
        {guide && (
          <Paper
            elevation={0}
            sx={{
              bgcolor: "#0f172a",
              border: "1px solid #334155",
              borderRadius: 2,
              overflow: "hidden",
            }}
          >
            {/* 헤더 */}
            <Box
              sx={{
                bgcolor: expandedIdx === currentIdx ? "#1d4ed8" : expandedIdx < currentIdx ? "#166534" : "#334155",
                px: 2, py: 1.5,
              }}
            >
              <Typography sx={{ fontSize: "16px", fontWeight: 700, color: "#fff" }}>
                {STAGES[expandedIdx]?.short} — {expanded && stageName}
                {expandedIdx !== currentIdx && (
                  <Chip
                    label={expandedIdx < currentIdx ? "완료" : "예정"}
                    size="small"
                    sx={{ ml: 1, fontSize: "11px", bgcolor: "rgba(255,255,255,0.15)", color: "#fff" }}
                  />
                )}
              </Typography>
            </Box>

            <Box sx={{ p: 2, display: "flex", flexDirection: "column", gap: 1 }}>
              {/* 세부 절차 */}
              <Accordion disableGutters sx={{ bgcolor: "#1e293b", borderRadius: 1 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: "#94a3b8" }} />}>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <CheckCircleOutlineIcon sx={{ color: "#22c55e", fontSize: 18 }} />
                    <Typography sx={{ fontSize: "14px", fontWeight: 600, color: "#e2e8f0" }}>
                      세부 절차
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails sx={{ pt: 0 }}>
                  {guide.subStages.map((s, i) => (
                    <Box key={i} sx={{ display: "flex", gap: 1, mb: 0.5, alignItems: "flex-start" }}>
                      <Box sx={{
                        minWidth: 20, height: 20, borderRadius: "50%",
                        bgcolor: "#334155", display: "flex", alignItems: "center",
                        justifyContent: "center", mt: "2px",
                      }}>
                        <Typography sx={{ fontSize: "10px", color: "#94a3b8" }}>{i + 1}</Typography>
                      </Box>
                      <Typography sx={{ fontSize: "13px", color: "#cbd5e1" }}>{s}</Typography>
                    </Box>
                  ))}
                </AccordionDetails>
              </Accordion>

              {/* 유의사항 */}
              <Accordion disableGutters sx={{ bgcolor: "#1e293b", borderRadius: 1 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: "#94a3b8" }} />}>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <WarningAmberIcon sx={{ color: "#f59e0b", fontSize: 18 }} />
                    <Typography sx={{ fontSize: "14px", fontWeight: 600, color: "#fbbf24" }}>
                      유의사항
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails sx={{ pt: 0 }}>
                  {guide.cautions.map((c, i) => (
                    <Alert
                      key={i}
                      severity={c.startsWith("【하드락") ? "error" : "warning"}
                      sx={{ mb: 0.5, fontSize: "13px", py: 0.3,
                            "& .MuiAlert-message": { fontSize: "13px" } }}
                    >
                      {c}
                    </Alert>
                  ))}
                </AccordionDetails>
              </Accordion>

              {/* 계약서 작성 시 유의사항 */}
              <Accordion disableGutters sx={{ bgcolor: "#1e293b", borderRadius: 1 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: "#94a3b8" }} />}>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <GavelIcon sx={{ color: "#a78bfa", fontSize: 18 }} />
                    <Typography sx={{ fontSize: "14px", fontWeight: 600, color: "#c4b5fd" }}>
                      계약서 작성 시 유의사항
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails sx={{ pt: 0 }}>
                  <List dense disablePadding>
                    {guide.contractCautions.map((c, i) => (
                      <ListItem key={i} sx={{ py: 0.3, px: 0, alignItems: "flex-start" }}>
                        <ListItemIcon sx={{ minWidth: 20, mt: "4px" }}>
                          <Box sx={{ width: 6, height: 6, borderRadius: "50%", bgcolor: "#7c3aed" }} />
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Typography sx={{ fontSize: "13px", color: "#cbd5e1" }}>{c}</Typography>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                </AccordionDetails>
              </Accordion>

              {/* 비례율 정보 */}
              {guide.proportionalInfo && (
                <Accordion disableGutters sx={{ bgcolor: "#1e293b", borderRadius: 1 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: "#94a3b8" }} />}>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      <CalculateIcon sx={{ color: "#38bdf8", fontSize: 18 }} />
                      <Typography sx={{ fontSize: "14px", fontWeight: 600, color: "#7dd3fc" }}>
                        비례율 산정
                      </Typography>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails sx={{ pt: 0 }}>
                    <Typography sx={{ fontSize: "13px", color: "#94a3b8", mb: 0.8 }}>
                      {guide.proportionalInfo.title}
                    </Typography>
                    <Box sx={{
                      bgcolor: "#0f172a", border: "1px solid #1e40af",
                      borderRadius: 1, px: 2, py: 1, mb: 1,
                    }}>
                      <Typography sx={{ fontSize: "13px", color: "#60a5fa", fontFamily: "monospace" }}>
                        {guide.proportionalInfo.formula}
                      </Typography>
                    </Box>
                    {guide.proportionalInfo.notes.map((n, i) => (
                      <Typography key={i} sx={{ fontSize: "12px", color: "#94a3b8", mb: 0.3 }}>
                        • {n}
                      </Typography>
                    ))}
                  </AccordionDetails>
                </Accordion>
              )}

              {/* 이주비 정보 */}
              {guide.relocationInfo && (
                <Accordion disableGutters sx={{ bgcolor: "#1e293b", borderRadius: 1 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: "#94a3b8" }} />}>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      <HomeWorkIcon sx={{ color: "#34d399", fontSize: 18 }} />
                      <Typography sx={{ fontSize: "14px", fontWeight: 600, color: "#6ee7b7" }}>
                        이주비 기준
                      </Typography>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails sx={{ pt: 0 }}>
                    <Typography sx={{ fontSize: "13px", fontWeight: 600, color: "#e2e8f0", mb: 0.5 }}>
                      {guide.relocationInfo.title}
                    </Typography>
                    {guide.relocationInfo.items.map((item, i) => (
                      <Typography key={i} sx={{ fontSize: "13px", color: "#94a3b8", mb: 0.3 }}>
                        • {item}
                      </Typography>
                    ))}
                    {guide.relocationInfo.caution && (
                      <Alert severity="warning" sx={{ mt: 1, fontSize: "12px",
                        "& .MuiAlert-message": { fontSize: "12px" } }}>
                        {guide.relocationInfo.caution}
                      </Alert>
                    )}
                  </AccordionDetails>
                </Accordion>
              )}
            </Box>
          </Paper>
        )}
      </Collapse>
    </Box>
  );
}
