"use client";
import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { apiService } from "../../services/api_service";
import { useDocumentStatus } from "../../hooks/useDocumentStatus";
import { Button, Card } from "../../components/combined_ui";
import Sidebar from "../../components/Sidebar";

export default function UploadPage() {
  const router = useRouter();
  const [isAuthorized, setIsAuthorized] = useState(false);
  
  const [file, setFile] = useState<File | null>(null);
  const [docId, setDocId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [resetKey, setResetKey] = useState<number>(0); 
  
  const { status, isPolling } = useDocumentStatus(docId);

  // CRITICAL FIX: Ensure anonymous users cannot access the upload portal
  useEffect(() => {
    const token = localStorage.getItem("jwt_token");
    if (!token) {
      router.push("/login");
    } else {
      setIsAuthorized(true);
    }
  }, [router]);

  const handleUpload = async () => {
    if (!file) return;
    setError(null);
    try {
      const result = await apiService.uploadDocument(file);
      setDocId(result.id);
    } catch (err: any) {
      setError(err.message || "Upload failed.");
    }
  };

  const handleReset = () => {
    setFile(null);
    setDocId(null);
    setError(null);
    setResetKey(prev => prev + 1);
  };

  // Prevent UI rendering until token is validated
  if (!isAuthorized) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <p className="text-sm font-medium text-gray-500">Authenticating secure session...</p>
      </div>
    );
  }

  const isReady = status === "READY";
  const isFailed = status === "FAILED";

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 p-8 overflow-y-auto flex items-center justify-center">
        <Card className="w-full max-w-lg p-8">
          <h1 className="text-2xl font-semibold mb-4 text-gray-900">Upload Medical Report</h1>
          <p className="text-sm text-gray-500 mb-6">Supported formats: text-based PDFs (e.g., Blood tests, MRIs, Discharge summaries).</p>
          
          {error && <div className="mb-4 text-sm text-red-600 bg-red-50 p-3 rounded-md border border-red-200">{error}</div>}
          
          <div className="space-y-4">
            <input 
              key={resetKey} 
              type="file" 
              accept="application/pdf" 
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 transition-colors"
              disabled={isPolling}
            />
            
            {!isPolling && !isReady && !isFailed && (
              <Button onClick={handleUpload} disabled={!file} className="w-full">
                Process Document
              </Button>
            )}

            {isPolling && (
              <div className="p-4 bg-blue-50 text-blue-800 rounded-md border border-blue-200">
                <p className="font-medium flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-blue-300 border-t-blue-800 rounded-full animate-spin"></span>
                  Processing Status: {status}
                </p>
                <p className="text-xs mt-1 ml-6">Extracting clinical knowledge. This happens in the background.</p>
              </div>
            )}

            {isReady && (
              <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
                <div className="p-4 bg-green-50 text-green-800 rounded-md border border-green-200">
                  <p className="font-medium">Success!</p>
                  <p className="text-sm mt-1">Document processed and clinical profile updated successfully.</p>
                </div>
                <div className="flex gap-3">
                  <Button onClick={() => router.push("/dashboard")} className="flex-1 bg-green-600 hover:bg-green-700">
                    Go to Dashboard
                  </Button>
                  <Button onClick={handleReset} variant="secondary" className="flex-1">
                    Upload Another
                  </Button>
                </div>
              </div>
            )}

            {isFailed && (
              <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
                <div className="p-4 bg-red-50 text-red-800 rounded-md border border-red-200">
                  Processing failed. The document may be corrupted or unsupported.
                </div>
                <Button onClick={handleReset} variant="secondary" className="w-full">
                  Try Another File
                </Button>
              </div>
            )}
          </div>
        </Card>
      </main>
    </div>
  );
}