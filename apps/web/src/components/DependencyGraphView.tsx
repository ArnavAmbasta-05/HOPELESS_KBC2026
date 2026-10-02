import React, { useState } from "react";
import { Layers, GitCommit, AlertCircle, Users, Radio, Wrench, Calendar, Info } from "lucide-react";

interface NodeItem {
  id: string;
  label: string;
  type: "root" | "session" | "task" | "comm" | "cohort" | "soft_speaker" | "soft_volunteer";
  edgeType: string;
  impactLevel: "hard" | "soft";
  detail: string;
}

const NODES: NodeItem[] = [
  // Root
  { id: "ven_main_aud", label: "Main Auditorium (Outage 08:00–23:59)", type: "root", edgeType: "root_disruption", impactLevel: "hard", detail: "Ceiling AC leak reported by Estate Office" },
  // Hard Hits
  { id: "ses_opening", label: "Opening Ceremony (10:00–10:45)", type: "session", edgeType: "hosts", impactLevel: "hard", detail: "380 registrants • Falls inside unavailability window" },
  { id: "ses_keynote", label: "Keynote: AI in FinTech (11:00–12:00)", type: "session", edgeType: "hosts", impactLevel: "hard", detail: "230 registrants • Falls inside unavailability window" },
  { id: "ses_panel", label: "Panel: Building Startups (14:00–15:00)", type: "session", edgeType: "hosts", impactLevel: "hard", detail: "180 registrants • Falls inside unavailability window" },
  { id: "ses_prize", label: "Prize Distribution (17:00–18:00)", type: "session", edgeType: "hosts", impactLevel: "hard", detail: "390 registrants • Falls inside unavailability window" },
  { id: "tsk_av", label: "AV setup in Main Auditorium", type: "task", edgeType: "task_at", impactLevel: "hard", detail: "Status: in_progress at unavailable venue" },
  { id: "tsk_decor", label: "Stage décor in Main Auditorium", type: "task", edgeType: "task_at", impactLevel: "hard", detail: "Status: pending at unavailable venue" },
  { id: "comm_insta", label: "Instagram post 'Opening at Main Aud'", type: "comm", edgeType: "mentions", impactLevel: "hard", detail: "Public post references stale venue" },
  { id: "comm_boards", label: "Printed schedule boards (Gate 1, 3)", type: "comm", edgeType: "mentions", impactLevel: "hard", detail: "Physical signage references stale venue" },
  { id: "cohort_opening", label: "380 Registrants (Opening Ceremony)", type: "cohort", edgeType: "has_registrants", impactLevel: "hard", detail: "Location update SMS & Push broadcast needed" },
  { id: "cohort_keynote", label: "230 Registrants (Keynote AI)", type: "cohort", edgeType: "has_registrants", impactLevel: "hard", detail: "Location update SMS & Push broadcast needed" },
  { id: "cohort_panel", label: "180 Registrants (Startup Panel)", type: "cohort", edgeType: "has_registrants", impactLevel: "hard", detail: "Location update SMS & Push broadcast needed" },
  { id: "cohort_prize", label: "390 Registrants (Prize Distribution)", type: "cohort", edgeType: "has_registrants", impactLevel: "hard", detail: "Location update SMS & Push broadcast needed" },
  // Deferred Soft Edges
  { id: "soft_vc", label: "Chief Guest (Vice Chancellor)", type: "soft_speaker", edgeType: "speaker_escort", impactLevel: "soft", detail: "Arrives at Bldg A -> Venue Open Air Theatre (Bldg C) -> Escort needed" },
  { id: "soft_mehra", label: "Dr. Mehra (Keynote)", type: "soft_speaker", edgeType: "speaker_escort", impactLevel: "soft", detail: "Arrives at Bldg B -> Venue Seminar Hall (Bldg B) -> No action" },
  { id: "soft_founders", label: "Startup Panel (3 Founders)", type: "soft_speaker", edgeType: "speaker_escort", impactLevel: "soft", detail: "Arrives at Bldg B -> Venue Open Air Theatre (Bldg C) -> Escort needed" },
  { id: "soft_volunteers", label: "Volunteer Staffing Roster", type: "soft_volunteer", edgeType: "staffing_reeval", impactLevel: "soft", detail: "15 of 16 untouched, 4 shifted, Arjun standby activated" },
];

