import "./globals.css";
import { Inter, Nunito_Sans } from "next/font/google";
import { Toaster } from "sonner";
import { cn } from "@/lib/utils";
import { ThemeProvider } from "@/components/theme-provider";

const fontSans = Inter({ subsets: ["latin"], variable: "--font-sans" });

const fontDisplay = Nunito_Sans({
  subsets: ["latin"],
  variable: "--font-display",
});

export const metadata = {
  title: "Assistente de Agendamento Médico",
  description:
    "Use o assistente virtual para agendar consultas e exames de forma rápida e fácil.",
  openGraph: {
    images: [
      {
        url: "/og?title=Assistente de Agendamento Médico",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    images: [
      {
        url: "/og?title=Assistente de Agendamento Médico",
      },
    ],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
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
        >
          {children}
          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  );
}
