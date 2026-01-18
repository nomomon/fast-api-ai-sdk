// frontend/next.config.ts
import '@/envConfig.ts';
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'standalone',
  async rewrites() {
    // Debugging: Log what the server sees
    console.log('Rewriting to Backend URL:', process.env.BASE_BACKEND_URL);

    const backendUrl = process.env.BASE_BACKEND_URL || 'http://localhost:8000';

    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
