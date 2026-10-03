import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  AlertTriangle,
  Building2,
  Users,
  Clock,
  ArrowRight,
  ShieldCheck,
  GitBranch,
  Share2,
  Sparkles,
  MapPin,
  CalendarDays,
  Radio,
  Activity,
  Gauge,
  Zap,
  ArrowUpRight,
} from "lucide-react";
import { ChangeProposal } from "../types";
import { NavSection } from "./Sidebar";
import { getRole } from "../lib/roles";
import {
  Reveal,
  RevealGroup,
  Item,
  AnimatedNumber,
  SectionHeader,
  Pill,
  PrimaryButton,
  GhostButton,
  Tilt,
  LiveDot,
} from "./ui";

interface OverviewProps {
  proposal: ChangeProposal | null;
  onNavigate: (section: NavSection) => void;
  onSimulate: () => Promise<void>;
  isSimulating: boolean;
  currentRole: string;
}

const NAV_CARDS: Record<
  Exclude<NavSection, "participant" | "overview">,
  { title: string; desc: string; icon: React.ElementType; tone: string }
> = {
  venues: { title: "Venues & Capacities", desc: "Auditoriums · seat caps · AV rigs · staff.", icon: Building2, tone: "#22d3ee" },
  schedule: { title: "Master Schedule", desc: "Sessions · VIP guests · hostel transport.", icon: CalendarDays, tone: "#818cf8" },
  dependencies: { title: "Dependency Graph", desc: "Blast radius · hard & soft impact edges.", icon: Share2, tone: "#f472b6" },
  simulation: { title: "Simulation Studio", desc: "CP-SAT solver · change proposals.", icon: GitBranch, tone: "#a855f7" },
  map: { title: "Campus Digital Twin", desc: "Live shuttles · gates · corridors.", icon: MapPin, tone: "#2dd4bf" },
  volunteers: { title: "Volunteers & Shifts", desc: "Skill match · rebalance · standby.", icon: Users, tone: "#34d399" },
  "notion-ai": { title: "Notion & AI Co-Pilot", desc: "Live 32-page sync · AI supervisor.", icon: Sparkles, tone: "#fbbf24" },
};

const ROLE_FOCUS: Record<string, { title: string; value: string; detail: string; tone: string }[]> = {
  transport_lead: [
    { title: "Shuttle 2 fault", value: "Rerouted", detail: "Coach Bus A dispatched to Bay 4, 50 seats online.", tone: "#fb7185" },
    { title: "Corridor C6→C7", value: "450 m", detail: "5-min walk / 2-min shuttle link holding steady.", tone: "#38bdf8" },
    { title: "Hostel cohorts", value: "6 routes", detail: "1,180 students mapped across KP & QC fleets.", tone: "#2dd4bf" },
  ],
  security_lead: [
    { title: "Gate 1 ingest", value: "380 scanned", detail: "Optical counters nominal, no bottleneck.", tone: "#34d399" },
    { title: "OAT occupancy", value: "570 / 600", detail: "95% — monitor for overflow at valedictory.", tone: "#fbbf24" },
    { title: "Crowd alerts", value: "0 active", detail: "All zones below threshold this hour.", tone: "#22d3ee" },
  ],
  tech_lead: [
    { title: "Keynote AV", value: "Standby up", detail: "Arjun Sharma activated for C7 Bose F1 line.", tone: "#818cf8" },
    { title: "OAT rig", value: "Weatherised", detail: "Canopy on standby, 12% rain risk.", tone: "#2dd4bf" },
    { title: "Power", value: "100% backup", detail: "All relocated venues on genset + UPS.", tone: "#34d399" },
  ],
  volunteer_coordinator: [
    { title: "Roster integrity", value: "15 / 16", detail: "Only one shift touched by the re-home.", tone: "#34d399" },
    { title: "Standby pool", value: "2 ready", detail: "Nearest-first dispatch armed.", tone: "#22d3ee" },
    { title: "Reassignments", value: "4 moved", detail: "Skill-matched to new venues automatically.", tone: "#fbbf24" },
  ],
  stage_manager: [
    { title: "Run of show", value: "On time", detail: "Opening cue locked for 10:00 at OAT.", tone: "#34d399" },
    { title: "Rehearsal N08", value: "0m slack", detail: "At risk — escalated to Stage Lead.", tone: "#fb7185" },
    { title: "Speaker protocol", value: "4 confirmed", detail: "Escorts assigned for all VIP arrivals.", tone: "#818cf8" },
  ],
};

