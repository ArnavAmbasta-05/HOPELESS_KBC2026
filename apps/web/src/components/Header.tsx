import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Shield, RefreshCw, ChevronDown, Bell, Check, LogOut, Sparkles } from "lucide-react";
import { NavSection } from "./Sidebar";
import { ROLES, getRole } from "../lib/roles";

interface HeaderProps {
  currentRole: string;
  onRoleChange: (role: string) => void;
  /** Switch persona — routes through the login screen to re-authenticate. */
  onSwitchPersona: (role: string) => void;
  /** Sign out of the current persona. */
  onLogout: () => void;
  /** Open the public product features page. */
  onOpenFeatures: () => void;
  activeSection: NavSection;
  onRefresh: () => void;
  isSimulating: boolean;
}

const SECTION_TITLES: Record<NavSection, string> = {
  overview: "Command Overview",
  venues: "Venues & Auditoriums",
  schedule: "Master Schedule",
  dependencies: "Dependency Graph",
  simulation: "Simulation Studio",
  map: "Campus Digital Twin",
  volunteers: "Volunteers & Shifts",
  "notion-ai": "Notion & AI Center",
  participant: "Participant Portal & Attendance",
};

function useClock() {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);
  return now.toLocaleTimeString("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    timeZone: "Asia/Kolkata",
  });
}

