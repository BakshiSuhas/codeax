import type { Metadata } from "next";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "Codeax",
  description: "Autonomous GitHub code analysis platform"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
