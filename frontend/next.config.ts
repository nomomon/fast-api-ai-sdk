import '@/envConfig.ts';
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  async redirects() {
    return [
      {
        source: '/api/chat',
        destination: `${process.env.BASE_BACKEND_URL}/api/chat`,
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
