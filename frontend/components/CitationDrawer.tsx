import { Citation } from "../lib/types";
import { Button } from "./combined_ui";

interface Props {
  citation: Citation | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function CitationDrawer({ citation, isOpen, onClose }: Props) {
  if (!isOpen || !citation) return null;

  return (
    <>
      {/* Dimming backdrop overlay */}
      <div 
        className="fixed inset-0 bg-void/80 z-40 transition-opacity backdrop-blur-sm" 
        onClick={onClose}
      />
      
      {/* Drawer Panel */}
      <div className="fixed inset-y-0 right-0 w-96 bg-void/95 shadow-[-20px_0_50px_rgba(0,0,0,0.8)] border-l border-glassBorder p-6 transform transition-transform z-50 overflow-y-auto">
        <div className="flex justify-between items-center mb-8 border-b border-glassBorder pb-4">
          <h2 className="text-xs font-bold tracking-[0.2em] text-cyber uppercase flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyber shadow-cyber-glow animate-pulse"></span>
            Evidence Source
          </h2>
          <Button onClick={onClose} variant="secondary" className="px-3 py-1 text-[10px]">Close</Button>
        </div>
        
        <div className="space-y-6">
          <div>
            <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Source Document</h4>
            <p className="text-sm text-slate-200 mt-1.5 font-mono break-words">{citation.document_name}</p>
          </div>
          
          <div>
            <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Page Reference</h4>
            <p className="text-xs font-bold text-cyber mt-2 font-mono shadow-[0_0_10px_rgba(0,240,255,0.1)] inline-block px-3 py-1.5 bg-cyber/10 rounded border border-cyber/30">
              PAGE {citation.page_number}
            </p>
          </div>

          <div>
            <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Extracted Excerpt</h4>
            <div className="bg-glass border border-glassBorder p-4 mt-2 rounded-md text-sm text-slate-300 font-mono leading-relaxed whitespace-pre-wrap shadow-inner relative overflow-hidden">
              {/* Glowing vertical accent line */}
              <div className="absolute left-0 top-0 bottom-0 w-1 bg-cyber shadow-cyber-glow"></div>
              "{citation.excerpt}"
            </div>
          </div>
        </div>
      </div>
    </>
  );
}