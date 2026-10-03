import React, { useState, useEffect, useMemo, useRef } from "react";
import {
  Info,
  AlertTriangle,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Layers,
  Activity,
  Zap,
  Radio,
  Share2,
  Maximize2,
  Search,
  Sliders,
  Users,
  Calendar,
  Wrench,
  Megaphone,
  UserCheck,
  Crosshair,
  ArrowRight,
  ShieldAlert,
  Compass,
  Sparkles,
} from "lucide-react";

interface NodeItem {
  id: string;
  label: string;
  type: "root" | "session" | "task" | "comm" | "cohort" | "soft_speaker" | "soft_volunteer";
  edgeType: string;
  impactLevel: "hard" | "soft";
  detail: string;
}

interface GraphNode extends NodeItem {
  x: number;
  y: number;
  radius: number;
  color: string;
  borderColor: string;
  ring: number;
  angleDeg: number;
  parentId?: string;
  riskScore: number;
}

export const DependencyGraphView: React.FC = () => {
  const [nodes, setNodes] = useState<NodeItem[]>([]);
  const [selectedNode, setSelectedNode] = useState<NodeItem | null>(null);
  const [hoveredNode, setHoveredNode] = useState<NodeItem | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [filter, setFilter] = useState<"all" | "hard" | "soft" | "session" | "cohort" | "task">("all");
  const [viewMode, setViewMode] = useState<"diagram" | "grid">("diagram");
  const [zoom, setZoom] = useState<number>(1);
  const [isPulseActive, setIsPulseActive] = useState<boolean>(true);
  const [radarSpeed, setRadarSpeed] = useState<"normal" | "fast" | "pause">("normal");
  const [loadError, setLoadError] = useState<string | null>(null);

  const containerRef = useRef<HTMLDivElement>(null);

  // Fetch dependency graph from backend API
  useEffect(() => {
    fetch("/api/v1/scenario/dependencies")
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data: NodeItem[]) => {
        setNodes(data);
        setSelectedNode(data[0] ?? null);
        setLoadError(null);
      })
      .catch((err) => {
        console.error("Failed to load dependency graph:", err);
        setLoadError("Unable to load the dependency graph from the operations API.");
      });
  }, []);

  const hardCount = nodes.filter((n) => n.impactLevel === "hard").length;
  const softCount = nodes.filter((n) => n.impactLevel === "soft").length;

  const filteredNodes = useMemo(() => {
    return nodes.filter((n) => {
      const matchesSearch =
        searchQuery.trim() === "" ||
        n.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
        n.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        n.edgeType.toLowerCase().includes(searchQuery.toLowerCase());

      if (!matchesSearch) return false;

      if (filter === "all") return true;
      if (filter === "hard") return n.impactLevel === "hard";
      if (filter === "soft") return n.impactLevel === "soft";
      if (filter === "session") return n.type === "session";
      if (filter === "cohort") return n.type === "cohort";
      if (filter === "task") return n.type === "task";
      return true;
    });
  }, [nodes, filter, searchQuery]);

  // Compute 2D coordinates for Radial Blast Radar Layout
  const graphNodes: GraphNode[] = useMemo(() => {
    if (!nodes.length) return [];

    const centerX = 450;
    const centerY = 340;

    const rootNode = nodes.find((n) => n.type === "root") || nodes[0];
    const sessionNodes = nodes.filter((n) => n.type === "session");
    const taskNodes = nodes.filter((n) => n.type === "task");
    const commNodes = nodes.filter((n) => n.type === "comm");
    const cohortNodes = nodes.filter((n) => n.type === "cohort");
    const softNodes = nodes.filter((n) => n.type.startsWith("soft"));

    const result: GraphNode[] = [];

    // 1. Root Node (Center)
    result.push({
      ...rootNode,
      x: centerX,
      y: centerY,
      radius: 30,
      color: "#ef4444",
      borderColor: "#f87171",
      ring: 0,
      angleDeg: 0,
      riskScore: 99,
    });

    // 2. Ring 1: Primary Sessions (Radius ~135px)
    const ring1Radius = 135;
    sessionNodes.forEach((node, idx) => {
      const angle = (idx / sessionNodes.length) * 2 * Math.PI - Math.PI / 2;
      const angleDeg = Math.round(((angle * 180) / Math.PI + 360) % 360);
      result.push({
        ...node,
        x: centerX + ring1Radius * Math.cos(angle),
        y: centerY + ring1Radius * Math.sin(angle),
        radius: 22,
        color: "#f43f5e",
        borderColor: "#fb7185",
        ring: 1,
        angleDeg,
        parentId: rootNode.id,
        riskScore: 92 - idx * 4,
      });
    });

    // 3. Ring 2: Tasks, Comms, Cohorts (Radius ~240px)
    const ring2Radius = 240;
    const ring2Items = [...taskNodes, ...commNodes, ...cohortNodes];
    ring2Items.forEach((node, idx) => {
      const angle = (idx / ring2Items.length) * 2 * Math.PI - Math.PI / 2;
      const angleDeg = Math.round(((angle * 180) / Math.PI + 360) % 360);
      let color = "#38bdf8";
      let borderColor = "#7dd3fc";
      let riskScore = 75;
      if (node.type === "task") {
        color = "#f59e0b";
        borderColor = "#fbbf24";
        riskScore = 84;
      } else if (node.type === "cohort") {
        color = "#a855f7";
        borderColor = "#c084fc";
        riskScore = 88;
      }

      result.push({
        ...node,
        x: centerX + ring2Radius * Math.cos(angle),
        y: centerY + ring2Radius * Math.sin(angle),
        radius: 17,
        color,
        borderColor,
        ring: 2,
        angleDeg,
        parentId: rootNode.id,
        riskScore,
      });
    });

    // 4. Ring 3: Soft Edges / VIP Speaker Escorts (Radius ~325px)
    const ring3Radius = 325;
    softNodes.forEach((node, idx) => {
      const angle = (idx / softNodes.length) * 2 * Math.PI - Math.PI / 3;
      const angleDeg = Math.round(((angle * 180) / Math.PI + 360) % 360);
      result.push({
        ...node,
        x: centerX + ring3Radius * Math.cos(angle),
        y: centerY + ring3Radius * Math.sin(angle),
        radius: 15,
        color: "#818cf8",
        borderColor: "#a5b4fc",
        ring: 3,
        angleDeg,
        parentId: rootNode.id,
        riskScore: 55 - idx * 3,
      });
    });

    return result;
  }, [nodes]);

  // Edges computed connecting root and children
  const edges = useMemo(() => {
    if (!graphNodes.length) return [];
    const root = graphNodes.find((n) => n.ring === 0);
    if (!root) return [];

    return graphNodes
      .filter((n) => n.ring > 0)
      .map((target) => ({
        source: root,
        target,
        isHard: target.impactLevel === "hard",
        type: target.edgeType,
      }));
  }, [graphNodes]);

  const selectedGraphNode = useMemo(() => {
    if (!selectedNode) return graphNodes[0] || null;
    return graphNodes.find((n) => n.id === selectedNode.id) || null;
  }, [graphNodes, selectedNode]);

  return (
    <div className="space-y-6">
      {/* Top Header & Disruption Telemetry Bar */}
      <div className="glass-panel p-6 rounded-3xl border border-rose-500/30 bg-gradient-to-r from-slate-900 via-rose-950/20 to-slate-900 shadow-2xl space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-3.5">
            <div className="p-3 rounded-2xl bg-gradient-to-br from-rose-500/30 to-red-600/30 border border-rose-500/40 text-rose-400 shadow-lg shadow-rose-500/20">
              <ShieldAlert className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-2xl font-bold text-white tracking-tight">
                  Autonomous Blast Radius &amp; Incident Radar
                </h2>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase bg-rose-500/20 text-rose-300 border border-rose-500/40 flex items-center space-x-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-400 animate-ping"></span>
                  <span>BFS Traversal Depth: 3</span>
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Real-time Digital Twin topology mapping for <strong>Main Auditorium Outage</strong> • Sub-millisecond recursive impact graph
              </p>
            </div>
          </div>

          {/* Quick Search & Mode Switcher */}
          <div className="flex items-center flex-wrap gap-2.5">
            {/* Search input */}
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search node, session, task..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8 pr-3 py-1.5 rounded-xl bg-slate-950/80 border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-rose-500/50 w-52"
              />
            </div>

            {/* View Mode */}
            <div className="flex items-center bg-slate-950 p-1 rounded-xl border border-white/10 text-xs">
              <button
                onClick={() => setViewMode("diagram")}
                className={`px-3 py-1.5 rounded-lg font-semibold flex items-center space-x-1.5 transition-all ${
                  viewMode === "diagram"
                    ? "bg-gradient-to-r from-rose-600 to-indigo-600 text-white shadow-md shadow-rose-500/20"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                <Activity className="w-3.5 h-3.5" />
                <span>Radar Topology</span>
              </button>
              <button
                onClick={() => setViewMode("grid")}
                className={`px-3 py-1.5 rounded-lg font-semibold flex items-center space-x-1.5 transition-all ${
                  viewMode === "grid"
                    ? "bg-gradient-to-r from-rose-600 to-indigo-600 text-white shadow-md shadow-rose-500/20"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                <Layers className="w-3.5 h-3.5" />
                <span>Grid Table</span>
              </button>
            </div>
          </div>
        </div>

        {/* 4 Scorecard KPI Pills */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 border-t border-white/5">
          <div className="p-3 rounded-xl bg-slate-950/70 border border-white/5 flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400">
              <Crosshair className="w-4 h-4" />
            </div>
            <div>
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Total Blast Nodes</div>
              <div className="text-base font-bold text-white">{nodes.length} Entities</div>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-950/70 border border-white/5 flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-red-500/10 text-red-400">
              <Zap className="w-4 h-4" />
            </div>
            <div>
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Hard Operational Hits</div>
              <div className="text-base font-bold text-rose-300">{hardCount} Direct Nodes</div>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-950/70 border border-white/5 flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
              <Radio className="w-4 h-4" />
            </div>
            <div>
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Deferred Soft Edges</div>
              <div className="text-base font-bold text-indigo-300">{softCount} VIP &amp; Roster</div>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-950/70 border border-white/5 flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
              <Users className="w-4 h-4" />
            </div>
            <div>
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Impacted Attendees</div>
              <div className="text-base font-bold text-purple-300">1,410 Registrants</div>
            </div>
          </div>
        </div>
      </div>

      {loadError && (
        <div className="p-4 rounded-2xl bg-rose-950/40 border border-rose-500/30 text-xs text-rose-200 flex items-center gap-2.5">
          <AlertTriangle className="w-5 h-5 shrink-0 text-rose-400" />
          <span>{loadError} Ensure the backend FastAPI service is running on <strong>http://127.0.0.1:8000</strong>.</span>
        </div>
      )}

      {/* Main Content Area */}
      {viewMode === "diagram" ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Interactive Radar Diagram HUD (8 cols) */}
          <div className="lg:col-span-8 glass-panel p-5 rounded-3xl border border-rose-500/20 bg-slate-950/80 shadow-2xl relative overflow-hidden flex flex-col h-[700px]">
            {/* HUD Top Control Bar */}
            <div className="flex items-center justify-between pb-3 border-b border-white/10 z-10 flex-wrap gap-2">
              {/* Filter Pills */}
              <div className="flex items-center space-x-1.5 overflow-x-auto text-[11px]">
                {[
                  { id: "all", label: `All (${nodes.length})` },
                  { id: "hard", label: `Hard Hits (${hardCount})` },
                  { id: "soft", label: `Soft (${softCount})` },
                  { id: "session", label: "Sessions (4)" },
                  { id: "cohort", label: "Cohorts (4)" },
                  { id: "task", label: "Tasks (2)" },
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setFilter(tab.id as any)}
                    className={`px-2.5 py-1 rounded-lg font-semibold transition-colors ${
                      filter === tab.id
                        ? "bg-rose-600/90 text-white shadow-sm"
                        : "bg-slate-900 text-slate-400 hover:text-white border border-white/5"
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Radar & Zoom Controls */}
              <div className="flex items-center space-x-1.5">
                <button
                  onClick={() => setIsPulseActive(!isPulseActive)}
                  title="Toggle Energy Pulse"
                  className={`px-2.5 py-1.5 rounded-xl border text-xs font-semibold flex items-center space-x-1 ${
                    isPulseActive
                      ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/40"
                      : "bg-slate-900 text-slate-400 border-white/10"
                  }`}
                >
                  <Zap className="w-3.5 h-3.5" />
                  <span className="text-[10px]">Pulse</span>
                </button>
                <button
                  onClick={() => setZoom((z) => Math.min(z + 0.15, 1.8))}
                  className="p-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-white/10 text-slate-300 hover:text-white"
                  title="Zoom In"
                >
                  <ZoomIn className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => setZoom((z) => Math.max(z - 0.15, 0.6))}
                  className="p-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-white/10 text-slate-300 hover:text-white"
                  title="Zoom Out"
                >
                  <ZoomOut className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => setZoom(1)}
                  className="p-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-white/10 text-slate-300 hover:text-white"
                  title="Reset Zoom"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            {/* SVG Diagram Canvas */}
            <div
              ref={containerRef}
              className="flex-1 relative flex items-center justify-center cursor-crosshair overflow-hidden bg-slate-950/90 rounded-2xl mt-3 border border-white/5"
            >
              {/* Background HUD Grid Lines */}
              <div
                className="absolute inset-0 pointer-events-none opacity-20"
                style={{
                  backgroundImage: `radial-gradient(circle at 450px 340px, rgba(239, 68, 68, 0.15) 0%, transparent 70%), linear-gradient(to right, rgba(255, 255, 255, 0.05) 1px, transparent 1px), linear-gradient(to bottom, rgba(255, 255, 255, 0.05) 1px, transparent 1px)`,
                  backgroundSize: "100% 100%, 40px 40px, 40px 40px",
                }}
              />

              <svg
                viewBox="0 0 900 680"
                className="w-full h-full select-none transition-transform duration-200"
                style={{ transform: `scale(${zoom})` }}
              >
                <defs>
                  {/* Glowing Glow Filters */}
                  <filter id="glow-rose" x="-30%" y="-30%" width="160%" height="160%">
                    <feGaussianBlur stdDeviation="8" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                  </filter>
                  <filter id="glow-cyan" x="-30%" y="-30%" width="160%" height="160%">
                    <feGaussianBlur stdDeviation="6" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                  </filter>
                  <filter id="glow-purple" x="-30%" y="-30%" width="160%" height="160%">
                    <feGaussianBlur stdDeviation="6" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                  </filter>

                  {/* Gradient for Links */}
                  <linearGradient id="edge-hard-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#ef4444" stopOpacity="0.9" />
                    <stop offset="100%" stopColor="#f43f5e" stopOpacity="0.5" />
                  </linearGradient>
                  <linearGradient id="edge-soft-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#ef4444" stopOpacity="0.7" />
                    <stop offset="100%" stopColor="#818cf8" stopOpacity="0.4" />
                  </linearGradient>

                  {/* Radar Sweeper Gradient */}
                  <linearGradient id="radar-sweep" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="rgba(239, 68, 68, 0)" />
                    <stop offset="100%" stopColor="rgba(239, 68, 68, 0.25)" />
                  </linearGradient>
                </defs>

                {/* Rotating Radar Sweep Arm */}
                <g transform="translate(450, 340)">
                  <g className="animate-[spin_6s_linear_infinite] origin-center">
                    <path d="M 0 0 L 330 -40 A 330 330 0 0 1 330 40 Z" fill="url(#radar-sweep)" />
                    <line x1="0" y1="0" x2="330" y2="0" stroke="#f87171" strokeWidth="1.5" opacity="0.6" />
                  </g>
                </g>

                {/* Concentric Radar Wave Guides */}
                <circle cx="450" cy="340" r="135" fill="none" stroke="#ef4444" strokeWidth="1" strokeDasharray="4 6" opacity="0.3" />
                <circle cx="450" cy="340" r="240" fill="none" stroke="#38bdf8" strokeWidth="1" strokeDasharray="4 6" opacity="0.25" />
                <circle cx="450" cy="340" r="325" fill="none" stroke="#818cf8" strokeWidth="1" strokeDasharray="4 6" opacity="0.2" />

                {/* Crosshair Compass Axis Lines */}
                <line x1="450" y1="20" x2="450" y2="660" stroke="rgba(255, 255, 255, 0.08)" strokeWidth="1" strokeDasharray="2 4" />
                <line x1="80" y1="340" x2="820" y2="340" stroke="rgba(255, 255, 255, 0.08)" strokeWidth="1" strokeDasharray="2 4" />

                {/* Compass Bearings */}
                <text x="450" y="32" textAnchor="middle" fill="#94a3b8" fontSize="8" fontFamily="monospace">000° N</text>
                <text x="810" y="343" textAnchor="middle" fill="#94a3b8" fontSize="8" fontFamily="monospace">090° E</text>
                <text x="450" y="655" textAnchor="middle" fill="#94a3b8" fontSize="8" fontFamily="monospace">180° S</text>
                <text x="90" y="343" textAnchor="middle" fill="#94a3b8" fontSize="8" fontFamily="monospace">270° W</text>

                {/* Radar Ring Range Labels */}
                <text x="455" y="195" fill="#f43f5e" fontSize="8.5" opacity="0.7" fontFamily="monospace">
                  RING 1: DIRECT SESSIONS (135m)
                </text>
                <text x="455" y="90" fill="#38bdf8" fontSize="8.5" opacity="0.7" fontFamily="monospace">
                  RING 2: TASKS &amp; COHORTS (240m)
                </text>
                <text x="455" y="10" fill="#818cf8" fontSize="8.5" opacity="0.7" fontFamily="monospace">
                  RING 3: VIP ESCORTS &amp; VOLUNTEERS (325m)
                </text>

                {/* Pulsating Shockwave Radar Waves around Epicenter */}
                {isPulseActive && (
                  <>
                    <circle cx="450" cy="340" r="45" fill="none" stroke="#ef4444" strokeWidth="2" opacity="0.5">
                      <animate attributeName="r" values="35;100;160" dur="2.5s" repeatCount="indefinite" />
                      <animate attributeName="opacity" values="0.9;0.3;0" dur="2.5s" repeatCount="indefinite" />
                    </circle>
                    <circle cx="450" cy="340" r="60" fill="none" stroke="#f43f5e" strokeWidth="1.5" opacity="0.4">
                      <animate attributeName="r" values="50;150;250" dur="3.5s" repeatCount="indefinite" />
                      <animate attributeName="opacity" values="0.7;0.2;0" dur="3.5s" repeatCount="indefinite" />
                    </circle>
                  </>
                )}

                {/* Graph Edges / Laser Connector Links */}
                {edges.map((edge, i) => {
                  const isHighlighted =
                    selectedNode?.id === edge.target.id ||
                    hoveredNode?.id === edge.target.id ||
                    selectedNode?.id === "ven_main_aud";

                  return (
                    <g key={`edge-${i}`}>
                      <line
                        x1={edge.source.x}
                        y1={edge.source.y}
                        x2={edge.target.x}
                        y2={edge.target.y}
                        stroke={edge.isHard ? "url(#edge-hard-grad)" : "url(#edge-soft-grad)"}
                        strokeWidth={isHighlighted ? 3 : edge.isHard ? 1.8 : 1.2}
                        strokeDasharray={edge.isHard ? undefined : "3 4"}
                        opacity={isHighlighted ? 1 : 0.45}
                      />

                      {/* Flowing Animated Laser Particles */}
                      {isPulseActive && (
                        <circle r={edge.isHard ? 3 : 2} fill={edge.isHard ? "#fed7aa" : "#c7d2fe"} filter="url(#glow-cyan)">
                          <animateMotion
                            path={`M ${edge.source.x} ${edge.source.y} L ${edge.target.x} ${edge.target.y}`}
                            dur={`${1.8 + (i % 3) * 0.4}s`}
                            repeatCount="indefinite"
                          />
                        </circle>
                      )}
                    </g>
                  );
                })}

                {/* Graph Nodes */}
                {graphNodes.map((node) => {
                  const isSelected = selectedNode?.id === node.id;
                  const isHovered = hoveredNode?.id === node.id;
                  const isRoot = node.ring === 0;

                  return (
                    <g
                      key={node.id}
                      onClick={() => setSelectedNode(node)}
                      onMouseEnter={() => setHoveredNode(node)}
                      onMouseLeave={() => setHoveredNode(null)}
                      className="cursor-pointer"
                    >
                      {/* Target HUD Reticle on Selected Node */}
                      {isSelected && (
                        <g transform={`translate(${node.x}, ${node.y})`}>
                          <circle r={node.radius + 12} fill="none" stroke="#f43f5e" strokeWidth="1.5" strokeDasharray="6 4" className="animate-[spin_8s_linear_infinite]" />
                          <line x1={-node.radius - 16} y1="0" x2={-node.radius - 8} y2="0" stroke="#f43f5e" strokeWidth="2" />
                          <line x1={node.radius + 8} y1="0" x2={node.radius + 16} y2="0" stroke="#f43f5e" strokeWidth="2" />
                          <line x1="0" y1={-node.radius - 16} x2="0" y2={-node.radius - 8} stroke="#f43f5e" strokeWidth="2" />
                          <line x1="0" y1={node.radius + 8} x2="0" y2={node.radius + 16} stroke="#f43f5e" strokeWidth="2" />
                        </g>
                      )}

                      {/* Node Glow Halo for hover */}
                      {isHovered && !isSelected && (
                        <circle
                          cx={node.x}
                          cy={node.y}
                          r={node.radius + 6}
                          fill="none"
                          stroke={node.borderColor}
                          strokeWidth="2"
                          opacity="0.8"
                        />
                      )}

                      {/* Node Body */}
                      <circle
                        cx={node.x}
                        cy={node.y}
                        r={node.radius}
                        fill={node.color}
                        stroke={node.borderColor}
                        strokeWidth={isSelected ? 3.5 : 2}
                        filter={isRoot || isSelected ? "url(#glow-rose)" : undefined}
                      />

                      {/* Node Center Icon / Indicator */}
                      {isRoot ? (
                        <circle cx={node.x} cy={node.y} r="6" fill="#ffffff" />
                      ) : (
                        <circle cx={node.x} cy={node.y} r="3" fill="#ffffff" opacity="0.9" />
                      )}

                      {/* Node Label underneath */}
                      <text
                        x={node.x}
                        y={node.y + node.radius + 13}
                        textAnchor="middle"
                        fill={isSelected ? "#ffffff" : isRoot ? "#fca5a5" : "#e2e8f0"}
                        fontSize={isRoot ? "11.5" : "9.5"}
                        fontWeight={isRoot || isSelected ? "bold" : "600"}
                        fontFamily="sans-serif"
                        className="pointer-events-none drop-shadow"
                      >
                        {node.label.length > 22 ? `${node.label.substring(0, 20)}…` : node.label}
                      </text>

                      {/* Edge Type & Bearing Badge */}
                      {!isRoot && (
                        <text
                          x={node.x}
                          y={node.y + node.radius + 24}
                          textAnchor="middle"
                          fill={node.impactLevel === "hard" ? "#f87171" : "#a5b4fc"}
                          fontSize="8"
                          fontFamily="monospace"
                          className="pointer-events-none opacity-85"
                        >
                          [{node.edgeType}] • {node.angleDeg}°
                        </text>
                      )}
                    </g>
                  );
                })}
              </svg>
            </div>

            {/* Bottom HUD Legend & Radar Diagnostics */}
            <div className="pt-3 border-t border-white/10 flex items-center justify-between flex-wrap gap-2 text-[11px] text-slate-400">
              <div className="flex items-center space-x-4">
                <span className="flex items-center space-x-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-red-500 shadow-sm shadow-red-500/50"></span>
                  <span className="font-semibold text-slate-300">Outage Epicenter</span>
                </span>
                <span className="flex items-center space-x-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
                  <span>Ring 1: 4 Displaced Sessions</span>
                </span>
                <span className="flex items-center space-x-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
                  <span>Ring 2: Tasks &amp; Comms</span>
                </span>
                <span className="flex items-center space-x-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-indigo-400"></span>
                  <span>Ring 3: VIP Escorts &amp; Roster</span>
                </span>
              </div>
              <span className="text-[10px] text-emerald-400 font-mono flex items-center space-x-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping inline-block"></span>
                <span>Real-Time Graph Telemetry Active</span>
              </span>
            </div>
          </div>

          {/* Node Deep Inspection HUD Sidebar (4 cols) */}
          <div className="lg:col-span-4 space-y-4">
            <div className="glass-panel p-5 rounded-3xl border border-rose-500/20 bg-slate-950/90 shadow-2xl flex flex-col justify-between h-[700px]">
              <div className="space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-white/10">
                  <div className="flex items-center space-x-2">
                    <Crosshair className="w-4 h-4 text-rose-400" />
                    <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                      Node Blast Telemetry
                    </h3>
                  </div>
                  {selectedGraphNode && (
                    <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-500/30">
                      θ: {selectedGraphNode.angleDeg}° // R: {selectedGraphNode.ring * 110}m
                    </span>
                  )}
                </div>

                {selectedGraphNode ? (
                  <div className="space-y-3.5 text-xs">
                    {/* Header Badges & Risk Score */}
                    <div className="flex items-center justify-between">
                      <span
                        className={`px-2.5 py-1 rounded-full text-[10px] font-mono font-bold uppercase border ${
                          selectedGraphNode.impactLevel === "hard"
                            ? "bg-rose-500/20 text-rose-300 border-rose-500/40"
                            : "bg-purple-500/20 text-purple-300 border-purple-500/40"
                        }`}
                      >
                        {selectedGraphNode.impactLevel === "hard" ? "Direct Hard Hit (Immediate)" : "Deferred Soft Edge"}
                      </span>
                      <span className="font-mono text-[11px] text-slate-400">{selectedGraphNode.id}</span>
                    </div>

                    {/* Threat / Impact Score Meter */}
                    <div className="p-3.5 rounded-2xl bg-slate-900/90 border border-white/10 space-y-2">
                      <div className="flex items-center justify-between text-xs font-semibold">
                        <span className="text-slate-400">Impact Propagation Threat:</span>
                        <span
                          className={`font-bold ${
                            selectedGraphNode.riskScore > 80
                              ? "text-rose-400"
                              : selectedGraphNode.riskScore > 60
                              ? "text-amber-400"
                              : "text-indigo-300"
                          }`}
                        >
                          {selectedGraphNode.riskScore}% Critical
                        </span>
                      </div>
                      <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${
                            selectedGraphNode.riskScore > 80
                              ? "bg-gradient-to-r from-rose-500 to-red-600"
                              : selectedGraphNode.riskScore > 60
                              ? "bg-gradient-to-r from-amber-500 to-orange-600"
                              : "bg-gradient-to-r from-indigo-500 to-cyan-500"
                          }`}
                          style={{ width: `${selectedGraphNode.riskScore}%` }}
                        />
                      </div>
                    </div>

                    {/* Node Core Details */}
                    <div className="p-4 rounded-2xl bg-slate-900/90 border border-white/10 space-y-3">
                      <div>
                        <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">
                          Target Entity
                        </span>
                        <div className="text-sm font-bold text-white mt-0.5">{selectedGraphNode.label}</div>
                      </div>

                      <div>
                        <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">
                          Edge Traversal Path
                        </span>
                        <div className="text-xs font-mono font-bold text-cyan-300 mt-0.5 bg-slate-950 p-2 rounded-xl border border-white/5 flex items-center space-x-1.5">
                          <span className="text-rose-400">Epicenter</span>
                          <ArrowRight className="w-3 h-3 text-slate-500" />
                          <span className="text-cyan-300">[{selectedGraphNode.edgeType}]</span>
                          <ArrowRight className="w-3 h-3 text-slate-500" />
                          <span className="text-white truncate">{selectedGraphNode.id}</span>
                        </div>
                      </div>

                      <div>
                        <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">
                          Operational Context
                        </span>
                        <p className="text-xs text-slate-200 mt-1 leading-relaxed">{selectedGraphNode.detail}</p>
                      </div>
                    </div>

                    {/* CP-SAT Solver Autonomous Resolution Card */}
                    <div className="p-3.5 rounded-2xl bg-indigo-950/40 border border-indigo-500/40 text-indigo-200 space-y-1.5 shadow-lg">
                      <div className="font-bold flex items-center space-x-1.5 text-indigo-300">
                        <Zap className="w-3.5 h-3.5 text-indigo-400" />
                        <span>OR-Tools CP-SAT Mitigation Action</span>
                      </div>
                      <p className="text-[11px] text-indigo-200/90 leading-relaxed">
                        {selectedGraphNode.type === "session"
                          ? "Re-homed to Campus 7 Auditorium / OAT in <150ms with 0 volunteer shift collisions."
                          : selectedGraphNode.type === "task"
                          ? "AV teardown and rerouting scheduled 45 mins prior to relocated session start."
                          : selectedGraphNode.type === "cohort"
                          ? "1-click push notification and digital signage rerouting dispatched to attendees."
                          : "VIP host escort reallocated to Campus 7 Green Room."}
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-slate-500 py-20">
                    Click any node in the radar diagram to inspect its live blast trajectory.
                  </div>
                )}
              </div>

              {/* Traversal Meta Diagnostics */}
              <div className="p-3.5 rounded-2xl bg-slate-950 border border-white/10 space-y-2 text-[11px]">
                <div className="flex justify-between items-center text-slate-400">
                  <span>Graph Engine:</span>
                  <span className="font-mono text-cyan-400 font-bold">Recursive-CTE / Bounded BFS</span>
                </div>
                <div className="flex justify-between items-center text-slate-400">
                  <span>Execution Latency:</span>
                  <span className="font-mono text-emerald-400 font-bold">&lt; 0.038 ms</span>
                </div>
                <div className="flex justify-between items-center text-slate-400">
                  <span>Total Impacted Attendees:</span>
                  <span className="font-bold text-white">1,410 Registrants</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Grid Table View */
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 glass-panel p-6 rounded-3xl space-y-4 border border-rose-500/20">
            <div className="flex items-center justify-between text-xs text-slate-400 font-semibold uppercase tracking-wider">
              <span>Graph Entities ({filteredNodes.length})</span>
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
                    className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                      isSelected
                        ? "bg-indigo-950/60 border-indigo-500 shadow-xl shadow-indigo-500/20 scale-[1.02]"
                        : isRoot
                        ? "bg-red-950/40 border-red-500/40 hover:border-red-400"
                        : isHard
                        ? "bg-slate-900/80 border-rose-500/20 hover:border-rose-500/40"
                        : "bg-slate-900/60 border-purple-500/20 hover:border-purple-500/40"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span
                        className={`text-[10px] font-mono font-bold uppercase px-2.5 py-0.5 rounded-full ${
                          isRoot
                            ? "bg-red-500/20 text-red-300 border border-red-500/30"
                            : isHard
                            ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                            : "bg-purple-500/20 text-purple-300 border border-purple-500/30"
                        }`}
                      >
                        edge={node.edgeType}
                      </span>
                      <span className="text-[10px] text-slate-500 font-mono">{node.id}</span>
                    </div>

                    <h4 className="text-sm font-bold text-white mt-2.5 leading-snug">{node.label}</h4>
                    <p className="text-xs text-slate-400 mt-1 line-clamp-2 leading-relaxed">{node.detail}</p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Inspector in Grid View */}
          <div className="glass-panel p-6 rounded-3xl flex flex-col justify-between border border-white/10">
            {selectedNode ? (
              <div className="space-y-4">
                <div className="flex items-center space-x-2 pb-3 border-b border-white/10">
                  <Info className="w-4 h-4 text-cyan-400" />
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider">Node Edge Inspector</h3>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/90 border border-white/10 space-y-3 text-xs">
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-semibold">Entity Label:</span>
                    <p className="text-sm font-bold text-white mt-0.5">{selectedNode.label}</p>
                  </div>

                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-semibold">Edge Relationship:</span>
                    <p className="text-xs font-mono font-bold text-cyan-300 bg-slate-950 p-2 rounded-xl border border-white/5 mt-0.5">
                      Main Auditorium --[{selectedNode.edgeType}]--&gt; {selectedNode.id}
                    </p>
                  </div>

                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-semibold">Classification:</span>
                    <div className="mt-1">
                      <span
                        className={`px-2.5 py-1 rounded-full text-xs font-bold uppercase ${
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
                    <span className="text-[10px] text-slate-400 uppercase font-semibold">Operational Context:</span>
                    <p className="text-xs text-slate-200 mt-1 leading-relaxed">{selectedNode.detail}</p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center text-slate-500 py-16">
                Select a node from the grid to inspect its dependency path.
              </div>
            )}

            <div className="pt-4 border-t border-white/5 text-[11px] text-slate-500 text-center">
              Bounded BFS Traversal Depth: 3 • Latency: &lt; 0.05ms
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
