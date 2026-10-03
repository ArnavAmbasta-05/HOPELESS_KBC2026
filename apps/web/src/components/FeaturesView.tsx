import React, { Suspense } from "react";
import { motion } from "framer-motion";
import {
  ShieldCheck,
  ShieldAlert,
  Bot,
  Lock,
  GitBranch,
  Share2,
  Cpu,
  MapPin,
  CloudRain,
  Send,
  QrCode,
  Database,
  ClipboardCheck,
  Users,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  Radio,
} from "lucide-react";

// Reuse the live interactive dot-field background.
const DotField = React.lazy(() =>
  import("./three/DotField").then((m) => ({ default: m.DotField }))
);

interface FeaturesViewProps {
  authed: boolean;
  onEnter: () => void;
}

const ACCENT: [string, string] = ["#22d3ee", "#6366f1"];

interface Feature {
  icon: React.ElementType;
  title: string;
  desc: string;
  tone: string;
  badge?: string;
}

interface Group {
  kicker: string;
  title: string;
  blurb: string;
  features: Feature[];
}

const GROUPS: Group[] = [
  {
    kicker: "AI you can trust",
    title: "A copilot with guardrails",
    blurb:
      "KoreX's AI helps you plan and explain — but it can never go rogue, leak secrets, or act on its own.",
    features: [
      {
        icon: ShieldAlert,
        title: "Anti-jailbreak AI guard",
        desc: "Every message is screened before it reaches the AI. Attempts to override its rules, extract secrets, or break out are blocked instantly and logged.",
        tone: "#fb7185",
        badge: "New",
      },
      {
        icon: Bot,
        title: "Grounded & clearly labelled",
        desc: "AI answers are tagged “AI-generated, unverified” and cite their sources, so you always know what's a fact versus a suggestion.",
        tone: "#22d3ee",
      },
      {
        icon: ClipboardCheck,
        title: "Human approval required",
        desc: "The AI drafts plans; it never commits changes. A person reviews and approves every action before anything happens.",
        tone: "#34d399",
      },
    ],
  },
  {
    kicker: "Governance & security",
    title: "The right people, the right powers",
    blurb: "Sensitive actions are locked down. Everything important is recorded.",
    features: [
      {
        icon: Lock,
        title: "Super-admin-only event cancellation",
        desc: "No one can cancel an event without super-admin authority. Every attempt is checked and every cancellation is written to an audit ledger.",
        tone: "#a855f7",
        badge: "New",
      },
      {
        icon: ShieldCheck,
        title: "Role-based command center",
        desc: "Eight operational personas — from Event Commander to Transport Lead — each see only the tools and data their job needs.",
        tone: "#818cf8",
      },
      {
        icon: ClipboardCheck,
        title: "Full audit trail",
        desc: "Who did what, when. Approvals, cancellations and overrides are all traceable with correlation IDs.",
        tone: "#2dd4bf",
      },
    ],
  },
  {
    kicker: "For participants",
    title: "Everyone knows where to be",
    blurb: "Attendees get exactly what they need, on the channels they use.",
    features: [
      {
        icon: Send,
        title: "Personal itinerary to every participant",
        desc: "Each registered attendee receives their event details, venue and timings — plus their transport plan: shuttle route, pickup point and pickup time.",
        tone: "#fbbf24",
        badge: "New",
      },
      {
        icon: QrCode,
        title: "QR attendance, even offline",
        desc: "Fast QR check-in at the gates with a resilient offline queue that syncs automatically when the network returns.",
        tone: "#22d3ee",
      },
      {
        icon: Radio,
        title: "Instant change notices",
        desc: "When a venue or time changes, affected participants are notified right away — no stale printed boards or missed updates.",
        tone: "#34d399",
      },
    ],
  },
  {
    kicker: "Operations intelligence",
    title: "See the ripple before it hits",
    blurb: "When one thing changes, KoreX shows everything it touches — and fixes it.",
    features: [
      {
        icon: Share2,
        title: "Dependency blast-radius",
        desc: "Change a venue and instantly see every impacted session, task, volunteer and communication — hard hits and deferred ripples.",
        tone: "#f472b6",
      },
      {
        icon: Cpu,
        title: "Constraint solvers",
        desc: "Re-home sessions and re-balance volunteers automatically, respecting capacity, timing and skills — with zero clashes.",
        tone: "#818cf8",
      },
      {
        icon: GitBranch,
        title: "What-if simulation studio",
        desc: "Test a schedule or venue change safely in a branch, review the diff, then approve it into the live plan.",
        tone: "#a855f7",
      },
      {
        icon: MapPin,
        title: "Live campus digital twin",
        desc: "A real map of venues, gates, corridors and shuttles with real KIIT coordinates and walking/transit distances.",
        tone: "#2dd4bf",
      },
      {
        icon: CloudRain,
        title: "Weather resilience",
        desc: "Live weather for the campus triggers contingency plans for outdoor venues before the rain arrives.",
        tone: "#38bdf8",
      },
      {
        icon: Database,
        title: "Live Notion knowledge layer",
        desc: "Operational records and post-event knowledge sync to Notion, with safe retries and a dead-letter queue so nothing is lost.",
        tone: "#22d3ee",
      },
    ],
  },
];

const STATS = [
  { v: "8", l: "operational personas" },
  { v: "Live", l: "Notion · Gemini · CARTO · weather" },
  { v: "0", l: "AI auto-commits — approval always" },
  { v: "100%", l: "actions audited" },
];

