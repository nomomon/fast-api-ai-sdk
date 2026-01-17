import { NextResponse } from 'next/server';
import { SUPPORTED_MODELS } from '@/lib/constants';
import { gateway } from '@/lib/gateway';

export async function GET() {
  const allModels = await gateway.getAvailableModels();
  return NextResponse.json({
    models: allModels.models.filter((model) => SUPPORTED_MODELS.includes(model.id)),
  });
}
