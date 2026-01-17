import { SUPPORTED_MODELS } from '@/lib/constants';
import { gateway } from '@/lib/gateway';
import { NextResponse } from 'next/server';

export async function GET() {
  const allModels = await gateway.getAvailableModels();
  return NextResponse.json({
    models: allModels.models.filter((model) => SUPPORTED_MODELS.includes(model.id)),
  });
}
