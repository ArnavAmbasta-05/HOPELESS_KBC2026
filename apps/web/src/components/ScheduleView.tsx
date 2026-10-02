import React, { useState } from "react";
import {
  CalendarDays,
  Clock,
  MapPin,
  Users,
  Mic,
  Award,
  Bus,
  Tag,
  Search,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";

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

export const KIIT_SCHEDULE: ScheduledEvent[] = [
  {
    id: "ses_opening",
    title: "Opening Ceremony & Inaugural Keynote",
    date: "2026-10-15",
    timeWindow: "10:00 – 10:45 IST",
    hostingSociety: "KSAC & KIIT Student Council",
    speaker: {
      name: "Prof. S. Acharya",
      designation: "Vice Chancellor, KIIT University",
      arrivalGate: "Gate 1 (Campus 6 VIP Gate)",
      vipEscortAssigned: "Arjun Sharma (Lead Volunteer)",
    },
    originalVenue: "Main Auditorium (Campus 6)",
    currentVenue: "Open Air Theatre (Campus 6)",
    isRelocated: true,
    registrantCount: 380,
    hostelDistribution: [
      { hostelName: "King's Palace KP-6 (Boys)", count: 140, shuttleRoute: "Route 1 (KP-6 -> C6/C7)" },
      { hostelName: "King's Palace KP-7 (Boys)", count: 110, shuttleRoute: "Route 1 (KP-7 -> C6/C7)" },
      { hostelName: "Queen's Castle QC-1 (Girls)", count: 80, shuttleRoute: "Route 2 (QC -> C6/C7)" },
      { hostelName: "Day Scholars / Guests", count: 50, shuttleRoute: "Direct Campus Entry" },
    ],
    category: "Ceremony",
    status: "Relocated",
  },
  {
    id: "ses_keynote_ai",
    title: "Keynote: AI in Autonomous Event Operations & FinTech",
    date: "2026-10-15",
    timeWindow: "11:00 – 12:00 IST",
    hostingSociety: "KIIT AI Society & IEEE Student Branch",
    speaker: {
      name: "Dr. Rohit Mishra",
      designation: "Principal AI Architect, Ex-Google / Anthropic Contributor",
      arrivalGate: "Gate 2 (Campus 7 Link Gate)",
      vipEscortAssigned: "Pooja Verma (Tech Volunteer)",
    },
    originalVenue: "Main Auditorium (Campus 6)",
    currentVenue: "Auditorium / Seminar Hall (Campus 7)",
    isRelocated: true,
    registrantCount: 230,
    hostelDistribution: [
      { hostelName: "King's Palace KP-14 (Tech Hub)", count: 120, shuttleRoute: "Route 3 (KP-14 -> C7)" },
      { hostelName: "Queen's Castle QC-2 (Girls)", count: 60, shuttleRoute: "Route 2 (QC -> C7)" },
      { hostelName: "King's Palace KP-9", count: 50, shuttleRoute: "Route 1 (KP-9 -> C7)" },
    ],
    category: "Keynote",
    status: "Relocated",
  },
  {
    id: "ses_panel_startups",
    title: "Panel: Scaling Student Startups from Campus to Series A",
    date: "2026-10-15",
    timeWindow: "14:00 – 15:00 IST",
    hostingSociety: "KIIT E-Cell (Entrepreneurship Cell)",
    speaker: {
      name: "3 Alumni Founders",
      designation: "Shark Tank Featured Founders (KIIT TBI Incubatees)",
      arrivalGate: "Gate 1 (Campus 6 Main Entry)",
      vipEscortAssigned: "Vikram Das (E-Cell Coordinator)",
    },
    originalVenue: "Main Auditorium (Campus 6)",
    currentVenue: "Open Air Theatre (Campus 6)",
    isRelocated: true,
    registrantCount: 180,
    hostelDistribution: [
      { hostelName: "King's Palace KP-6", count: 70, shuttleRoute: "Route 1" },
      { hostelName: "Queen's Castle QC-3", count: 60, shuttleRoute: "Route 2" },
      { hostelName: "Campus 15 Hostels", count: 50, shuttleRoute: "Route 3" },
    ],
    category: "Panel Discussion",
    status: "Relocated",
  },
  {
    id: "ses_valedictory",
    title: "Grand Valedictory Ceremony & Conclave Awards",
    date: "2026-10-15",
    timeWindow: "17:00 – 18:00 IST",
    hostingSociety: "KBC 2026 Steering Committee",
    speaker: {
      name: "Registrar & Conclave Director",
      designation: "KIIT University Leadership",
      arrivalGate: "Gate 1 (VIP Entry)",
      vipEscortAssigned: "Stage Management Core",
    },
    originalVenue: "Main Auditorium (Campus 6)",
    currentVenue: "Open Air Theatre (Campus 6)",
    isRelocated: true,
    registrantCount: 390,
    hostelDistribution: [
      { hostelName: "All Hostels (KP-6, KP-7, KP-14)", count: 240, shuttleRoute: "Fleet Shuttles 1-4" },
      { hostelName: "All Hostels (QC-1, QC-2, QC-3)", count: 150, shuttleRoute: "Fleet Shuttles 5-6" },
    ],
    category: "Ceremony",
    status: "Relocated",
  },
];

export const ScheduleView: React.FC = () => {
  const [selectedEvent, setSelectedEvent] = useState<ScheduledEvent | null>(KIIT_SCHEDULE[0]);
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");

  const filteredEvents = KIIT_SCHEDULE.filter((ev) => {
    const matchesSearch =
      ev.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ev.hostingSociety.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ev.speaker.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = categoryFilter === "all" || ev.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight">
            Event Schedule & Master Timeline
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Date & time-wise schedule, guest speaker arrival coordination, and student hostel transport mapping.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="px-3.5 py-1.5 rounded-xl bg-slate-900 border border-white/10 text-xs">
            <span className="text-slate-400">Total Registered Audience:</span>{" "}
            <span className="font-bold text-cyan-400">1,180 Attendees</span>
          </div>
          <div className="px-3.5 py-1.5 rounded-xl bg-slate-900 border border-white/10 text-xs">
            <span className="text-slate-400">Festival Date:</span>{" "}
            <span className="font-bold text-white">15 Oct 2026</span>
          </div>
        </div>
      </div>

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
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Timeline Events List (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          {filteredEvents.map((ev) => {
            const isSelected = selectedEvent?.id === ev.id;
            return (
              <div
                key={ev.id}
                onClick={() => setSelectedEvent(ev)}
                className={`p-5 rounded-2xl cursor-pointer transition-all border ${
                  isSelected
                    ? "bg-slate-900/95 border-cyan-500/50 shadow-xl shadow-cyan-500/10"
                    : "bg-slate-900/60 border-white/5 hover:border-white/20 hover:bg-slate-900/80"
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

                  {ev.isRelocated && (
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase bg-amber-500/20 text-amber-300 border border-amber-500/40 shrink-0">
                      RELOCATED
                    </span>
                  )}
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
      </div>
    </div>
  );
};
