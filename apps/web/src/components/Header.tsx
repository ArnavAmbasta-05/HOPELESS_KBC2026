import React from "react";
import { Shield, Radio, RefreshCw, ChevronDown, Bell } from "lucide-react";
import { NavSection } from "./Sidebar";

interface HeaderProps {
  currentRole: string;
  onRoleChange: (role: string) => void;
  activeSection: NavSection;
  onRefresh: () => void;
  isSimulating: boolean;
}

const ROLES = [
  { id: "event_commander", name: "Event Commander" },
  { id: "ops_lead", name: "Operations Lead" },
  { id: "tech_lead", name: "Tech / AV Lead" },
  { id: "stage_manager", name: "Stage Manager" },
  { id: "volunteer_coordinator", name: "Volunteer Coordinator" },
  { id: "security_lead", name: "Security & Crowd Lead" },
  { id: "transport_lead", name: "Transport & Fleet Lead" },
  { id: "super_admin", name: "Super Admin" },
];

const SECTION_TITLES: Record<NavSection, string> = {
  overview: "Executive Operations Overview",
  venues: "Venues & Auditoriums Directory",
  schedule: "Master Schedule & Timeline",
  simulation: "Simulation Studio & Change Proposals",
  map: "Campus 2.5D Digital Twin Map",
  volunteers: "Volunteers & Shift Roster",
  "notion-ai": "Notion & AI Integration Center",
  participant: "Participant Portal & QR Scanner",
};

export const Header: React.FC<HeaderProps> = ({
  currentRole,
  onRoleChange,
  activeSection,
  onRefresh,
  isSimulating,
}) => {
  return (
    <header className="h-16 bg-[#080d1a]/95 backdrop-blur-md border-b border-white/10 px-6 flex items-center justify-between shrink-0 select-none z-30">
      {/* Breadcrumb Section Title */}
      <div className="flex items-center space-x-3">
        <span className="text-xs font-semibold text-slate-500">Platform</span>
        <span className="text-slate-600">/</span>
        <h2 className="text-sm font-bold text-white tracking-tight">
          {SECTION_TITLES[activeSection] || "Operations"}
        </h2>
      </div>

      {/* Right Controls: Live Telemetry, Notifications & Role Selector */}
      <div className="flex items-center space-x-4">
        {/* Live SSE Pulse */}
        <div className="hidden sm:flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-900 border border-emerald-500/30 text-emerald-400 text-xs font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-400 radar-dot" />
          <span>LIVE TELEMETRY</span>
          <span className="text-slate-600">•</span>
          <span className="text-slate-400 font-mono text-[11px]">08:00:14 IST</span>
        </div>

        {/* Refresh button */}
        <button
          onClick={onRefresh}
          disabled={isSimulating}
          title="Refresh Telemetry & Solvers"
          className="p-2 rounded-xl bg-slate-900 border border-white/10 hover:border-cyan-500/40 text-slate-400 hover:text-white transition-all"
        >
          <RefreshCw className={`w-4 h-4 ${isSimulating ? "animate-spin text-cyan-400" : ""}`} />
        </button>

        {/* Role Selector Dropdown */}
        <div className="relative">
          <div className="flex items-center space-x-2 bg-slate-900/90 border border-white/10 rounded-xl px-3 py-1.5 text-xs text-slate-200">
            <Shield className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            <select
              value={currentRole}
              onChange={(e) => onRoleChange(e.target.value)}
              className="bg-transparent text-xs font-bold text-white focus:outline-none cursor-pointer pr-2"
            >
              {ROLES.map((r) => (
                <option key={r.id} value={r.id} className="bg-[#0f172a] text-white">
                  {r.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>
    </header>
  );
};
