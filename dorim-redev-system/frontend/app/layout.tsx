import type { Metadata } from "next";
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

export const metadata: Metadata = {
  title: "도림사거리 역세권 재개발 통합관리",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>
        <AppRouterCacheProvider>
          <ThemeProvider theme={theme}>
            <CssBaseline />
            {children}
          </ThemeProvider>
        </AppRouterCacheProvider>
      </body>
    </html>
  );
}
