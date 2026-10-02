import React from "react";
import {
  LayoutDashboard,
  Building2,
  CalendarDays,
  GitBranch,
  MapPin,
  Users2,
  Sparkles,
  QrCode,
  Radio,
  ChevronRight,
} from "lucide-react";

export type NavSection =
  | "overview"
  | "venues"
  | "schedule"
  | "simulation"
  | "map"
  | "volunteers"
  | "notion-ai"
  | "participant";

interface SidebarProps {
  activeSection: NavSection;
  onSectionChange: (section: NavSection) => void;
  hasActiveBranch: boolean;
  incidentCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeSection,
  onSectionChange,
  hasActiveBranch,
  incidentCount,
}) => {
  const navItems = [
    {
      id: "overview" as NavSection,
      label: "Overview",
      icon: LayoutDashboard,
      badge: incidentCount > 0 ? `${incidentCount} Alert` : undefined,
      badgeColor: "bg-rose-500/20 text-rose-300 border-rose-500/40",
    },
    {
      id: "venues" as NavSection,
      label: "Venues & Auditoriums",
      icon: Building2,
      subtitle: "Capacities, AV & Staff",
    },
    {
      id: "schedule" as NavSection,
      label: "Master Schedule",
      icon: CalendarDays,
      subtitle: "Timeline, Speakers & Hostels",
    },
    {
      id: "simulation" as NavSection,
      label: "Simulation Studio",
      icon: GitBranch,
      badge: hasActiveBranch ? "Active Branch" : undefined,
      badgeColor: "bg-cyan-500/20 text-cyan-300 border-cyan-500/40 animate-pulse",
      subtitle: "What-If Solver & Distances",
    },
    {
      id: "map" as NavSection,
      label: "Campus 2.5D Map",
      icon: MapPin,
      subtitle: "Live Shuttles & Gates",
    },
    {
      id: "volunteers" as NavSection,
      label: "Volunteers & Shifts",
      icon: Users2,
      subtitle: "Skill Matching & Standby",
    },
    {
      id: "notion-ai" as NavSection,
      label: "Notion & AI Center",
      icon: Sparkles,
      subtitle: "Live Sync & AI Co-Pilot",
    },
  ];

  return (
    <aside className="w-64 bg-[#080d1a] border-r border-white/10 flex flex-col shrink-0 select-none">
      {/* Brand Header */}
      <div className="p-4 border-b border-white/10 flex items-center space-x-3">
        <img
          src="/logo.png"
          alt="KoreX Logo"
          className="w-10 h-10 object-contain rounded-xl shadow-lg shadow-cyan-500/20 shrink-0 border border-white/10 bg-slate-950 p-1"
        />
        <div className="min-w-0">
          <div className="flex items-center space-x-2">
            <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-cyan-300 via-indigo-200 to-purple-300 bg-clip-text text-transparent">
              KoreX
            </span>
            <span className="text-[10px] font-bold uppercase px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
              Enterprise
            </span>
          </div>
          <p className="text-[11px] text-slate-400 font-medium">KIIT EventOps Command</p>
        </div>
      </div>

      {/* Live Operational Status */}
      <div className="mx-3 mt-4 p-3 rounded-xl bg-slate-900/80 border border-white/5 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 radar-dot" />
          <span className="text-xs font-semibold text-slate-200">KBC 2026 Conclave</span>
        </div>
        <span className="text-[10px] text-emerald-400 font-mono font-medium">LIVE</span>
      </div>

      {/* Main Navigation List */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-500">
          Core Operations
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeSection === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSectionChange(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-left transition-all group ${
                isActive
                  ? "bg-gradient-to-r from-cyan-600/30 to-indigo-600/20 text-white border border-cyan-500/40 shadow-lg shadow-cyan-500/10 font-semibold"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40 border border-transparent font-medium"
              }`}
            >
              <div className="flex items-center space-x-3 min-w-0">
                <Icon
                  className={`w-4 h-4 shrink-0 transition-colors ${
                    isActive ? "text-cyan-400" : "text-slate-400 group-hover:text-slate-300"
                  }`}
                />
                <div className="min-w-0">
                  <div className="text-xs truncate">{item.label}</div>
                  {item.subtitle && !isActive && (
                    <div className="text-[10px] text-slate-500 truncate">{item.subtitle}</div>
                  )}
                </div>
              </div>

              {item.badge && (
                <span
                  className={`ml-2 text-[10px] font-bold px-2 py-0.5 rounded-full border shrink-0 ${
                    item.badgeColor || "bg-slate-800 text-slate-300 border-white/10"
                  }`}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Quick Launch: Participant Portal */}
      <div className="p-3 border-t border-white/10">
        <a
          href="/participant"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-between p-2.5 rounded-xl bg-slate-900/90 border border-white/10 hover:border-cyan-500/40 hover:bg-slate-800/60 transition-all text-slate-300 hover:text-white group"
        >
          <div className="flex items-center space-x-2.5">
            <QrCode className="w-4 h-4 text-cyan-400" />
            <div>
              <div className="text-xs font-semibold">Participant Portal</div>
              <div className="text-[10px] text-slate-500">QR Check-in & Passes</div>
            </div>
          </div>
          <ChevronRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-cyan-400 transition-transform group-hover:translate-x-0.5" />
        </a>
      </div>
    </aside>
  );
};
