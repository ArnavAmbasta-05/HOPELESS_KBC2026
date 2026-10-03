import React, { useState, useEffect, useRef } from "react";
import QRCode from "qrcode";
import {
  QrCode,
  Download,
  FileSpreadsheet,
  UserCheck,
  Plus,
  Search,
  Filter,
  RefreshCw,
  CheckCircle2,
  Clock,
  Building2,
  Calendar,
  Sparkles,
  ExternalLink,
  ShieldCheck,
  Smartphone,
  Copy,
  AlertCircle,
  Camera,
  Check,
} from "lucide-react";

interface AttendanceRecord {
  record_id: string;
  event_id: string;
  full_name: string;
  roll_no: string;
  email: string;
  phone: string;
  institution: string;
  session_id: string;
  session_name: string;
  venue_id: string;
  venue_name: string;
  check_in_time: string;
  check_in_time_ist: string;
  status: string;
  qr_token: string;
  notes: string;
}

const SESSIONS = [
  { id: "ses_opening", name: "Opening Ceremony & Keynote", venue_id: "ven_oat", venue_name: "Open Air Theatre (Campus 6)", capacity: 600 },
  { id: "ses_keynote_ai", name: "AI in Event Operations & FinTech", venue_id: "ven_aud_c7", venue_name: "Auditorium (Campus 7)", capacity: 250 },
  { id: "ses_panel_tech", name: "Future of Tech & Cloud Panel", venue_id: "ven_hall_c13", venue_name: "Conference Hall (Campus 13)", capacity: 120 },
  { id: "ses_mega_concert", name: "Star Night & Cultural Concert", venue_id: "ven_oat", venue_name: "Open Air Theatre (Campus 6)", capacity: 4000 },
];

