'use client';

import { McpDashboard } from '@/components/mcp';
import { SkillDashboard } from '@/components/skill';

export default function DashboardPage() {
  return (
    <div className="flex flex-1 flex-col gap-8 p-4">
      <div className="flex items-center justify-between mt-12">
        <h1 className="text-2xl font-semibold">Dashboard</h1>
      </div>
      <McpDashboard />
      <SkillDashboard />
    </div>
  );
}