const DEFAULT_FOCUS = [
  { title: "Sessions re-homed", value: "4 / 4", detail: "Opening, Keynote, Panel & Valedictory placed.", tone: "#34d399" },
  { title: "Roster integrity", value: "15 / 16", detail: "Minimal-disturbance CP-SAT solve.", tone: "#22d3ee" },
  { title: "Task at risk", value: "N08", detail: "0-min slack — escalated to Stage Lead.", tone: "#fb7185" },
];

interface OverviewKpis {
  impactedSessions: number;
  registrantsAtRisk: number;
  volunteersTotal: number;
  volunteersReassigned: number;
  volunteersStandby: number;
  followUpTasks: number;
  venuesTotal: number;
  totalSeating: number;
}

import { getApiUrl } from "../lib/api";

export const OverviewView: React.FC<OverviewProps> = ({ onNavigate, currentRole, onSimulate, isSimulating }) => {
  const role = getRole(currentRole);
  const focus = ROLE_FOCUS[currentRole] ?? DEFAULT_FOCUS;

  // KPIs are derived server-side from the same golden-seed scenario the solver
  // uses: GET /api/v1/scenario/overview.
  const [kpiData, setKpiData] = useState<OverviewKpis | null>(null);
  useEffect(() => {
    fetch(getApiUrl("/api/v1/scenario/overview"))
      .then((res) => (res.ok ? res.json() : Promise.reject(new Error(`HTTP ${res.status}`))))
      .then((d: OverviewKpis) => setKpiData(d))
      .catch((err) => console.error("Failed to load overview KPIs:", err));
  }, []);

  const KPIS = [
    {
      label: "Impacted sessions",
      value: kpiData?.impactedSessions ?? 4,
      suffix: "",
      icon: CalendarDays,
      tone: "#22d3ee",
      hint: "Sessions at the unavailable venue — all require re-homing",
    },
    {
      label: "Registrants at risk",
      value: kpiData?.registrantsAtRisk ?? 1180,
      suffix: "",
      icon: Users,
      tone: "#818cf8",
      hint: "SMS + app push queued across affected hostel cohorts",
    },
    {
      label: "Volunteer roster",
      value: kpiData?.volunteersTotal ?? 16,
      suffix: "",
      icon: ShieldCheck,
      tone: "#34d399",
      hint: `${kpiData?.volunteersStandby ?? 4} standby ready · ${kpiData?.volunteersReassigned ?? 3} to reassign`,
    },
    {
      label: "Follow-up tasks",
      value: kpiData?.followUpTasks ?? 12,
      suffix: "",
      icon: Clock,
      tone: "#fbbf24",
      hint: "Re-home, equipment, comms and cohort-notification actions",
    },
  ];
  const quickSections = role.sections.filter((s) => s !== "overview") as Exclude<
    NavSection,
    "participant" | "overview"
  >[];

  return (
    <div className="space-y-5 md:space-y-6">
      {/* ===== HERO BAND — text tile + open 3D core ===== */}
      <section className="grid grid-cols-12 gap-5">
        <Reveal as="div" className="col-span-12 lg:col-span-7 xl:col-span-8">
          <div className="bento aurora-ring p-7 md:p-10 min-h-[360px] h-full flex flex-col justify-center">
            <div className="absolute inset-0 bg-techgrid opacity-50" />
            <div className="relative space-y-5 max-w-2xl">
              <div className="flex flex-wrap items-center gap-2">
                <Pill tone="cyan"><LiveDot /> {role.name}</Pill>
                <Pill tone="violet">KBC 2026 · KIIT University</Pill>
              </div>
              <h1 className="font-display text-4xl md:text-5xl xl:text-6xl font-bold leading-[1.02] tracking-tight text-white">
                The operation,
                <br />
                <span className="text-aurora">orchestrated</span> live.
              </h1>
              <p className="text-[15px] text-slate-300/90 leading-relaxed max-w-xl">
                {role.mandate} KoreX fuses a live digital twin, constraint solvers and a grounded AI supervisor into
                one command surface — turning a venue outage into a reviewed plan, not a crisis.
              </p>
              <div className="flex flex-wrap items-center gap-3 pt-1">
                {role.sections.includes("simulation") ? (
                  <PrimaryButton onClick={() => onNavigate("simulation")} icon={<GitBranch className="w-4 h-4" />}>
                    Open Simulation Studio <ArrowRight className="w-3.5 h-3.5" />
                  </PrimaryButton>
                ) : (
                  <PrimaryButton onClick={() => onNavigate(quickSections[0] ?? "overview")} icon={<Zap className="w-4 h-4" />}>
                    Go to my console <ArrowRight className="w-3.5 h-3.5" />
                  </PrimaryButton>
                )}
                <GhostButton onClick={onSimulate} icon={<Radio className={`w-4 h-4 ${isSimulating ? "animate-spin text-cyan-300" : ""}`} />}>
                  {isSimulating ? "Solving…" : "Re-run telemetry"}
                </GhostButton>
              </div>
            </div>
          </div>
        </Reveal>

        {/* Right column: open to the 3D core, with a floating translucent vitals card */}
        <Reveal as="div" delay={0.1} className="col-span-12 lg:col-span-5 xl:col-span-4">
          <div className="relative min-h-[360px] h-full flex flex-col justify-between rounded-3xl overflow-hidden">
            <div className="flex items-center justify-between px-1 pt-1">
              <span className="kicker" style={{ color: "var(--role-accent)" }}>Live digital twin</span>
              <span className="flex items-center gap-1.5 text-[10px] font-mono text-slate-400">
                <LiveDot /> rendering
              </span>
            </div>

            {/* the 3D operations core glows through this open space */}
            <div className="flex-1 flex items-center justify-center">
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
                className="font-display text-[11px] tracking-[0.3em] text-white/30 uppercase rotate-0"
              >
                operations core
              </motion.div>
            </div>

            <Tilt max={6}>
              <div className="rounded-2xl glass-soft p-5 space-y-3.5">
                <div className="flex items-center justify-between">
                  <span className="kicker">Operation vitals</span>
                  <Gauge className="w-4 h-4 text-cyan-300" />
                </div>
                {[
                  { l: "Plan readiness", v: 98, c: "#34d399" },
                  { l: "Constraint satisfaction", v: 100, c: "#22d3ee" },
                  { l: "Comms delivered", v: 92, c: "#818cf8" },
                ].map((m) => (
                  <div key={m.l} className="space-y-1.5">
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="text-slate-400">{m.l}</span>
                      <span className="font-mono font-bold" style={{ color: m.c }}>{m.v}%</span>
                    </div>
                    <div className="h-1.5 rounded-full bg-white/[0.06] overflow-hidden">
                      <motion.div
                        className="h-full rounded-full"
                        style={{ backgroundColor: m.c }}
                        initial={{ width: 0 }}
                        whileInView={{ width: `${m.v}%` }}
                        viewport={{ once: true }}
                        transition={{ duration: 1.3, ease: [0.16, 1, 0.3, 1] }}
                      />
                    </div>
                  </div>
                ))}
                <div className="pt-1.5 border-t border-white/5 flex items-center gap-2 text-[11px] text-slate-400">
                  <Activity className="w-3.5 h-3.5 text-emerald-400" />
                  <span>All solvers green · last solve &lt; 2s ago</span>
                </div>
              </div>
            </Tilt>
          </div>
        </Reveal>
      </section>

      {/* ===== INCIDENT BANNER ===== */}
      <Reveal delay={0.05}>
        <div className="relative overflow-hidden rounded-3xl bento p-5 md:p-6" style={{ borderColor: "rgba(251,113,133,0.3)" }}>
          <div className="absolute inset-y-0 left-0 w-1 bg-gradient-to-b from-rose-400 to-rose-600" />
          <div className="absolute -right-10 -top-10 w-48 h-48 rounded-full blur-3xl opacity-20 bg-rose-500" />
          <div className="relative flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-start gap-4">
              <div className="w-11 h-11 rounded-xl bg-rose-500/15 border border-rose-500/40 flex items-center justify-center shrink-0">
                <AlertTriangle className="w-5 h-5 text-rose-300 animate-pulse" />
              </div>
              <div className="space-y-1">
                <div className="flex flex-wrap items-center gap-2">
                  <Pill tone="rose">Active outage · 08:00 IST</Pill>
                  <span className="text-[11px] text-slate-400">Source: Notion webhook (Estate Office)</span>
                </div>
                <h2 className="font-display text-lg md:text-xl font-bold text-white">
                  Main Auditorium unavailable — 08:00 to 23:59
                </h2>
                <p className="text-[13px] text-slate-300/90 max-w-2xl leading-relaxed">
                  Emergency ceiling AC leak. 4 conclave sessions (1,180 registered attendees) require re-homing with
                  zero schedule collisions.
                </p>
              </div>
            </div>
            {role.sections.includes("simulation") && (
              <PrimaryButton onClick={() => onNavigate("simulation")} className="shrink-0" icon={<GitBranch className="w-4 h-4" />}>
                Resolve now <ArrowRight className="w-3.5 h-3.5" />
              </PrimaryButton>
            )}
          </div>
        </div>
      </Reveal>

      {/* ===== KPI BENTO ROW ===== */}
      <RevealGroup className="grid grid-cols-2 lg:grid-cols-4 gap-5">
        {KPIS.map((k) => {
          const Icon = k.icon;
          return (
            <Item key={k.label}>
              <Tilt max={7} className="h-full">
                <div className="bento glass-panel-hover h-full p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="kicker">{k.label}</span>
                    <span
                      className="w-9 h-9 rounded-xl flex items-center justify-center border"
                      style={{ color: k.tone, backgroundColor: `${k.tone}1f`, borderColor: `${k.tone}40` }}
                    >
                      <Icon className="w-4 h-4" />
                    </span>
                  </div>
                  <div className="font-display text-3xl md:text-4xl font-bold text-white">
                    <AnimatedNumber value={k.value} suffix={k.suffix} />
                  </div>
                  <p className="text-[11px] text-slate-400 leading-relaxed">{k.hint}</p>
                </div>
              </Tilt>
            </Item>
          );
        })}
      </RevealGroup>

      {/* ===== FOCUS + MODULES BENTO ===== */}
      <section className="grid grid-cols-12 gap-5">
        {/* focus */}
        <div className="col-span-12 lg:col-span-5 space-y-4">
          <SectionHeader kicker={`${role.tag} priorities`} title="Your focus now" />
          <RevealGroup className="space-y-3">
            {focus.map((f) => (
              <Item key={f.title}>
                <div className="bento glass-panel-hover p-4 flex items-center gap-4">
                  <span className="w-1.5 self-stretch rounded-full shrink-0" style={{ backgroundColor: f.tone }} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-3">
                      <span className="text-sm font-bold text-white truncate">{f.title}</span>
                      <span className="text-xs font-mono font-bold shrink-0" style={{ color: f.tone }}>{f.value}</span>
                    </div>
                    <p className="text-[11px] text-slate-400 mt-0.5 leading-relaxed">{f.detail}</p>
                  </div>
                </div>
              </Item>
            ))}
          </RevealGroup>
        </div>

        {/* modules */}
        <div className="col-span-12 lg:col-span-7 space-y-4">
          <SectionHeader kicker="Jump to" title="Your modules" />
          <RevealGroup className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {quickSections.map((s) => {
              const c = NAV_CARDS[s];
              if (!c) return null;
              const Icon = c.icon;
              return (
                <Item key={s}>
                  <Tilt max={6}>
                    <button
                      onClick={() => onNavigate(s)}
                      className="bento glass-panel-hover w-full text-left p-5 group"
                    >
                      <div className="flex items-center justify-between">
                        <span
                          className="w-11 h-11 rounded-xl flex items-center justify-center border"
                          style={{ color: c.tone, backgroundColor: `${c.tone}1f`, borderColor: `${c.tone}40` }}
                        >
                          <Icon className="w-5 h-5" />
                        </span>
                        <ArrowUpRight className="w-5 h-5 text-slate-500 group-hover:text-white group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all" />
                      </div>
                      <h4 className="font-display text-base font-bold text-white mt-3.5">{c.title}</h4>
                      <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">{c.desc}</p>
                    </button>
                  </Tilt>
                </Item>
              );
            })}
          </RevealGroup>
        </div>
      </section>

      {/* ===== RISK MATRIX ===== */}
      <section className="space-y-4">
        <SectionHeader kicker="TAD §10" title="Priority risk matrix" />
        <RevealGroup className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <Item>
            <div className="bento glass-panel-hover p-5 border-l-2 border-l-rose-400 space-y-2">
              <div className="flex items-center justify-between">
                <Pill tone="rose">RISK-01 · High</Pill>
                <span className="text-[11px] font-bold text-rose-300 font-mono">Slack: 0 min</span>
              </div>
              <h4 className="text-sm font-bold text-white">Task N08 — Opening Act rehearsal at OAT</h4>
              <p className="text-[12px] text-slate-300/90 leading-relaxed">
                Estimated finish 09:45 matches the hard door-open deadline. Any stage-sound delay cascades into the
                VIP Opening Ceremony.
              </p>
            </div>
          </Item>
          <Item>
            <div className="bento glass-panel-hover p-5 border-l-2 border-l-amber-400 space-y-2">
              <div className="flex items-center justify-between">
                <Pill tone="amber">RISK-02 · Medium</Pill>
                <span className="text-[11px] font-bold text-amber-300 font-mono">Cap 600</span>
              </div>
              <h4 className="text-sm font-bold text-white">OAT outdoor capacity & weather monitor</h4>
              <p className="text-[12px] text-slate-300/90 leading-relaxed">
                3 sessions moved outdoors. Rain risk 12% (clear sky). Waterproof canopy rig staged on standby in Store.
              </p>
            </div>
          </Item>
        </RevealGroup>
      </section>
    </div>
  );
};
