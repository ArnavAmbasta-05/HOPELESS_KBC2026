import React from "react";
import { motion } from "framer-motion";
import {
  AlertTriangle,
  Building2,
  Users,
  Clock,
  ArrowRight,
  ShieldCheck,
  GitBranch,
  Sparkles,
  MapPin,
  CalendarDays,
  Radio,
  Bus,
  Activity,
  Gauge,
  Zap,
} from "lucide-react";
import { ChangeProposal } from "../types";
import { NavSection } from "./Sidebar";
import { getRole } from "../lib/roles";
import {
  Reveal,
  RevealGroup,
  Item,
  StatCard,
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
  venues: {
    title: "Venues & Capacities",
    desc: "Inspect 6 auditoriums, seat caps, AV rigs & staff rosters.",
    icon: Building2,
    tone: "#22d3ee",
  },
  schedule: {
    title: "Master Schedule",
    desc: "Date-wise sessions, VIP guests & hostel transport mapping.",
    icon: CalendarDays,
    tone: "#818cf8",
  },
  simulation: {
    title: "Simulation Studio",
    desc: "Run the CP-SAT solver and review change proposals.",
    icon: GitBranch,
    tone: "#a855f7",
  },
  map: {
    title: "Campus Digital Twin",
    desc: "Track live shuttles, gate crowds & walking corridors.",
    icon: MapPin,
    tone: "#2dd4bf",
  },
  volunteers: {
    title: "Volunteers & Shifts",
    desc: "Skill-match, rebalance shifts & dispatch standby crew.",
    icon: Users,
    tone: "#34d399",
  },
  "notion-ai": {
    title: "Notion & AI Co-Pilot",
    desc: "Monitor live 32-page sync & query the AI supervisor.",
    icon: Sparkles,
    tone: "#fbbf24",
  },
};

// Per-role "focus" cards — the three things this persona should watch now.
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

