// frontend/app/layout.tsx
import "../styles/globals.css";

export const metadata = {
  title: "Clinical Intelligence Copilot",
  description: "AI-powered clinical record analysis",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}