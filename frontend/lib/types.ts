export interface Citation {
  document_name: string;
  page_number: number;
  excerpt: string;
}

export interface ChatMessage {
  role: "user" | "ai" | "system";
  content: string;
  citations?: Citation[];
}

export interface Document {
  id: string;
  filename: string;
  status: string;
  storage_path: string;
  uploaded_at: string;
}

export interface Condition {
  id: string;
  name: string;
}

export interface Medication {
  id: string;
  name: string;
  dosage: string;
  frequency: string;
}

export interface LabResult {
  id: string;
  parameter: string;
  value: string;
  unit: string;
  is_abnormal: boolean;
}

export interface PatientProfile {
  conditions: Condition[];
  medications: Medication[];
  labs: LabResult[];
}

export interface TimelineEvent {
  id: string;
  date: string;
  event_type: string;
  description: string;
  document_id?: string;
}