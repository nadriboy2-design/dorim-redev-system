/** @type {import('next').NextConfig} */
const nextConfig = {
  // 백엔드 API 기본 URL — Vercel 대시보드 env var 없이도 동작하는 빌드타임 기본값
  env: {
    NEXT_PUBLIC_API_URL:
      process.env.NEXT_PUBLIC_API_URL ||
      "https://dorim-redev-backend.onrender.com",
  },

  async rewrites() {
    // 로컬 개발 시에만 프록시 (프로덕션에서는 NEXT_PUBLIC_API_URL 사용)
    if (process.env.NODE_ENV === "development" && !process.env.NEXT_PUBLIC_API_URL) {
      return [
        {
          source: "/api/:path*",
          destination: "http://localhost:8000/api/:path*",
        },
      ];
    }
    return [];
  },

  // 이미지 최적화 허용 도메인
  images: {
    domains: [],
  },
};

export default nextConfig;
