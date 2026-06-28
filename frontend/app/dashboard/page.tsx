"use client";
import { useEffect, useState } from "react";
import { apiService } from "../../services/api_service";
import ChatPanel from "../../components/ChatPanel";
import ClinicalSummaryCard from "../../components/ClinicalSummaryCard";
import { PatientProfile } from "../../lib/types";

export default function DashboardPage() {
  const [profile, setProfile] = useState<PatientProfile | null>(null);

  useEffect(() => {
    apiService.getPatientProfile()
      .then(setProfile)
      .catch(console.error);
  }, []);

  return (
    <div className="h-full grid grid-cols-12 gap-6">
      <div className="col-span-12 xl:col-span-4 h-full flex flex-col min-h-0 overflow-y-auto pr-1 custom-scrollbar">
        
        {/* Header Block */}
        <div className="mb-4 bg-glass p-6 rounded-xl border border-glassBorder shadow-2xl backdrop-blur-md relative overflow-hidden">
          <div className="absolute inset-0 bg-[linear-gradient(45deg,rgba(0,240,255,0.03)_25%,transparent_25%,transparent_50%,rgba(0,240,255,0.03)_50%,rgba(0,240,255,0.03)_75%,transparent_75%,transparent)] bg-[size:10px_10px] z-0 pointer-events-none"></div>
          <div className="relative z-10">
            <h2 className="text-xs font-bold text-cyber tracking-[0.2em] uppercase">Patient Clinical Record</h2>
            <p className="text-[10px] font-mono text-slate-500 mt-1.5 tracking-widest uppercase">Live Inference Engine Overview</p>
          </div>
        </div>
        
        {/* Dynamic Profile Load */}
        <div className="flex-1">
          {profile ? (
            <ClinicalSummaryCard profile={profile} />
          ) : (
            <div className="p-8 text-center bg-glass rounded-xl border border-dashed border-slate-800 text-cyber text-[10px] font-bold tracking-widest uppercase animate-pulse">
              Syncing Systemic Entities...
            </div>
          )}
        </div>
      </div>
      
      {/* Main Chat Area */}
      <div className="col-span-12 xl:col-span-8 h-full bg-void rounded-xl border border-glassBorder shadow-2xl overflow-hidden relative">
        <ChatPanel />
      </div>
    </div>
  );
}