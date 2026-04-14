import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Source_Serif_4 } from "next/font/google";
import "./globals.css";
import { Analytics } from "@vercel/analytics/next";
import { Nav } from "@/components/layout/nav";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const sourceSerif = Source_Serif_4({
  variable: "--font-serif",
  subsets: ["latin"],
  weight: ["400", "600", "700"],
});

export const metadata: Metadata = {
  title: "Support Ticket Classification — Method Comparison",
  description:
    "Comparing classification methods for support ticket routing: from TF-IDF to fine-tuned LLMs. Which approach wins, and when?",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} ${sourceSerif.variable} h-full antialiased`}
      style={{ backgroundColor: "#fcfbf7" }}
    >
      <body className="min-h-full flex" style={{ backgroundColor: "#fcfbf7", color: "#1a1917" }}>
        <Nav />
        <main className="flex-1 ml-60 min-h-screen">{children}</main>
        <Analytics />
      </body>
    </html>
  );
}
