"use client";

import { useEffect, useState } from "react";
import { apiService } from "../../../services/api_service";
import TimelinePanel from "../../../components/TimelinePanel";
import { TimelineEvent } from "../../../lib/types";

export default function TimelinePage() {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTimeline = async () => {
      try {
        const data = await apiService.getTimelineEvents();
        setEvents(data);
      } catch (err: any) {
        setError(err.message || "Failed to load timeline.");
      } finally {
        setLoading(false);
      }
    };
    fetchTimeline();
  }, []);

  if (loading) return <div className="text-gray-600">Loading timeline...</div>;
  if (error) return <div className="text-red-600">{error}</div>;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-semibold text-gray-900">Longitudinal Clinical History</h1>
      <p className="text-gray-500 mb-6">A chronological view of extracted medical events across all uploaded reports.</p>
      <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
        <TimelinePanel events={events} />
      </div>
    </div>
  );
}
