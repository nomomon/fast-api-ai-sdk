import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { ThemeProvider } from "next-themes";
import "./globals.css";
import { AuthProvider } from "@/components/providers/session-provider";
import {
	APP_DESCRIPTION,
	APP_NAME,
	ICON_PATHS,
	SOCIAL,
	THEME_COLOR_DARK,
	THEME_COLOR_LIGHT,
	URLS,
} from "@/lib/constants/seo";

const geistSans = Geist({
	variable: "--font-geist-sans",
	subsets: ["latin"],
});

const geistMono = Geist_Mono({
	variable: "--font-geist-mono",
	subsets: ["latin"],
});

export const metadata: Metadata = {
	title: {
		default: APP_NAME,
		template: `%s | ${APP_NAME}`,
	},
	description: APP_DESCRIPTION,
	keywords: ["AI", "Chatbot", "Next.js", "Vercel AI SDK", "FastAPI"],
	authors: [{ name: APP_NAME }],
	creator: APP_NAME,
	metadataBase: new URL(URLS.baseUrl),
	openGraph: {
		type: SOCIAL.type,
		locale: SOCIAL.locale,
		url: URLS.baseUrl,
		siteName: SOCIAL.siteName,
		title: APP_NAME,
		description: APP_DESCRIPTION,
		images: [
			{
				url: ICON_PATHS.icon512,
				width: 512,
				height: 512,
				alt: APP_NAME,
			},
		],
	},
	twitter: {
		card: "summary_large_image",
		title: APP_NAME,
		description: APP_DESCRIPTION,
		images: [ICON_PATHS.icon512],
	},
	icons: {
		icon: [
			{ url: ICON_PATHS.favicon, sizes: "any" },
			{ url: ICON_PATHS.icon192, sizes: "192x192", type: "image/png" },
			{ url: ICON_PATHS.icon512, sizes: "512x512", type: "image/png" },
		],
		apple: [
			{ url: ICON_PATHS.appleTouchIcon, sizes: "180x180", type: "image/png" },
		],
	},
	manifest: "/manifest.json",
};

export const viewport: Viewport = {
	themeColor: [
		{ media: "(prefers-color-scheme: light)", color: THEME_COLOR_LIGHT },
		{ media: "(prefers-color-scheme: dark)", color: THEME_COLOR_DARK },
	],
};
export default function RootLayout({
	children,
}: Readonly<{
	children: React.ReactNode;
}>) {
	return (
		<html lang="en" suppressHydrationWarning>
			<body
				className={`${geistSans.variable} ${geistMono.variable} antialiased`}
			>
				<AuthProvider>
					<ThemeProvider
						attribute="class"
						defaultTheme="system"
						enableSystem
						disableTransitionOnChange
					>
						{children}
					</ThemeProvider>
				</AuthProvider>
			</body>
		</html>
	);
}
