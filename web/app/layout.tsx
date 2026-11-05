import type { Metadata, Viewport } from "next";
import { Nunito, Pixelify_Sans } from "next/font/google";
import "./globals.css";

const nunito = Nunito({ subsets: ["latin"], weight: ["600", "700", "800"], variable: "--font-nunito" });
const pixelify = Pixelify_Sans({ subsets: ["latin"], weight: ["500", "700"], variable: "--font-pixelify" });

export const metadata: Metadata = {
  title: "Tuli",
  description: "4 jogos rápidos por dia para acompanhar sua voz e seus movimentos.",
};

export const viewport: Viewport = { width: "device-width", initialScale: 1, themeColor: "#CF3A46" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className={`${nunito.variable} ${pixelify.variable}`}>
      <body className="font-sans antialiased">
        <main className="mx-auto min-h-dvh max-w-md">{children}</main>
      </body>
    </html>
  );
}
