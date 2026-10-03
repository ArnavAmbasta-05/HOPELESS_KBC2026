import React, { useState, useEffect } from "react";
import {
  CalendarDays,
  Clock,
  Users,
  Mic,
  Bus,
  Search,
  AlertTriangle,
} from "lucide-react";
import { Reveal, SectionHeader } from "./ui";

export interface ScheduledEvent {
  id: string;
  title: string;
  date: string;
  timeWindow: string;
  hostingSociety: string;
  speaker: {
    name: string;
    designation: string;
    arrivalGate: string;
    vipEscortAssigned: string;
  };
  originalVenue: string;
  currentVenue: string;
  isRelocated: boolean;
  registrantCount: number;
  hostelDistribution: {
    hostelName: string;
    count: number;
    shuttleRoute: string;
  }[];
  category: "Ceremony" | "Keynote" | "Panel Discussion" | "Workshop";
  status: "Scheduled" | "Relocated" | "In Progress" | "Completed";
}

// Schedule data (with the solver's relocation applied) is served live by
// the backend scenario service: GET /api/v1/scenario/sessions.

export const ScheduleView: React.FC = () => {
  const [events, setEvents] = useState<ScheduledEvent[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<ScheduledEvent | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [loadError, setLoadError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchSchedule = () => {
    setIsRefreshing(true);
    fetch("/api/v1/scenario/sessions")
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data: ScheduledEvent[]) => {
        setEvents(data);
        if (!selectedEvent && data.length > 0) {
          setSelectedEvent(data[0]);
        }
        setLoadError(null);
      })
      .catch((err) => {
        console.error("Failed to load schedule:", err);
        setLoadError("Unable to load the schedule from the operations API.");
      })
      .finally(() => setIsRefreshing(false));
  };

  // Initial load + periodic 5-second polling from live Notion backend
  useEffect(() => {
    fetchSchedule();
    const interval = setInterval(fetchSchedule, 5000);
    return () => clearInterval(interval);
  }, []);

  const filteredEvents = events.filter((ev) => {
    const matchesSearch =
      ev.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ev.hostingSociety.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ev.speaker.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = categoryFilter === "all" || ev.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="space-y-8">
      {/* Header */}
      <Reveal>
        <SectionHeader
          kicker="Run of show"
          title={<>Event schedule &amp; <span className="text-aurora">master timeline</span></>}
          subtitle="Time-wise sessions, guest-speaker arrival coordination and student hostel transport mapping."
          icon={<CalendarDays className="w-3.5 h-3.5" />}
          right={
            <div className="flex items-center gap-3">
              <button
                onClick={fetchSchedule}
                disabled={isRefreshing}
                className="px-3.5 py-2 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-cyan-500/30 text-xs font-bold text-cyan-300 flex items-center space-x-1.5 transition-all shadow-sm"
                title="Fetch latest updates from Notion"
              >
                <span className={`w-2 h-2 rounded-full ${isRefreshing ? "bg-cyan-400 animate-ping" : "bg-emerald-400 animate-pulse"}`} />
                <span>{isRefreshing ? "Syncing..." : "Live Notion Ingest"}</span>
              </button>
              <div className="px-3.5 py-2 rounded-xl glass-soft text-xs">
                <span className="text-slate-400">Audience:</span>{" "}
                <span className="font-bold text-cyan-300">
                  {events.reduce((sum, e) => sum + e.registrantCount, 0).toLocaleString()}
                </span>
              </div>
              <div className="px-3.5 py-2 rounded-xl glass-soft text-xs">
                <span className="text-slate-400">Date:</span>{" "}
                <span className="font-bold text-white">15 Oct 2026</span>
              </div>
            </div>
          }
        />
      </Reveal>

      {loadError && (
        <div className="p-3 rounded-xl bg-rose-950/40 border border-rose-500/30 text-xs text-rose-200 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{loadError} Ensure the API is running on :8000.</span>
        </div>
      )}

      {/* Filter Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search event, speaker, hosting society..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-900/90 border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50"
          />
        </div>

        <div className="flex items-center space-x-2 w-full sm:w-auto overflow-x-auto">
          {["all", "Ceremony", "Keynote", "Panel Discussion"].map((cat) => (
            <button
              key={cat}
              onClick={() => setCategoryFilter(cat)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                categoryFilter === cat
                  ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                  : "text-slate-400 hover:text-slate-200 bg-slate-900/60 border border-white/5"
              }`}
            >
              {cat === "all" ? "All Tracks" : cat}
            </button>
          ))}
        </div>
      </div>

      {/* Main Split View */}
      <Reveal className="grid grid-cols-1 lg:grid-cols-12 gap-6" as="div">
        {/* Timeline Events List (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          {filteredEvents.map((ev) => {
            const isSelected = selectedEvent?.id === ev.id;
            return (
              <div
                key={ev.id}
                onClick={() => setSelectedEvent(ev)}
                className={`rail-card p-5 rounded-2xl cursor-pointer transition-all border ${
                  isSelected
                    ? "glass-panel border-cyan-500/50 shadow-glow-cyan"
                    : "glass-soft border-white/5 hover:border-white/20 hover:-translate-y-0.5"
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2.5">
                      <span className="text-xs font-bold text-cyan-400 flex items-center space-x-1">
                        <Clock className="w-3.5 h-3.5" />
                        <span>{ev.timeWindow}</span>
                      </span>
                      <span className="text-slate-600">•</span>
                      <span className="text-xs text-slate-400 font-medium">{ev.hostingSociety}</span>
                    </div>

                    <h3 className="text-base font-bold text-white">{ev.title}</h3>
                  </div>

                  <span
                    className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase border shrink-0 ${
                      ev.status.toUpperCase() === "CANCELLED"
                        ? "bg-rose-500/20 text-rose-300 border-rose-500/40"
                        : ev.status.toUpperCase() === "RELOCATED"
                        ? "bg-amber-500/20 text-amber-300 border-amber-500/40"
                        : "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                    }`}
                  >
                    {ev.status}
                  </span>
                </div>

                {/* Speaker & Venue Footprint */}
                <div className="mt-3.5 p-3 rounded-xl bg-slate-950/60 border border-white/5 grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-slate-500 text-[10px] uppercase font-bold">Keynote / Guest:</span>
                    <div className="font-semibold text-white truncate">{ev.speaker.name}</div>
                    <div className="text-[11px] text-slate-400 truncate">{ev.speaker.designation}</div>
                  </div>

                  <div>
                    <span className="text-slate-500 text-[10px] uppercase font-bold">Assigned Venue:</span>
                    <div className="font-semibold text-emerald-400 truncate">{ev.currentVenue}</div>
                    {ev.isRelocated && (
                      <div className="text-[10px] text-rose-300/80 line-through truncate">
                        Was: {ev.originalVenue}
                      </div>
                    )}
                  </div>
                </div>

                {/* Footer Metrics */}
                <div className="mt-3.5 pt-3 border-t border-white/5 flex items-center justify-between text-xs text-slate-400">
                  <div className="flex items-center space-x-3">
                    <span className="flex items-center space-x-1">
                      <Users className="w-3.5 h-3.5 text-indigo-400" />
                      <span>{ev.registrantCount} Registered</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <Bus className="w-3.5 h-3.5 text-cyan-400" />
                      <span>{ev.hostelDistribution.length} Hostel Cohorts</span>
                    </span>
                  </div>

                  <span className="text-[11px] text-slate-500 font-mono">ID: {ev.id}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Selected Event Inspector & Hostel Transport Mapping (5 cols) */}
        <div className="lg:col-span-5">
          {selectedEvent ? (
            <div className="glass-panel p-6 rounded-2xl sticky top-24 space-y-6">
              <div>
                <span className="px-2.5 py-1 rounded-md text-[10px] font-bold uppercase bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  {selectedEvent.category}
                </span>
                <h2 className="text-lg font-black text-white mt-2">{selectedEvent.title}</h2>
                <div className="text-xs text-cyan-400 font-semibold mt-1 flex items-center space-x-1.5">
                  <Clock className="w-3.5 h-3.5" />
                  <span>{selectedEvent.timeWindow} • 15 October 2026</span>
                </div>
              </div>

              {/* Speaker Escort Protocol */}
              <div className="p-4 rounded-xl bg-slate-900/90 border border-white/10 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-white flex items-center space-x-1.5">
                    <Mic className="w-4 h-4 text-cyan-400" />
                    <span>Speaker VIP Protocol</span>
                  </span>
                  <span className="text-[10px] text-emerald-400 font-bold uppercase">CONFIRMED</span>
                </div>
                <div className="text-xs">
                  <div className="font-semibold text-slate-200">{selectedEvent.speaker.name}</div>
                  <div className="text-slate-400 text-[11px]">{selectedEvent.speaker.designation}</div>
                </div>
                <div className="pt-2 border-t border-white/5 grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-slate-500 text-[10px]">Arrival Point</span>
                    <div className="font-medium text-slate-300">{selectedEvent.speaker.arrivalGate}</div>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[10px]">Assigned VIP Escort</span>
                    <div className="font-medium text-cyan-300">{selectedEvent.speaker.vipEscortAssigned}</div>
                  </div>
                </div>
              </div>

              {/* Student Hostel Demographics & Transport Shuttles */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2.5 flex items-center space-x-1.5">
                  <Bus className="w-4 h-4 text-cyan-400" />
                  <span>Hostel Registrations & Shuttle Planning</span>
                </h4>
                <div className="space-y-2">
                  {selectedEvent.hostelDistribution.map((hostel, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl bg-slate-900/80 border border-white/5 flex items-center justify-between text-xs"
                    >
                      <div>
                        <div className="font-semibold text-white">{hostel.hostelName}</div>
                        <div className="text-[10px] text-cyan-400 font-medium">{hostel.shuttleRoute}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-white">{hostel.count}</div>
                        <div className="text-[10px] text-slate-500">Students</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Re-homing Audit Trail */}
              {selectedEvent.isRelocated && (
                <div className="p-3.5 rounded-xl bg-amber-950/30 border border-amber-500/30 text-xs space-y-1">
                  <div className="font-bold text-amber-300 flex items-center space-x-1.5">
                    <AlertTriangle className="w-4 h-4" />
                    <span>Relocation Audit Trace (AT-01)</span>
                  </div>
                  <p className="text-slate-300 text-[11px]">
                    Displaced from <strong>{selectedEvent.originalVenue}</strong> due to Main Auditorium ceiling outage.
                    Relocated to <strong>{selectedEvent.currentVenue}</strong> with automated SMS broadcast sent to all {selectedEvent.registrantCount} registered hostel students.
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="glass-panel p-12 text-center text-slate-500 text-xs">
              Select an event to inspect attendee demographics and transport shuttles.
            </div>
          )}
        </div>
      </Reveal>
    </div>
  );
};
