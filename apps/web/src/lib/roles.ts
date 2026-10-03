import type { NavSection } from "../components/Sidebar";

export interface RoleDef {
  id: string;
  name: string;
  /** short tag shown in the sidebar / header chip */
  tag: string;
  /** one-line mandate shown contextually */
  mandate: string;
  /** two-stop accent gradient used to theme the whole shell for this role */
  accent: [string, string];
  /** sections this role is allowed to open, in display order */
  sections: NavSection[];
  /** clearance level affects the admin surface */
  clearance: "operator" | "lead" | "command" | "root";
}

/**
 * All operational personas. Each persona sees a different slice of the
 * command center. `event_commander` + `super_admin` get the full surface;
 * functional leads get a focused subset relevant to their mandate.
 */
export const ROLES: RoleDef[] = [
  {
    id: "event_commander",
    name: "Event Commander",
    tag: "Command",
    mandate: "Full-spectrum authority over the KBC 2026 operation.",
    accent: ["#22d3ee", "#6366f1"],
    sections: ["overview", "venues", "schedule", "dependencies", "simulation", "map", "volunteers", "notion-ai", "participant"],
    clearance: "command",
  },
  {
    id: "ops_lead",
    name: "Operations Lead",
    tag: "Ops",
    mandate: "Keep every session homed, staffed and on-time.",
    accent: ["#34d399", "#22d3ee"],
    sections: ["overview", "venues", "schedule", "dependencies", "simulation", "map", "volunteers", "participant"],
    clearance: "lead",
  },
  {
    id: "tech_lead",
    name: "Tech / AV Lead",
    tag: "A/V",
    mandate: "Guarantee rigs, power and signal for every stage.",
    accent: ["#818cf8", "#a855f7"],
    sections: ["overview", "venues", "schedule", "simulation", "notion-ai"],
    clearance: "lead",
  },
  {
    id: "stage_manager",
    name: "Stage Manager",
    tag: "Stage",
    mandate: "Run of show, cues and speaker readiness.",
    accent: ["#fbbf24", "#fb7185"],
    sections: ["overview", "schedule", "venues", "volunteers"],
    clearance: "lead",
  },
  {
    id: "volunteer_coordinator",
    name: "Volunteer Coordinator",
    tag: "Crew",
    mandate: "Skill-match, shift and dispatch the volunteer corps.",
    accent: ["#2dd4bf", "#34d399"],
    sections: ["overview", "volunteers", "schedule", "map", "participant"],
    clearance: "lead",
  },
  {
    id: "security_lead",
    name: "Security & Crowd Lead",
    tag: "Safety",
    mandate: "Gate flow, occupancy and crowd safety across campus.",
    accent: ["#fb7185", "#f59e0b"],
    sections: ["overview", "map", "venues", "volunteers", "schedule", "participant"],
    clearance: "lead",
  },
  {
    id: "transport_lead",
    name: "Transport & Fleet Lead",
    tag: "Fleet",
    mandate: "Shuttles, corridors and hostel-to-venue mobility.",
    accent: ["#38bdf8", "#2dd4bf"],
    sections: ["overview", "map", "schedule"],
    clearance: "lead",
  },
  {
    id: "super_admin",
    name: "Super Admin",
    tag: "Root",
    mandate: "Platform root — every surface, every integration, every write.",
    accent: ["#a855f7", "#22d3ee"],
    sections: ["overview", "venues", "schedule", "dependencies", "simulation", "map", "volunteers", "notion-ai", "participant"],
    clearance: "root",
  },
];

export const ROLE_MAP: Record<string, RoleDef> = Object.fromEntries(
  ROLES.map((r) => [r.id, r])
);

export function getRole(id: string): RoleDef {
  return ROLE_MAP[id] ?? ROLES[0];
}

export function canAccess(roleId: string, section: NavSection): boolean {
  return getRole(roleId).sections.includes(section);
}
