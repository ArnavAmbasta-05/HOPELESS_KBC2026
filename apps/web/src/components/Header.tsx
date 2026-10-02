import React from "react";
import { Shield, Activity, Radio, AlertTriangle, RefreshCw } from "lucide-react";

interface HeaderProps {
  currentRole: string;
  onRoleChange: (role: string) => void;
  activeTab: "dashboard" | "proposal" | "graph";
  onTabChange: (tab: "dashboard" | "proposal" | "graph") => void;
  hasActiveBranch: boolean;
  onRefresh: () => void;
  isSimulating: boolean;
}

const ROLES = [
  { id: "event_commander", name: "Event Commander" },
  { id: "ops_lead", name: "Operations Lead" },
  { id: "tech_lead", name: "Tech / AV Lead" },
  { id: "stage_manager", name: "Stage Manager" },
  { id: "volunteer_coordinator", name: "Volunteer Coordinator" },
  { id: "super_admin", name: "Super Admin" },
];

export const Header: React.FC<HeaderProps> = ({
  currentRole,
  onRoleChange,
  activeTab,
  onTabChange,
  hasActiveBranch,
  onRefresh,
  isSimulating,
}) => {
  return (
    <header className="sticky top-0 z-50 bg-[#090d16]/95 backdrop-blur-md border-b border-white/10 px-6 py-3.5 flex items-center justify-between shadow-xl">
      {/* Brand & Tagline */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2.5">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-500 via-indigo-500 to-purple-500 flex items-center justify-center font-black text-white text-xl shadow-lg shadow-indigo-500/20 tracking-wider">
            K
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-cyan-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">
                KoreX
              </span>
              <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                Command Center v1.0
              </span>
            </div>
            <p className="text-[11px] text-slate-400 tracking-wide">
              KIIT EventOps AI Command Center • KBC 2026
            </p>
          </div>
        </div>

        {/* Live SSE / System Health pill */}
        <div className="hidden md:flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-800/60 border border-emerald-500/30 text-emerald-400 text-xs font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-400 pulse-live" />
          <span>LIVE SSE CONNECTED</span>
          <span className="text-slate-500">•</span>
          <span className="text-slate-400">08:00:14 IST</span>
        </div>
      </div>

      {/* Navigation Tabs */}
      <nav className="flex items-center space-x-1.5 bg-slate-900/80 p-1 rounded-xl border border-white/5">
        <button
          onClick={() => onTabChange("dashboard")}
          className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            activeTab === "dashboard"
              ? "bg-gradient-to-r from-indigo-600 to-indigo-500 text-white shadow-md shadow-indigo-600/30"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
          }`}
        >
          Operations Dashboard
        </button>

        <button
          onClick={() => onTabChange("proposal")}
          className={`px-4 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-2 transition-all ${
            activeTab === "proposal"
              ? "bg-gradient-to-r from-cyan-600 to-cyan-500 text-white shadow-md shadow-cyan-600/30"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
          }`}
        >
          <span>Change Proposal</span>
          {hasActiveBranch && (
            <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
          )}
        </button>

        <button
          onClick={() => onTabChange("graph")}
          className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            activeTab === "graph"
              ? "bg-gradient-to-r from-purple-600 to-purple-500 text-white shadow-md shadow-purple-600/30"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
          }`}
        >
          Dependency Graph
        </button>
      </nav>

      {/* Role Switcher & Actions */}
      <div className="flex items-center space-x-3">
        <button
          onClick={onRefresh}
          disabled={isSimulating}
          title="Refresh Simulation & Live State"
          className="p-2 rounded-lg bg-slate-800/60 hover:bg-slate-700/80 text-slate-300 border border-white/10 transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${isSimulating ? "animate-spin text-cyan-400" : ""}`} />
        </button>

        <div className="flex items-center space-x-2 bg-slate-900/90 px-3 py-1.5 rounded-xl border border-white/10">
          <Shield className="w-3.5 h-3.5 text-indigo-400" />
          <select
            value={currentRole}
            onChange={(e) => onRoleChange(e.target.value)}
            className="bg-transparent text-xs font-semibold text-slate-200 focus:outline-none cursor-pointer"
          >
            {ROLES.map((r) => (
              <option key={r.id} value={r.id} className="bg-slate-900 text-slate-200">
                {r.name}
              </option>
            ))}
          </select>
        </div>
      </div>
    </header>
  );
};
