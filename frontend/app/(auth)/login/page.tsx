"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { apiService } from "../../../services/api_service";
import { Button, Input, Card } from "../../../components/combined_ui";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await apiService.login({ email, password });
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Failed to authenticate.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-void relative overflow-hidden">
      {/* Subtle background glow */}
      <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-cyber/10 via-void to-void z-0"></div>
      
      {/* Scanline overlay */}
      <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(to_bottom,rgba(0,240,255,0.015)_1px,transparent_1px)] bg-[size:100%_4px] z-0"></div>

      <Card className="w-full max-w-md p-8 z-10 relative">
        <div className="flex flex-col items-center mb-8">
          <div className="w-3 h-3 rounded-full bg-cyber shadow-cyber-glow animate-pulse mb-4"></div>
          <h1 className="text-xl font-bold tracking-[0.2em] text-white uppercase">
            System <span className="text-cyber drop-shadow-[0_0_8px_rgba(0,240,255,0.8)]">Access</span>
          </h1>
          <p className="text-[10px] text-slate-500 font-mono mt-2 tracking-widest uppercase">Authenticate to proceed</p>
        </div>
        
        {error && (
          <div className="mb-6 p-3 text-[10px] font-mono text-neon bg-neon/10 border border-neon/30 rounded shadow-[0_0_10px_rgba(255,0,85,0.1)] uppercase tracking-wider text-center">
            SYS_ERR: {error}
          </div>
        )}
        
        <form onSubmit={handleLogin} className="space-y-6">
          <div className="space-y-4">
            <Input 
              type="email" 
              placeholder="OPERATIVE EMAIL" 
              value={email} 
              onChange={(e) => setEmail(e.target.value)} 
              required 
              className="font-mono text-xs tracking-wider"
            />
            <Input 
              type="password" 
              placeholder="ACCESS KEY" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              required 
              className="font-mono text-xs tracking-wider"
            />
          </div>
          
          <div className="space-y-4 pt-2">
            <Button type="submit" disabled={loading} className="w-full group">
              <span className="group-hover:drop-shadow-[0_0_8px_rgba(0,240,255,0.8)]">
                {loading ? "AUTHENTICATING..." : "INITIALIZE SESSION"}
              </span>
            </Button>
            
            {/* New Sign Up Routing Section */}
            <div className="text-center pt-5 border-t border-glassBorder mt-2">
              <p className="text-[10px] text-slate-500 font-mono tracking-widest uppercase mb-3">
                Unregistered Operative?
              </p>
              <Link href="/signup" className="w-full inline-block">
                <Button type="button" variant="secondary" className="w-full hover:text-cyber hover:border-cyber/50 hover:shadow-cyber-glow transition-all duration-300">
                  REQUEST ACCESS (SIGN UP)
                </Button>
              </Link>
            </div>
          </div>
        </form>
      </Card>
    </div>
  );
}