export const FeaturesView: React.FC<FeaturesViewProps> = ({ authed, onEnter }) => {
  return (
    <div
      className="relative min-h-screen w-screen overflow-x-hidden text-slate-100 font-sans"
      style={
        {
          "--role-accent": ACCENT[0],
          "--role-accent-2": ACCENT[1],
          background:
            "radial-gradient(1200px 600px at 15% -10%, rgba(34,211,238,0.10), transparent), radial-gradient(1000px 500px at 100% 0%, rgba(129,140,248,0.10), transparent), #06090f",
        } as React.CSSProperties
      }
    >
      <Suspense fallback={null}>
        <DotField accent={ACCENT} />
      </Suspense>
      <div
        aria-hidden
        className="absolute inset-0 pointer-events-none"
        style={{ background: "radial-gradient(120% 120% at 50% 30%, transparent 45%, rgba(4,6,15,0.6) 100%)" }}
      />

      <div className="relative z-10 max-w-6xl mx-auto px-5 md:px-8">
        {/* Top bar */}
        <header className="flex items-center justify-between py-5">
          <div className="flex items-center gap-3">
            <img src="/logo.png" alt="KoreX" className="h-9 w-auto object-contain" />
          </div>
          <button
            onClick={onEnter}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-xs md:text-sm font-bold text-white shadow-lg flex items-center gap-2 transition-all"
          >
            {authed ? "Open console" : "Sign in"} <ArrowRight className="w-4 h-4" />
          </button>
        </header>

        {/* Hero */}
        <motion.section
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          className="pt-10 md:pt-16 pb-10 max-w-3xl"
        >
          <span className="kicker text-[11px] flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-cyan-300" /> KBC 2026 · KIIT University
          </span>
          <h1 className="font-display text-4xl md:text-6xl font-bold leading-[1.03] tracking-tight text-white mt-3">
            Run a complex event like a <span className="text-aurora">command center</span>.
          </h1>
          <p className="text-[15px] md:text-lg text-slate-300/90 leading-relaxed mt-5">
            KoreX turns hundreds of moving parts — venues, sessions, volunteers, transport,
            registrations and communications — into one live, dependency-aware operation. When
            something changes, it shows the ripple and fixes it, with safe AI and strict controls.
          </p>
          <div className="flex flex-wrap items-center gap-3 mt-7">
            <button
              onClick={onEnter}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-sm font-bold text-white shadow-lg flex items-center gap-2 transition-all"
            >
              {authed ? "Open the console" : "Launch the console"} <ArrowRight className="w-4 h-4" />
            </button>
            <a
              href="#features"
              className="px-5 py-2.5 rounded-xl glass-soft text-sm font-semibold text-slate-200 hover:text-white transition-all"
            >
              Explore features
            </a>
          </div>
        </motion.section>

        {/* Stats */}
        <section className="grid grid-cols-2 md:grid-cols-4 gap-4 pb-14">
          {STATS.map((s) => (
            <div key={s.l} className="glass-soft rounded-2xl p-4">
              <div className="font-display text-2xl md:text-3xl font-bold text-white">{s.v}</div>
              <div className="text-[11px] text-slate-400 mt-1 leading-snug">{s.l}</div>
            </div>
          ))}
        </section>

        {/* Feature groups */}
        <div id="features" className="space-y-16 pb-20">
          {GROUPS.map((g) => (
            <section key={g.title}>
              <div className="max-w-2xl mb-6">
                <span className="kicker text-[11px]">{g.kicker}</span>
                <h2 className="font-display text-2xl md:text-3xl font-bold text-white tracking-tight mt-2">
                  {g.title}
                </h2>
                <p className="text-sm text-slate-400 mt-2 leading-relaxed">{g.blurb}</p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {g.features.map((f) => {
                  const Icon = f.icon;
                  return (
                    <motion.div
                      key={f.title}
                      initial={{ opacity: 0, y: 14 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      viewport={{ once: true, margin: "-10% 0px" }}
                      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
                      className="bento glass-panel-hover p-5 rounded-2xl h-full"
                    >
                      <div className="flex items-center justify-between">
                        <span
                          className="w-11 h-11 rounded-xl flex items-center justify-center border"
                          style={{ color: f.tone, backgroundColor: `${f.tone}1f`, borderColor: `${f.tone}40` }}
                        >
                          <Icon className="w-5 h-5" />
                        </span>
                        {f.badge && (
                          <span className="px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                            {f.badge}
                          </span>
                        )}
                      </div>
                      <h3 className="font-display text-base font-bold text-white mt-3.5">{f.title}</h3>
                      <p className="text-[12.5px] text-slate-400 mt-1.5 leading-relaxed">{f.desc}</p>
                    </motion.div>
                  );
                })}
              </div>
            </section>
          ))}
        </div>

        {/* CTA footer */}
        <section className="pb-20">
          <div className="bento aurora-ring rounded-3xl p-8 md:p-12 text-center relative overflow-hidden">
            <div className="absolute inset-0 bg-techgrid opacity-40" />
            <div className="relative space-y-4 max-w-2xl mx-auto">
              <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
              <h2 className="font-display text-2xl md:text-3xl font-bold text-white">
                One operation. One command surface.
              </h2>
              <p className="text-sm text-slate-300/90 leading-relaxed">
                Sign in with any persona to see the live command center — venues, dependencies,
                simulation, the campus twin, the AI copilot and the participant portal.
              </p>
              <div className="flex items-center justify-center gap-3 pt-2">
                <button
                  onClick={onEnter}
                  className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-sm font-bold text-white shadow-lg flex items-center gap-2 transition-all"
                >
                  {authed ? "Open console" : "Sign in"} <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
          <p className="text-center text-[11px] text-slate-600 mt-8 flex items-center justify-center gap-2">
            <Users className="w-3.5 h-3.5" /> KoreX — KIIT EventOps AI Command Center · KBC 2026
          </p>
        </section>
      </div>
    </div>
  );
};
