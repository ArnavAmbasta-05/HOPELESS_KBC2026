import React, { useState } from "react";
import {
  CheckCircle,
  XCircle,
  AlertTriangle,
  Sparkles,
  GitBranch,
  Layers,
  ArrowRight,
  ShieldCheck,
  Building,
  Users,
  Clock,
  Send,
  HelpCircle,
  FileCheck
} from "lucide-react";
import { ChangeProposal } from "../types";

interface ProposalReviewViewProps {
  proposal: ChangeProposal | null;
  onApprove: (proposalId: string) => Promise<void>;
  onReject: (proposalId: string, reason: string) => Promise<void>;
  isActionLoading: boolean;
  actionMessage: string | null;
}

export const ProposalReviewView: React.FC<ProposalReviewViewProps> = ({
  proposal,
  onApprove,
  onReject,
  isActionLoading,
  actionMessage,
}) => {
  const [rejectModalOpen, setRejectModalOpen] = useState(false);
  const [rejectReason, setRejectReason] = useState("");
  const [activeSubTab, setActiveSubTab] = useState<"venues" | "volunteers" | "tasks" | "diff">("venues");

  if (!proposal) {
    return (
      <div className="glass-panel p-12 text-center">
        <GitBranch className="w-12 h-12 text-slate-500 mx-auto mb-3 animate-pulse" />
        <h3 className="text-lg font-bold text-white">No Active Simulation Branch</h3>
        <p className="text-sm text-slate-400 mt-1">
          Trigger a simulation from the dashboard to generate a what-if Change Proposal.
        </p>
      </div>
    );
  }

  const isApproved = proposal.status === "approved" || proposal.status === "committed";
  const isRejected = proposal.status === "rejected";

  return (
    <div className="space-y-6">
      {/* 1. Branch Status Bar & Metadata */}
      <div className="glass-panel p-6 relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-3">
              <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 flex items-center space-x-1.5">
                <GitBranch className="w-3.5 h-3.5" />
                <span>BRANCH: {proposal.proposal_id}</span>
              </span>

              {isApproved && (
                <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center space-x-1">
                  <CheckCircle className="w-3.5 h-3.5" />
                  <span>COMMITTED TO OPERATIONAL STATE</span>
                </span>
              )}

              {isRejected && (
                <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-rose-500/20 text-rose-300 border border-rose-500/40 flex items-center space-x-1">
                  <XCircle className="w-3.5 h-3.5" />
                  <span>REJECTED (ZERO WRITES TO BASELINE)</span>
                </span>
              )}

              {!isApproved && !isRejected && (
                <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-amber-500/20 text-amber-300 border border-amber-500/40 animate-pulse">
                  STATE: BRANCH ONLY (AWAITING APPROVAL)
                </span>
              )}
            </div>

            <h2 className="text-2xl font-black text-white mt-2">
              Change Proposal: Main Auditorium Outage Response Plan
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Event: {proposal.event_id} • Baseline Rev: #{proposal.baseline_revision} • Proposal Rev: #{proposal.version} • Created: {new Date(proposal.created_at).toLocaleTimeString()} IST
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-3 shrink-0">
            {!isApproved && !isRejected && (
              <>
                <button
                  onClick={() => setRejectModalOpen(true)}
                  disabled={isActionLoading}
                  className="px-4 py-2.5 rounded-xl bg-rose-950/60 hover:bg-rose-900/80 text-rose-300 border border-rose-500/40 font-semibold text-xs flex items-center space-x-1.5 transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
                >
                  <XCircle className="w-4 h-4 text-rose-400" />
                  <span>Reject Proposal</span>
                </button>

                <button
                  onClick={() => onApprove(proposal.proposal_id)}
                  disabled={isActionLoading}
                  className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs shadow-lg shadow-emerald-600/30 flex items-center space-x-2 transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
                >
                  <CheckCircle className="w-4 h-4" />
                  <span>Approve & Apply Plan</span>
                </button>
              </>
            )}

            {isApproved && (
              <div className="flex items-center space-x-2 text-emerald-400 text-xs font-semibold px-4 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/30">
                <ShieldCheck className="w-4 h-4" />
                <span>Committed by {proposal.approved_by || "Operator"}</span>
              </div>
            )}
          </div>
        </div>

        {actionMessage && (
          <div className="mt-4 p-3 rounded-lg bg-indigo-500/10 border border-indigo-500/30 text-xs text-indigo-300">
            {actionMessage}
          </div>
        )}
      </div>

      {/* 2. AI Narrative Summary Card (BR-014, NFR-AI-001, AT-07) */}
      <div className="glass-panel p-5 border-indigo-500/30 bg-gradient-to-br from-indigo-950/30 via-slate-900 to-slate-900">
        <div className="flex items-center justify-between pb-3 border-b border-white/10">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            <h3 className="text-sm font-bold text-indigo-300">AI Narrative Summary</h3>
          </div>
          <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
            [AI-GENERATED — Unverified Narrative; Facts Below Are Truth]
          </span>
        </div>
        <p className="text-sm text-slate-200 mt-3 leading-relaxed">
          {proposal.ai_summary}
        </p>
      </div>

      {/* 3. Detailed Artifact Sub-Tabs */}
      <div className="glass-panel p-6">
        <div className="flex items-center space-x-2 border-b border-white/10 pb-4">
          <button
            onClick={() => setActiveSubTab("venues")}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
              activeSubTab === "venues"
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Venue Re-homing & Explainability
          </button>

          <button
            onClick={() => setActiveSubTab("volunteers")}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
              activeSubTab === "volunteers"
                ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/40"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Volunteer Shifts (CP-SAT)
          </button>

          <button
            onClick={() => setActiveSubTab("tasks")}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
              activeSubTab === "tasks"
                ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            17 Follow-up Tasks & Slack
          </button>

          <button
            onClick={() => setActiveSubTab("diff")}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
              activeSubTab === "diff"
                ? "bg-purple-500/20 text-purple-300 border border-purple-500/40"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Proposal Semantic Diff
          </button>
        </div>

        {/* Sub-Tab 1: Venues & Retained Rejections */}
        {activeSubTab === "venues" && (
          <div className="mt-5 space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Resolved Session Reallocations ({proposal.venue_resolution.assignments.length})
              </h4>
              <span className="text-xs text-slate-400">
                Total Rejection Reasons Logged: <strong className="text-cyan-400">{proposal.venue_resolution.total_rejections_logged}</strong>
              </span>
            </div>

            <div className="grid grid-cols-1 gap-4">
              {proposal.venue_resolution.assignments.map((assignment) => (
                <div
                  key={assignment.session_id}
                  className="p-4 rounded-xl bg-slate-900/80 border border-white/10 space-y-3"
                >
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
                    <div>
                      <h5 className="font-bold text-white text-sm">{assignment.session_name}</h5>
                      <p className="text-xs text-slate-400">
                        Registered: <strong className="text-slate-200">{assignment.registrants}</strong> • New Venue: <strong className="text-emerald-400">{assignment.new_venue_name}</strong> (Cap {assignment.capacity}, {assignment.new_venue_building})
                      </p>
                    </div>
                    {assignment.required_equipment.length > 0 && (
                      <div className="flex flex-wrap gap-1.5">
                        {assignment.required_equipment.map((eq, i) => (
                          <span
                            key={i}
                            className="px-2.5 py-1 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[11px] font-semibold"
                          >
                            + {eq}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Explainability / Retained Rejection Reasons */}
                  <div className="p-3 rounded-lg bg-slate-950/70 border border-white/5 space-y-1">
                    <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                      Rejected Candidate Venues (Explainability Trace):
                    </span>
                    <ul className="space-y-1 mt-1 text-xs text-slate-300">
                      {assignment.rejections.map((rej, i) => (
                        <li key={i} className="flex items-center space-x-2">
                          <span className="text-rose-400 font-bold">✗</span>
                          <span>{rej.reason}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>

            {/* Speaker Soft Re-evaluation */}
            <div className="mt-6 pt-4 border-t border-white/10">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
                Speaker Soft-Edge Re-evaluations
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {proposal.venue_resolution.speaker_reevaluations.map((spk) => (
                  <div
                    key={spk.speaker_id}
                    className="p-3 rounded-xl bg-slate-900/60 border border-white/5 flex items-start space-x-3 text-xs"
                  >
                    <span className={`font-bold ${spk.escort_needed ? "text-rose-400" : "text-emerald-400"}`}>
                      {spk.status_symbol}
                    </span>
                    <div>
                      <span className="font-semibold text-white">{spk.name}</span>{" "}
                      <span className="text-slate-400">({spk.title})</span>
                      <p className="text-[11px] text-slate-300 mt-0.5">{spk.note}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Sub-Tab 2: Volunteers */}
        {activeSubTab === "volunteers" && (
          <div className="mt-5 space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Shift Re-allocations (Google OR-Tools CP-SAT)
              </h4>
              <span className="text-xs text-emerald-400 font-semibold">
                {proposal.volunteer_reallocation.untouched_count} of {proposal.volunteer_reallocation.total_volunteers} Assignments Untouched
              </span>
            </div>

            <div className="grid grid-cols-1 gap-3">
              {proposal.volunteer_reallocation.changes.map((change, i) => (
                <div
                  key={i}
                  className={`p-3 rounded-xl border flex items-center justify-between text-xs ${
                    change.action === "removed"
                      ? "bg-rose-950/20 border-rose-500/30 text-rose-300"
                      : change.action === "standby_activated"
                      ? "bg-amber-950/20 border-amber-500/30 text-amber-300"
                      : "bg-emerald-950/20 border-emerald-500/30 text-emerald-300"
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <span className="font-bold font-mono uppercase text-[11px]">
                      {change.action === "removed" ? "− REMOVED" : "+ ASSIGNED"}
                    </span>
                    <span className="font-bold text-white text-sm">{change.name}</span>
                    <span className="text-slate-400">• {change.note}</span>
                  </div>

                  {change.is_standby_activated && (
                    <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 text-[10px] font-bold">
                      STANDBY ACTIVATED
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Sub-Tab 3: Tasks & Slack */}
        {activeSubTab === "tasks" && (
          <div className="mt-5 space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Operational Follow-up Tasks (17 Tasks Generated)
              </h4>
              <span className="text-xs text-rose-400 font-bold">
                1 Task AT RISK (Slack 0m)
              </span>
            </div>

            <div className="overflow-x-auto rounded-xl border border-white/10">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-900/90 text-[11px] text-slate-400 uppercase font-semibold border-b border-white/10">
                  <tr>
                    <th className="p-3">ID</th>
                    <th className="p-3">Team</th>
                    <th className="p-3">Task Description</th>
                    <th className="p-3">Est. Finish</th>
                    <th className="p-3">Deadline</th>
                    <th className="p-3">Slack</th>
                    <th className="p-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {proposal.task_plan.map((task) => (
                    <tr
                      key={task.task_id}
                      className={`hover:bg-slate-800/40 transition-colors ${
                        task.is_at_risk ? "bg-rose-950/30 text-rose-200" : ""
                      }`}
                    >
                      <td className="p-3 font-mono font-bold text-white">{task.task_id}</td>
                      <td className="p-3 font-semibold text-slate-400 uppercase">{task.team}</td>
                      <td className="p-3 font-medium text-white">{task.description}</td>
                      <td className="p-3 text-slate-300">{task.estimated_finish_str}</td>
                      <td className="p-3 text-slate-300">{task.deadline_str}</td>
                      <td className={`p-3 font-bold ${task.is_at_risk ? "text-rose-400" : "text-emerald-400"}`}>
                        {task.slack_minutes}m
                      </td>
                      <td className="p-3">
                        {task.is_at_risk ? (
                          <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/40 font-bold text-[10px]">
                            AT RISK
                          </span>
                        ) : (
                          <span className="text-emerald-400 font-medium">OK</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Escalation Item */}
            {proposal.escalations.length > 0 && (
              <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/40 flex items-center space-x-3 text-xs text-rose-200">
                <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
                <div>
                  <span className="font-bold">Automated Role Escalation:</span>{" "}
                  {proposal.escalations[0].reason}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Sub-Tab 4: Diff */}
        {activeSubTab === "diff" && (
          <div className="mt-5 space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Semantic State Diff ({proposal.diff.total_changes} Object Mutations)
              </h4>
              <div className="flex space-x-2 text-xs font-semibold">
                <span className="text-emerald-400">+{proposal.diff.added_count} Added</span>
                <span className="text-rose-400">−{proposal.diff.removed_count} Removed</span>
                <span className="text-amber-400">~{proposal.diff.modified_count} Modified</span>
              </div>
            </div>

            <div className="space-y-2">
              {proposal.diff.items.map((item, i) => (
                <div
                  key={i}
                  className="p-3 rounded-lg bg-slate-900/60 border border-white/5 flex items-center justify-between text-xs"
                >
                  <div className="flex items-center space-x-3">
                    <span
                      className={`px-2 py-0.5 rounded font-mono text-[10px] font-bold uppercase ${
                        item.action === "added"
                          ? "bg-emerald-500/20 text-emerald-300"
                          : item.action === "removed"
                          ? "bg-rose-500/20 text-rose-300"
                          : "bg-amber-500/20 text-amber-300"
                      }`}
                    >
                      {item.action}
                    </span>
                    <span className="text-slate-400 font-mono">[{item.entity_type}]</span>
                    <span className="text-white font-medium">{item.summary}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Reject Modal */}
      {rejectModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel p-6 max-w-md w-full border-rose-500/30">
            <h3 className="text-lg font-bold text-white">Reject Change Proposal</h3>
            <p className="text-xs text-slate-300 mt-1">
              Rejecting guarantees <strong>ZERO</strong> operational writes to active event twin data (AT-08).
            </p>

            <textarea
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="Enter reason for rejection..."
              className="w-full mt-3 p-3 rounded-lg bg-slate-900 border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-rose-500"
              rows={3}
            />

            <div className="flex justify-end space-x-3 mt-4">
              <button
                onClick={() => setRejectModalOpen(false)}
                className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  onReject(proposal.proposal_id, rejectReason);
                  setRejectModalOpen(false);
                }}
                className="px-4 py-2 rounded-lg bg-rose-600 text-white text-xs font-bold shadow-lg shadow-rose-600/30"
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
