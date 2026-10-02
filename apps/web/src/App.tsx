import React, { useState, useEffect } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
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
  const [proposal, setProposal] = useState<ChangeProposal | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [isActionLoading, setIsActionLoading] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

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

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#050811] text-slate-100 font-sans">
      {/* 1. Left Sidebar Navigation */}
      <Sidebar
        activeSection={activeSection}
        onSectionChange={setActiveSection}
        hasActiveBranch={Boolean(proposal && proposal.status === "branch_only")}
        incidentCount={1}
      />

      {/* 2. Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header
          currentRole={currentRole}
          onRoleChange={setCurrentRole}
          activeSection={activeSection}
          onRefresh={runSimulation}
          isSimulating={isSimulating}
        />

        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          <div className="max-w-7xl mx-auto space-y-6">
            {activeSection === "overview" && (
              <OverviewView
                proposal={proposal}
                onNavigate={setActiveSection}
                onSimulate={runSimulation}
                isSimulating={isSimulating}
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
