import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard,
  Building2,
  CalendarDays,
  GitBranch,
  MapPin,
  Users2,
  Sparkles,
  QrCode,
  ChevronRight,
  PanelLeftClose,
  PanelLeftOpen,
  ShieldCheck,
  type LucideIcon,
} from "lucide-react";
import { getRole } from "../lib/roles";

export type NavSection =
  | "overview"
  | "venues"
  | "schedule"
  | "simulation"
  | "map"
  | "volunteers"
  | "notion-ai"
  | "participant";

interface NavMeta {
  label: string;
  icon: LucideIcon;
  subtitle: string;
}

const NAV_META: Record<Exclude<NavSection, "participant">, NavMeta> = {
  overview: { label: "Command Overview", icon: LayoutDashboard, subtitle: "Live situational picture" },
  venues: { label: "Venues & Auditoriums", icon: Building2, subtitle: "Capacities, AV & staff" },
  schedule: { label: "Master Schedule", icon: CalendarDays, subtitle: "Timeline, speakers, hostels" },
  simulation: { label: "Simulation Studio", icon: GitBranch, subtitle: "What-if solver & diffs" },
  map: { label: "Campus Digital Twin", icon: MapPin, subtitle: "Shuttles, gates & corridors" },
  volunteers: { label: "Volunteers & Shifts", icon: Users2, subtitle: "Skill match & standby" },
  "notion-ai": { label: "Notion & AI Center", icon: Sparkles, subtitle: "Live sync & co-pilot" },
};

