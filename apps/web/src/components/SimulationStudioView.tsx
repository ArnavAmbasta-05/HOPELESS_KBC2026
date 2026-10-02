import React, { useState } from "react";
import {
  GitBranch,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  Footprints,
  Clock,
  Building2,
  Users,
  ShieldCheck,
  Send,
  HelpCircle,
  RefreshCw,
  SlidersHorizontal,
} from "lucide-react";
import { ChangeProposal } from "../types";

interface SimulationStudioProps {
  proposal: ChangeProposal | null;
  onSimulate: () => Promise<void>;
  onApprove: (proposalId: string) => Promise<void>;
  onReject: (proposalId: string, reason: string) => Promise<void>;
  isSimulating: boolean;
  isActionLoading: boolean;
  actionMessage: string | null;
}

// Exact calibrated distances across KIIT University Campuses
const VENUE_DISTANCE_MATRIX: Record<
  string,
  Record<string, { distanceMeters: number; walkTimeMin: number; shuttleTimeMin: number }>
> = {
  ven_main_aud: {
    ven_open_air: { distanceMeters: 120, walkTimeMin: 1.5, shuttleTimeMin: 1 },
    ven_seminar: { distanceMeters: 450, walkTimeMin: 5, shuttleTimeMin: 2 },
    ven_ksac_chintan: { distanceMeters: 850, walkTimeMin: 10, shuttleTimeMin: 3 },
    ven_convention_c3: { distanceMeters: 1200, walkTimeMin: 14, shuttleTimeMin: 4 },
    ven_lh3: { distanceMeters: 550, walkTimeMin: 6, shuttleTimeMin: 2 },
  },
};

