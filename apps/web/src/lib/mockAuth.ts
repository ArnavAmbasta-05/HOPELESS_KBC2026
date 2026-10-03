// Mock authentication for persona switching.
//
// IMPORTANT: this is NOT real authentication. Credentials are checked entirely
// in the browser against the static table below — there is no server-side
// verification, no password hashing and no session token. It exists so each
// persona switch goes through a login screen for the demo. Replace this module
// with the real OIDC / JWT flow (the backend already ships a provider) before
// any production deployment.

export interface MockCredential {
  username: string;
  password: string;
}

// One demo credential per persona. Shown on the login screen on purpose.
// Default demo password is the same for every persona for easy demoing.
const DEFAULT_PASSWORD = "12345678";

export const MOCK_CREDENTIALS: Record<string, MockCredential> = {
  event_commander: { username: "commander", password: DEFAULT_PASSWORD },
  ops_lead: { username: "ops.lead", password: DEFAULT_PASSWORD },
  tech_lead: { username: "av.lead", password: DEFAULT_PASSWORD },
  stage_manager: { username: "stage.mgr", password: DEFAULT_PASSWORD },
  volunteer_coordinator: { username: "crew.lead", password: DEFAULT_PASSWORD },
  security_lead: { username: "safety.lead", password: DEFAULT_PASSWORD },
  transport_lead: { username: "fleet.lead", password: DEFAULT_PASSWORD },
  super_admin: { username: "root", password: DEFAULT_PASSWORD },
};

const STORAGE_KEY = "korex.authedRole";

/** Mock credential check — returns true when username + password match the persona. */
export function verifyCredentials(roleId: string, username: string, password: string): boolean {
  const cred = MOCK_CREDENTIALS[roleId];
  if (!cred) return false;
  return username.trim() === cred.username && password === cred.password;
}

/** Persist the signed-in persona so a page refresh does not drop the demo session. */
export function persistAuthedRole(roleId: string | null): void {
  try {
    if (roleId) localStorage.setItem(STORAGE_KEY, roleId);
    else localStorage.removeItem(STORAGE_KEY);
  } catch {
    /* storage may be unavailable (private window) — degrade gracefully */
  }
}

/** Read back the persisted persona, if any. */
export function loadAuthedRole(): string | null {
  try {
    const v = localStorage.getItem(STORAGE_KEY);
    return v && MOCK_CREDENTIALS[v] ? v : null;
  } catch {
    return null;
  }
}
