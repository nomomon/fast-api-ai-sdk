/**
 * SEO and PWA constants for the application
 * Centralized configuration for metadata, manifest, and SEO settings
 */

export const APP_NAME = 'AI Chatbot Demo';
export const APP_SHORT_NAME = 'AI Chatbot';
export const APP_DESCRIPTION = 'A demo chatbot built with the AI SDK by Vercel';

// GitHub URL
// Shameless self-promo
export const GITHUB_URL = {
  url: 'https://github.com/nomomon/fast-api-ai-sdk',
  label: 'nomomon/fast-api-ai-sdk',
} as const;

// Theme colors (using oklch format from globals.css)
// Light mode colors
export const THEME_COLOR_LIGHT = '#ffffff'; // oklch(0.99 0 0) - background color
export const BACKGROUND_COLOR_LIGHT = '#ffffff'; // oklch(0.99 0 0)

// Dark mode colors
export const THEME_COLOR_DARK = '#141414'; // oklch(0.08 0 0) - background color
export const BACKGROUND_COLOR_DARK = '#141414'; // oklch(0.08 0 0)

// For manifest, we'll use light mode as default
export const THEME_COLOR = THEME_COLOR_LIGHT;
export const BACKGROUND_COLOR = BACKGROUND_COLOR_LIGHT;

// Icon paths and sizes
export const ICON_PATHS = {
  svg: '/icons/app-icon.svg',
  icon192: '/icons/icon-192.png',
  icon512: '/icons/icon-512.png',
  appleTouchIcon: '/icons/apple-touch-icon.png',
  favicon: '/favicon.ico',
} as const;

// Icon sizes for manifest
export const ICON_SIZES = {
  small: '192x192',
  large: '512x512',
  apple: '180x180',
} as const;

// URLs
export const URLS = {
  startUrl: '/',
  baseUrl: process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000',
} as const;

// Open Graph and Twitter Card defaults
export const SOCIAL = {
  siteName: APP_NAME,
  type: 'website',
  locale: 'en_US',
} as const;

/**
 * Generate manifest icons array
 * Returns an array of icon objects for PWA manifest
 */
export function getManifestIcons(): Array<{
  src: string;
  sizes: string;
  type: string;
}> {
  return [
    {
      src: ICON_PATHS.icon192,
      sizes: ICON_SIZES.small,
      type: 'image/png',
    },
    {
      src: ICON_PATHS.icon512,
      sizes: ICON_SIZES.large,
      type: 'image/png',
    },
    {
      src: ICON_PATHS.appleTouchIcon,
      sizes: ICON_SIZES.apple,
      type: 'image/png',
    },
  ];
}
