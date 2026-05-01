/** @type {import('next').NextConfig} */
const nextConfig = {
  // Vercel 배포 시 외부 백엔드 API를 프록시로 처리
  // NEXT_PUBLIC_API_URL 환경 변수로 백엔드 주소 설정
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
