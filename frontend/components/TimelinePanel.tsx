import { TimelineEvent } from "../lib/types";

export default function TimelinePanel({ events }: { events: TimelineEvent[] }) {
  if (events.length === 0) {
    return <p className="text-gray-500 text-sm">No timeline events recorded yet.</p>;
  }

  return (
    <div className="relative border-l border-gray-200 ml-3 space-y-8">
      {events.map((event) => (
        <div key={event.id} className="relative pl-6">
          <div className="absolute w-3 h-3 bg-blue-500 rounded-full -left-1.5 top-1.5 border-2 border-white"></div>
          <div className="flex flex-col">
            <span className="text-xs font-semibold text-blue-600 mb-1">{event.date}</span>
            <span className="text-sm font-medium text-gray-900">{event.event_type}</span>
            <p className="text-sm text-gray-600 mt-1">{event.description}</p>
          </div>
        </div>
      ))}
    </div>
  );
}

