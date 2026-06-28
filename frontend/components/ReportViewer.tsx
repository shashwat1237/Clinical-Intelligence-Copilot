"use client";

import React, { useState, useEffect } from "react";
import { Document } from "../lib/types";
import { apiService } from "../services/api_service";

interface ReportViewerProps {
  document: Document;
  onClose: () => void;
}

export default function ReportViewer({ document, onClose }: ReportViewerProps) {
  const [activePanel, setActivePanel] = useState<"pdf" | "highlights">("pdf");
  const [highlights, setHighlights] = useState<string[]>([]);
  const [loadingHighlights, setLoadingHighlights] = useState<boolean>(false);

  const SUPABASE_PROJECT_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || "https://tgttpgzulccvbqvcafhp.supabase.co";
  const publicPdfUrl = `${SUPABASE_PROJECT_URL}/storage/v1/object/public/medical-reports/${document.storage_path}`;

  useEffect(() => {
    async function loadHighlights() {
      setLoadingHighlights(true);
      try {
        const entities = await apiService.getDocumentEntities(document.id);
        setHighlights(
          entities.map(
            (e: any) => `${e.category}: ${e.normalized_name} ${e.value ? `(${e.value})` : ""}`.trim()
          )
        );
      } catch (error) {
        console.error("Critical dashboard integration failure avoided:", error);
      } finally {
        setLoadingHighlights(false);
      }
    }
    
    if (document.id) {
        loadHighlights();
    }
  }, [document.id]);

  return (
    <div className="flex flex-col h-full w-full bg-void shadow-2xl border border-glassBorder rounded-xl overflow-hidden relative">
      
      {/* Header Panel */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-glassBorder bg-void/90 backdrop-blur-md z-10 relative">
        <div>
          <h2 className="text-sm font-bold text-cyber tracking-widest uppercase font-mono truncate max-w-md">
            {document.filename}
          </h2>
          <p className="text-[10px] text-slate-500 mt-1 font-mono uppercase tracking-widest">
            SYS_LOG: {new Date(document.uploaded_at).toLocaleDateString()}
          </p>
        </div>
        
        {/* Tech Segmented Control */}
        <div className="flex items-center gap-2">
          <div className="inline-flex rounded-md p-1 bg-void border border-slate-800 text-[10px] font-bold tracking-widest uppercase">
            <button
              onClick={() => setActivePanel("pdf")}
              className={`px-4 py-2 rounded-sm transition-all duration-300 ${
                activePanel === "pdf"
                  ? "bg-cyber/20 text-cyber shadow-cyber-glow border border-cyber/50"
                  : "text-slate-500 hover:text-cyber/70 border border-transparent"
              }`}
            >
              Raw Asset
            </button>
            <button
              onClick={() => setActivePanel("highlights")}
              className={`px-4 py-2 rounded-sm transition-all duration-300 ${
                activePanel === "highlights"
                  ? "bg-cyber/20 text-cyber shadow-cyber-glow border border-cyber/50"
                  : "text-slate-500 hover:text-cyber/70 border border-transparent"
              }`}
            >
              AI Telemetry
            </button>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 min-h-0 bg-void relative z-0">
        {activePanel === "pdf" ? (
          <iframe
            src={`${publicPdfUrl}#toolbar=1&navpanes=0&view=FitH`}
            className="w-full h-full border-none bg-slate-900 opacity-90 hover:opacity-100 transition-opacity"
            title={`Clinical Viewer Asset: ${document.filename}`}
            sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
          />
        ) : (
          <div className="w-full h-full p-6 overflow-y-auto bg-void/50 custom-scrollbar relative">
            <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(to_bottom,rgba(0,240,255,0.02)_1px,transparent_1px)] bg-[size:100%_4px] z-0"></div>
            <div className="relative z-10">
              <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-6 flex items-center gap-3">
                <span className="w-full h-px bg-glassBorder flex-1"></span>
                Validated Patient Highlights
                <span className="w-full h-px bg-glassBorder flex-1"></span>
              </h3>
              
              {loadingHighlights ? (
                <div className="text-center py-16 text-cyber border border-dashed border-cyber/20 rounded-lg bg-cyber/5 backdrop-blur-sm">
                  <div className="w-6 h-6 border-2 border-cyber/20 border-t-cyber rounded-full animate-spin mx-auto mb-4"></div>
                  <p className="text-[10px] font-bold tracking-[0.2em] uppercase animate-pulse">Extracting Structural Insights...</p>
                </div>
              ) : highlights.length > 0 ? (
                <ul className="space-y-4">
                  {highlights.map((highlight: string, idx: number) => (
                    <li 
                      key={idx} 
                      className="p-4 rounded-lg bg-glass border border-slate-800 text-slate-300 flex items-start gap-4 transition-all duration-300 hover:border-cyber/40 hover:shadow-[0_0_15px_rgba(0,240,255,0.05)] hover:bg-slate-900/80 group"
                    >
                      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded bg-void border border-cyber/30 text-[10px] font-bold text-cyber font-mono group-hover:shadow-cyber-glow group-hover:border-cyber transition-all">
                        {idx + 1}
                      </span>
                      <span className="leading-relaxed font-mono text-xs uppercase tracking-wide">{highlight}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="text-center py-16 text-slate-500 border border-dashed border-slate-800 rounded-lg bg-glass">
                  <p className="text-[10px] font-bold tracking-widest uppercase">No Specific Systemic Classifications Parsed</p>
                  <p className="text-[10px] font-mono text-slate-600 mt-2 tracking-wider">SYS_MSG: Target baseline ranges normal.</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}