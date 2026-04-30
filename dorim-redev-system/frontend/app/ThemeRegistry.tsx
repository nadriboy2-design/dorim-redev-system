"use client";
import { AppRouterCacheProvider } from "@mui/material-nextjs/v14-appRouter";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";

const theme = createTheme({
  typography: {
    fontSize: 16,
    body1: { fontSize: "16px" },
    body2: { fontSize: "16px" },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          minHeight: "44px",
          fontSize: "16px",
        },
      },
    },
  },
  palette: {
    mode: "dark",
    primary: { main: "#3b82f6" },
    success: { main: "#22c55e" },
    error: { main: "#ef4444" },
  },
});

export default function ThemeRegistry({ children }: { children: React.ReactNode }) {
  return (
    <AppRouterCacheProvider>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </AppRouterCacheProvider>
  );
}
