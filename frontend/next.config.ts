// frontend/next.config.ts
import '@/envConfig.ts';
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'standalone',
  async rewrites() {
    // TODO: docker env variable not working, fix later
    const backendUrl = process.env.BASE_BACKEND_URL || 'http://backend:8000';

    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
