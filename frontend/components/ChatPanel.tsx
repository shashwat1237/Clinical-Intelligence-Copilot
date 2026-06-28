"use client";
import React, { useState, useRef, useEffect } from "react";
import { useChat } from "../hooks/useChat";
import { Citation } from "../lib/types";
import { Input, Button, Badge } from "./combined_ui";
import CitationDrawer from "./CitationDrawer";

const formatMessageText = (text: string) => {
  const parts = text.split(/(\*\*.*?\*\*)/g);
  return parts.map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return (
        <strong key={index} className="font-semibold text-white drop-shadow-[0_0_5px_rgba(255,255,255,0.4)]">
          {part.slice(2, -2)}
        </strong>
      );
    }
    return <React.Fragment key={index}>{part}</React.Fragment>;
  });
};

export default function ChatPanel() {
  const { messages, loading, sendMessage, clearMessages } = useChat();
  const [input, setInput] = useState("");
  const [activeCitation, setActiveCitation] = useState<Citation | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    sendMessage(input);
    setInput("");
  };

  return (
    <div className="flex flex-col h-full relative bg-void/50 backdrop-blur-md rounded-xl border border-glassBorder shadow-2xl overflow-hidden">
      
      {/* Subtle CRT Scanline Overlay */}
      <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(to_bottom,rgba(0,240,255,0.015)_1px,transparent_1px)] bg-[size:100%_4px] z-0"></div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6 z-10 custom-scrollbar">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-lg p-5 backdrop-blur-lg border shadow-xl ${
              msg.role === 'user' 
                ? 'bg-cyber/10 border-cyber/30 text-cyber rounded-br-sm' 
                : 'bg-glass border-glassBorder text-slate-300 rounded-bl-sm'
            }`}>
              
              <p className="text-sm leading-relaxed whitespace-pre-wrap font-mono">
                {msg.role === 'ai' ? formatMessageText(msg.content) : msg.content}
              </p>
              
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-5 flex flex-wrap gap-2 pt-4 border-t border-glassBorder">
                  {msg.citations.map((cit, cIdx) => (
                    <Badge 
                      key={cIdx} 
                      className={`cursor-pointer transition-all duration-300 ${
                        msg.role === 'user' 
                          ? 'border-cyber/50 text-cyber hover:shadow-cyber-glow hover:bg-cyber/20' 
                          : 'border-slate-700 bg-slate-900/50 text-slate-400 hover:text-cyber hover:border-cyber/50 hover:bg-cyber/10'
                      }`}
                      onClick={() => setActiveCitation(cit)}
                    >
                      [{cIdx + 1}] {cit.document_name}
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-glass border border-glassBorder text-cyber rounded-lg rounded-bl-sm p-4 shadow-cyber-glow backdrop-blur-lg text-[10px] font-bold uppercase tracking-widest flex items-center gap-4">
              <div className="w-3.5 h-3.5 border-2 border-cyber/20 border-t-cyber rounded-full animate-spin"></div>
              Processing Telemetry...
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 bg-void/90 border-t border-glassBorder backdrop-blur-xl z-20">
        <form onSubmit={handleSubmit} className="flex gap-3">
          
          <button
            type="button"
            onClick={() => {
              if (window.confirm("Purge all telemetry logs? This cannot be undone.")) {
                clearMessages();
              }
            }}
            disabled={loading || messages.length === 0}
            className="flex items-center justify-center px-4 rounded-md border border-neon/30 text-neon bg-neon/5 hover:bg-neon/20 hover:border-neon hover:shadow-neon-glow hover:text-white transition-all duration-300 disabled:opacity-50 disabled:pointer-events-none"
            title="Purge Telemetry Log"
          >
            <span className="font-mono font-bold text-lg leading-none">⎚</span>
          </button>

          <Input 
            value={input} 
            onChange={(e) => setInput(e.target.value)}
            placeholder="QUERY CLINICAL REPOSITORY..."
            className="flex-1 font-mono tracking-wide text-xs uppercase"
            disabled={loading}
          />
          <Button type="submit" disabled={loading || !input.trim()} className="px-8 shadow-sm group">
            <span className="group-hover:drop-shadow-[0_0_8px_rgba(0,240,255,0.8)]">Execute</span>
          </Button>
        </form>
      </div>

      <CitationDrawer 
        citation={activeCitation} 
        isOpen={!!activeCitation} 
        onClose={() => setActiveCitation(null)} 
      />
    </div>
  );
}