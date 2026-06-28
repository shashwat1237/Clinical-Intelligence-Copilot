import { useState, useEffect } from "react";
import { apiService } from "../services/api_service";

export function useDocumentStatus(documentId: string | null) {
  const [status, setStatus] = useState<string>("IDLE");
  const [isPolling, setIsPolling] = useState(false);

  useEffect(() => {
    // FIX: Force reset the state if documentId is null so the UI can mount a fresh upload form
    if (!documentId) {
      setStatus("IDLE");
      setIsPolling(false);
      return;
    }

    setIsPolling(true);
    setStatus("QUEUED");

    const interval = setInterval(async () => {
      try {
        const result = await apiService.getDocumentStatus(documentId);
        setStatus(result.status);
        
        if (result.status === "READY" || result.status === "FAILED") {
          clearInterval(interval);
          setIsPolling(false);
        }
      } catch (error) {
        console.error("Status polling failed:", error);
        clearInterval(interval);
        setIsPolling(false);
        setStatus("FAILED");
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [documentId]);

  return { status, isPolling };
}