export const OverviewView: React.FC<OverviewProps> = ({ onNavigate, currentRole, onSimulate, isSimulating }) => {
  const role = getRole(currentRole);
  const focus = ROLE_FOCUS[currentRole] ?? DEFAULT_FOCUS;
  const quickSections = role.sections.filter(
    (s) => s !== "overview"
  ) as Exclude<NavSection, "participant" | "overview">[];

  return (
    <div className="space-y-10">
      {/* ===== HERO ===== */}
      <Reveal>
        <div className="relative overflow-hidden rounded-3xl glass-panel aurora-ring">
          <div className="absolute inset-0 bg-techgrid opacity-60" />
          <div
            className="absolute -top-24 -right-16 h-72 w-72 rounded-full blur-3xl opacity-30"
            style={{ background: `radial-gradient(circle, ${role.accent[0]}, transparent 70%)` }}
          />
          <div className="relative grid grid-cols-1 lg:grid-cols-12 gap-8 p-7 md:p-9">
            <div className="lg:col-span-7 space-y-5">
              <div className="flex flex-wrap items-center gap-2">
                <Pill tone="cyan">
                  <LiveDot /> {role.name}
                </Pill>
                <Pill tone="violet">KBC 2026 · KIIT University</Pill>
              </div>
              <h1 className="font-display text-3xl md:text-[42px] font-bold leading-[1.05] tracking-tight text-white">
                The operation, <span className="text-aurora">orchestrated</span>
                <br className="hidden md:block" /> in real time.
              </h1>
              <p className="text-sm md:text-[15px] text-slate-300/90 leading-relaxed max-w-xl">
                {role.mandate} KoreX fuses a live digital twin, constraint solvers and a grounded AI
                supervisor into one command surface — so a venue outage becomes a reviewed plan, not a crisis.
              </p>
              <div className="flex flex-wrap items-center gap-3 pt-1">
                {role.sections.includes("simulation") ? (
                  <PrimaryButton onClick={() => onNavigate("simulation")} icon={<GitBranch className="w-4 h-4" />}>
                    Open Simulation Studio
                    <ArrowRight className="w-3.5 h-3.5" />
                  </PrimaryButton>
                ) : (
                  <PrimaryButton onClick={() => onNavigate(quickSections[0] ?? "overview")} icon={<Zap className="w-4 h-4" />}>
                    Go to my console
                    <ArrowRight className="w-3.5 h-3.5" />
                  </PrimaryButton>
                )}
                <GhostButton onClick={onSimulate} icon={<Radio className={`w-4 h-4 ${isSimulating ? "animate-spin text-cyan-300" : ""}`} />}>
                  {isSimulating ? "Solving…" : "Re-run telemetry"}
                </GhostButton>
              </div>
            </div>

            {/* vitals */}
            <div className="lg:col-span-5">
              <Tilt max={7}>
                <div className="rounded-2xl border border-white/10 bg-[#070b16]/70 p-5 space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="kicker">Operation Vitals</span>
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
                        <span className="font-mono font-bold" style={{ color: m.c }}>
                          {m.v}%
                        </span>
                      </div>
                      <div className="h-1.5 rounded-full bg-white/5 overflow-hidden">
                        <motion.div
                          className="h-full rounded-full"
                          style={{ backgroundColor: m.c }}
                          initial={{ width: 0 }}
                          whileInView={{ width: `${m.v}%` }}
                          viewport={{ once: true }}
                          transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
                        />
                      </div>
                    </div>
                  ))}
                  <div className="pt-2 border-t border-white/5 flex items-center gap-2 text-[11px] text-slate-400">
                    <Activity className="w-3.5 h-3.5 text-emerald-400" />
                    <span>All solvers green · last solve &lt; 2s ago</span>
                  </div>
                </div>
              </Tilt>
            </div>
          </div>
        </div>
      </Reveal>

      {/* ===== INCIDENT BANNER ===== */}
      <Reveal delay={0.05}>
        <div className="relative overflow-hidden rounded-2xl border border-rose-500/30 bg-gradient-to-r from-rose-950/60 via-[#0a0f1e]/80 to-[#0a0f1e]/80 p-5 md:p-6">
          <div className="absolute inset-y-0 left-0 w-1 bg-gradient-to-b from-rose-400 to-rose-600" />
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-start gap-4">
              <div className="w-11 h-11 rounded-xl bg-rose-500/15 border border-rose-500/40 flex items-center justify-center shrink-0">
                <AlertTriangle className="w-5 h-5 text-rose-300 animate-pulse" />
              </div>
              <div className="space-y-1">
                <div className="flex flex-wrap items-center gap-2">
                  <Pill tone="rose">Active outage · 08:00 IST</Pill>
                  <span className="text-[11px] text-slate-400">Source: Notion webhook (Estate Office)</span>
                </div>
                <h2 className="font-display text-lg font-bold text-white">
                  Main Auditorium unavailable — 08:00 to 23:59
                </h2>
                <p className="text-[13px] text-slate-300/90 max-w-2xl leading-relaxed">
                  Emergency ceiling AC leak. 4 conclave sessions (1,180 registered attendees) require re-homing
                  with zero schedule collisions.
                </p>
              </div>
            </div>
            {role.sections.includes("simulation") && (
              <PrimaryButton onClick={() => onNavigate("simulation")} className="shrink-0" icon={<GitBranch className="w-4 h-4" />}>
                Resolve now
                <ArrowRight className="w-3.5 h-3.5" />
              </PrimaryButton>
            )}
          </div>
        </div>
      </Reveal>

      {/* ===== KPI STRIP ===== */}
      <section className="space-y-4">
        <SectionHeader kicker="Live metrics" title="Situational snapshot" />
        <RevealGroup className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Item>
            <StatCard
              label="Impacted sessions"
              value={4}
              icon={<CalendarDays className="w-4 h-4" />}
              tone="#22d3ee"
              hint="Opening (380) · Keynote (230) · Panel (180) · Prize (390) — 100% re-homed"
            />
          </Item>
          <Item>
            <StatCard
              label="Registrants at risk"
              value={1180}
              icon={<Users className="w-4 h-4" />}
              tone="#818cf8"
              hint="SMS + app push broadcast queued across 6 hostel cohorts"
            />
          </Item>
          <Item>
            <StatCard
              label="Volunteer shifts intact"
              value={15}
              suffix=" / 16"
              icon={<ShieldCheck className="w-4 h-4" />}
              tone="#34d399"
              hint="4 reassigned + 1 standby activated (Arjun for Keynote AV)"
            />
          </Item>
          <Item>
            <StatCard
              label="Follow-up tasks"
              value={17}
              icon={<Clock className="w-4 h-4" />}
              tone="#fbbf24"
              hint="Task N08 at 0-min slack escalated to Stage Lead"
            />
          </Item>
        </RevealGroup>
      </section>

      {/* ===== ROLE FOCUS + QUICK NAV ===== */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* role focus */}
        <div className="lg:col-span-5 space-y-4">
          <SectionHeader kicker={`${role.tag} priorities`} title="Your focus right now" />
          <RevealGroup className="space-y-3">
            {focus.map((f) => (
              <Item key={f.title}>
                <div className="rail-card glass-panel glass-panel-hover p-4 rounded-2xl flex items-center gap-4">
                  <span
                    className="w-1.5 self-stretch rounded-full shrink-0"
                    style={{ backgroundColor: f.tone }}
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-3">
                      <span className="text-sm font-bold text-white truncate">{f.title}</span>
                      <span className="text-xs font-mono font-bold shrink-0" style={{ color: f.tone }}>
                        {f.value}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 mt-0.5 leading-relaxed">{f.detail}</p>
                  </div>
                </div>
              </Item>
            ))}
          </RevealGroup>
        </div>

        {/* quick nav */}
        <div className="lg:col-span-7 space-y-4">
          <SectionHeader kicker="Jump to" title="Your modules" />
          <RevealGroup className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {quickSections.map((s) => {
              const c = NAV_CARDS[s];
              if (!c) return null;
              const Icon = c.icon;
              return (
                <Item key={s}>
                  <Tilt max={6}>
                    <button
                      onClick={() => onNavigate(s)}
                      className="rail-card glass-panel glass-panel-hover w-full text-left p-5 rounded-2xl group"
                    >
                      <div className="flex items-center justify-between">
                        <span
                          className="w-10 h-10 rounded-xl flex items-center justify-center border"
                          style={{ color: c.tone, backgroundColor: `${c.tone}1f`, borderColor: `${c.tone}40` }}
                        >
                          <Icon className="w-5 h-5" />
                        </span>
                        <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-white group-hover:translate-x-1 transition-all" />
                      </div>
                      <h4 className="font-display text-sm font-bold text-white mt-3">{c.title}</h4>
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
        <RevealGroup className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Item>
            <div className="glass-panel rail-card p-5 rounded-2xl border-l-2 border-l-rose-400 space-y-2">
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
            <div className="glass-panel rail-card p-5 rounded-2xl border-l-2 border-l-amber-400 space-y-2">
              <div className="flex items-center justify-between">
                <Pill tone="amber">RISK-02 · Medium</Pill>
                <span className="text-[11px] font-bold text-amber-300 font-mono">Cap 600</span>
              </div>
              <h4 className="text-sm font-bold text-white">OAT outdoor capacity & weather monitor</h4>
              <p className="text-[12px] text-slate-300/90 leading-relaxed">
                3 sessions moved outdoors. Rain risk 12% (clear sky). Waterproof canopy rig staged on standby in
                Store.
              </p>
            </div>
          </Item>
        </RevealGroup>
      </section>
    </div>
  );
};
