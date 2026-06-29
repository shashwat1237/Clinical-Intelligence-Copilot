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
  // 🚨 NEW: Track uploading state specifically for the button
  const [isUploading, setIsUploading] = useState(false); 
  const [resetKey, setResetKey] = useState<number>(0); 
  
  const { status, isPolling } = useDocumentStatus(docId);

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
    
    // 🚨 LOCK: Disable the button and start the spinner
    setIsUploading(true);
    setError(null);
    
    try {
      const result = await apiService.uploadDocument(file);
      setDocId(result.id);
    } catch (err: any) {
      setError(err.message || "Upload failed.");
      setIsUploading(false); // Only unlock if it fails
    }
  };

  const handleReset = () => {
    setFile(null);
    setDocId(null);
    setError(null);
    setIsUploading(false); // Reset upload lock
    setResetKey(prev => prev + 1);
  };

  // ... (authorization check and UI rendering remain same)

  return (
    // ... (Sidebar and Card wrapper remain same)
            
            {/* UPDATED: Added isUploading to the disabled logic */}
            {!isPolling && !isReady && !isFailed && (
              <Button 
                onClick={handleUpload} 
                disabled={!file || isUploading} 
                className="w-full"
              >
                {isUploading ? "Initializing..." : "Process Document"}
              </Button>
            )}

            {/* Combined UI: Show upload spinner or polling spinner */}
            {(isUploading || isPolling) && (
              <div className="p-4 bg-blue-50 text-blue-800 rounded-md border border-blue-200">
                <p className="font-medium flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-blue-300 border-t-blue-800 rounded-full animate-spin"></span>
                  {isUploading ? "Uploading..." : `Processing Status: ${status}`}
                </p>
                <p className="text-xs mt-1 ml-6">Extracting clinical knowledge. This happens in the background.</p>
              </div>
            )}
    // ...
