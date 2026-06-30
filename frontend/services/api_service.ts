import { PatientProfile, TimelineEvent, Document, ChatMessage } from "../lib/types";

const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL;

class ApiService {
  private getHeaders(): HeadersInit {
    const token = typeof window !== "undefined" ? localStorage.getItem("jwt_token") : null;
    return {
      "Content-Type": "application/json",
      ...(token ? { "Authorization": `Bearer ${token}` } : {})
    };
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers = { ...this.getHeaders(), ...(options.headers || {}) };

    const res = await fetch(`${BASE_URL}${endpoint}`, {
      cache: "no-store",
      ...options,
      headers,
    });

    if (!res.ok) {
      if (res.status === 401 && typeof window !== "undefined") {
        localStorage.removeItem("jwt_token");
        window.location.href = "/login";
        return Promise.reject(new Error("Session expired. Please log in again."));
      }
      
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || `Networking Failure Code: ${res.status}`);
    }
    return res.json();
  }

  async login(credentials: any) {
    const data = await this.request<any>("/auth/login", { method: "POST", body: JSON.stringify(credentials) });
    if (typeof window !== "undefined" && data.access_token) {
      localStorage.setItem("jwt_token", data.access_token);
    }
    return data;
  }
  
  async signup(credentials: any) {
    const data = await this.request<any>("/auth/signup", { method: "POST", body: JSON.stringify(credentials) });
    if (typeof window !== "undefined" && data.access_token) {
      localStorage.setItem("jwt_token", data.access_token);
    }
    return data;
  }

  logout() {
    if (typeof window !== "undefined") {
      localStorage.removeItem("jwt_token");
    }
  }

  getPatientProfile() {
    return this.request<PatientProfile>("/patients/profile");
  }

  getTimelineEvents() {
    return this.request<TimelineEvent[]>("/timeline");
  }

  getDocuments() {
    return this.request<Document[]>("/documents");
  }

  getDocumentEntities(id: string) {
    return this.request<any[]>(`/documents/${id}/entities`);
  }

  getDocumentStatus(id: string) {
    return this.request<{ status: string }>(`/documents/${id}/status`);
  }

  deleteDocument(id: string) {
    return this.request<{ detail: string }>(`/documents/${id}`, { method: "DELETE" });
  }

  async uploadDocument(file: File) {
    const formData = new FormData();
    formData.append("file", file);

    const token = typeof window !== "undefined" ? localStorage.getItem("jwt_token") : null;
    
    const res = await fetch(`${BASE_URL}/upload`, {
      method: "POST",
      cache: "no-store",
      headers: { ...(token ? { "Authorization": `Bearer ${token}` } : {}) },
      body: formData
    });

    if (!res.ok) {
      if (res.status === 401 && typeof window !== "undefined") {
        localStorage.removeItem("jwt_token");
        window.location.href = "/login";
      }
      throw new Error("Upload handler operation failure.");
    }
    return res.json();
  }

  sendChatMessage(message: string) {
    return this.request<ChatMessage>("/chat", { method: "POST", body: JSON.stringify({ message }) });
  }

  getChatHistory() {
    return this.request<ChatMessage[]>("/chat/history");
  }

  clearChatHistory() {
    return this.request<{ detail: string }>("/chat", { method: "DELETE" });
  }
}

export const apiService = new ApiService();
