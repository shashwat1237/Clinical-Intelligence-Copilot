import React from "react";

export function Button({ className = "", variant = "primary", ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "secondary" }) {
  const base = "inline-flex items-center justify-center rounded-md text-xs font-bold transition-all duration-300 disabled:opacity-50 disabled:pointer-events-none px-5 py-2.5 uppercase tracking-widest backdrop-blur-sm";
  const variants = {
    primary: "bg-cyber/10 text-cyber border border-cyber/50 hover:bg-cyber hover:text-void hover:shadow-cyber-glow",
    secondary: "bg-slate-900/50 text-slate-400 border border-slate-800 hover:text-cyber hover:border-cyber/50"
  };
  return <button className={`${base} ${variants[variant]} ${className}`} {...props} />;
}

export function Input({ className = "", ...props }: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input 
      className={`flex h-11 w-full rounded-md border border-slate-800 bg-void/80 px-4 py-2 text-sm text-slate-200 placeholder:text-slate-600 transition-all duration-300 focus:outline-none focus:border-cyber focus:shadow-cyber-glow focus:bg-void disabled:cursor-not-allowed disabled:opacity-50 ${className}`} 
      {...props} 
    />
  );
}

export function Card({ className = "", children }: { className?: string, children: React.ReactNode }) {
  return (
    <div className={`bg-glass backdrop-blur-md rounded-xl border border-glassBorder shadow-2xl ${className}`}>
      {children}
    </div>
  );
}

export function Badge({ className = "", variant = "default", children, ...props }: React.HTMLAttributes<HTMLSpanElement> & { variant?: "default" | "destructive" }) {
  const base = "inline-flex items-center rounded-sm border px-2.5 py-1 text-[10px] font-bold tracking-widest transition-all backdrop-blur-sm uppercase";
  const variants = {
    default: "border-cyber/30 bg-cyber/10 text-cyber shadow-[0_0_10px_rgba(0,240,255,0.1)]",
    destructive: "border-neon/40 bg-neon/15 text-neon shadow-neon-glow"
  };
  return <span className={`${base} ${variants[variant]} ${className}`} {...props}>{children}</span>;
}