export const Header: React.FC<HeaderProps> = ({
  currentRole,
  onSwitchPersona,
  onLogout,
  onOpenFeatures,
  activeSection,
  onRefresh,
  isSimulating,
}) => {
  const role = getRole(currentRole);
  const clock = useClock();
  const [roleOpen, setRoleOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) {
        setRoleOpen(false);
        setNotifOpen(false);
      }
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  const notifications = [
    { t: "Main Auditorium flagged unavailable", s: "Estate Office · 08:00", tone: "#fb7185" },
    { t: "4 sessions re-homed to OAT & C7", s: "Venue solver · 08:01", tone: "#34d399" },
    { t: "Arjun Sharma activated for Keynote AV", s: "Volunteer solver · 08:02", tone: "#22d3ee" },
  ];

  return (
    <header
      ref={rootRef}
      className="relative z-30 h-[72px] shrink-0 pl-2 pr-4 md:pr-6 flex items-center justify-between gap-3"
    >
      {/* Brand lockup — Large direct logo image from assets */}
      <div className="flex items-center gap-4 min-w-0">
        <img
          src="/logo.png"
          alt="KoreX EventOps"
          className="h-10 md:h-11 w-auto object-contain shrink-0 drop-shadow-[0_0_16px_rgba(34,211,238,0.25)]"
        />

        {/* breadcrumb */}
        <div className="hidden md:flex items-center gap-2 pl-4 border-l border-white/10">
          <AnimatePresence mode="wait">
            <motion.span
              key={activeSection}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.25 }}
              className="font-display text-base font-bold text-white/95 tracking-tight truncate"
            >
              {SECTION_TITLES[activeSection]}
            </motion.span>
          </AnimatePresence>
        </div>
      </div>


      {/* Controls */}
      <div className="flex items-center gap-2 shrink-0">
        <div className="hidden xl:flex items-center gap-2 px-3 py-1.5 rounded-xl glass-soft text-xs">
          <span className="w-2 h-2 rounded-full bg-emerald-400 radar-dot text-emerald-400" />
          <span className="text-emerald-300 font-semibold tracking-wide">LIVE</span>
          <span className="text-slate-600">·</span>
          <span className="font-mono text-slate-300 text-[11px] tabular-nums">{clock} IST</span>
        </div>

        <button
          onClick={onOpenFeatures}
          title="View product features"
          className="hidden sm:flex items-center gap-1.5 px-3 py-2 rounded-xl glass-soft text-xs font-semibold text-slate-300 hover:text-white hover:border-cyan-400/40 transition-all"
        >
          <Sparkles className="w-3.5 h-3.5 text-cyan-300" />
          <span>Features</span>
        </button>

        <button
          onClick={onRefresh}
          disabled={isSimulating}
          title="Re-run solvers & telemetry"
          className="p-2.5 rounded-xl glass-soft text-slate-400 hover:text-white hover:border-cyan-400/40 transition-all"
        >
          <RefreshCw className={`w-4 h-4 ${isSimulating ? "animate-spin text-cyan-300" : ""}`} />
        </button>

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => {
              setNotifOpen((v) => !v);
              setRoleOpen(false);
            }}
            className="relative p-2.5 rounded-xl glass-soft text-slate-400 hover:text-white hover:border-cyan-400/40 transition-all"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-rose-400 ring-2 ring-[#06090f]" />
          </button>
          <AnimatePresence>
            {notifOpen && (
              <motion.div
                initial={{ opacity: 0, y: -6, scale: 0.96 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -6, scale: 0.96 }}
                transition={{ duration: 0.15, ease: "easeOut" }}
                className="absolute right-0 top-[calc(100%+8px)] w-80 max-w-[calc(100vw-1.5rem)] glass-panel rounded-2xl p-2 z-50 shadow-2xl border border-white/10 flex flex-col origin-top-right"
                style={{ maxHeight: "min(340px, calc(100vh - 100px))" }}
              >
                <div className="sticky top-0 bg-[#070b14]/95 backdrop-blur-md px-3 py-2 flex items-center justify-between rounded-xl z-10 border-b border-white/5 mb-1 shrink-0">
                  <span className="kicker text-[10px]">Incident Feed</span>
                  <span className="text-[10px] text-emerald-400 font-bold font-mono">● LIVE</span>
                </div>
                <div className="overflow-y-auto pr-1 space-y-1 overscroll-contain flex-1">
                  {notifications.map((n, i) => (
                    <div key={i} className="flex items-start gap-2.5 px-3 py-2 rounded-xl hover:bg-white/[0.04] transition-colors">
                      <span className="mt-1 w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: n.tone }} />
                      <div className="min-w-0">
                        <div className="text-xs font-semibold text-slate-100 leading-tight">{n.t}</div>
                        <div className="text-[10px] text-slate-500 mt-0.5">{n.s}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Role switcher */}
        <div className="relative">
          <button
            onClick={() => {
              setRoleOpen((v) => !v);
              setNotifOpen(false);
            }}
            className="flex items-center gap-2.5 pl-2 pr-2.5 py-1.5 rounded-xl glass-soft hover:border-white/20 transition-all"
          >
            <span
              className="w-7 h-7 rounded-lg flex items-center justify-center text-[11px] font-bold text-white shrink-0"
              style={{ backgroundImage: `linear-gradient(135deg, ${role.accent[0]}, ${role.accent[1]})` }}
            >
              {role.tag.slice(0, 2)}
            </span>
            <div className="text-left hidden md:block max-w-[140px]">
              <div className="text-xs font-bold text-white leading-tight truncate">{role.name}</div>
              <div className="text-[9px] text-slate-500 uppercase tracking-wider">{role.clearance}</div>
            </div>
            <ChevronDown className={`w-3.5 h-3.5 text-slate-400 transition-transform ${roleOpen ? "rotate-180" : ""}`} />
          </button>

          <AnimatePresence>
            {roleOpen && (
              <motion.div
                initial={{ opacity: 0, y: -6, scale: 0.96 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -6, scale: 0.96 }}
                transition={{ duration: 0.15, ease: "easeOut" }}
                className="absolute right-0 top-[calc(100%+8px)] w-72 max-w-[calc(100vw-1.5rem)] glass-panel rounded-2xl p-2 z-50 shadow-2xl border border-white/10 flex flex-col origin-top-right"
                style={{ maxHeight: "min(340px, calc(100vh - 100px))" }}
              >
                <div className="sticky top-0 bg-[#070b14]/95 backdrop-blur-md px-3 py-2 flex items-center justify-between rounded-xl z-10 border-b border-white/5 mb-1 shrink-0">
                  <div className="flex items-center gap-2">
                    <Shield className="w-3.5 h-3.5 text-cyan-300" />
                    <span className="kicker text-[10px]">Switch Persona · re-login</span>
                  </div>
                  <span className="text-[10px] text-slate-400 font-mono">{ROLES.length} Roles</span>
                </div>
                <div className="overflow-y-auto pr-1 space-y-1 overscroll-contain flex-1">
                  {ROLES.map((r) => {
                    const active = r.id === currentRole;
                    return (
                      <button
                        key={r.id}
                        onClick={() => {
                          setRoleOpen(false);
                          onSwitchPersona(r.id);
                        }}
                        title="Sign in as this persona"
                        className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-xl text-left transition-colors ${
                          active ? "bg-white/[0.08] border border-cyan-500/30" : "hover:bg-white/[0.04]"
                        }`}
                      >
                        <span
                          className="w-6 h-6 rounded-lg flex items-center justify-center text-[10px] font-bold text-white shrink-0"
                          style={{ backgroundImage: `linear-gradient(135deg, ${r.accent[0]}, ${r.accent[1]})` }}
                        >
                          {r.tag.slice(0, 2)}
                        </span>
                        <div className="min-w-0 flex-1">
                          <div className="text-xs font-semibold text-slate-100 truncate">{r.name}</div>
                          <div className="text-[9px] text-slate-500 truncate">
                            {r.sections.length} modules · {r.clearance}
                          </div>
                        </div>
                        {active && <Check className="w-3.5 h-3.5 text-cyan-300 shrink-0" />}
                      </button>
                    );
                  })}
                </div>
                <div className="shrink-0 pt-1.5 mt-1 border-t border-white/5">
                  <button
                    onClick={() => {
                      setRoleOpen(false);
                      onLogout();
                    }}
                    className="w-full flex items-center gap-2 px-2.5 py-2 rounded-xl text-left text-rose-300 hover:bg-rose-500/10 transition-colors"
                  >
                    <LogOut className="w-3.5 h-3.5 shrink-0" />
                    <span className="text-xs font-semibold">Sign out</span>
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </header>
  );
};
