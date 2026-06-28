"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "../../components/Sidebar";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("jwt_token");
    if (!token) {
      router.push("/login");
    } else {
      setLoading(false);
    }
  }, [router]);

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-void text-cyber">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-2 border-cyber/20 border-t-cyber rounded-full animate-spin shadow-cyber-glow"></div>
          <span className="text-xs font-bold tracking-[0.2em] uppercase animate-pulse">Authenticating Secure Session...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-void text-slate-300 overflow-hidden relative">
      {/* Subtle radial glow in the center of the dark canvas */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-cyber/5 via-void to-void pointer-events-none z-0"></div>
      
      <Sidebar />
      <main className="flex-1 overflow-hidden p-6 z-10 relative">
        {children}
      </main>
    </div>
  );
}