import React, { useState, useEffect } from "react";
import { Zap, Search, CheckCircle2, AlertTriangle } from "lucide-react";
import { Reveal, RevealGroup, Item, SectionHeader } from "./ui";

export interface VolunteerMember {
  id: string;
  name: string;
  phone: string;
  role: string;
  skill: "AV & Sound Engineering" | "VIP Dignitary Escort" | "Stage Décor & Logistics" | "Crowd Control & Scanning" | "Registration & Hospitality";
  status: "Assigned" | "Shifted" | "Standby" | "Active Standby";
  assignedVenue: string;
  assignedSession?: string;
  hoursWorked: number;
}

// Volunteer roster is served live by the backend scenario service
// (GET /api/v1/scenario/volunteers) — the same seed the volunteer
// CP-SAT solver uses. No hardcoded roster here.

export const VolunteersView: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [skillFilter, setSkillFilter] = useState("all");
  const [roster, setRoster] = useState<VolunteerMember[]>([]);
  const [notif, setNotif] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  // Roster is served live by the backend scenario service (same seed the
  // volunteer CP-SAT solver uses): GET /api/v1/scenario/volunteers.
  useEffect(() => {
    fetch("/api/v1/scenario/volunteers")
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data: VolunteerMember[]) => {
        setRoster(data);
        setLoadError(null);
      })
      .catch((err) => {
        console.error("Failed to load volunteers:", err);
        setLoadError("Unable to load the volunteer roster from the operations API.");
      });
  }, []);

  const activateStandby = (id: string, name: string) => {
    setRoster((prev) =>
      prev.map((v) => (v.id === id ? { ...v, status: "Active Standby" as const } : v))
    );
    setNotif(`Activated ${name} to Active Standby! Dispatched SMS dispatch to mobile.`);
    setTimeout(() => setNotif(null), 4000);
  };

  const filtered = roster.filter((v) => {
    const matchesSearch =
      v.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      v.assignedVenue.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSkill = skillFilter === "all" || v.skill === skillFilter;
    return matchesSearch && matchesSkill;
  });

  return (
    <div className="space-y-8">
      {/* Action Notification */}
      {notif && (
        <div className="p-3.5 rounded-2xl bg-cyan-950/60 border border-cyan-500/40 text-xs font-semibold text-cyan-200 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-cyan-300" />
          <span>{notif}</span>
        </div>
      )}

      {loadError && (
        <div className="p-3.5 rounded-2xl bg-rose-950/40 border border-rose-500/30 text-xs font-semibold text-rose-200 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-rose-300" />
          <span>{loadError} Ensure the API is running on :8000.</span>
        </div>
      )}

      {/* Header */}
      <Reveal>
        <SectionHeader
          kicker="Crew command"
          title={<>Volunteers &amp; <span className="text-aurora">staffing roster</span></>}
          subtitle="Real-time skill matching (CP-SAT), nearest-standby dispatch and shift rebalancing during disruptions."
          icon={<Zap className="w-3.5 h-3.5" />}
          right={
            <div className="flex items-center gap-3">
              <div className="px-3.5 py-2 rounded-xl glass-soft text-xs">
                <span className="text-slate-400">Active crew:</span>{" "}
                <span className="font-bold text-cyan-300">
                  {roster.filter((v) => v.status !== "Active Standby").length}
                </span>
              </div>
              <div className="px-3.5 py-2 rounded-xl glass-soft text-xs">
                <span className="text-slate-400">Standby:</span>{" "}
                <span className="font-bold text-emerald-300">
                  {roster.filter((v) => v.status === "Active Standby").length} ready
                </span>
              </div>
            </div>
          }
        />
      </Reveal>

      {/* Filter Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search volunteer name, venue, phone..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-900/90 border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50"
          />
        </div>

        <div className="flex items-center space-x-2 w-full sm:w-auto overflow-x-auto">
          {["all", "AV & Sound Engineering", "VIP Dignitary Escort", "Stage Décor & Logistics", "Crowd Control & Scanning"].map((sk) => (
            <button
              key={sk}
              onClick={() => setSkillFilter(sk)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                skillFilter === sk
                  ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                  : "text-slate-400 hover:text-slate-200 bg-slate-900/60 border border-white/5"
              }`}
            >
              {sk === "all" ? "All Skills" : sk.split(" ")[0] + " " + (sk.split(" ")[1] || "")}
            </button>
          ))}
        </div>
      </div>

      {/* Roster Cards Grid */}
      <RevealGroup className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((v) => (
          <Item
            key={v.id}
            className="rail-card glass-panel glass-panel-hover p-5 rounded-2xl space-y-3.5"
          >
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-sm font-bold text-white">{v.name}</h3>
                <div className="text-[11px] text-slate-400 font-medium">{v.role}</div>
              </div>

              <span
                className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                  v.status === "Active Standby"
                    ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 animate-pulse"
                    : v.status === "Shifted"
                    ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                    : v.status === "Standby"
                    ? "bg-slate-800 text-slate-300 border border-white/10"
                    : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                }`}
              >
                {v.status}
              </span>
            </div>

            {/* Skill Tag & Venue */}
            <div className="space-y-1 text-xs">
              <div className="flex items-center space-x-1.5 text-cyan-400 font-semibold">
                <Zap className="w-3.5 h-3.5" />
                <span>{v.skill}</span>
              </div>
              <div className="text-slate-300 text-[11px]">
                Assigned: <strong>{v.assignedVenue}</strong>
              </div>
              {v.assignedSession && (
                <div className="text-slate-400 text-[10px]">Session: {v.assignedSession}</div>
              )}
            </div>

            {/* Footer / Actions */}
            <div className="pt-3 border-t border-white/5 flex items-center justify-between text-xs">
              <span className="text-slate-500 font-mono text-[11px]">{v.phone}</span>

              {v.status === "Standby" && (
                <button
                  onClick={() => activateStandby(v.id, v.name)}
                  className="px-2.5 py-1 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-[10px] shadow"
                >
                  Call Standby
                </button>
              )}
            </div>
          </Item>
        ))}
      </RevealGroup>
    </div>
  );
};
