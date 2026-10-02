import React from "react";
import {
  AlertTriangle,
  MapPin,
  Clock,
  Users,
  CheckCircle2,
  ArrowRight,
  TrendingUp,
  Volume2,
  Calendar,
  Layers,
  Sparkles,
  Info
} from "lucide-react";
import { ChangeProposal } from "../types";

interface DashboardViewProps {
  proposal: ChangeProposal | null;
  onReviewProposal: () => void;
  onSimulate: () => void;
  isSimulating: boolean;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  proposal,
  onReviewProposal,
  onSimulate,
  isSimulating,
}) => {
  return (
    <div className="space-y-6">
      {/* 1. Major Disruption Alert Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-red-950/80 via-slate-900 to-slate-900 border border-red-500/30 p-6 shadow-2xl backdrop-blur-xl">
        <div className="absolute top-0 right-0 w-96 h-full bg-red-500/5 blur-3xl pointer-events-none" />
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div className="flex items-start space-x-4">
            <div className="p-3 bg-red-500/20 text-red-400 rounded-xl border border-red-500/30 mt-1">
              <AlertTriangle className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center space-x-2.5">
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold tracking-wide uppercase bg-red-500/20 text-red-300 border border-red-500/40">
                  Active Disruption • 08:00 IST
                </span>
                <span className="text-xs text-slate-400">Source: Notion Webhook / Estate Office</span>
              </div>
              <h2 className="text-xl font-bold text-white mt-1">
                Main Auditorium Unavailable (08:00 – 23:59)
              </h2>
              <p className="text-sm text-slate-300 mt-1 max-w-2xl">
                Reason: Emergency ceiling AC leak reported. 4 major conclave sessions (1,180 registered participants), AV crews, and stage decor directly impacted.
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3 shrink-0">
            {proposal ? (
              <button
                onClick={onReviewProposal}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-semibold text-sm shadow-lg shadow-indigo-500/25 flex items-center space-x-2 transition-all hover:scale-105 active:scale-95"
              >
                <span>Review Change Proposal</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={onSimulate}
                disabled={isSimulating}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-semibold text-sm shadow-lg shadow-indigo-500/25 flex items-center space-x-2 transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
              >
                <Sparkles className="w-4 h-4" />
                <span>{isSimulating ? "Simulating AI Twin..." : "Run AI Simulation Branch"}</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* 2. Key Operational Metrics Tiles (TAD §7, FR-LIVE-002) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Tile 1: Impacted Sessions */}
        <div className="glass-panel p-5 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Impacted Sessions
            </span>
            <Calendar className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-white">4</span>
            <span className="text-xs text-amber-400 font-medium">100% Re-homed in Proposal</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            Opening (380), Keynote (230), Panel (180), Prize (390)
          </p>
          <div className="mt-3 pt-3 border-t border-white/5 flex items-center justify-between text-[11px] text-slate-500">
            <span>Source: Digital Twin Graph</span>
            <span>Live • 08:00:10</span>
          </div>
        </div>

        {/* Tile 2: Affected Attendees */}
        <div className="glass-panel p-5 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Registrants at Risk
            </span>
            <Users className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-white">1,180</span>
            <span className="text-xs text-emerald-400 font-medium">Broadcast Queued</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            SMS + Push notifications mapped across 4 cohorts
          </p>
          <div className="mt-3 pt-3 border-t border-white/5 flex items-center justify-between text-[11px] text-slate-500">
            <span>Source: Attendance Twin</span>
            <span>Live • 08:00:10</span>
          </div>
        </div>

        {/* Tile 3: Volunteer Re-allocation */}
        <div className="glass-panel p-5 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Volunteer Shifts
            </span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-white">15 / 16</span>
            <span className="text-xs text-cyan-400 font-medium">Untouched (CP-SAT)</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            4 shifted + 1 Standby Activated (Arjun for Keynote AV)
          </p>
          <div className="mt-3 pt-3 border-t border-white/5 flex items-center justify-between text-[11px] text-slate-500">
            <span>Source: OR-Tools Optimizer</span>
            <span>Live • 08:00:10</span>
          </div>
        </div>

        {/* Tile 4: Follow-up Tasks */}
        <div className="glass-panel p-5 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Follow-up Tasks
            </span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-white">17</span>
            <span className="text-xs text-rose-400 font-medium">1 At Risk (Slack 0m)</span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            Task N08 escalated to Stage Lead for immediate handoff
          </p>
          <div className="mt-3 pt-3 border-t border-white/5 flex items-center justify-between text-[11px] text-slate-500">
            <span>Source: EDF Task Planner</span>
            <span>Live • 08:00:10</span>
          </div>
        </div>
      </div>

      {/* 3. Top Risks & Next Action Widget (NFR-USE-001, NFR-USE-002) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Risks Card */}
        <div className="glass-panel p-6 lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2.5">
              <div className="w-2.5 h-2.5 rounded-full bg-rose-500 pulse-live" />
              <h3 className="text-base font-bold text-white">Top Operational Risks (Priority Matrix)</h3>
            </div>
            <span className="text-xs font-semibold px-2.5 py-1 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">
              Commander Overview (≤2 Views)
            </span>
          </div>

          <div className="space-y-3">
            {/* Risk Item 1: N08 Zero Slack */}
            <div className="p-4 rounded-xl bg-slate-900/90 border border-rose-500/30 flex flex-col md:flex-row md:items-center justify-between gap-3">
              <div className="flex items-start space-x-3">
                <span className="px-2 py-1 rounded bg-rose-500/20 text-rose-400 font-mono text-xs font-bold shrink-0">
                  RISK-01 • HIGH
                </span>
                <div>
                  <h4 className="text-sm font-semibold text-white">
                    N08 "Opening act rehearsal at Open Air Theatre" — Slack 0m
                  </h4>
                  <p className="text-xs text-slate-300 mt-0.5">
                    Estimated finish 09:45 matches hard deadline 09:45 when attendee doors open. Any sound check delay impacts VIP Opening Ceremony.
                  </p>
                  <p className="text-[11px] text-emerald-400 mt-1">
                    Mitigation: Stage décor and sound check teams assigned expedited priority transfer.
                  </p>
                </div>
              </div>
              <button
                onClick={onReviewProposal}
                className="px-3.5 py-1.5 rounded-lg bg-rose-600/30 hover:bg-rose-600/50 text-rose-200 border border-rose-500/40 text-xs font-semibold shrink-0 transition-all"
              >
                Inspect Escalation
              </button>
            </div>

            {/* Risk Item 2: Outdoor Weather Contingency */}
            <div className="p-4 rounded-xl bg-slate-900/90 border border-amber-500/30 flex flex-col md:flex-row md:items-center justify-between gap-3">
              <div className="flex items-start space-x-3">
                <span className="px-2 py-1 rounded bg-amber-500/20 text-amber-400 font-mono text-xs font-bold shrink-0">
                  RISK-02 • MEDIUM
                </span>
                <div>
                  <h4 className="text-sm font-semibold text-white">
                    Open Air Theatre Outdoor Venue Capacity & Weather
                  </h4>
                  <p className="text-xs text-slate-300 mt-0.5">
                    3 sessions moved to Open Air Theatre (Capacity 600). Contingent on dry weather during 10:00–18:00 window.
                  </p>
                  <p className="text-[11px] text-emerald-400 mt-1">
                    Mitigation: Weather resilience worker active; indoor portable canopy rig on standby in Store.
                  </p>
                </div>
              </div>
              <button
                onClick={onReviewProposal}
                className="px-3.5 py-1.5 rounded-lg bg-amber-600/30 hover:bg-amber-600/50 text-amber-200 border border-amber-500/40 text-xs font-semibold shrink-0 transition-all"
              >
                View Equipment
              </button>
            </div>
          </div>
        </div>

        {/* Live Blast Radius Mini-Card */}
        <div className="glass-panel p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-bold text-white">Blast Radius Summary</h3>
              <span className="text-[11px] px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300">
                12 Hard Hits
              </span>
            </div>

            <div className="space-y-2.5 text-xs text-slate-300">
              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-white/5">
                <span className="text-slate-400">Root Cause:</span>
                <span className="font-semibold text-white">Main Auditorium Outage</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-white/5">
                <span className="text-slate-400">Disrupted Sessions:</span>
                <span className="font-semibold text-amber-400">4 Sessions</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-white/5">
                <span className="text-slate-400">Pre-existing Tasks:</span>
                <span className="font-semibold text-rose-400">2 Tasks (AV & Décor)</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-white/5">
                <span className="text-slate-400">Stale Public Comms:</span>
                <span className="font-semibold text-cyan-400">3 Notifications</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-white/5">
                <span className="text-slate-400">Deferred Soft Edges:</span>
                <span className="font-semibold text-purple-400">7 Soft Edges</span>
              </div>
            </div>
          </div>

          <button
            onClick={onReviewProposal}
            className="w-full mt-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold text-xs border border-white/10 flex items-center justify-center space-x-2 transition-all"
          >
            <span>Open Simulation Workspace</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
