import '@/envConfig.ts';
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'standalone',
  async redirects() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.BASE_BACKEND_URL}/api/:path*`,
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
