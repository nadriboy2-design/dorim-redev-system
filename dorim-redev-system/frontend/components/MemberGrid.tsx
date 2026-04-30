"use client";
import { useState } from "react";
import { DataGrid, GridColDef, GridRenderCellParams } from "@mui/x-data-grid";
import {
  Switch, Typography, Box, Chip, Button, IconButton,
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Select, MenuItem, FormControl, InputLabel,
  FormControlLabel, Checkbox, Grid, Divider, Alert,
  Tabs, Tab, Paper, Tooltip,
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import CalculateIcon from "@mui/icons-material/Calculate";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import { Member, patchConsent, updateMember } from "@/lib/api";

interface Props {
  members: Member[];
  onConsentChange: (updatedMembers: Member[]) => void;
}

function won(val: number | undefined) {
  if (!val) return "0원";
  return val.toLocaleString() + "원";
}

// ── 개인 상세 편집 모달 ────────────────────────────────────────────────────
function MemberDetailModal({
  member,
  open,
  onClose,
  onSave,
}: {
  member: Member;
  open: boolean;
  onClose: () => void;
  onSave: (updated: Member) => void;
}) {
  const [draft, setDraft] = useState<Member>({ ...member });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState(0);

  const set = (field: keyof Member, value: unknown) =>
    setDraft((prev) => ({ ...prev, [field]: value }));

  // 비례율 변경 시 권리가액·이주비·청산금 자동 재계산
  const recalc = (prevVal?: number, propRate?: number, allocPrice?: number) => {
    const pv = prevVal ?? draft.prev_asset_value;
    const pr = propRate ?? draft.proportional_rate;
    const ap = allocPrice ?? draft.estimated_alloc_price;
    const rights = Math.round(pv * pr / 100);
    const reloc  = Math.round(rights * 0.6);
    const settle = ap > 0 ? ap - rights : 0;
    setDraft((d) => ({
      ...d,
      prev_asset_value: pv,
      proportional_rate: pr,
      estimated_alloc_price: ap,
      rights_value: rights,
      relocation_cost: reloc,
      settlement_amount: settle,
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      const updated = await updateMember(draft.member_id, draft);
      onSave(updated);
      onClose();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "저장 실패");
    } finally {
      setSaving(false);
    }
  };

  const settlColor = draft.settlement_amount > 0 ? "#ef4444" : draft.settlement_amount < 0 ? "#22c55e" : "#94a3b8";
  const settlLabel = draft.settlement_amount > 0
    ? `납부 ${won(draft.settlement_amount)}`
    : draft.settlement_amount < 0
    ? `환급 ${won(Math.abs(draft.settlement_amount))}`
    : "미산정";

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth
      PaperProps={{ sx: { bgcolor: "#0f172a", color: "#e2e8f0" } }}>
      <DialogTitle sx={{ borderBottom: "1px solid #334155", pb: 1 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <Typography sx={{ fontSize: "18px", fontWeight: 700 }}>
            조합원 상세 — {draft.name} ({draft.member_id})
          </Typography>
          <Chip
            label={draft.ownership_type}
            size="small"
            sx={{ bgcolor: "#1e293b", color: "#94a3b8", fontSize: "12px" }}
          />
          {draft.has_illegal_building && (
            <Chip label="무허가건물" size="small" color="error" sx={{ fontSize: "12px" }} />
          )}
        </Box>
      </DialogTitle>

      <Tabs value={tab} onChange={(_, v) => setTab(v)}
        sx={{ bgcolor: "#1e293b", "& .MuiTab-root": { fontSize: "13px", color: "#94a3b8" },
              "& .Mui-selected": { color: "#60a5fa !important" } }}>
        <Tab label="기본정보" />
        <Tab label="재산정보" />
        <Tab label="권리분석" />
        <Tab label="동의·메모" />
      </Tabs>

      <DialogContent sx={{ pt: 2 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2, fontSize: "14px" }}>{error}</Alert>
        )}

        {/* ── 탭 0: 기본정보 ── */}
        {tab === 0 && (
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <TextField fullWidth label="성명" value={draft.name}
                onChange={(e) => set("name", e.target.value)}
                InputLabelProps={{ sx: { color: "#94a3b8" } }}
                inputProps={{ style: { color: "#e2e8f0", fontSize: "14px" } }}
                sx={{ "& .MuiOutlinedInput-root": { "& fieldset": { borderColor: "#334155" } } }}
              />
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="연락처" value={draft.phone}
                onChange={(e) => set("phone", e.target.value)}
                InputLabelProps={{ sx: { color: "#94a3b8" } }}
                inputProps={{ style: { color: "#e2e8f0", fontSize: "14px" } }}
                sx={{ "& .MuiOutlinedInput-root": { "& fieldset": { borderColor: "#334155" } } }}
              />
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="생년월일" value={draft.birth_date}
                placeholder="YYYY-MM-DD"
                onChange={(e) => set("birth_date", e.target.value)}
                InputLabelProps={{ sx: { color: "#94a3b8" } }}
                inputProps={{ style: { color: "#e2e8f0", fontSize: "14px" } }}
                sx={{ "& .MuiOutlinedInput-root": { "& fieldset": { borderColor: "#334155" } } }}
              />
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel sx={{ color: "#94a3b8", fontSize: "14px" }}>소유유형</InputLabel>
                <Select value={draft.ownership_type}
                  onChange={(e) => set("ownership_type", e.target.value)}
                  label="소유유형"
                  sx={{ color: "#e2e8f0", fontSize: "14px",
                    "& .MuiOutlinedInput-notchedOutline": { borderColor: "#334155" } }}>
                  {["토지+건물","토지만","건물만","무허가건물"].map((v) => (
                    <MenuItem key={v} value={v}>{v}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth label="물건지 주소" value={draft.address}
                onChange={(e) => set("address", e.target.value)}
                InputLabelProps={{ sx: { color: "#94a3b8" } }}
                inputProps={{ style: { color: "#e2e8f0", fontSize: "14px" } }}
                sx={{ "& .MuiOutlinedInput-root": { "& fieldset": { borderColor: "#334155" } } }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth label="현재 거주지" value={draft.current_address}
                onChange={(e) => set("current_address", e.target.value)}
                InputLabelProps={{ sx: { color: "#94a3b8" } }}
                inputProps={{ style: { color: "#e2e8f0", fontSize: "14px" } }}
                sx={{ "& .MuiOutlinedInput-root": { "& fieldset": { borderColor: "#334155" } } }}
              />
            </Grid>
            <Grid item xs={6}>
              <FormControlLabel
                control={
                  <Checkbox checked={!!draft.has_illegal_building}
                    onChange={(e) => set("has_illegal_building", e.target.checked)}
                    sx={{ color: "#94a3b8" }} />
                }
                label={<Typography sx={{ fontSize: "14px", color: "#e2e8f0" }}>무허가건물 소유</Typography>}
              />
            </Grid>
          </Grid>
        )}

        {/* ── 탭 1: 재산정보 ── */}
        {tab === 1 && (
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <TextField fullWidth label="토지면적 (㎡)" type="number"
                value={draft.land_area}
                onChange={(e) => set("land_area", parseFloat(e.target.value) || 0)}
                InputLabelProps={{ sx: { color: "#94a3b8" } }}
                inputProps={{ style: { color: "#e2e8f0", fontSize: "14px" } }}
                sx={{ "& .MuiOutlinedInput-root": { "& fieldset": { borderColor: "#334155" } } }}
              />
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="건물면적 (㎡)" type="number"
                value={draft.building_area}
                onChange={(e) => set("building_area", parseFloat(e.target.value) || 0)}
                InputLabelProps={{ sx: { color: "#94a3b8" } }}
                inputProps={{ style: { color: "#e2e8f0", fontSize: "14px" } }}
                sx={{ "& .MuiOutlinedInput-root": { "& fieldset": { borderColor: "#334155" } } }}
              />
            </Grid>
            <Grid item xs={12}>
              <Divider sx={{ borderColor: "#334155", my: 1 }} />
              <Typography sx={{ fontSize: "13px", color: "#94a3b8", mb: 1 }}>
                종전자산평가액 또는 비례율 변경 시 권리가액·이주비·청산금이 자동 재계산됩니다.
              </Typography>
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="종전자산평가액 (원)" type="number"
                value={draft.prev_asset_value}
                onChange={(e) => recalc(parseInt(e.target.value) || 0)}
                InputLabelProps={{ sx: { color: "#94a3b8" } }}
                inputProps={{ style: { color: "#e2e8f0", fontSize: "14px" } }}
                sx={{ "& .MuiOutlinedInput-root": { "& fieldset": { borderColor: "#334155" } } }}
                helperText={<span style={{ color: "#64748b", fontSize: "11px" }}>감정평가 결과 기준</span>}
              />
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="비례율 (%)" type="number"
                value={draft.proportional_rate}
                onChange={(e) => recalc(undefined, parseFloat(e.target.value) || 110)}
                InputLabelProps={{ sx: { color: "#94a3b8" } }}
                inputProps={{ style: { color: "#60a5fa", fontSize: "14px", fontWeight: 700 }, step: "0.01" }}
                sx={{ "& .MuiOutlinedInput-root": { "& fieldset": { borderColor: "#334155" } } }}
                helperText={<span style={{ color: "#64748b", fontSize: "11px" }}>(종후총가액-총사업비)/종전총가액×100</span>}
              />
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="분양예정가액 (원)" type="number"
                value={draft.estimated_alloc_price}
                onChange={(e) => recalc(undefined, undefined, parseInt(e.target.value) || 0)}
                InputLabelProps={{ sx: { color: "#94a3b8" } }}
                inputProps={{ style: { color: "#e2e8f0", fontSize: "14px" } }}
                sx={{ "& .MuiOutlinedInput-root": { "& fieldset": { borderColor: "#334155" } } }}
              />
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel sx={{ color: "#94a3b8", fontSize: "14px" }}>분양신청 타입</InputLabel>
                <Select value={draft.alloc_area_type}
                  onChange={(e) => set("alloc_area_type", e.target.value)}
                  label="분양신청 타입"
                  sx={{ color: "#e2e8f0", fontSize: "14px",
                    "& .MuiOutlinedInput-notchedOutline": { borderColor: "#334155" } }}>
                  {["59A","84A","84B","120A","미신청"].map((v) => (
                    <MenuItem key={v} value={v}>{v}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        )}

        {/* ── 탭 2: 권리분석 ── */}
        {tab === 2 && (
          <Box>
            <Alert severity="info" icon={<CalculateIcon />}
              sx={{ mb: 2, fontSize: "13px", "& .MuiAlert-message": { fontSize: "13px" } }}>
              비례율 기반 개인별 권리분석 — 종전자산평가액 변경 시 자동 재계산됩니다.
            </Alert>

            {/* 계산 카드 */}
            {[
              { label: "종전자산평가액", val: draft.prev_asset_value, color: "#94a3b8", desc: "감정평가 결과" },
              { label: `비례율 (${draft.proportional_rate.toFixed(2)}%)`, val: null, color: "#60a5fa", desc: "(종후자산-총사업비)÷종전자산×100" },
              { label: "권리가액", val: draft.rights_value, color: "#60a5fa", desc: "종전평가액 × 비례율", formula: true },
              { label: "이주비 (권리가액×60%)", val: draft.relocation_cost, color: "#34d399", desc: "시중은행 협약대출 한도" },
              { label: "분양예정가액", val: draft.estimated_alloc_price, color: "#f59e0b", desc: draft.alloc_area_type || "미신청" },
              { label: "청산금", val: draft.settlement_amount, color: settlColor, desc: "분양예정가액 - 권리가액" },
            ].map((row, i) => (
              <Paper key={i} elevation={0} sx={{
                bgcolor: "#1e293b", p: 1.5, mb: 1, borderRadius: 1,
                display: "flex", justifyContent: "space-between", alignItems: "center",
                border: row.label === "청산금" ? `1px solid ${settlColor}40` : "none",
              }}>
                <Box>
                  <Typography sx={{ fontSize: "13px", color: "#94a3b8" }}>{row.label}</Typography>
                  <Typography sx={{ fontSize: "11px", color: "#475569" }}>{row.desc}</Typography>
                </Box>
                <Typography sx={{ fontSize: "16px", fontWeight: 700, color: row.color }}>
                  {row.val !== null ? won(row.val) : "—"}
                </Typography>
              </Paper>
            ))}

            {/* 청산금 요약 */}
            <Box sx={{
              mt: 1, p: 1.5, borderRadius: 1,
              bgcolor: draft.settlement_amount > 0 ? "#2d0a0a" : draft.settlement_amount < 0 ? "#0a2d15" : "#1e293b",
              border: `1px solid ${settlColor}`,
            }}>
              <Typography sx={{ fontSize: "15px", fontWeight: 700, color: settlColor, textAlign: "center" }}>
                청산금: {settlLabel}
              </Typography>
              <Typography sx={{ fontSize: "11px", color: "#64748b", textAlign: "center", mt: 0.3 }}>
                {draft.settlement_amount > 0 ? "추가 납부 → 분할납부 가능 (계약 협의)"
                  : draft.settlement_amount < 0 ? "조합으로부터 환급 수령"
                  : "분양 미신청 → 현금청산 대상"}
              </Typography>
            </Box>

            <FormControlLabel
              sx={{ mt: 2 }}
              control={
                <Checkbox checked={!!draft.is_sale_target}
                  onChange={(e) => set("is_sale_target", e.target.checked)}
                  sx={{ color: "#94a3b8" }} />
              }
              label={<Typography sx={{ fontSize: "14px", color: "#e2e8f0" }}>분양대상 여부</Typography>}
            />
          </Box>
        )}

        {/* ── 탭 3: 동의·메모 ── */}
        {tab === 3 && (
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Box sx={{
                display: "flex", alignItems: "center", gap: 2,
                bgcolor: "#1e293b", p: 2, borderRadius: 1,
              }}>
                <Switch
                  checked={!!draft.consent}
                  onChange={(e) => set("consent", e.target.checked)}
                  color="success"
                />
                <Typography sx={{ fontSize: "16px", color: draft.consent ? "#22c55e" : "#94a3b8", fontWeight: 600 }}>
                  {draft.consent ? "동의 완료" : "미동의"}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="동의 날짜" value={draft.consent_date}
                placeholder="YYYY-MM-DD"
                onChange={(e) => set("consent_date", e.target.value)}
                InputLabelProps={{ sx: { color: "#94a3b8" } }}
                inputProps={{ style: { color: "#e2e8f0", fontSize: "14px" } }}
                sx={{ "& .MuiOutlinedInput-root": { "& fieldset": { borderColor: "#334155" } } }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth multiline rows={4} label="특이사항 및 메모"
                value={draft.memo}
                onChange={(e) => set("memo", e.target.value)}
                InputLabelProps={{ sx: { color: "#94a3b8" } }}
                inputProps={{ style: { color: "#e2e8f0", fontSize: "14px" } }}
                sx={{ "& .MuiOutlinedInput-root": { "& fieldset": { borderColor: "#334155" } } }}
                placeholder="소송 현황, 연락 불가 사유, 특수 상황 등"
              />
            </Grid>
          </Grid>
        )}
      </DialogContent>

      <DialogActions sx={{ borderTop: "1px solid #334155", px: 3, py: 2 }}>
        <Button onClick={onClose} sx={{ color: "#94a3b8" }}>취소</Button>
        <Button variant="contained" onClick={handleSave} disabled={saving} sx={{ fontSize: "14px" }}>
          {saving ? "저장 중..." : "저장"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

// ── MemberGrid 메인 ───────────────────────────────────────────────────────────
export default function MemberGrid({ members, onConsentChange }: Props) {
  const [rows, setRows] = useState<Member[]>(members);
  const [loadingId, setLoadingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedMember, setSelectedMember] = useState<Member | null>(null);

  const handleToggle = async (memberId: number, currentConsent: boolean) => {
    setLoadingId(memberId);
    setError(null);
    try {
      await patchConsent(memberId, !currentConsent);
      const updated = rows.map((m) =>
        m.member_id === memberId ? { ...m, consent: !currentConsent } : m
      );
      setRows(updated);
      onConsentChange(updated);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "오류 발생");
    } finally {
      setLoadingId(null);
    }
  };

  const handleSave = (updated: Member) => {
    const next = rows.map((m) => m.member_id === updated.member_id ? updated : m);
    setRows(next);
    onConsentChange(next);
  };

  // ── 통계 요약 ────────────────────────────────────────────────────────────
  const totalPrevAsset = rows.reduce((s, m) => s + (m.prev_asset_value || 0), 0);
  const totalRights    = rows.reduce((s, m) => s + (m.rights_value || 0), 0);
  const totalReloc     = rows.reduce((s, m) => s + (m.relocation_cost || 0), 0);
  const avgPropRate    = rows.length
    ? rows.reduce((s, m) => s + (m.proportional_rate || 0), 0) / rows.length
    : 0;

  const columns: GridColDef[] = [
    { field: "member_id", headerName: "번호", width: 70 },
    { field: "name", headerName: "성명", width: 80 },
    { field: "address", headerName: "주소 (물건지)", flex: 1, minWidth: 180 },
    {
      field: "ownership_type", headerName: "소유유형", width: 100,
      renderCell: (p: GridRenderCellParams) => (
        <Chip label={p.value as string} size="small"
          sx={{ fontSize: "11px", bgcolor: "#1e293b", color: "#94a3b8" }} />
      ),
    },
    {
      field: "prev_asset_value", headerName: "종전평가액", width: 130,
      renderCell: (p: GridRenderCellParams) =>
        <Typography sx={{ fontSize: "13px" }}>{won(p.value as number)}</Typography>,
    },
    {
      field: "proportional_rate", headerName: "비례율", width: 80,
      renderCell: (p: GridRenderCellParams) => (
        <Typography sx={{ fontSize: "13px", color: "#60a5fa", fontWeight: 700 }}>
          {(p.value as number)?.toFixed(1)}%
        </Typography>
      ),
    },
    {
      field: "rights_value", headerName: "권리가액", width: 130,
      renderCell: (p: GridRenderCellParams) =>
        <Typography sx={{ fontSize: "13px", color: "#60a5fa" }}>{won(p.value as number)}</Typography>,
    },
    {
      field: "relocation_cost", headerName: "이주비(60%)", width: 130,
      renderCell: (p: GridRenderCellParams) =>
        <Typography sx={{ fontSize: "13px", color: "#34d399" }}>{won(p.value as number)}</Typography>,
    },
    {
      field: "settlement_amount", headerName: "청산금", width: 130,
      renderCell: (p: GridRenderCellParams) => {
        const v = p.value as number;
        const c = v > 0 ? "#ef4444" : v < 0 ? "#22c55e" : "#94a3b8";
        const l = v > 0 ? `납부 ${won(v)}` : v < 0 ? `환급 ${won(Math.abs(v))}` : "미산정";
        return <Typography sx={{ fontSize: "12px", color: c, fontWeight: 600 }}>{l}</Typography>;
      },
    },
    {
      field: "is_sale_target", headerName: "분양", width: 70,
      renderCell: (p: GridRenderCellParams) => (
        <Chip label={p.value ? "대상" : "비대상"} size="small"
          color={p.value ? "success" : "default"}
          sx={{ fontSize: "11px" }} />
      ),
    },
    {
      field: "consent", headerName: "동의", width: 130,
      renderCell: (p: GridRenderCellParams) => (
        <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
          <Switch checked={!!p.row.consent} size="small"
            disabled={loadingId === p.row.member_id}
            onChange={() => handleToggle(p.row.member_id, !!p.row.consent)}
            color="success" />
          <Typography sx={{ fontSize: "12px", color: p.row.consent ? "#22c55e" : "#94a3b8" }}>
            {p.row.consent ? "동의" : "미동의"}
          </Typography>
        </Box>
      ),
    },
    {
      field: "actions", headerName: "상세", width: 70, sortable: false,
      renderCell: (p: GridRenderCellParams) => (
        <Tooltip title="상세 편집">
          <IconButton size="small" onClick={() => setSelectedMember(p.row as Member)}
            sx={{ color: "#60a5fa" }}>
            <EditIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      ),
    },
  ];

  return (
    <Box>
      {/* 통계 요약 바 */}
      <Box sx={{
        display: "grid", gridTemplateColumns: "repeat(4, 1fr)",
        gap: 1, mb: 2,
      }}>
        {[
          { label: "비례율 (평균)", val: `${avgPropRate.toFixed(1)}%`, color: "#60a5fa" },
          { label: "종전자산 합계", val: won(totalPrevAsset), color: "#94a3b8" },
          { label: "권리가액 합계", val: won(totalRights), color: "#60a5fa" },
          { label: "이주비 합계", val: won(totalReloc), color: "#34d399" },
        ].map((s) => (
          <Box key={s.label} sx={{
            bgcolor: "#1e293b", p: 1.5, borderRadius: 1, textAlign: "center",
          }}>
            <Typography sx={{ fontSize: "18px", fontWeight: 700, color: s.color }}>{s.val}</Typography>
            <Typography sx={{ fontSize: "12px", color: "#64748b" }}>{s.label}</Typography>
          </Box>
        ))}
      </Box>

      {error && (
        <Typography sx={{ color: "#ef4444", fontSize: "14px", mb: 1, p: 1, bgcolor: "#2d0a0a", borderRadius: 1 }}>
          ⚠️ {error}
        </Typography>
      )}

      <DataGrid
        rows={rows}
        columns={columns}
        getRowId={(r) => r.member_id}
        pageSizeOptions={[10, 20, 50]}
        initialState={{ pagination: { paginationModel: { pageSize: 10 } } }}
        sx={{
          fontSize: "13px",
          "& .MuiDataGrid-columnHeader": { fontSize: "13px", bgcolor: "#1e293b" },
          "& .MuiDataGrid-row:hover": { bgcolor: "#1e293b40" },
          bgcolor: "#0f172a",
          color: "#e2e8f0",
          border: "1px solid #334155",
        }}
      />

      {/* 상세 편집 모달 */}
      {selectedMember && (
        <MemberDetailModal
          member={selectedMember}
          open={!!selectedMember}
          onClose={() => setSelectedMember(null)}
          onSave={handleSave}
        />
      )}
    </Box>
  );
}
