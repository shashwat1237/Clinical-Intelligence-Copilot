"use client";

import React, { useEffect, useState } from "react";
import { Document } from "../../../lib/types";
import { apiService } from "../../../services/api_service";

export default function ReportsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);

  const handleDelete = async (docId: string) => {
    if (!window.confirm("WARNING: Purging this asset will permanently delete it and its vector embeddings. Continue?")) return;
    try {
      await apiService.deleteDocument(docId);
      setDocuments(prev => prev.filter(d => d.id !== docId));
    } catch (error) {
      console.error("Failed to delete document:", error);
      alert("Failed to delete the asset. Check console for logs.");
    }
  };

  useEffect(() => {
    async function fetchDocs() {
      try {
        const docs = await apiService.getDocuments();
        setDocuments(docs);
      } catch (error) {
        console.error("Failed to load reports:", error);
      } finally {
        setLoading(false);
      }
    }

    fetchDocs();
  }, []);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center bg-void">
        <div className="flex flex-col items-center gap-4">
          <div className="w-6 h-6 border-2 border-cyber/20 border-t-cyber rounded-full animate-spin"></div>
          <p className="text-[10px] font-bold text-cyber tracking-[0.2em] uppercase animate-pulse">
            Syncing with clinical knowledge database...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full bg-void rounded-xl border border-glassBorder shadow-2xl overflow-hidden flex flex-col relative">
      {/* Subtle Grid Overlay */}
      <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(rgba(0,240,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(0,240,255,0.02)_1px,transparent_1px)] bg-[size:30px_30px] z-0"></div>

      {/* Header */}
      <div className="border-b border-glassBorder bg-void/80 backdrop-blur-md px-6 py-5 z-10">
        <h1 className="text-sm font-bold text-cyber tracking-[0.2em] uppercase flex items-center gap-3">
          <span className="w-2 h-2 rounded-full bg-cyber shadow-cyber-glow"></span>
          Patient Records
        </h1>
        <p className="mt-1 text-[10px] text-slate-500 font-mono tracking-widest uppercase">
          SYS_LOG: {documents.length} ASSET{documents.length !== 1 ? "S" : ""} INDEXED
        </p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6 custom-scrollbar z-10">
        {documents.length === 0 ? (
          <div className="flex h-full items-center justify-center rounded-xl border border-dashed border-slate-800 bg-glass">
            <div className="text-center">
              <h2 className="text-xs font-bold text-slate-400 tracking-widest uppercase">
                No Assets Indexed
              </h2>
              <p className="mt-2 text-[10px] font-mono text-slate-600 tracking-wider">
                UPLOAD MEDICAL REPORTS TO INITIALIZE TELEMETRY.
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="rounded-lg border border-slate-800/80 bg-glass p-5 shadow-sm transition-all duration-300 hover:border-cyber/40 hover:shadow-[0_0_15px_rgba(0,240,255,0.05)] hover:bg-slate-900/50 group"
              >
                <div className="flex items-start justify-between gap-6">
                  <div className="min-w-0 flex-1">
                    <h2
                      className="break-all text-xs font-bold text-slate-300 font-mono tracking-wide group-hover:text-cyber transition-colors"
                      title={doc.filename}
                    >
                      {doc.filename}
                    </h2>

                    <div className="mt-4 grid grid-cols-1 gap-5 sm:grid-cols-2">
                      <div>
                        <p className="text-[10px] font-bold uppercase tracking-widest text-slate-600">
                          Upload Date
                        </p>
                        <p className="mt-1 text-[10px] font-mono text-slate-400">
                          {new Date(doc.uploaded_at).toLocaleString()}
                        </p>
                      </div>

                      <div>
                        <p className="text-[10px] font-bold uppercase tracking-widest text-slate-600">
                          System Status
                        </p>
                        <span
                          className={`mt-1.5 inline-flex rounded-sm border px-2 py-0.5 text-[9px] font-bold tracking-widest uppercase shadow-sm ${
                            doc.status === "READY"
                              ? "bg-cyber/10 text-cyber border-cyber/30 shadow-[0_0_8px_rgba(0,240,255,0.1)]"
                              : doc.status === "FAILED"
                              ? "bg-neon/10 text-neon border-neon/30 shadow-[0_0_8px_rgba(255,0,85,0.1)]"
                              : "bg-slate-800/50 text-slate-300 border-slate-600"
                          }`}
                        >
                          {doc.status}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => handleDelete(doc.id)}
                      title="Purge Asset"
                      className="flex h-12 w-12 shrink-0 items-center justify-center rounded bg-void border border-neon/30 text-neon/70 hover:border-neon hover:text-neon hover:shadow-neon-glow transition-all duration-300"
                    >
                      <span className="text-xl">✕</span>
                    </button>

                    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded bg-void border border-slate-800 text-slate-500 group-hover:border-cyber/30 group-hover:text-cyber transition-all">
                      <span className="text-xl">▤</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}