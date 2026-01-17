import { NextResponse } from "next/server";
import { SUPPORTED_MODELS } from "@/lib/constants";

export async function GET() {
  // Return static model list since gateway was removed
  const staticModels = SUPPORTED_MODELS.map(id => ({
    id,
    name: id.split('/').pop() || id,
    provider: id.split('/')[0] || 'unknown'
  }));
  
  return NextResponse.json({
    models: staticModels,
  });
}