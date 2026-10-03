import React, { useState, useEffect, Suspense } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { NavSection } from "./components/Sidebar";
import { OrbitalRail } from "./components/OrbitalRail";
import { Header } from "./components/Header";
import { OverviewView } from "./components/OverviewView";
import { VenuesView } from "./components/VenuesView";
import { ScheduleView } from "./components/ScheduleView";
import { DependencyGraphView } from "./components/DependencyGraphView";
import { SimulationStudioView } from "./components/SimulationStudioView";
import { CampusMapView } from "./components/CampusMapView";
import { VolunteersView } from "./components/VolunteersView";
import { NotionAiCenterView } from "./components/NotionAiCenterView";
import { ParticipantPortalView } from "./components/ParticipantPortalView";
import { LoginView } from "./components/LoginView";
import { FeaturesView } from "./components/FeaturesView";
import { ChangeProposal } from "./types";
import { getRole } from "./lib/roles";
import { loadAuthedRole, persistAuthedRole } from "./lib/mockAuth";
import { getApiUrl } from "./lib/api";

// WebGL field is heavy (three.js) — load it lazily so it never blocks first paint.
const CommandBackground = React.lazy(() =>
  import("./components/three/CommandBackground").then((m) => ({
    default: m.CommandBackground,
  }))
);

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
    },
  },
});

