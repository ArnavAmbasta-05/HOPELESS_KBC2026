import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Shield, RefreshCw, ChevronDown, Bell, Check, Search } from "lucide-react";
import { NavSection } from "./Sidebar";
import { ROLES, getRole } from "../lib/roles";

interface HeaderProps {
  currentRole: string;
  onRoleChange: (role: string) => void;
  activeSection: NavSection;
  onRefresh: () => void;
  isSimulating: boolean;
}

const SECTION_TITLES: Record<NavSection, string> = {
  overview: "Command Overview",
  venues: "Venues & Auditoriums",
  schedule: "Master Schedule",
  simulation: "Simulation Studio",
  map: "Campus Digital Twin",
  volunteers: "Volunteers & Shifts",
  "notion-ai": "Notion & AI Center",
  participant: "Participant Portal",
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
  onRoleChange,
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
      className="relative z-30 h-16 shrink-0 px-5 flex items-center justify-between border-b border-white/[0.07] bg-[#06090f]/70 backdrop-blur-xl"
    >
      {/* Breadcrumb + mandate */}
      <div className="flex items-center gap-3 min-w-0">
        <span className="text-[11px] font-semibold text-slate-500 hidden sm:inline">KoreX</span>
        <span className="text-slate-600 hidden sm:inline">/</span>
        <div className="min-w-0">
          <AnimatePresence mode="wait">
            <motion.h2
              key={activeSection}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.25 }}
              className="font-display text-sm font-bold text-white tracking-tight truncate"
            >
              {SECTION_TITLES[activeSection]}
            </motion.h2>
          </AnimatePresence>
          <p className="text-[10px] text-slate-500 truncate hidden md:block">{role.mandate}</p>
        </div>
      </div>

      <div className="flex items-center gap-2.5">
        {/* Live clock */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-xl glass-soft text-xs">
          <span className="w-2 h-2 rounded-full bg-emerald-400 radar-dot text-emerald-400" />
          <span className="text-emerald-300 font-semibold tracking-wide">LIVE</span>
          <span className="text-slate-600">·</span>
          <span className="font-mono text-slate-300 text-[11px] tabular-nums">{clock} IST</span>
        </div>

        {/* Refresh */}
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
                initial={{ opacity: 0, y: 8, scale: 0.97 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 8, scale: 0.97 }}
                transition={{ duration: 0.18 }}
                className="absolute right-0 mt-2 w-80 glass-panel rounded-2xl p-2 z-50"
              >
                <div className="px-3 py-2 flex items-center justify-between">
                  <span className="kicker">Incident Feed</span>
                  <span className="text-[10px] text-slate-500">live</span>
                </div>
                {notifications.map((n, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-2.5 px-3 py-2.5 rounded-xl hover:bg-white/[0.04] transition-colors"
                  >
                    <span
                      className="mt-1 w-2 h-2 rounded-full shrink-0"
                      style={{ backgroundColor: n.tone }}
                    />
                    <div className="min-w-0">
                      <div className="text-xs font-semibold text-slate-100">{n.t}</div>
                      <div className="text-[10px] text-slate-500">{n.s}</div>
                    </div>
                  </div>
                ))}
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
            className="flex items-center gap-2.5 pl-2.5 pr-3 py-1.5 rounded-xl glass-soft hover:border-white/20 transition-all"
          >
            <span
              className="w-7 h-7 rounded-lg flex items-center justify-center text-[11px] font-bold text-white shrink-0"
              style={{ backgroundImage: `linear-gradient(135deg, ${role.accent[0]}, ${role.accent[1]})` }}
            >
              {role.tag.slice(0, 2)}
            </span>
            <div className="text-left hidden sm:block">
              <div className="text-xs font-bold text-white leading-tight">{role.name}</div>
              <div className="text-[9px] text-slate-500 uppercase tracking-wider">{role.clearance}</div>
            </div>
            <ChevronDown className={`w-3.5 h-3.5 text-slate-400 transition-transform ${roleOpen ? "rotate-180" : ""}`} />
          </button>

          <AnimatePresence>
            {roleOpen && (
              <motion.div
                initial={{ opacity: 0, y: 8, scale: 0.97 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 8, scale: 0.97 }}
                transition={{ duration: 0.18 }}
                className="absolute right-0 mt-2 w-72 glass-panel rounded-2xl p-2 z-50 max-h-[70vh] overflow-y-auto"
              >
                <div className="px-3 py-2 flex items-center gap-2">
                  <Shield className="w-3.5 h-3.5 text-cyan-300" />
                  <span className="kicker">Switch Persona</span>
                </div>
                {ROLES.map((r) => {
                  const active = r.id === currentRole;
                  return (
                    <button
                      key={r.id}
                      onClick={() => {
                        onRoleChange(r.id);
                        setRoleOpen(false);
                      }}
                      className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-colors ${
                        active ? "bg-white/[0.06]" : "hover:bg-white/[0.04]"
                      }`}
                    >
                      <span
                        className="w-7 h-7 rounded-lg flex items-center justify-center text-[10px] font-bold text-white shrink-0"
                        style={{ backgroundImage: `linear-gradient(135deg, ${r.accent[0]}, ${r.accent[1]})` }}
                      >
                        {r.tag.slice(0, 2)}
                      </span>
                      <div className="min-w-0 flex-1">
                        <div className="text-xs font-bold text-slate-100 truncate">{r.name}</div>
                        <div className="text-[10px] text-slate-500 truncate">{r.sections.length} modules · {r.clearance}</div>
                      </div>
                      {active && <Check className="w-4 h-4 text-cyan-300 shrink-0" />}
                    </button>
                  );
                })}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </header>
  );
};
