// dorim-redev-system/frontend/components/LegalChat.tsx
"use client";
import { useState } from "react";
import { Box, TextField, Button, Typography, CircularProgress, Alert, Divider } from "@mui/material";

interface RagResult {
  answer: string;
  sources: { source: string; excerpt: string }[];
}

export default function LegalChat() {
  const [question, setQuestion]   = useState("");
  const [result, setResult]       = useState<RagResult | null>(null);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState<string | null>(null);

  const handleQuery = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("http://localhost:8000/api/rag/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.detail?.message ?? "질의 실패");
      setResult(json.data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "오류 발생");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ bgcolor: "#1e293b", p: 2, borderRadius: 2 }}>
      <Typography sx={{ fontSize: "18px", fontWeight: 700, mb: 1.5 }}>
        🤖 AI 법률 비서에게 묻기
      </Typography>
      <TextField
        fullWidth multiline rows={3}
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="예: 임원 해임 총회 소집 요건이 어떻게 되나요?"
        sx={{ mb: 1, "& .MuiInputBase-input": { fontSize: "16px" } }}
      />
      <Button fullWidth variant="contained" size="large"
              onClick={handleQuery} disabled={loading || !question.trim()}>
        {loading ? <CircularProgress size={20} /> : "질의하기"}
      </Button>

      {error && <Alert severity="error" sx={{ mt: 2, fontSize: "16px" }}>오류: {error}</Alert>}

      {result && (
        <Box sx={{ mt: 2 }}>
          <Divider sx={{ mb: 2 }} />
          <Typography sx={{ fontSize: "16px", whiteSpace: "pre-wrap", lineHeight: 1.8 }}>
            {result.answer}
          </Typography>
          <Box sx={{ mt: 2 }}>
            <Typography sx={{ fontSize: "16px", color: "#94a3b8", mb: 1 }}>📚 참고 법령</Typography>
            {result.sources.map((s, i) => (
              <Typography key={i} sx={{ fontSize: "16px", color: "#94a3b8", mb: 0.5 }}>
                [{s.source}] {s.excerpt}...
              </Typography>
            ))}
          </Box>
        </Box>
      )}
    </Box>
  );
}
