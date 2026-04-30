"use client";
import { useState } from "react";
import { DataGrid, GridColDef, GridRenderCellParams } from "@mui/x-data-grid";
import { Switch, Typography, Box, Chip } from "@mui/material";
import { Member, patchConsent } from "@/lib/api";

interface Props {
  members: Member[];
  onConsentChange: (updatedMembers: Member[]) => void;
}

export default function MemberGrid({ members, onConsentChange }: Props) {
  const [rows, setRows] = useState<Member[]>(members);
  const [loadingId, setLoadingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

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

  const columns: GridColDef[] = [
    { field: "member_id", headerName: "번호", width: 80 },
    { field: "address", headerName: "주소", flex: 1, minWidth: 200 },
    {
      field: "rights_value",
      headerName: "권리가액",
      width: 130,
      renderCell: (p: GridRenderCellParams) =>
        `${(p.value as number).toLocaleString()}원`,
    },
    {
      field: "is_sale_target",
      headerName: "분양대상",
      width: 100,
      renderCell: (p: GridRenderCellParams) => (
        <Chip
          label={p.value ? "대상" : "비대상"}
          size="small"
          color={p.value ? "success" : "default"}
          sx={{ fontSize: "14px" }}
        />
      ),
    },
    {
      field: "consent",
      headerName: "동의여부",
      width: 120,
      renderCell: (p: GridRenderCellParams) => (
        <Switch
          checked={!!p.row.consent}
          disabled={loadingId === p.row.member_id}
          onChange={() => handleToggle(p.row.member_id, !!p.row.consent)}
          color="success"
        />
      ),
    },
  ];

  return (
    <Box>
      {error && (
        <Typography
          sx={{
            color: "#ef4444",
            fontSize: "16px",
            mb: 1,
            p: 1,
            bgcolor: "#2d0a0a",
            borderRadius: 1,
          }}
        >
          ⚠️ {error}
        </Typography>
      )}
      <DataGrid
        rows={rows}
        columns={columns}
        getRowId={(r) => r.member_id}
        pageSizeOptions={[10, 20, 50]}
        initialState={{
          pagination: { paginationModel: { pageSize: 10 } },
        }}
        sx={{
          fontSize: "16px",
          "& .MuiDataGrid-columnHeader": { fontSize: "16px" },
        }}
      />
    </Box>
  );
}
