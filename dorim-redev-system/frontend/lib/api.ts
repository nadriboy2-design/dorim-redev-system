const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function fetchMembers() {
  const res = await fetch(`${BASE_URL}/api/members`);
  if (!res.ok) throw new Error("조합원 목록 조회 실패");
  const json = await res.json();
  return json.data as Member[];
}

export async function fetchMember(memberId: number) {
  const res = await fetch(`${BASE_URL}/api/members/${memberId}`);
  if (!res.ok) throw new Error("조합원 상세 조회 실패");
  const json = await res.json();
  return json.data as Member;
}

export async function fetchConsentRate() {
  const res = await fetch(`${BASE_URL}/api/consent-rate`);
  if (!res.ok) throw new Error("동의율 조회 실패");
  const json = await res.json();
  return json.data as ConsentRate;
}

export async function fetchWorkflowStatus() {
  const res = await fetch(`${BASE_URL}/api/workflow/status`);
  if (!res.ok) throw new Error("워크플로우 상태 조회 실패");
  const json = await res.json();
  return json.data as WorkflowStatus;
}

export async function fetchProportionalStats() {
  const res = await fetch(`${BASE_URL}/api/proportional-stats`);
  if (!res.ok) throw new Error("비례율 통계 조회 실패");
  const json = await res.json();
  return json.data as ProportionalStats;
}

export async function patchConsent(memberId: number, consent: boolean) {
  const res = await fetch(`${BASE_URL}/api/members/${memberId}/consent`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ consent }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail?.message ?? "동의여부 수정 실패");
  }
  return res.json();
}

export async function updateMember(memberId: number, fields: Partial<Member>) {
  const res = await fetch(`${BASE_URL}/api/members/${memberId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(fields),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail?.message ?? "조합원 정보 수정 실패");
  }
  const json = await res.json();
  return json.data as Member;
}

export async function generateDoc(docType: string, hasCostVerification = false) {
  const res = await fetch(`${BASE_URL}/api/workflow/generate-doc`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ doc_type: docType, has_cost_verification: hasCostVerification }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail?.message ?? "문서 생성 실패");
  }
  return res.blob();
}

// ── 타입 정의 ─────────────────────────────────────────────────────────────────
export interface Member {
  member_id: number;
  name: string;
  phone: string;
  birth_date: string;
  address: string;
  current_address: string;
  ownership_type: string;       // 토지+건물 / 토지만 / 건물만 / 무허가건물
  land_area: number;            // 토지면적(㎡)
  building_area: number;        // 건물면적(㎡)
  has_illegal_building: boolean;
  prev_asset_value: number;     // 종전자산평가액(원)
  proportional_rate: number;    // 비례율(%)
  rights_value: number;         // 권리가액(원) = 종전평가액 × 비례율
  is_sale_target: boolean;      // 분양대상
  alloc_area_type: string;      // 분양신청타입 (59A/84A/84B/120A/미신청)
  estimated_alloc_price: number;// 분양예정가액(원)
  relocation_cost: number;      // 이주비(원) = 권리가액 × 60%
  settlement_amount: number;    // 청산금(원) = 분양예정가액 - 권리가액
  consent: boolean;
  consent_date: string;
  memo: string;
}

export interface ConsentRate {
  total: number;
  consented: number;
  rate: number;
}

export interface ProportionalStats {
  proportional_rate: number;
  total_prev_asset_value: number;
  total_rights_value: number;
  total_relocation_cost: number;
  total_settlement_payment: number;
  total_settlement_refund: number;
  member_count: number;
}

export interface WorkflowStatus {
  current_stage: string;
  stage_name: string;
  consent_threshold: number;
  required_docs: string[];
  consent_rate: ConsentRate;
  is_threshold_met: boolean;
}