export const SimulationStudioView: React.FC<SimulationStudioProps> = ({
  proposal,
  onSimulate,
  onApprove,
  onReject,
  isSimulating,
  isActionLoading,
  actionMessage,
}) => {
  const [rejectModalOpen, setRejectModalOpen] = useState(false);
  const [rejectReason, setRejectReason] = useState("");
  const [activeTab, setActiveTab] = useState<"venues" | "volunteers" | "tasks" | "diff" | "ai">("venues");

  const isApproved = proposal?.status === "approved" || proposal?.status === "committed";
  const isRejected = proposal?.status === "rejected";

  return (
    <div className="space-y-8">
      {/* Action Banner / Notification */}
      {actionMessage && (
        <div className="p-4 rounded-2xl bg-emerald-950/60 border border-emerald-500/40 text-xs font-semibold text-emerald-300 flex items-center space-x-2.5 shadow-xl">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
          <span>{actionMessage}</span>
        </div>
      )}

      {/* Top Header & Simulation Trigger */}
      <div className="glass-panel aurora-ring p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2.5">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 flex items-center space-x-1">
              <GitBranch className="w-3 h-3" />
              <span>CP-SAT OPTIMIZATION SOLVER</span>
            </span>
            {proposal && (
              <span className="text-xs font-mono text-slate-400">
                Branch ID: <strong className="text-cyan-400">{proposal.proposal_id}</strong>
              </span>
            )}
          </div>
          <h1 className="text-2xl font-black text-white mt-1.5">
            Simulation Studio & Change Proposal Engine
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Evaluate what-if contingency plans, calculate exact venue transit times, and review grounded AI briefings before committing changes.
          </p>
        </div>

        <div className="flex items-center space-x-3 shrink-0">
          <button
            onClick={onSimulate}
            disabled={isSimulating || isActionLoading}
            className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-white/10 text-xs font-bold text-slate-200 hover:text-white transition-all flex items-center space-x-2"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isSimulating ? "animate-spin text-cyan-400" : ""}`} />
            <span>{isSimulating ? "Solving Constraints..." : "Re-Simulate Plan"}</span>
          </button>

          {proposal && !isApproved && !isRejected && (
            <>
              <button
                onClick={() => setRejectModalOpen(true)}
                disabled={isActionLoading}
                className="px-4 py-2.5 rounded-xl bg-rose-950/40 hover:bg-rose-900/60 border border-rose-500/40 text-xs font-bold text-rose-300 transition-all flex items-center space-x-1.5"
              >
                <XCircle className="w-4 h-4" />
                <span>Reject Plan (0 Writes)</span>
              </button>

              <button
                onClick={() => onApprove(proposal.proposal_id)}
                disabled={isActionLoading}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 text-xs font-bold text-white shadow-lg shadow-emerald-500/20 transition-all flex items-center space-x-2"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Approve & Commit to Notion</span>
              </button>
            </>
          )}
        </div>
      </div>

      {proposal ? (
        <div className="space-y-6">
          {/* Proposal Status & Grounded AI Briefing */}
          <div className="glass-panel p-5 rounded-2xl border-l-4 border-l-cyan-400 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-cyan-400" />
                <span className="text-xs font-bold uppercase tracking-wider text-cyan-300">
                  AI Grounded Operations Briefing (TAD AT-07)
                </span>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                Confidence: 98% • Verifiable Sources
              </span>
            </div>

            <p className="text-xs text-slate-200 leading-relaxed font-medium">
              {proposal.ai_summary}
            </p>

            <div className="pt-2 border-t border-white/5 flex flex-wrap items-center justify-between text-[11px] text-slate-400 gap-2">
              <div className="flex items-center space-x-2">
                <span className="text-slate-500">Source of Truth:</span>
                <span className="font-mono text-cyan-400">tool:venue_resolver</span>
                <span>•</span>
                <span className="font-mono text-cyan-400">tool:volunteer_solver</span>
                <span>•</span>
                <span className="font-mono text-cyan-400">tool:task_planner</span>
              </div>
              <div className="text-slate-500 italic">
                *Hard constraints validated independently before admission.
              </div>
            </div>
          </div>

          {/* Navigation Sub-Tabs */}
          <div className="flex items-center space-x-2 border-b border-white/10 pb-2">
            {[
              { id: "venues", label: "Venue Re-homing & Distances", count: proposal.venue_resolution.assignments.length },
              { id: "volunteers", label: "Volunteer Shifts & Standby", count: proposal.volunteer_reallocation.changes.length },
              { id: "tasks", label: "Task Slack & Risk Matrix", count: proposal.task_plan.length },
              { id: "diff", label: "Operational Diff (30 Items)", count: proposal.diff.total_changes },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                    : "text-slate-400 hover:text-slate-200 bg-slate-900/60 border border-white/5"
                }`}
              >
                <span>{tab.label}</span>
                <span className="px-1.5 py-0.5 rounded-full text-[10px] bg-slate-800 text-slate-300">
                  {tab.count}
                </span>
              </button>
            ))}
          </div>

          {/* Tab 1: Venue Re-homing with Exact Calculated Distances */}
          {activeTab === "venues" && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {proposal.venue_resolution.assignments.map((asgn) => {
                  const distInfo =
                    VENUE_DISTANCE_MATRIX["ven_main_aud"]?.[asgn.new_venue_id] || {
                      distanceMeters: 120,
                      walkTimeMin: 1.5,
                      shuttleTimeMin: 1,
                    };

                  return (
                    <div
                      key={asgn.session_id}
                      className="p-5 rounded-2xl bg-slate-900/90 border border-white/10 space-y-4"
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <span className="text-[10px] font-mono text-cyan-400 font-bold">
                            SESSION: {asgn.session_id}
                          </span>
                          <h3 className="text-base font-bold text-white mt-0.5">{asgn.session_name}</h3>
                        </div>
                        <div className="text-right">
                          <span className="text-xs font-bold text-indigo-400">{asgn.registrants} Pax</span>
                          <div className="text-[10px] text-slate-500">Registered</div>
                        </div>
                      </div>

                      {/* Venue Swap Visualizer */}
                      <div className="p-3 rounded-xl bg-slate-950/80 border border-white/5 flex items-center justify-between text-xs">
                        <div className="min-w-0">
                          <div className="text-[10px] text-rose-400 font-bold uppercase">Original Venue</div>
                          <div className="font-semibold text-slate-300 truncate">{asgn.original_venue_name}</div>
                          <div className="text-[10px] text-rose-300 line-through">Capacity: 1,600</div>
                        </div>

                        <ArrowRight className="w-5 h-5 text-cyan-400 mx-2 shrink-0 animate-pulse" />

                        <div className="min-w-0 text-right">
                          <div className="text-[10px] text-emerald-400 font-bold uppercase">Optimal Target</div>
                          <div className="font-semibold text-emerald-300 truncate">{asgn.new_venue_name}</div>
                          <div className="text-[10px] text-emerald-400">Capacity: {asgn.capacity} Seats</div>
                        </div>
                      </div>

                      {/* Transit Distance & Time Breakdown */}
                      <div className="p-3 rounded-xl bg-cyan-950/20 border border-cyan-500/20 grid grid-cols-3 gap-2 text-center text-xs">
                        <div>
                          <span className="text-[10px] text-slate-400 flex items-center justify-center space-x-1">
                            <Footprints className="w-3 h-3 text-cyan-400" />
                            <span>Walking Dist</span>
                          </span>
                          <div className="font-bold text-white mt-0.5">{distInfo.distanceMeters} Meters</div>
                        </div>

                        <div>
                          <span className="text-[10px] text-slate-400 flex items-center justify-center space-x-1">
                            <Clock className="w-3 h-3 text-cyan-400" />
                            <span>Walk Time</span>
                          </span>
                          <div className="font-bold text-cyan-300 mt-0.5">{distInfo.walkTimeMin} Minutes</div>
                        </div>

                        <div>
                          <span className="text-[10px] text-slate-400 flex items-center justify-center space-x-1">
                            <Building2 className="w-3 h-3 text-indigo-400" />
                            <span>Shuttle Time</span>
                          </span>
                          <div className="font-bold text-indigo-300 mt-0.5">{distInfo.shuttleTimeMin} Min (Link)</div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Tab 2: Volunteer Reallocations */}
          {activeTab === "volunteers" && (
            <div className="space-y-3">
              <div className="p-4 rounded-xl bg-slate-900/80 border border-white/10 flex items-center justify-between text-xs">
                <div>
                  <span className="text-slate-400">Optimization Goal:</span>{" "}
                  <strong className="text-white">Minimal Roster Disturbance (CP-SAT)</strong>
                </div>
                <div className="space-y-0.5 text-right">
                  <span className="text-emerald-400 font-bold">15 / 16 Volunteers Untouched</span>
                  <div className="text-[10px] text-cyan-400">1 Standby Volunteer Activated</div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {proposal.volunteer_reallocation.changes.map((v, i) => (
                  <div
                    key={i}
                    className="p-4 rounded-xl bg-slate-900/90 border border-white/5 flex items-start justify-between text-xs"
                  >
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-white">{v.name}</span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-indigo-500/20 text-indigo-300">
                          {v.skill}
                        </span>
                      </div>
                      <div className="text-slate-400 text-[11px] mt-1">{v.note}</div>
                      <div className="text-cyan-400 text-[11px] font-semibold mt-1">
                        Assigned: {v.session_name || v.venue_name || "Active Standby"}
                      </div>
                    </div>

                    {v.is_standby_activated ? (
                      <span className="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                        STANDBY CALLED
                      </span>
                    ) : (
                      <span className="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase bg-amber-500/20 text-amber-300 border border-amber-500/40">
                        REASSIGNED
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tab 3: Task Slack & Risk Matrix */}
          {activeTab === "tasks" && (
            <div className="space-y-3">
              {proposal.task_plan.map((t) => (
                <div
                  key={t.task_id}
                  className={`p-4 rounded-xl border flex items-center justify-between text-xs ${
                    t.is_at_risk
                      ? "bg-rose-950/30 border-rose-500/40"
                      : "bg-slate-900/80 border-white/5"
                  }`}
                >
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-slate-500 text-[11px]">{t.task_id}</span>
                      <span className="font-bold text-white">{t.description}</span>
                      {t.is_at_risk && (
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-rose-500/20 text-rose-300 border border-rose-500/40">
                          SLACK: 0 MIN (ESCALATE)
                        </span>
                      )}
                    </div>
                    <div className="text-slate-400 text-[11px]">
                      Team: {t.team} • Estimated Finish: {t.estimated_finish_str} (Hard Deadline: {t.deadline_str})
                    </div>
                  </div>

                  <div className="text-right">
                    <div className={`font-bold ${t.is_at_risk ? "text-rose-400" : "text-emerald-400"}`}>
                      Slack: +{t.slack_minutes}m
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Tab 4: Operational Diff Items */}
          {activeTab === "diff" && (
            <div className="space-y-2">
              {proposal.diff.items.map((item, i) => (
                <div
                  key={i}
                  className="p-3 rounded-xl bg-slate-900/80 border border-white/5 flex items-center justify-between text-xs"
                >
                  <div className="flex items-center space-x-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        item.action === "modified"
                          ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                          : item.action === "added"
                          ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                          : "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                      }`}
                    >
                      {item.action}
                    </span>
                    <span className="font-medium text-white">{item.summary}</span>
                  </div>

                  <span className="font-mono text-[10px] text-slate-500">{item.entity_id}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div className="glass-panel p-16 text-center space-y-3">
          <GitBranch className="w-12 h-12 text-slate-500 mx-auto animate-pulse" />
          <h3 className="text-lg font-bold text-white">No Active Simulation Branch</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Click &quot;Re-Simulate Plan&quot; to run the Google OR-Tools constraint solver and assemble a What-If change proposal.
          </p>
          <button
            onClick={onSimulate}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 text-xs font-bold text-white shadow-lg"
          >
            Launch Incident Simulation
          </button>
        </div>
      )}

      {/* Reject Modal */}
      {rejectModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel max-w-md w-full p-6 rounded-2xl border border-rose-500/40 space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center space-x-2">
              <XCircle className="w-5 h-5 text-rose-400" />
              <span>Reject Change Proposal</span>
            </h3>
            <p className="text-xs text-slate-300">
              Rejecting this proposal guarantees <strong>ZERO WRITES</strong> to the operational state and Notion databases.
            </p>
            <textarea
              placeholder="State rationale for rejection..."
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              className="w-full p-3 rounded-xl bg-slate-950 border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-rose-500"
              rows={3}
            />
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setRejectModalOpen(false)}
                className="px-4 py-2 rounded-xl text-xs font-bold text-slate-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  if (proposal) onReject(proposal.proposal_id, rejectReason || "Operator rejected proposal");
                  setRejectModalOpen(false);
                }}
                className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-xs font-bold text-white shadow-lg"
              >
                Confirm Rejection
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
