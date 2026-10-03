import React from "react";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  Building2,
  CalendarDays,
  GitBranch,
  Share2,
  MapPin,
  Users2,
  Sparkles,
  QrCode,
  type LucideIcon,
} from "lucide-react";
import { NavSection } from "./Sidebar";
import { getRole } from "../lib/roles";

interface NavMeta {
  label: string;
  icon: LucideIcon;
  subtitle: string;
}

const NAV_META: Record<NavSection, NavMeta> = {
  overview: { label: "Command Overview", icon: LayoutDashboard, subtitle: "Live situational picture" },
  venues: { label: "Venues & Auditoriums", icon: Building2, subtitle: "Capacities · AV · staff" },
  schedule: { label: "Master Schedule", icon: CalendarDays, subtitle: "Timeline · speakers · hostels" },
  dependencies: { label: "Dependency Graph", icon: Share2, subtitle: "Blast radius & impact" },
  simulation: { label: "Simulation Studio", icon: GitBranch, subtitle: "What-if solver & diffs" },
  map: { label: "Campus Digital Twin", icon: MapPin, subtitle: "Shuttles · gates · corridors" },
  volunteers: { label: "Volunteers & Shifts", icon: Users2, subtitle: "Skill match & standby" },
  "notion-ai": { label: "Notion & AI Center", icon: Sparkles, subtitle: "Live sync & co-pilot" },
  participant: { label: "Participant QR Portal", icon: QrCode, subtitle: "Gate passes & attendance Excel" },
};

interface Props {
  activeSection: NavSection;
  onSectionChange: (s: NavSection) => void;
  currentRole: string;
  incidentCount: number;
  hasActiveBranch: boolean;
}

const Flyout: React.FC<{ title: string; subtitle?: string }> = ({ title, subtitle }) => (
  <span className="node-flyout">
    <span className="flex flex-col glass-panel rounded-xl px-3.5 py-2 shadow-xl">
      <span className="text-xs font-bold text-white leading-tight">{title}</span>
      {subtitle && <span className="text-[10px] text-slate-400 leading-tight mt-0.5">{subtitle}</span>}
    </span>
  </span>
);

export const OrbitalRail: React.FC<Props> = ({
  activeSection,
  onSectionChange,
  currentRole,
  incidentCount,
  hasActiveBranch,
}) => {
  const role = getRole(currentRole);

  const dot = (id: NavSection) => {
    if (id === "overview" && incidentCount > 0) return "#fb7185";
    if (id === "simulation" && hasActiveBranch) return role.accent[0];
    return null;
  };

  return (
    <aside className="relative z-40 shrink-0 w-[96px] h-full flex flex-col items-center justify-start py-5 space-y-4 overflow-visible">
      {/* Brand orb */}
      <button
        onClick={() => onSectionChange("overview")}
        className="orbital-node orbital-item group relative"
        title="KoreX"
      >
        <span className="orbital-ring" />
        <span
          className="relative w-14 h-14 rounded-full flex items-center justify-center border border-white/15 overflow-hidden"
          style={{
            background: `radial-gradient(circle at 30% 25%, ${role.accent[0]}33, rgba(5,8,16,0.9))`,
            boxShadow: `0 0 28px -6px ${role.accent[0]}`,
          }}
        >
          <img src="/logo.png" alt="KoreX" className="w-9 h-9 object-contain" />
        </span>
        <Flyout title="KoreX — EventOps" subtitle="KBC 2026 Command Center" />
      </button>

      {/* Nav dock */}
      <div className="relative flex items-center">
        <div className="flex flex-col items-center gap-2.5 p-2.5 rounded-full glass-panel overflow-visible">
          {role.sections.map((id) => {
            const meta = NAV_META[id];
            if (!meta) return null;
            const Icon = meta.icon;
            const isActive = activeSection === id;
            const badge = dot(id);
            return (
              <button
                key={id}
                onClick={() => onSectionChange(id)}
                className="orbital-node orbital-item relative"
                title={meta.label}
              >
                {isActive && (
                  <motion.span
                    layoutId="orbital-active"
                    transition={{ type: "spring", stiffness: 420, damping: 32 }}
                    className="absolute inset-0 rounded-full"
                    style={{
                      background: `linear-gradient(135deg, ${role.accent[0]}, ${role.accent[1]})`,
                      boxShadow: `0 0 26px -4px ${role.accent[0]}`,
                    }}
                  />
                )}
                {isActive && <span className="orbital-ring" />}
                <span
                  className={`relative z-10 w-12 h-12 rounded-full flex items-center justify-center border transition-colors ${
                    isActive
                      ? "border-white/20 text-white"
                      : "border-white/10 text-slate-400 hover:text-white bg-white/[0.03] hover:bg-white/[0.07]"
                  }`}
                >
                  <Icon className="w-[19px] h-[19px]" />
                </span>
                {badge && (
                  <span
                    className="absolute top-0 right-0 z-20 w-2.5 h-2.5 rounded-full ring-2 ring-[#06090f]"
                    style={{ backgroundColor: badge }}
                  />
                )}
                <Flyout title={meta.label} subtitle={meta.subtitle} />
              </button>
            );
          })}
        </div>
      </div>
    </aside>
  );
};
