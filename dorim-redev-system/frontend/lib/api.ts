const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function fetchMembers() {
  const res = await fetch(`${BASE_URL}/api/members`);
  if (!res.ok) throw new Error("조합원 목록 조회 실패");
  const json = await res.json();
  return json.data as Member[];
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

// ── 타입 정의 ────────────────────────────────
export interface Member {
  member_id: number;
  address: string;
  birth_date: string;
  is_sale_target: boolean;
  rights_value: number;
  consent: boolean;
}

export interface ConsentRate {
  total: number;
  consented: number;
  rate: number;
}

export interface WorkflowStatus {
  current_stage: string;
  stage_name: string;
  consent_threshold: number;
  required_docs: string[];
  consent_rate: ConsentRate;
  is_threshold_met: boolean;
}