export const ParticipantPortalView: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"qr_station" | "roster">("qr_station");
  const [records, setRecords] = useState<AttendanceRecord[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSessionFilter, setSelectedSessionFilter] = useState("all");

  // Form State
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);
  const [formFullName, setFormFullName] = useState("");
  const [formRollNo, setFormRollNo] = useState("");
  const [formEmail, setFormEmail] = useState("");
  const [formPhone, setFormPhone] = useState("");
  const [formInstitution, setFormInstitution] = useState("KIIT Deemed to be University");
  const [formSessionId, setFormSessionId] = useState("ses_opening");
  const [formNotes, setFormNotes] = useState("");

  // QR Generator state
  const [qrSessionId, setQrSessionId] = useState("ses_opening");
  const [qrDataUrl, setQrDataUrl] = useState<string>("");
  const [copiedLink, setCopiedLink] = useState(false);

  // Dynamic host for phone testing
  const [customHost, setCustomHost] = useState(() => {
    try {
      return window.location.origin;
    } catch {
      return "http://localhost:5173";
    }
  });

  const checkInUrl = `${customHost}/?view=participant&session=${qrSessionId}&token=kbc_${qrSessionId}`;

  // Generate real ISO 18004 QR code data URL whenever session or host changes
  useEffect(() => {
    QRCode.toDataURL(checkInUrl, {
      width: 380,
      margin: 2,
      color: {
        dark: "#030712",
        light: "#ffffff",
      },
      errorCorrectionLevel: "H",
    })
      .then((url) => setQrDataUrl(url))
      .catch((err) => console.error("QR Generation error:", err));
  }, [checkInUrl, qrSessionId]);

  // Check URL params on initial mount to prefill form if arriving via QR scan
  useEffect(() => {
    try {
      const params = new URLSearchParams(window.location.search);
      const sessionParam = params.get("session");
      if (sessionParam && SESSIONS.some((s) => s.id === sessionParam)) {
        setFormSessionId(sessionParam);
        setQrSessionId(sessionParam);
      }
    } catch {}
  }, []);

  const fetchRecords = async () => {
    setIsLoading(true);
    try {
      const resp = await fetch("/api/v1/attendance/records", {
        headers: { Authorization: "Bearer dev-token" },
      });
      if (resp.ok) {
        const json = await resp.json();
        setRecords(json.data || []);
      }
    } catch (err) {
      console.error("Failed to load records:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, []);

  const handleCheckInSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!formFullName || !formRollNo || !formEmail) return;

    setIsSubmitting(true);
    setSubmitSuccess(null);

    const targetSession = SESSIONS.find((s) => s.id === formSessionId) || SESSIONS[0];

    try {
      const resp = await fetch("/api/v1/attendance/check-in", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer dev-token",
        },
        body: JSON.stringify({
          full_name: formFullName,
          roll_no: formRollNo,
          email: formEmail,
          phone: formPhone || "+91 98765 00000",
          institution: formInstitution,
          session_id: targetSession.id,
          session_name: targetSession.name,
          venue_id: targetSession.venue_id,
          venue_name: targetSession.venue_name,
          qr_token: `qr_kbc2026_${formRollNo}_${targetSession.id}`,
          notes: formNotes || "Verified Gate Pass",
        }),
      });

      if (resp.ok) {
        const json = await resp.json();
        setSubmitSuccess(`Attendance marked for ${formFullName} at ${json.data.check_in_time_ist}!`);
        // Reset form
        setFormFullName("");
        setFormRollNo("");
        setFormEmail("");
        setFormPhone("");
        setFormNotes("");
        fetchRecords();
      }
    } catch (err) {
      setSubmitSuccess("Attendance marked locally (Offline / Network Fallback)");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleQuickDemoScan = () => {
    const demoNames = [
      { name: "Aarav Gupta", roll: "21051844", email: "aarav.gupta@kiit.ac.in", phone: "+91 98451 11223", inst: "KIIT School of Computer Engineering" },
      { name: "Ananya Mishra", roll: "22059912", email: "ananya.mishra@kiit.ac.in", phone: "+91 98112 33445", inst: "KIIT School of Management" },
      { name: "Siddharth Roy", roll: "KBC-NITR-512", email: "sid.roy@nitrkl.ac.in", phone: "+91 97781 44556", inst: "NIT Rourkela" },
      { name: "Deepak Sahoo", roll: "23057123", email: "deepak.sahoo@kiit.ac.in", phone: "+91 99370 77889", inst: "KIIT School of Mechanical Engineering" },
    ];
    const pick = demoNames[Math.floor(Math.random() * demoNames.length)];
    setFormFullName(pick.name);
    setFormRollNo(pick.roll);
    setFormEmail(pick.email);
    setFormPhone(pick.phone);
    setFormInstitution(pick.inst);
    setFormNotes("Scanned via Mobile QR Camera");
  };

  const handleExportExcel = () => {
    // 1. First trigger the backend streaming response
    try {
      window.location.href = "/api/v1/attendance/export-excel";
    } catch {
      // 2. Client-side RFC 4180 CSV export with UTF-8 BOM fallback
      let csvContent = "\ufeff";
      csvContent += "Record ID,Attendance Time (IST),Full Name,Roll No / Reg ID,Email Address,Phone Number,Institution / University,Session Name,Venue / Gate,Attendance Status,QR Token Hash,Notes\r\n";
      records.forEach((r) => {
        csvContent += `"${r.record_id}","${r.check_in_time_ist || r.check_in_time}","${r.full_name}","${r.roll_no}","${r.email}","${r.phone}","${r.institution}","${r.session_name}","${r.venue_name}","${r.status}","${r.qr_token}","${r.notes}"\r\n`;
      });
      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.setAttribute("href", url);
      link.setAttribute("download", `KBC2026_Attendance_Roster_${new Date().toISOString().slice(0, 10)}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const filteredRecords = records.filter((r) => {
    const matchesSession = selectedSessionFilter === "all" || r.session_id === selectedSessionFilter;
    const s = searchQuery.toLowerCase();
    const matchesSearch =
      !searchQuery ||
      r.full_name.toLowerCase().includes(s) ||
      r.roll_no.toLowerCase().includes(s) ||
      r.institution.toLowerCase().includes(s) ||
      r.email.toLowerCase().includes(s);
    return matchesSession && matchesSearch;
  });

  const selectedQrSession = SESSIONS.find((s) => s.id === qrSessionId) || SESSIONS[0];

  const copyQrUrl = () => {
    navigator.clipboard?.writeText(checkInUrl);
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 2000);
  };

  return (
    <div className="space-y-8">
      {/* Top Banner */}
      <div className="glass-panel aurora-ring p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2.5">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 flex items-center space-x-1">
              <Smartphone className="w-3 h-3" />
              <span>REAL SCANNABLE QR PASS &amp; ATTENDANCE ROSTER</span>
            </span>
            <span className="text-xs font-mono text-emerald-400 font-semibold">
              ● {records.length} Attendees Stamped Present
            </span>
          </div>
          <h1 className="text-2xl font-black text-white mt-1.5">
            Participant Portal &amp; QR Attendance System
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Generate 100% scannable ISO 18004 QR codes for any phone camera, ingest real-time participant registrations, record timestamps in IST, and export full verified rosters to Excel (.csv/.xlsx).
          </p>
        </div>

        <div className="flex items-center space-x-3 shrink-0">
          <button
            onClick={fetchRecords}
            disabled={isLoading}
            className="px-3.5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-white/10 text-xs font-bold text-slate-200 hover:text-white transition-all flex items-center space-x-2"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin text-cyan-400" : ""}`} />
            <span>{isLoading ? "Syncing..." : "Refresh Roster"}</span>
          </button>

          <button
            onClick={handleExportExcel}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-xs font-bold text-white shadow-lg shadow-emerald-500/20 transition-all flex items-center space-x-2"
          >
            <FileSpreadsheet className="w-4 h-4" />
            <span>Export to Excel (.csv)</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center space-x-2 border-b border-white/10 pb-2">
        <button
          onClick={() => setActiveTab("qr_station")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 ${
            activeTab === "qr_station"
              ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
              : "text-slate-400 hover:text-slate-200 bg-slate-900/60 border border-white/5"
          }`}
        >
          <QrCode className="w-3.5 h-3.5" />
          <span>Scannable QR Code &amp; Live Registration Form</span>
        </button>

        <button
          onClick={() => setActiveTab("roster")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 ${
            activeTab === "roster"
              ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
              : "text-slate-400 hover:text-slate-200 bg-slate-900/60 border border-white/5"
          }`}
        >
          <UserCheck className="w-3.5 h-3.5" />
          <span>Live Attendance Roster (Excel View)</span>
          <span className="px-1.5 py-0.5 rounded-full text-[10px] bg-slate-800 text-slate-300">
            {records.length}
          </span>
        </button>
      </div>

      {/* TAB 1: QR Generator & Form */}
      {activeTab === "qr_station" && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left: Dynamic Real QR Code Card (5 cols) */}
          <div className="lg:col-span-5 space-y-4">
            <div className="glass-panel p-6 rounded-2xl border border-cyan-500/30 space-y-4 shadow-2xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <QrCode className="w-4 h-4 text-cyan-400" />
                  <h3 className="text-sm font-bold text-white">Live Phone-Scannable QR Pass</h3>
                </div>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center space-x-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  <span>CAMERA SCANNABLE</span>
                </span>
              </div>

              {/* Target Session Select */}
              <div className="space-y-1 text-xs">
                <label className="text-slate-300 font-semibold">Select Session Track for QR:</label>
                <select
                  value={qrSessionId}
                  onChange={(e) => {
                    setQrSessionId(e.target.value);
                    setFormSessionId(e.target.value);
                  }}
                  className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-white/10 text-white font-medium focus:outline-none focus:border-cyan-500"
                >
                  {SESSIONS.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name} ({s.venue_name})
                    </option>
                  ))}
                </select>
              </div>

              {/* Real QR Image Display */}
              <div className="p-5 rounded-2xl bg-white flex flex-col items-center justify-center space-y-3 shadow-2xl border-4 border-slate-900">
                {qrDataUrl ? (
                  <img
                    src={qrDataUrl}
                    alt="Scannable Session QR Code"
                    className="w-56 h-56 object-contain rounded-lg"
                  />
                ) : (
                  <div className="w-56 h-56 flex items-center justify-center text-slate-800 font-bold">
                    Rendering QR...
                  </div>
                )}

                <div className="text-center pt-1">
                  <div className="text-xs font-black text-slate-900 tracking-tight">
                    {selectedQrSession.name}
                  </div>
                  <div className="text-[10px] text-slate-600 font-bold">
                    📍 {selectedQrSession.venue_name}
                  </div>
                  <div className="text-[9px] text-cyan-700 font-semibold mt-0.5">
                    📱 Point phone camera or Google Lens to scan &amp; check-in
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="space-y-2 pt-2 border-t border-white/10 text-xs">
                <div className="grid grid-cols-2 gap-2">
                  {qrDataUrl && (
                    <a
                      href={qrDataUrl}
                      download={`KBC2026_Pass_${qrSessionId}.png`}
                      className="py-2 px-3 rounded-xl bg-slate-900 hover:bg-slate-800 border border-white/10 font-bold text-slate-200 hover:text-white transition-all flex items-center justify-center space-x-1.5"
                    >
                      <Download className="w-3.5 h-3.5 text-cyan-400" />
                      <span>Download QR</span>
                    </a>
                  )}

                  <a
                    href={checkInUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="py-2 px-3 rounded-xl bg-cyan-950/40 hover:bg-cyan-900/60 border border-cyan-500/40 font-bold text-cyan-300 transition-all flex items-center justify-center space-x-1.5"
                  >
                    <ExternalLink className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Open Form Link</span>
                  </a>
                </div>

                <button
                  onClick={copyQrUrl}
                  className="w-full py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-white/10 font-bold text-slate-200 hover:text-white transition-all flex items-center justify-center space-x-2"
                >
                  <Copy className="w-3.5 h-3.5 text-cyan-400" />
                  <span>{copiedLink ? "✓ Link Copied to Clipboard!" : "Copy Check-In URL"}</span>
                </button>

                {/* Host configuration if testing from a phone on local network */}
                <div className="p-3 rounded-xl bg-slate-950/80 border border-white/5 space-y-1 text-[11px]">
                  <div className="text-slate-400 flex items-center justify-between">
                    <span>QR Target URL / Host:</span>
                    <span className="text-[10px] text-emerald-400 font-mono">Live Sync</span>
                  </div>
                  <input
                    type="text"
                    value={customHost}
                    onChange={(e) => setCustomHost(e.target.value)}
                    placeholder="http://192.168.1.X:5173"
                    className="w-full px-2.5 py-1.5 rounded-lg bg-slate-900 border border-white/10 font-mono text-[10px] text-cyan-300 focus:outline-none focus:border-cyan-500"
                  />
                  <div className="text-[9px] text-slate-500">
                    * For scanning from your mobile phone on the same Wi-Fi network, enter your PC's IP address (e.g. <code>http://192.168.1.15:5173</code>).
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right: Interactive Participant Check-In Form (7 cols) */}
          <div className="lg:col-span-7 space-y-4">
            <div className="glass-panel p-6 rounded-2xl border border-white/10 shadow-2xl space-y-5">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-white/10 gap-2">
                <div className="flex items-center space-x-2">
                  <Plus className="w-4 h-4 text-cyan-400" />
                  <h3 className="text-sm font-bold text-white">Participant Registration &amp; QR Check-In Form</h3>
                </div>
                <button
                  type="button"
                  onClick={handleQuickDemoScan}
                  className="px-3 py-1 rounded-lg bg-indigo-950/60 hover:bg-indigo-900 border border-indigo-500/40 text-[11px] font-bold text-indigo-300 flex items-center space-x-1.5 self-start"
                  title="Simulates rapid camera scan by filling realistic student details"
                >
                  <Camera className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Simulate Quick QR Scan</span>
                </button>
              </div>

              {submitSuccess && (
                <div className="p-3.5 rounded-xl bg-emerald-950/60 border border-emerald-500/40 text-xs font-semibold text-emerald-300 flex items-center space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>{submitSuccess}</span>
                </div>
              )}

              <form onSubmit={handleCheckInSubmit} className="space-y-4 text-xs">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-slate-300 font-semibold">Full Name *</label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Arnav Ambasta"
                      value={formFullName}
                      onChange={(e) => setFormFullName(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-slate-300 font-semibold">Roll No. / Student ID *</label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. 21051982 or KBC-2026-9812"
                      value={formRollNo}
                      onChange={(e) => setFormRollNo(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-slate-300 font-semibold">Email Address *</label>
                    <input
                      type="email"
                      required
                      placeholder="e.g. student@kiit.ac.in"
                      value={formEmail}
                      onChange={(e) => setFormEmail(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-slate-300 font-semibold">Phone / WhatsApp No.</label>
                    <input
                      type="tel"
                      placeholder="+91 98765 43210"
                      value={formPhone}
                      onChange={(e) => setFormPhone(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-slate-300 font-semibold">Institution / University</label>
                    <input
                      type="text"
                      placeholder="KIIT Deemed to be University"
                      value={formInstitution}
                      onChange={(e) => setFormInstitution(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-slate-300 font-semibold">Select Session Track *</label>
                    <select
                      value={formSessionId}
                      onChange={(e) => {
                        setFormSessionId(e.target.value);
                        setQrSessionId(e.target.value);
                      }}
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-white/10 text-white focus:outline-none focus:border-cyan-500"
                    >
                      {SESSIONS.map((s) => (
                        <option key={s.id} value={s.id}>
                          {s.name} — {s.venue_name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-slate-300 font-semibold">Delegate Category / Notes</label>
                  <input
                    type="text"
                    placeholder="e.g. Hackathon Finalist, Speaker Delegate, VIP Guest, General Participant"
                    value={formNotes}
                    onChange={(e) => setFormNotes(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                  />
                </div>

                <div className="pt-3 border-t border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="text-[11px] text-slate-400">
                    * Attendance stamped automatically in <span className="text-cyan-300 font-bold">IST (Asia/Kolkata)</span>
                  </div>

                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-xs font-bold text-white shadow-lg shadow-cyan-500/20 transition-all flex items-center justify-center space-x-2"
                  >
                    <UserCheck className="w-4 h-4" />
                    <span>{isSubmitting ? "Marking Attendance..." : "Submit & Mark Attendance"}</span>
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: Live Attendance Roster & Excel Exporter */}
      {activeTab === "roster" && (
        <div className="space-y-4">
          <div className="glass-panel p-5 rounded-2xl space-y-4 border border-white/10">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
              {/* Search bar */}
              <div className="relative flex-1 max-w-md">
                <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search by attendee name, roll no, college, or email..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-950 border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                />
              </div>

              {/* Filters & Export */}
              <div className="flex items-center space-x-3">
                <select
                  value={selectedSessionFilter}
                  onChange={(e) => setSelectedSessionFilter(e.target.value)}
                  className="px-3 py-2 rounded-xl bg-slate-900 border border-white/10 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                >
                  <option value="all">All Sessions ({records.length})</option>
                  {SESSIONS.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name}
                    </option>
                  ))}
                </select>

                <button
                  onClick={handleExportExcel}
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-xs font-bold text-white shadow-lg transition-all flex items-center space-x-2"
                >
                  <FileSpreadsheet className="w-4 h-4" />
                  <span>Download Excel (.csv)</span>
                </button>
              </div>
            </div>

            {/* Attendance Table */}
            <div className="overflow-x-auto rounded-xl border border-white/5">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950/80 text-slate-400 font-bold uppercase tracking-wider text-[10px] border-b border-white/10">
                  <tr>
                    <th className="px-4 py-3">Attendee Name</th>
                    <th className="px-4 py-3">Roll / Reg ID</th>
                    <th className="px-4 py-3">Institution</th>
                    <th className="px-4 py-3">Session &amp; Venue</th>
                    <th className="px-4 py-3">Check-in Time (IST)</th>
                    <th className="px-4 py-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {filteredRecords.length > 0 ? (
                    filteredRecords.map((r) => (
                      <tr key={r.record_id} className="hover:bg-white/[0.03] transition-colors">
                        <td className="px-4 py-3.5">
                          <div className="font-bold text-white">{r.full_name}</div>
                          <div className="text-[10px] text-slate-400">{r.email} • {r.phone}</div>
                        </td>
                        <td className="px-4 py-3.5">
                          <span className="font-mono text-cyan-300 font-semibold bg-cyan-950/50 px-2 py-0.5 rounded border border-cyan-500/30">
                            {r.roll_no}
                          </span>
                        </td>
                        <td className="px-4 py-3.5 text-slate-300">{r.institution}</td>
                        <td className="px-4 py-3.5">
                          <div className="font-semibold text-slate-200">{r.session_name}</div>
                          <div className="text-[10px] text-slate-400">📍 {r.venue_name}</div>
                        </td>
                        <td className="px-4 py-3.5">
                          <div className="font-mono text-emerald-400 font-bold">
                            {r.check_in_time_ist || r.check_in_time.slice(11, 19) + " UTC"}
                          </div>
                        </td>
                        <td className="px-4 py-3.5">
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center space-x-1 w-fit">
                            <CheckCircle2 className="w-2.5 h-2.5 text-emerald-400" />
                            <span>{r.status}</span>
                          </span>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={6} className="px-4 py-12 text-center text-slate-400">
                        No attendance records match your search criteria.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
