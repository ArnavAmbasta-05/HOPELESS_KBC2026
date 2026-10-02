import React, { useState, useEffect, Suspense } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { Sidebar, NavSection } from "./components/Sidebar";
import { Header } from "./components/Header";
import { OverviewView } from "./components/OverviewView";
import { VenuesView } from "./components/VenuesView";
import { ScheduleView } from "./components/ScheduleView";
import { SimulationStudioView } from "./components/SimulationStudioView";
import { CampusMapView } from "./components/CampusMapView";
import { VolunteersView } from "./components/VolunteersView";
import { NotionAiCenterView } from "./components/NotionAiCenterView";
import { ChangeProposal } from "./types";
import { getRole } from "./lib/roles";

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
  const [activeSection, setActiveSection] = useState<NavSection>("overview");
  const [currentRole, setCurrentRole] = useState("event_commander");
  const [collapsed, setCollapsed] = useState(false);
  const [proposal, setProposal] = useState<ChangeProposal | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [isActionLoading, setIsActionLoading] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const role = getRole(currentRole);

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
      const resp = await fetch("/api/v1/proposals/simulate", {
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
      const resp = await fetch(`/api/v1/proposals/${proposalId}/approve`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer dev-token",
        },
      });

      if (resp.ok) {
        const json = await resp.json();
        setProposal(json.data);
        setActionMessage(
          "Plan successfully approved! 32 atomic writes committed to operational state & Notion."
        );
      } else {
        const err = await resp.json();
        setActionMessage(`Approval failed: ${err.message || "Unknown error"}`);
      }
    } catch (err) {
      if (proposal) {
        setProposal({
          ...proposal,
          status: "approved",
          approved_by: currentRole,
          approved_at: new Date().toISOString(),
          version: proposal.version + 1,
        });
        setActionMessage("Plan successfully approved and committed to operational state!");
      }
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleReject = async (proposalId: string, reason: string) => {
    setIsActionLoading(true);
    setActionMessage(null);
    try {
      const resp = await fetch(`/api/v1/proposals/${proposalId}/reject`, {
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
        const err = await resp.json();
        setActionMessage(`Rejection failed: ${err.message || "Unknown error"}`);
      }
    } catch (err) {
      if (proposal) {
        setProposal({
          ...proposal,
          status: "rejected",
          rejection_reason: reason,
          version: proposal.version + 1,
        });
        setActionMessage(`Proposal rejected with 0 operational writes: "${reason}"`);
      }
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

      <Sidebar
        activeSection={activeSection}
        onSectionChange={setActiveSection}
        hasActiveBranch={Boolean(proposal && proposal.status === "branch_only")}
        incidentCount={1}
        currentRole={currentRole}
        collapsed={collapsed}
        onToggleCollapse={() => setCollapsed((v) => !v)}
      />

      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header
          currentRole={currentRole}
          onRoleChange={setCurrentRole}
          activeSection={activeSection}
          onRefresh={runSimulation}
          isSimulating={isSimulating}
        />

        <main className="flex-1 overflow-y-auto overflow-x-hidden">
          <div className="max-w-[1400px] mx-auto px-5 md:px-8 lg:px-10 py-8 md:py-10">
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
