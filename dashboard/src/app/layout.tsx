import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Silver Tier Dashboard - Personal AI Employee",
  description: "Dashboard for managing your Personal AI Employee tasks and approvals",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
