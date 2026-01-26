#!/usr/bin/env node

/**
 * Script to generate PNG icons from app-icon.svg
 * Generates: icon-192.png, icon-512.png, and apple-touch-icon.png
 */

import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Try to import sharp, fallback to a message if not available
let sharp;
try {
  sharp = (await import('sharp')).default;
} catch (_error) {
  console.error(
    'Error: sharp is not installed. Please install it by running:',
    '\n  pnpm add -D sharp',
    '\n  or',
    '\n  npm install --save-dev sharp'
  );
  process.exit(1);
}

const svgPath = join(__dirname, '../public/icons/app-icon.svg');
const iconsDir = join(__dirname, '../public/icons');

// Icon sizes to generate
const iconSizes = [
  { name: 'icon-192.png', size: 192 },
  { name: 'icon-512.png', size: 512 },
  { name: 'apple-touch-icon.png', size: 180 },
];

async function generateIcons() {
  try {
    // Read the SVG file
    const svgBuffer = readFileSync(svgPath);

    console.log('Generating icons from app-icon.svg...');

    // Generate each icon size
    for (const { name, size } of iconSizes) {
      const outputPath = join(iconsDir, name);

      await sharp(svgBuffer)
        .resize(size, size, {
          fit: 'contain',
          background: { r: 0, g: 0, b: 0, alpha: 1 }, // Black background
        })
        .png()
        .toFile(outputPath);

      console.log(`✓ Generated ${name} (${size}x${size})`);
    }

    console.log('\n✅ All icons generated successfully!');
  } catch (error) {
    console.error('Error generating icons:', error);
    process.exit(1);
  }
}

generateIcons();
