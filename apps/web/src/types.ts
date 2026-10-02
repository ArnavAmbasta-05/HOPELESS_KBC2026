export interface VenueRejectionReason {
  venue_id: string;
  venue_name: string;
  capacity: number;
  registrants: number;
  reason: string;
}

export interface SessionVenueAssignment {
  session_id: string;
  session_name: string;
  original_venue_id: string;
  original_venue_name: string;
  new_venue_id: string;
  new_venue_name: string;
  new_venue_building: string;
  registrants: number;
  capacity: number;
  required_equipment: string[];
  rejections: VenueRejectionReason[];
}

export interface SpeakerReevalItem {
  speaker_id: string;
  name: string;
  title: string;
  session_id: string;
  session_name: string;
  arrival_building: string;
  venue_building: string;
  escort_needed: boolean;
  status_symbol: string;
  note: string;
}

export interface VenueResolutionResult {
  event_id: string;
  status: string;
  assignments: SessionVenueAssignment[];
  speaker_reevaluations: SpeakerReevalItem[];
  total_rejections_logged: number;
}

export interface VolunteerAssignmentChange {
  action: string;
  staff_id: string;
  name: string;
  role: string;
  skill: string;
  session_id?: string;
  session_name?: string;
  venue_id?: string;
  venue_name?: string;
  is_standby_activated: boolean;
  note: string;
}

export interface VolunteerReallocationResult {
  event_id: string;
  status: string;
  total_volunteers: number;
  untouched_count: number;
  changes_count: number;
  changes: VolunteerAssignmentChange[];
  standby_activations: string[];
}

export interface PlannedTask {
  task_id: string;
  description: string;
  team: string;
  venue_name?: string;
  session_name?: string;
  duration_minutes: number;
  deadline_str: string;
  estimated_finish_str: string;
  slack_minutes: number;
  is_at_risk: boolean;
  depends_on: string[];
}

export interface EscalationItem {
  task_id: string;
  description: string;
  slack: string;
  escalate_to_role: string;
  reason: string;
}

export interface ObjectDiffItem {
  entity_type: string;
  entity_id: string;
  action: "added" | "removed" | "modified" | "untouched";
  summary: string;
  old_state?: Record<string, any>;
  new_state?: Record<string, any>;
}

export interface SimulationDiff {
  total_changes: number;
  added_count: number;
  removed_count: number;
  modified_count: number;
  items: ObjectDiffItem[];
}

export interface RiskItem {
  risk_id: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  title: string;
  description: string;
  affected_entity_id: string;
  mitigation: string;
}

export interface RiskPlan {
  overall_risk: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  at_risk_tasks_count: number;
  at_risk_tasks: PlannedTask[];
  unresolved_dependencies: string[];
  risks: RiskItem[];
}

export interface ChangeProposal {
  proposal_id: string;
  event_id: string;
  baseline_revision: number;
  version: number;
  status: "branch_only" | "pending_approval" | "approved" | "rejected" | "committed";
  created_at: string;
  created_by: string;
  trigger: {
    trigger_type: string;
    venue_id?: string;
    venue_name?: string;
    time_window: string;
    reason: string;
    reported_by: string;
    reported_at: string;
  };
  blast_radius_summary: {
    root_unavailable_venue: string;
    hard_hits_count: number;
    soft_edges_count: number;
    impacted_sessions: Array<{ session_id: string; name: string; registrants: number }>;
    impacted_tasks: string[];
    impacted_comms: string[];
    deferred_soft_edges: string[];
  };
  venue_resolution: VenueResolutionResult;
  volunteer_reallocation: VolunteerReallocationResult;
  task_plan: PlannedTask[];
  escalations: EscalationItem[];
  risk_plan: RiskPlan;
  diff: SimulationDiff;
  ai_summary: string;
  is_ai_generated_summary: boolean;
  approved_by?: string | null;
  approved_at?: string | null;
  rejection_reason?: string | null;
  commit_result?: Record<string, any> | null;
}
