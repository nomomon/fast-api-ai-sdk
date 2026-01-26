import type { MetadataRoute } from 'next';
import {
  APP_DESCRIPTION,
  APP_NAME,
  APP_SHORT_NAME,
  BACKGROUND_COLOR,
  getManifestIcons,
  THEME_COLOR,
  URLS,
} from '@/lib/constants/seo';

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: APP_NAME,
    short_name: APP_SHORT_NAME,
    description: APP_DESCRIPTION,
    start_url: URLS.startUrl,
    display: 'standalone',
    background_color: BACKGROUND_COLOR,
    theme_color: THEME_COLOR,
    icons: getManifestIcons(),
  };
}
