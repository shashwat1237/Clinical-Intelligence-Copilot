import { PatientProfile } from "../lib/types";
import { Card, Badge } from "./combined_ui";

export default function ClinicalSummaryCard({ profile }: { profile: PatientProfile }) {
  return (
    <Card className="p-6 bg-glass shadow-2xl border border-glassBorder space-y-6 relative overflow-hidden h-full">
      {/* Scanline / Grid effect background */}
      <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(rgba(0,240,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(0,240,255,0.03)_1px,transparent_1px)] bg-[size:20px_20px] z-0"></div>

      <div className="relative z-10">
        <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-neon shadow-neon-glow animate-pulse"></span>
          Active Conditions
        </h3>
        <ul className="space-y-2">
          {profile.conditions.map(c => (
            <li key={c.id} className="text-xs font-mono text-slate-300 flex items-center bg-void/60 px-3 py-2 border border-slate-800/80 rounded backdrop-blur-sm">
              <span className="text-neon mr-3">⚠</span>
              {c.name}
            </li>
          ))}
          {profile.conditions.length === 0 && <li className="text-xs font-mono text-slate-600 tracking-wider">NO KNOWN CONDITIONS</li>}
        </ul>
      </div>
      
      <div className="border-t border-glassBorder pt-5 relative z-10">
        <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-cyber shadow-cyber-glow"></span>
          Current Medications
        </h3>
        <ul className="space-y-2">
          {profile.medications.map(m => (
            <li key={m.id} className="text-sm text-slate-300 flex flex-col bg-void/60 border border-slate-800/80 p-3 rounded hover:border-cyber/30 transition-colors backdrop-blur-sm group">
              <span className="font-bold text-cyber font-mono text-xs uppercase tracking-wide group-hover:drop-shadow-[0_0_5px_rgba(0,240,255,0.5)] transition-all">{m.name}</span>
              <span className="text-[10px] text-slate-500 mt-1 font-mono tracking-wider">{m.dosage} // {m.frequency}</span>
            </li>
          ))}
           {profile.medications.length === 0 && <li className="text-xs font-mono text-slate-600 tracking-wider">NO ACTIVE MEDICATIONS</li>}
        </ul>
      </div>

      <div className="border-t border-glassBorder pt-5 relative z-10">
        <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-slate-400"></span>
          Latest Flagged Labs
        </h3>
        <ul className="space-y-2">
          {profile.labs.slice(0, 5).map(l => (
            <li key={l.id} className="flex justify-between items-center bg-void/60 p-2.5 rounded border border-slate-800/80 hover:bg-slate-900 transition-colors backdrop-blur-sm">
              <span className="text-slate-400 font-mono text-[10px] uppercase tracking-wider">{l.parameter}</span>
              <Badge variant={l.is_abnormal ? "destructive" : "default"}>
                {l.value} {l.unit}
              </Badge>
            </li>
          ))}
           {profile.labs.length === 0 && <li className="text-xs font-mono text-slate-600 tracking-wider">NO LAB RESULTS RECORDED</li>}
        </ul>
      </div>
    </Card>
  );
}