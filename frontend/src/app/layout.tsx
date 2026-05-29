import type { Metadata } from "next";
import { Inter, Playfair_Display } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const playfair = Playfair_Display({ subsets: ["latin"], variable: "--font-playfair" });

export const metadata: Metadata = {
  title: "Aura | AI Jewellery Try-On",
  description: "Experience premium virtual jewellery try-on powered by AI.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${playfair.variable} font-sans bg-zinc-950 text-zinc-50 antialiased selection:bg-amber-900 selection:text-amber-50 min-h-screen flex flex-col`}>
        {children}
      </body>
    </html>
  );
}
