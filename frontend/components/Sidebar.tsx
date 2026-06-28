"use client";
import { usePathname } from "next/navigation";
import Link from "next/link";

export default function Sidebar() {
  const pathname = usePathname();
  
  const navItems = [
    { name: "Dashboard", path: "/dashboard", icon: "◱" },
    { name: "Reports", path: "/dashboard/reports", icon: "▤" },
    { name: "Upload", path: "/upload", icon: "⇪" },
  ];

  return (
    <div className="w-64 bg-void/90 backdrop-blur-xl border-r border-glassBorder text-slate-400 h-screen flex flex-col p-6 relative z-20 shadow-2xl">
      
      {/* System Brand Identity */}
      <div className="mb-12 flex items-center gap-3">
        <div className="w-2 h-2 rounded-full bg-cyber shadow-cyber-glow animate-pulse"></div>
        <h1 className="text-xs font-bold tracking-[0.2em] text-white uppercase">
          Clinical<span className="text-cyber drop-shadow-[0_0_8px_rgba(0,240,255,0.8)]">Copilot</span>
        </h1>
      </div>

      <nav className="flex-1 space-y-3">
        {navItems.map((item) => {
          const isActive = pathname === item.path;
          return (
            <Link 
              key={item.path}
              href={item.path}
              className={`flex items-center gap-4 px-4 py-3 rounded-r-md transition-all duration-300 text-xs font-bold tracking-wider uppercase border-l-2 ${
                isActive 
                  ? "bg-cyber/10 border-cyber text-cyber shadow-[inset_4px_0_0_rgba(0,240,255,0.1)]" 
                  : "border-transparent text-slate-500 hover:bg-slate-900/80 hover:text-slate-300 hover:border-slate-700"
              }`}
            >
              <span className="text-lg opacity-80">{item.icon}</span>
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* Logout Action */}
      <div className="mt-auto border-t border-glassBorder pt-6">
        <button 
          onClick={() => { localStorage.removeItem("jwt_token"); window.location.href = "/login"; }}
          className="w-full text-left text-xs font-bold tracking-wider uppercase text-slate-600 hover:text-neon hover:drop-shadow-[0_0_8px_rgba(255,0,85,0.8)] transition-all duration-300 flex items-center gap-3"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-neon/50"></span>
          Terminate Session
        </button>
      </div>
    </div>
  );
}