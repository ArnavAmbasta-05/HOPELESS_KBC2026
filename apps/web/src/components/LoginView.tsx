import React, { useState, useEffect, Suspense } from "react";
import { motion } from "framer-motion";
import { Shield, Lock, User, ArrowRight, Check, KeyRound, AlertTriangle, Sparkles } from "lucide-react";
import { ROLES, getRole } from "../lib/roles";
import { MOCK_CREDENTIALS, verifyCredentials } from "../lib/mockAuth";

// WebGL dot field is heavy (three.js) — lazy-load so the gradient paints first.
const DotField = React.lazy(() =>
  import("./three/DotField").then((m) => ({ default: m.DotField }))
);

interface LoginViewProps {
  preselectRole?: string;
  onLogin: (roleId: string) => void;
  onViewFeatures?: () => void;
}

export const LoginView: React.FC<LoginViewProps> = ({ preselectRole, onLogin, onViewFeatures }) => {
  const [selectedRole, setSelectedRole] = useState<string>(preselectRole ?? "event_commander");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const role = getRole(selectedRole);
  const cred = MOCK_CREDENTIALS[selectedRole];

  // Clear any error and credentials when the persona changes.
  useEffect(() => {
    setError(null);
    setUsername("");
    setPassword("");
  }, [selectedRole]);

  const autofill = () => {
    if (cred) {
      setUsername(cred.username);
      setPassword(cred.password);
      setError(null);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    // Mock check — no network, no token. See lib/mockAuth.ts.
    const ok = verifyCredentials(selectedRole, username, password);
    window.setTimeout(() => {
      if (ok) {
        onLogin(selectedRole);
      } else {
        setError("Invalid credentials for this persona. Use the demo credentials shown below.");
        setSubmitting(false);
      }
    }, 350);
  };

  return (
    <div
      className="relative min-h-screen w-screen flex items-center justify-center overflow-y-auto text-slate-100 font-sans px-4 py-10"
      style={
        {
          "--role-accent": role.accent[0],
          "--role-accent-2": role.accent[1],
          background:
            "radial-gradient(1200px 600px at 20% -10%, rgba(34,211,238,0.10), transparent), radial-gradient(1000px 500px at 100% 0%, rgba(129,140,248,0.10), transparent), #06090f",
        } as React.CSSProperties
      }
    >
      {/* live interactive 3D dot-field background */}
      <Suspense fallback={null}>
        <DotField accent={role.accent} />
      </Suspense>
      {/* readability veil over the dots */}
      <div
        aria-hidden
        className="absolute inset-0 pointer-events-none"
        style={{ background: "radial-gradient(120% 120% at 50% 50%, transparent 40%, rgba(4,6,15,0.55) 100%)" }}
      />

      <motion.div
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        className="relative z-10 w-full max-w-4xl grid grid-cols-1 lg:grid-cols-5 gap-6"
      >
        {/* Left — brand + persona picker */}
        <div className="lg:col-span-3 space-y-5">
          <div className="flex items-center gap-3">
            <img
              src="/logo.png"
              alt="KoreX EventOps"
              className="h-10 w-auto object-contain drop-shadow-[0_0_16px_rgba(34,211,238,0.25)]"
            />
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase bg-amber-500/15 text-amber-300 border border-amber-500/40 flex items-center gap-1.5">
              <AlertTriangle className="w-3 h-3" /> Mock login · no real auth
            </span>
          </div>

          <div>
            <h1 className="font-display text-3xl md:text-4xl font-bold tracking-tight text-white">
              KBC 2026 Command Center
            </h1>
            <p className="text-sm text-slate-400 mt-1.5">
              Choose your operational persona, then sign in to open your role-specific console.
            </p>
            {onViewFeatures && (
              <button
                onClick={onViewFeatures}
                className="mt-2.5 inline-flex items-center gap-1.5 text-xs font-semibold text-cyan-300 hover:text-cyan-200 transition-colors"
              >
                <Sparkles className="w-3.5 h-3.5" /> Explore product features →
              </button>
            )}
          </div>

          <div className="flex items-center justify-between">
            <span className="kicker text-[10px] flex items-center gap-1.5">
              <Shield className="w-3.5 h-3.5 text-cyan-300" /> Select persona
            </span>
            <span className="text-[10px] text-slate-500 font-mono">{ROLES.length} roles</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {ROLES.map((r) => {
              const active = r.id === selectedRole;
              return (
                <button
                  key={r.id}
                  type="button"
                  onClick={() => setSelectedRole(r.id)}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-all border ${
                    active
                      ? "bg-white/[0.07] border-cyan-500/40 shadow-lg"
                      : "bg-slate-900/50 border-white/5 hover:border-white/20"
                  }`}
                >
                  <span
                    className="w-8 h-8 rounded-lg flex items-center justify-center text-[11px] font-bold text-white shrink-0"
                    style={{ backgroundImage: `linear-gradient(135deg, ${r.accent[0]}, ${r.accent[1]})` }}
                  >
                    {r.tag.slice(0, 2)}
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="text-xs font-bold text-slate-100 truncate">{r.name}</div>
                    <div className="text-[9px] text-slate-500 uppercase tracking-wider truncate">
                      {r.sections.length} modules · {r.clearance}
                    </div>
                  </div>
                  {active && <Check className="w-4 h-4 text-cyan-300 shrink-0" />}
                </button>
              );
            })}
          </div>
        </div>

        {/* Right — login form */}
        <div className="lg:col-span-2">
          <div className="glass-panel rounded-2xl p-6 space-y-5 sticky top-6">
            <div className="flex items-center gap-2.5">
              <span
                className="w-9 h-9 rounded-xl flex items-center justify-center text-xs font-bold text-white shrink-0"
                style={{ backgroundImage: `linear-gradient(135deg, ${role.accent[0]}, ${role.accent[1]})` }}
              >
                {role.tag.slice(0, 2)}
              </span>
              <div>
                <div className="text-sm font-bold text-white leading-tight">{role.name}</div>
                <div className="text-[10px] text-slate-500 uppercase tracking-wider">{role.clearance} clearance</div>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-3">
              <div className="relative">
                <User className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  autoComplete="username"
                  placeholder="Username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-9 pr-3 py-2.5 rounded-xl bg-slate-950 border border-white/10 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50"
                />
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  autoComplete="current-password"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-9 pr-3 py-2.5 rounded-xl bg-slate-950 border border-white/10 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50"
                />
              </div>

              {error && (
                <div className="p-2.5 rounded-xl bg-rose-950/40 border border-rose-500/30 text-[11px] text-rose-200 flex items-center gap-2">
                  <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={submitting || !username || !password}
                className="w-full px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-sm font-bold text-white shadow-lg disabled:opacity-50 flex items-center justify-center gap-2 transition-all"
              >
                {submitting ? (
                  <>
                    <Sparkles className="w-4 h-4 animate-spin" /> Signing in…
                  </>
                ) : (
                  <>
                    Enter console <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>

            {/* Demo credentials — visible on purpose for the mock login */}
            {cred && (
              <div className="p-3 rounded-xl bg-slate-900/80 border border-white/10 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                    <KeyRound className="w-3 h-3 text-amber-400" /> Demo credentials
                  </span>
                  <button
                    type="button"
                    onClick={autofill}
                    className="text-[10px] font-bold text-cyan-400 hover:text-cyan-300"
                  >
                    Autofill
                  </button>
                </div>
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-slate-500">Username</span>
                  <span className="font-mono text-slate-200">{cred.username}</span>
                </div>
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-slate-500">Password</span>
                  <span className="font-mono text-slate-200">{cred.password}</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
};
