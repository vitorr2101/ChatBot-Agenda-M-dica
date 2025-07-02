import "./globals.css";
import type { Metadata } from "next";
import { Inter, Nunito_Sans } from "next/font/google";
import { Toaster } from "sonner";

import { ThemeProvider } from "@/components/theme-provider";
import { cn } from "@/lib/utils";

const fontSans = Inter({ subsets: ["latin"], variable: "--font-sans" });

const fontDisplay = Nunito_Sans({
  subsets: ["latin"],
  variable: "--font-display",
});

const siteConfig = {
  name: "Ampla Saúde",
  description:
    "Use o assistente virtual para agendar consultas e exames de forma rápida e fácil.",
  // !TODO: Replace with your actual domain
  url: "http://localhost:3000",
};

export const metadata: Metadata = {
  metadataBase: new URL(siteConfig.url),
  title: {
    default: `Assistente de Agendamento | ${siteConfig.name}`,
    template: `%s | ${siteConfig.name}`,
  },
  description: siteConfig.description,
  keywords: [
    "agendamento médico",
    "consultas",
    "exames",
    "saúde",
    "clínica",
    "assistente virtual",
    "chatbot",
  ],
  authors: [
    {
      name: "Ampla Saúde",
      url: siteConfig.url,
    },
  ],
  creator: "Ampla Saúde",
  openGraph: {
    type: "website",
    locale: "pt_BR",
    url: siteConfig.url,
    title: siteConfig.name,
    description: siteConfig.description,
    siteName: siteConfig.name,
    images: [
      {
        url: `/og?title=Assistente de Agendamento Médico`,
        width: 1200,
        height: 630,
        alt: siteConfig.name,
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: siteConfig.name,
    description: siteConfig.description,
    images: [`/og?title=Assistente de Agendamento Médico`],
  },
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <body
        className={cn(
          fontSans.variable,
          fontDisplay.variable,
          "font-sans antialiased",
        )}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  );
}
