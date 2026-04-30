"use client";
import { useState, useRef } from "react";
import { Box, Button, Typography, TextField, Alert, CircularProgress, Paper } from "@mui/material";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface ReceiptData {
  date: string;
  store_name: string;
  supply_amount: number;
  vat: number;
  total_amount: number;
  ocr_available: boolean;
}

export default function ReceiptOcr() {
  const [receiptData, setReceiptData] = useState<ReceiptData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (file: File) => {
    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch(`${BASE_URL}/api/ocr/receipt`, {
        method: "POST",
        body: formData,
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.detail?.message ?? "OCR 처리 실패");
      setReceiptData(json.data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "오류 발생");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!receiptData) return;
    const res = await fetch(`${BASE_URL}/api/ocr/generate-pdf`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(receiptData),
    });
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "지출결의서.pdf";
    a.click();
  };

  return (
    <Box sx={{ bgcolor: "#1e293b", p: 2, borderRadius: 2 }}>
      <Typography sx={{ fontSize: "18px", fontWeight: 700, mb: 2 }}>
        🧾 영수증 → 지출결의서 자동 생성
      </Typography>

      <input
        type="file"
        accept="image/*"
        ref={fileRef}
        style={{ display: "none" }}
        onChange={(e) => e.target.files?.[0] && handleUpload(e.target.files[0])}
      />

      <Box
        sx={{ border: "2px dashed #334155", borderRadius: 2, p: 3, textAlign: "center",
              cursor: "pointer", mb: 2, "&:hover": { borderColor: "#3b82f6" } }}
        onClick={() => fileRef.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          const file = e.dataTransfer.files[0];
          if (file) handleUpload(file);
        }}
      >
        {loading ? (
          <CircularProgress size={40} />
        ) : (
          <>
            <Typography sx={{ fontSize: "16px", color: "#94a3b8" }}>
              📸 영수증 이미지를 드래그하거나 클릭하여 업로드
            </Typography>
            <Typography sx={{ fontSize: "14px", color: "#64748b", mt: 1 }}>
              JPG, PNG, GIF 지원
            </Typography>
          </>
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2, fontSize: "15px" }}>{error}</Alert>
      )}

      {receiptData && (
        <Paper sx={{ bgcolor: "#0f172a", p: 2, borderRadius: 1 }}>
          {!receiptData.ocr_available && (
            <Alert severity="info" sx={{ mb: 2, fontSize: "14px" }}>
              OCR 엔진 미설치 — 아래 필드를 직접 입력해주세요
            </Alert>
          )}
          {[
            { label: "일자", key: "date" as const },
            { label: "상호명", key: "store_name" as const },
          ].map(({ label, key }) => (
            <Box key={key} sx={{ mb: 1, display: "flex", alignItems: "center", gap: 2 }}>
              <Typography sx={{ fontSize: "14px", color: "#94a3b8", width: 80 }}>{label}</Typography>
              <TextField
                size="small" value={receiptData[key]}
                onChange={(e) => setReceiptData({ ...receiptData, [key]: e.target.value })}
                sx={{ flex: 1, "& .MuiInputBase-input": { fontSize: "16px" } }}
              />
            </Box>
          ))}
          <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 1, mt: 1 }}>
            <Box sx={{ textAlign: "center" }}>
              <Typography sx={{ fontSize: "12px", color: "#64748b" }}>공급가액</Typography>
              <Typography sx={{ fontSize: "18px", fontWeight: 700 }}>
                {receiptData.supply_amount.toLocaleString()}원
              </Typography>
            </Box>
            <Box sx={{ textAlign: "center" }}>
              <Typography sx={{ fontSize: "12px", color: "#64748b" }}>부가세</Typography>
              <Typography sx={{ fontSize: "18px", fontWeight: 700 }}>
                {receiptData.vat.toLocaleString()}원
              </Typography>
            </Box>
            <Box sx={{ textAlign: "center" }}>
              <Typography sx={{ fontSize: "12px", color: "#64748b" }}>합계</Typography>
              <Typography sx={{ fontSize: "20px", fontWeight: 700, color: "#22c55e" }}>
                {receiptData.total_amount.toLocaleString()}원
              </Typography>
            </Box>
          </Box>
          <Button fullWidth variant="contained" color="success" size="large"
                  sx={{ mt: 2 }} onClick={handleDownloadPdf}>
            📄 지출결의서 PDF 다운로드
          </Button>
        </Paper>
      )}
    </Box>
  );
}