export function MainSaaSApp() {
  const [activeSection, setActiveSection] = useState<NavSection>(() => {
    try {
      const params = new URLSearchParams(window.location.search);
      if (params.get("view") === "participant" || window.location.pathname.includes("participant")) {
        return "participant";
      }
    } catch {}
    return "overview";
  });
  // Public Features page (no auth). Deep-linkable via ?page=features.
  const [showFeatures, setShowFeatures] = useState<boolean>(() => {
    try {
      return new URLSearchParams(window.location.search).get("page") === "features";
    } catch {
      return false;
    }
  });

  const openFeatures = () => {
    setShowFeatures(true);
    try {
      const url = new URL(window.location.href);
      url.searchParams.set("page", "features");
      window.history.replaceState({}, "", url);
    } catch {}
  };

  const closeFeatures = () => {
    setShowFeatures(false);
    try {
      const url = new URL(window.location.href);
      url.searchParams.delete("page");
      window.history.replaceState({}, "", url);
    } catch {}
  };

  // Persona auth (mock — see lib/mockAuth.ts). authedRole === null => show login.
  const [authedRole, setAuthedRole] = useState<string | null>(() => loadAuthedRole());
  const [preselectRole, setPreselectRole] = useState<string>(() => loadAuthedRole() ?? "event_commander");
  const [currentRole, setCurrentRole] = useState(() => loadAuthedRole() ?? "event_commander");
  const [proposal, setProposal] = useState<ChangeProposal | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [isActionLoading, setIsActionLoading] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const role = getRole(currentRole);

  const handleLogin = (roleId: string) => {
    setAuthedRole(roleId);
    setCurrentRole(roleId);
    setPreselectRole(roleId);
    persistAuthedRole(roleId);
  };

  const handleLogout = () => {
    setAuthedRole(null);
    persistAuthedRole(null);
  };

  // Switching persona requires re-authenticating as that persona.
  const handleSwitchPersona = (roleId: string) => {
    setPreselectRole(roleId);
    setAuthedRole(null);
    persistAuthedRole(null);
  };

  // Keep the active module within the current role's clearance.
  useEffect(() => {
    if (!role.sections.includes(activeSection)) {
      setActiveSection(role.sections[0] ?? "overview");
    }
  }, [currentRole]); // eslint-disable-line react-hooks/exhaustive-deps

  // Auto-simulate Golden Scenario on initial load
  const runSimulation = async () => {
    setIsSimulating(true);
    setActionMessage(null);
    try {
      const resp = await fetch(getApiUrl("/api/v1/proposals/simulate"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer dev-token",
        },
        body: JSON.stringify({
          event_id: "evt_kbc2026",
          unavailable_venue_id: "ven_main_aud",
          reason: "Ceiling AC leak reported by Estate Office",
          time_window: "08:00–23:59",
          reported_by: "ops-lead (via Notion)",
        }),
      });

      if (resp.ok) {
        const json = await resp.json();
        setProposal(json.data);
      }
    } catch (err) {
      console.warn("API simulation error:", err);
    } finally {
      setIsSimulating(false);
    }
  };

  useEffect(() => {
    runSimulation();
  }, []);

  const handleApprove = async (proposalId: string) => {
    setIsActionLoading(true);
    setActionMessage(null);
    try {
      const resp = await fetch(getApiUrl(`/api/v1/proposals/${proposalId}/approve`), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer dev-token",
        },
      });

      if (resp.ok) {
        const json = await resp.json();
        setProposal(json.data);
        const writes = json.data?.external_writes?.length ?? json.data?.write_count;
        setActionMessage(
          writes != null
            ? `Plan approved — ${writes} atomic writes committed to operational state & Notion.`
            : "Plan approved and committed to operational state & Notion."
        );
      } else {
        const err = await resp.json().catch(() => ({}));
        setActionMessage(`Approval failed: ${err.message || `HTTP ${resp.status}`}`);
      }
    } catch (err) {
      // Do NOT fabricate a success state when the backend is unreachable — report it.
      setActionMessage(
        "Approval could not be committed — the operations API is unreachable. No writes were made."
      );
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleReject = async (proposalId: string, reason: string) => {
    setIsActionLoading(true);
    setActionMessage(null);
    try {
      const resp = await fetch(getApiUrl(`/api/v1/proposals/${proposalId}/reject`), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer dev-token",
        },
        body: JSON.stringify({ reason }),
      });

      if (resp.ok) {
        const json = await resp.json();
        setProposal(json.data);
        setActionMessage(`Proposal rejected with 0 operational writes: "${reason}"`);
      } else {
        const err = await resp.json().catch(() => ({}));
        setActionMessage(`Rejection failed: ${err.message || `HTTP ${resp.status}`}`);
      }
    } catch (err) {
      setActionMessage(
        "Rejection could not be recorded — the operations API is unreachable."
      );
    } finally {
      setIsActionLoading(false);
    }
  };

  const pageTransition = {
    initial: { opacity: 0, y: 18 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -12 },
    transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] as const },
  };

  // Public Features page — reachable with or without a session.
  if (showFeatures) {
    return <FeaturesView authed={Boolean(authedRole)} onEnter={closeFeatures} />;
  }

  // Gate the whole command center behind the (mock) persona login.
  if (!authedRole) {
    return (
      <LoginView
        preselectRole={preselectRole}
        onLogin={handleLogin}
        onViewFeatures={openFeatures}
      />
    );
  }

  return (
    <div
      className="relative flex h-screen w-screen overflow-hidden text-slate-100 font-sans"
      style={
        {
          "--role-accent": role.accent[0],
          "--role-accent-2": role.accent[1],
        } as React.CSSProperties
      }
    >
      <Suspense fallback={null}>
        <CommandBackground accent={role.accent} />
      </Suspense>

      <OrbitalRail
        activeSection={activeSection}
        onSectionChange={setActiveSection}
        hasActiveBranch={Boolean(proposal && proposal.status === "branch_only")}
        incidentCount={1}
        currentRole={currentRole}
      />

      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header
          currentRole={currentRole}
          onRoleChange={setCurrentRole}
          onSwitchPersona={handleSwitchPersona}
          onLogout={handleLogout}
          onOpenFeatures={openFeatures}
          activeSection={activeSection}
          onRefresh={runSimulation}
          isSimulating={isSimulating}
        />

        <main className="flex-1 overflow-y-auto overflow-x-hidden">
          <div className="w-full max-w-[1800px] mx-auto px-6 md:px-9 xl:px-12 pb-16 pt-2 md:pt-4">
            <AnimatePresence mode="wait">
              <motion.div key={activeSection + currentRole} {...pageTransition}>
                {activeSection === "overview" && (
                  <OverviewView
                    proposal={proposal}
                    onNavigate={setActiveSection}
                    onSimulate={runSimulation}
                    isSimulating={isSimulating}
                    currentRole={currentRole}
                  />
                )}
                {activeSection === "venues" && <VenuesView />}
                {activeSection === "schedule" && <ScheduleView />}
                {activeSection === "dependencies" && <DependencyGraphView />}
                {activeSection === "simulation" && (
                  <SimulationStudioView
                    proposal={proposal}
                    onSimulate={runSimulation}
                    onApprove={handleApprove}
                    onReject={handleReject}
                    isSimulating={isSimulating}
                    isActionLoading={isActionLoading}
                    actionMessage={actionMessage}
                  />
                )}
                {activeSection === "map" && <CampusMapView />}
                {activeSection === "volunteers" && <VolunteersView />}
                {activeSection === "notion-ai" && <NotionAiCenterView />}
                {activeSection === "participant" && <ParticipantPortalView />}
              </motion.div>
            </AnimatePresence>
          </div>
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MainSaaSApp />
    </QueryClientProvider>
  );
}
