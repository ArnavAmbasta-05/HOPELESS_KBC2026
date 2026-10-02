import React from "react";
import {
  AlertTriangle,
  Building2,
  Users,
  Clock,
  Radio,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  GitBranch,
  Sparkles,
  MapPin,
  CalendarDays,
} from "lucide-react";
import { ChangeProposal } from "../types";
import { NavSection } from "./Sidebar";

interface OverviewProps {
  proposal: ChangeProposal | null;
  onNavigate: (section: NavSection) => void;
  onSimulate: () => Promise<void>;
  isSimulating: boolean;
}

export const OverviewView: React.FC<OverviewProps> = ({
  proposal,
  onNavigate,
  onSimulate,
  isSimulating,
}) => {
  return (
    <div className="space-y-6">
      {/* 1. Critical Incident Alert Banner */}
      <div className="p-5 rounded-2xl bg-gradient-to-r from-rose-950/80 via-slate-900 to-slate-900 border border-rose-500/40 relative overflow-hidden shadow-2xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-start space-x-3.5">
            <div className="w-10 h-10 rounded-xl bg-rose-500/20 border border-rose-500/40 flex items-center justify-center shrink-0">
              <AlertTriangle className="w-5 h-5 text-rose-400 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-rose-500/30 text-rose-200 border border-rose-500/40">
                  ACTIVE OUTAGE • 08:00 AM IST
                </span>
                <span className="text-xs text-slate-400">Source: Notion Webhook (Estate Office)</span>
              </div>
              <h2 className="text-lg font-black text-white mt-1">
                Main Auditorium Unavailable (08:00 – 23:59)
              </h2>
              <p className="text-xs text-slate-300 mt-0.5">
                Emergency ceiling AC leak reported. 4 major conclave sessions (1,180 registered attendees) require re-homing.
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3 shrink-0">
            <button
              onClick={() => onNavigate("simulation")}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-xs font-bold text-white shadow-lg shadow-cyan-500/20 transition-all flex items-center space-x-2"
            >
              <GitBranch className="w-4 h-4" />
              <span>Open Simulation Studio</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* 2. Top-Level Live Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1 */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-white/10 hover:border-cyan-500/30 transition-all space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="font-bold uppercase tracking-wider text-[10px]">Impacted Sessions</span>
            <CalendarDays className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-black text-white">4</span>
            <span className="text-xs font-bold text-emerald-400">100% Re-homed</span>
          </div>
          <p className="text-[11px] text-slate-400">
            Opening (380), Keynote (230), Panel (180), Prize (390)
          </p>
        </div>

        {/* Card 2 */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-white/10 hover:border-cyan-500/30 transition-all space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="font-bold uppercase tracking-wider text-[10px]">Registrants at Risk</span>
            <Users className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-black text-white">1,180</span>
            <span className="text-xs font-bold text-cyan-400">Broadcast Queued</span>
          </div>
          <p className="text-[11px] text-slate-400">
            SMS + App Push alerts mapped across 6 hostel cohorts
          </p>
        </div>

        {/* Card 3 */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-white/10 hover:border-cyan-500/30 transition-all space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="font-bold uppercase tracking-wider text-[10px]">Volunteer Shifts</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-black text-white">15 / 16</span>
            <span className="text-xs font-bold text-emerald-400">Untouched</span>
          </div>
          <p className="text-[11px] text-slate-400">
            4 shifted + 1 Standby Activated (Arjun for Keynote AV)
          </p>
        </div>

        {/* Card 4 */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-white/10 hover:border-cyan-500/30 transition-all space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="font-bold uppercase tracking-wider text-[10px]">Follow-up Tasks</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-black text-white">17</span>
            <span className="text-xs font-bold text-rose-400">1 At Risk (0m Slack)</span>
          </div>
          <p className="text-[11px] text-slate-400">
            Task N08 escalated to Stage Lead for immediate handoff
          </p>
        </div>
      </div>

      {/* 3. Quick Actions & Operations Triage */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Quick Jump Modules (6 cols) */}
        <div className="lg:col-span-6 space-y-3">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Platform Navigation Shortcuts
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <button
              onClick={() => onNavigate("venues")}
              className="p-4 rounded-2xl bg-slate-900/80 border border-white/10 hover:border-cyan-500/40 hover:bg-slate-800/60 text-left transition-all group space-y-1.5"
            >
              <div className="flex items-center justify-between">
                <Building2 className="w-5 h-5 text-cyan-400" />
                <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-cyan-400 transition-transform group-hover:translate-x-1" />
              </div>
              <h4 className="text-sm font-bold text-white">Venues & Capacities</h4>
              <p className="text-[11px] text-slate-400">
                Inspect 6 auditoriums, seat caps, AV rigs & staff rosters.
              </p>
            </button>

            <button
              onClick={() => onNavigate("schedule")}
              className="p-4 rounded-2xl bg-slate-900/80 border border-white/10 hover:border-cyan-500/40 hover:bg-slate-800/60 text-left transition-all group space-y-1.5"
            >
              <div className="flex items-center justify-between">
                <CalendarDays className="w-5 h-5 text-indigo-400" />
                <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-indigo-400 transition-transform group-hover:translate-x-1" />
              </div>
              <h4 className="text-sm font-bold text-white">Master Schedule</h4>
              <p className="text-[11px] text-slate-400">
                Date-wise sessions, VIP guests & student hostel breakdown.
              </p>
            </button>

            <button
              onClick={() => onNavigate("map")}
              className="p-4 rounded-2xl bg-slate-900/80 border border-white/10 hover:border-cyan-500/40 hover:bg-slate-800/60 text-left transition-all group space-y-1.5"
            >
              <div className="flex items-center justify-between">
                <MapPin className="w-5 h-5 text-emerald-400" />
                <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-emerald-400 transition-transform group-hover:translate-x-1" />
              </div>
              <h4 className="text-sm font-bold text-white">Campus 2.5D Map</h4>
              <p className="text-[11px] text-slate-400">
                Track live electric shuttles, gate crowds & walking corridors.
              </p>
            </button>

            <button
              onClick={() => onNavigate("notion-ai")}
              className="p-4 rounded-2xl bg-slate-900/80 border border-white/10 hover:border-cyan-500/40 hover:bg-slate-800/60 text-left transition-all group space-y-1.5"
            >
              <div className="flex items-center justify-between">
                <Sparkles className="w-5 h-5 text-purple-400" />
                <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-purple-400 transition-transform group-hover:translate-x-1" />
              </div>
              <h4 className="text-sm font-bold text-white">Notion & AI Co-Pilot</h4>
              <p className="text-[11px] text-slate-400">
                Monitor live 32-page sync & query the AI supervisor.
              </p>
            </button>
          </div>
        </div>

        {/* Right: Operational Risks & Weather Status (6 cols) */}
        <div className="lg:col-span-6 space-y-3">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Priority Risk Matrix (TAD §10)
          </div>

          <div className="space-y-3">
            <div className="p-4 rounded-2xl bg-slate-900/90 border border-rose-500/30 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/40">
                  RISK-01 • HIGH PRIORITY
                </span>
                <span className="text-[11px] font-bold text-rose-400">Slack: 0 Min</span>
              </div>
              <h4 className="text-xs font-bold text-white">
                Task N08 &quot;Opening Act Rehearsal at Open Air Theatre&quot;
              </h4>
              <p className="text-[11px] text-slate-300">
                Estimated finish at 09:45 matches hard door opening deadline (09:45). Any stage sound delay impacts VIP Opening Ceremony.
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-slate-900/90 border border-amber-500/30 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40">
                  RISK-02 • MEDIUM PRIORITY
                </span>
                <span className="text-[11px] font-bold text-amber-400">Capacity 600</span>
              </div>
              <h4 className="text-xs font-bold text-white">
                Open Air Theatre Outdoor Venue Capacity & Weather Monitor
              </h4>
              <p className="text-[11px] text-slate-300">
                3 sessions moved to Open Air Theatre. Rain risk currently 12% (Clear Sky). Portable waterproof canopy rig placed on standby in Store.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
