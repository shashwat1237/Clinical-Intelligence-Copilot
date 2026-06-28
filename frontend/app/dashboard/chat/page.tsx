"use client";

import ChatPanel from "../../../components/ChatPanel";

export default function ChatPage() {
  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] max-w-5xl mx-auto">
      <div className="mb-4">
        <h1 className="text-2xl font-semibold text-gray-900">Clinical Intelligence Copilot</h1>
        <p className="text-sm text-gray-500">Ask evidence-backed questions about the structured patient record.</p>
      </div>
      <div className="flex-1 overflow-hidden bg-white rounded-lg shadow border border-gray-200">
        <ChatPanel />
      </div>
    </div>
  );
}