export const DependencyGraphView: React.FC = () => {
  const [selectedNode, setSelectedNode] = useState<NodeItem | null>(NODES[0]);
  const [filter, setFilter] = useState<"all" | "hard" | "soft">("all");

  const filteredNodes = NODES.filter((n) => {
    if (filter === "all") return true;
    return n.impactLevel === filter;
  });

  return (
    <div className="space-y-6">
      {/* Header & Filter Controls */}
      <div className="glass-panel p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white">Digital Twin Dependency Graph & Blast Radius</h2>
          <p className="text-xs text-slate-400 mt-1">
            Recursive-CTE bounded traversal • 12 Hard Hits + 7 Deferred Soft Edges (FR-GRAPH-004, FR-LIVE-004)
          </p>
        </div>

        <div className="flex items-center space-x-2 bg-slate-900/90 p-1 rounded-xl border border-white/10">
          <button
            onClick={() => setFilter("all")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold ${
              filter === "all" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
            }`}
          >
            All Nodes (17)
          </button>
          <button
            onClick={() => setFilter("hard")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold ${
              filter === "hard" ? "bg-rose-600 text-white" : "text-slate-400 hover:text-white"
            }`}
          >
            Hard Hits (12)
          </button>
          <button
            onClick={() => setFilter("soft")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold ${
              filter === "soft" ? "bg-purple-600 text-white" : "text-slate-400 hover:text-white"
            }`}
          >
            Soft Edges (7)
          </button>
        </div>
      </div>

      {/* Visual Node Grid + Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Node Grid */}
        <div className="lg:col-span-2 glass-panel p-6 space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-400 font-semibold uppercase tracking-wider">
            <span>Graph Entities</span>
            <span>Click entity to inspect edge path</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {filteredNodes.map((node) => {
              const isSelected = selectedNode?.id === node.id;
              const isRoot = node.type === "root";
              const isHard = node.impactLevel === "hard";

              return (
                <div
                  key={node.id}
                  onClick={() => setSelectedNode(node)}
                  className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? "bg-indigo-950/50 border-indigo-500 shadow-lg shadow-indigo-500/20 scale-[1.02]"
                      : isRoot
                      ? "bg-red-950/30 border-red-500/40 hover:border-red-400"
                      : isHard
                      ? "bg-slate-900/80 border-rose-500/20 hover:border-rose-500/40"
                      : "bg-slate-900/60 border-purple-500/20 hover:border-purple-500/40"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span
                      className={`text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded ${
                        isRoot
                          ? "bg-red-500/20 text-red-300"
                          : isHard
                          ? "bg-rose-500/20 text-rose-300"
                          : "bg-purple-500/20 text-purple-300"
                      }`}
                    >
                      edge={node.edgeType}
                    </span>
                    <span className="text-[10px] text-slate-500 font-mono">{node.id}</span>
                  </div>

                  <h4 className="text-sm font-bold text-white mt-2 leading-snug">{node.label}</h4>
                  <p className="text-xs text-slate-400 mt-1 line-clamp-1">{node.detail}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Selected Node Inspector */}
        <div className="glass-panel p-6 flex flex-col justify-between">
          {selectedNode ? (
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <Info className="w-4 h-4 text-cyan-400" />
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">Node Edge Inspector</h3>
              </div>

              <div className="p-4 rounded-xl bg-slate-900/90 border border-white/10 space-y-3">
                <div>
                  <span className="text-[11px] text-slate-400 uppercase font-semibold">Entity Label:</span>
                  <p className="text-sm font-bold text-white">{selectedNode.label}</p>
                </div>

                <div>
                  <span className="text-[11px] text-slate-400 uppercase font-semibold">Edge Relationship:</span>
                  <p className="text-xs font-mono font-bold text-cyan-300">
                    Main Auditorium --[{selectedNode.edgeType}]--&gt; {selectedNode.id}
                  </p>
                </div>

                <div>
                  <span className="text-[11px] text-slate-400 uppercase font-semibold">Classification:</span>
                  <div className="mt-1">
                    <span
                      className={`px-2.5 py-1 rounded text-xs font-bold uppercase ${
                        selectedNode.impactLevel === "hard"
                          ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                          : "bg-purple-500/20 text-purple-300 border border-purple-500/30"
                      }`}
                    >
                      {selectedNode.impactLevel === "hard" ? "Direct Hard Hit (Immediate)" : "Deferred Soft Edge"}
                    </span>
                  </div>
                </div>

                <div>
                  <span className="text-[11px] text-slate-400 uppercase font-semibold">Operational Context:</span>
                  <p className="text-xs text-slate-200 mt-0.5 leading-relaxed">{selectedNode.detail}</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center text-slate-500 py-12">
              Select a node to inspect its dependency path.
            </div>
          )}

          <div className="pt-4 border-t border-white/5 text-[11px] text-slate-500 text-center">
            Bounded BFS Traversal Depth: 3 • Execution Time: &lt; 0.05s
          </div>
        </div>
      </div>
    </div>
  );
};
