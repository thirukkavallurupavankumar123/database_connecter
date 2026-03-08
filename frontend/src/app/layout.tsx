import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";
import AppShell from "@/components/AppShell";

export const metadata: Metadata = {
  title: "ARGO Analytics — Enterprise GenAI Database Platform",
  description:
    "AI-powered enterprise analytics platform. Connect databases, ask questions in natural language, get insights.",
};

export default function RootLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#0f172a] text-slate-100 antialiased">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