interface SidebarProps {
  activeSection: NavSection;
  onSectionChange: (section: NavSection) => void;
  hasActiveBranch: boolean;
  incidentCount: number;
  currentRole: string;
  collapsed: boolean;
  onToggleCollapse: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeSection,
  onSectionChange,
  hasActiveBranch,
  incidentCount,
  currentRole,
  collapsed,
  onToggleCollapse,
}) => {
  const role = getRole(currentRole);

  const badgeFor = (id: NavSection): { text: string; className: string } | null => {
    if (id === "overview" && incidentCount > 0)
      return {
        text: `${incidentCount}`,
        className: "bg-rose-500/20 text-rose-200 border-rose-500/40",
      };
    if (id === "simulation" && hasActiveBranch)
      return {
        text: "LIVE",
        className: "bg-cyan-500/20 text-cyan-200 border-cyan-500/40",
      };
    return null;
  };

  return (
    <motion.aside
      animate={{ width: collapsed ? 80 : 272 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      className="relative z-20 flex flex-col shrink-0 select-none border-r border-white/[0.07] bg-[#06090f]/80 backdrop-blur-xl overflow-hidden"
    >
      {/* soft role glow at the top */}
      <div
        className="pointer-events-none absolute -top-16 left-1/2 -translate-x-1/2 h-40 w-40 rounded-full blur-3xl opacity-40"
        style={{ background: `radial-gradient(circle, ${role.accent[0]}, transparent 70%)` }}
      />

      {/* Brand */}
      <div className="relative p-4 border-b border-white/[0.07] flex items-center gap-3">
        <div className="relative shrink-0">
          <img
            src="/logo.png"
            alt="KoreX"
            className="w-10 h-10 object-contain rounded-xl border border-white/10 bg-[#04060f] p-1 shadow-lg shadow-cyan-500/20"
          />
          <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-emerald-400 border-2 border-[#06090f]" />
        </div>
        <AnimatePresence initial={false}>
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -8 }}
              transition={{ duration: 0.2 }}
              className="min-w-0"
            >
              <div className="flex items-center gap-2">
                <span className="font-display font-bold text-lg tracking-tight text-aurora">KoreX</span>
                <span className="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded bg-white/5 text-slate-300 border border-white/10">
                  v0.1
                </span>
              </div>
              <p className="text-[11px] text-slate-500 font-medium truncate">EventOps Command</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Live op status */}
      {!collapsed && (
        <div className="mx-3 mt-4 p-3 rounded-xl glass-soft flex items-center justify-between">
          <div className="flex items-center gap-2 min-w-0">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 radar-dot text-emerald-400 shrink-0" />
            <span className="text-xs font-semibold text-slate-200 truncate">KBC 2026 Conclave</span>
          </div>
          <span className="text-[10px] text-emerald-400 font-mono font-bold">LIVE</span>
        </div>
      )}

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {!collapsed && (
          <div className="px-3 pb-1.5 kicker flex items-center justify-between">
            <span>Operations</span>
            <span className="text-slate-600 normal-case tracking-normal font-mono">
              {role.sections.length} modules
            </span>
          </div>
        )}

        {role.sections.map((id) => {
          const meta = NAV_META[id as Exclude<NavSection, "participant">];
          if (!meta) return null;
          const Icon = meta.icon;
          const isActive = activeSection === id;
          const badge = badgeFor(id);

          return (
            <button
              key={id}
              onClick={() => onSectionChange(id)}
              title={collapsed ? meta.label : undefined}
              className={`group relative w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-colors ${
                isActive ? "text-white" : "text-slate-400 hover:text-slate-100"
              }`}
            >
              {isActive && (
                <motion.span
                  layoutId="nav-active"
                  transition={{ type: "spring", stiffness: 420, damping: 34 }}
                  className="absolute inset-0 rounded-xl border"
                  style={{
                    background: `linear-gradient(110deg, ${role.accent[0]}26, ${role.accent[1]}1a)`,
                    borderColor: `${role.accent[0]}59`,
                    boxShadow: `0 8px 30px -12px ${role.accent[0]}80`,
                  }}
                />
              )}
              {!isActive && (
                <span className="absolute inset-0 rounded-xl border border-transparent group-hover:bg-white/[0.04]" />
              )}

              <span className="relative z-10 shrink-0">
                <Icon
                  className="w-[18px] h-[18px] transition-colors"
                  style={isActive ? { color: role.accent[0] } : undefined}
                />
              </span>

              {!collapsed && (
                <span className="relative z-10 min-w-0 flex-1">
                  <span className="flex items-center justify-between gap-2">
                    <span className="text-[13px] font-semibold truncate">{meta.label}</span>
                    {badge && (
                      <span
                        className={`text-[9px] font-bold px-1.5 py-0.5 rounded-full border shrink-0 ${badge.className}`}
                      >
                        {badge.text}
                      </span>
                    )}
                  </span>
                  {!isActive && (
                    <span className="block text-[10px] text-slate-500 truncate">{meta.subtitle}</span>
                  )}
                </span>
              )}

              {collapsed && badge && (
                <span className="absolute top-1.5 right-1.5 z-10 w-1.5 h-1.5 rounded-full bg-rose-400" />
              )}
            </button>
          );
        })}
      </nav>

      {/* Role clearance chip */}
      {!collapsed && (
        <div className="px-3 pb-2">
          <div
            className="p-3 rounded-xl border flex items-center gap-2.5"
            style={{
              background: `linear-gradient(110deg, ${role.accent[0]}14, ${role.accent[1]}0d)`,
              borderColor: `${role.accent[0]}33`,
            }}
          >
            <ShieldCheck className="w-4 h-4 shrink-0" style={{ color: role.accent[0] }} />
            <div className="min-w-0">
              <div className="text-[11px] font-bold text-white truncate">{role.name}</div>
              <div className="text-[10px] text-slate-400 capitalize">{role.clearance} clearance</div>
            </div>
          </div>
        </div>
      )}

      {/* Participant portal */}
      <div className="p-3 border-t border-white/[0.07]">
        <a
          href="/participant"
          target="_blank"
          rel="noopener noreferrer"
          title="Participant Portal"
          className="flex items-center gap-2.5 p-2.5 rounded-xl glass-soft hover:border-cyan-500/40 hover:bg-white/[0.06] transition-all text-slate-300 hover:text-white group"
        >
          <QrCode className="w-4 h-4 text-cyan-300 shrink-0" />
          {!collapsed && (
            <>
              <div className="min-w-0 flex-1">
                <div className="text-xs font-semibold truncate">Participant Portal</div>
                <div className="text-[10px] text-slate-500 truncate">QR check-in & passes</div>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-cyan-300 group-hover:translate-x-0.5 transition-transform" />
            </>
          )}
        </a>
      </div>

      {/* Collapse toggle */}
      <button
        onClick={onToggleCollapse}
        className="absolute top-5 -right-0 translate-x-1/2 z-30 w-6 h-6 rounded-full bg-[#0b1120] border border-white/10 text-slate-400 hover:text-cyan-300 hover:border-cyan-400/40 flex items-center justify-center shadow-lg transition-colors"
        title={collapsed ? "Expand" : "Collapse"}
      >
        {collapsed ? <PanelLeftOpen className="w-3.5 h-3.5" /> : <PanelLeftClose className="w-3.5 h-3.5" />}
      </button>
    </motion.aside>
  );
};
