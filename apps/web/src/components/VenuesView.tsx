import React, { useState, useEffect } from "react";
import {
  Building2,
  Users,
  Tv,
  MapPin,
  AlertTriangle,
  CheckCircle2,
  CloudRain,
  Search,
  Zap,
} from "lucide-react";
import { Reveal, SectionHeader, Pill } from "./ui";

export interface VenueDetail {
  id: string;
  name: string;
  campus: string;
  building: string;
  capacity: number;
  currentOccupancy: number;
  type: "Indoor Auditorium" | "Outdoor Amphitheatre" | "Seminar Hall" | "Lecture Complex";
  status: "disrupted" | "active" | "standby" | "weather_warning";
  disruptionReason?: string;
  requiredStaff: {
    stageLead: number;
    avTechnicians: number;
    volunteers: number;
    security: number;
  };
  equipmentInventory: string[];
  powerBackup: string;
  coordinates: { lat: number; lng: number };
  weatherSensors?: {
    temp: string;
    rainRisk: string;
    windSpeed: string;
  };
}

// Venue data is served live by the backend scenario service
// (GET /api/v1/scenario/venues) — the SAME golden-seed source the CP-SAT
// solver, AI copilot and dependency engine use. No hardcoded roster here.

export const VenuesView: React.FC = () => {
  const [venues, setVenues] = useState<VenueDetail[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [selectedVenue, setSelectedVenue] = useState<VenueDetail | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  // Load venues from the backend scenario service (same source the solver uses).
  useEffect(() => {
    fetch("/api/v1/scenario/venues")
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data: VenueDetail[]) => {
        setVenues(data);
        setSelectedVenue(data[0] ?? null);
        setLoadError(null);
      })
      .catch((err) => {
        console.error("Failed to load venues:", err);
        setLoadError("Unable to load venues from the operations API.");
      });
  }, []);

  useEffect(() => {
    // Fetch live meteorological telemetry for Patia, Bhubaneswar
    fetch("/api/v1/weather/live-bhubaneswar")
      .then((res) => res.json())
      .then((data) => {
        if (data && data.temperature_celsius) {
          setVenues((prev) =>
            prev.map((v) =>
              v.id === "ven_open_air"
                ? {
                    ...v,
                    weatherSensors: {
                      temp: `${data.temperature_celsius}°C`,
                      rainRisk: `${data.precipitation_mm_per_hr > 0 ? "High Rain (" + data.precipitation_mm_per_hr + "mm)" : "0% (Clear)"}`,
                      windSpeed: `${data.wind_speed_kmh} km/h`,
                    },
                  }
                : v
            )
          );
        }
      })
      .catch((err) => console.warn("Live weather background fetch:", err));
  }, []);

  const filteredVenues = venues.filter((venue) => {
    const matchesSearch =
      venue.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      venue.campus.toLowerCase().includes(searchQuery.toLowerCase()) ||
      venue.building.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = typeFilter === "all" || venue.type === typeFilter;
    return matchesSearch && matchesType;
  });

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <Reveal>
        <SectionHeader
          kicker="Digital twin"
          title={<>Institutional venues &amp; <span className="text-aurora">auditoriums</span></>}
          subtitle="Real-time digital twin of every KIIT auditorium, OAT, AV inventory and staffing allocation."
          icon={<Building2 className="w-3.5 h-3.5" />}
          right={
            <div className="flex items-center gap-3">
              <div className="px-3.5 py-2 rounded-xl glass-soft text-xs">
                <span className="text-slate-400">Total seating:</span>{" "}
                <span className="font-bold text-cyan-300">
                  {venues.reduce((sum, v) => sum + v.capacity, 0).toLocaleString()}
                </span>
              </div>
              <div className="px-3.5 py-2 rounded-xl glass-soft text-xs">
                <span className="text-slate-400">Facilities:</span>{" "}
                <span className="font-bold text-white">{venues.length}</span>
              </div>
            </div>
          }
        />
      </Reveal>

      {loadError && (
        <div className="p-3 rounded-xl bg-rose-950/40 border border-rose-500/30 text-xs text-rose-200 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{loadError} Ensure the API is running on :8000.</span>
        </div>
      )}

      {/* Filter Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search venue name, campus, building..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-900/90 border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50"
          />
        </div>

        <div className="flex items-center space-x-2 w-full sm:w-auto overflow-x-auto">
          {["all", "Indoor Auditorium", "Outdoor Amphitheatre", "Seminar Hall", "Lecture Complex"].map((t) => (
            <button
              key={t}
              onClick={() => setTypeFilter(t)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                typeFilter === t
                  ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                  : "text-slate-400 hover:text-slate-200 bg-slate-900/60 border border-white/5"
              }`}
            >
              {t === "all" ? "All Types" : t}
            </button>
          ))}
        </div>
      </div>

      {/* Venues Grid & Detail Split */}
      <Reveal className="grid grid-cols-1 lg:grid-cols-12 gap-6" as="div">
        {/* Venues Cards (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          {filteredVenues.map((venue) => {
            const isSelected = selectedVenue?.id === venue.id;
            const occupancyPct = Math.round((venue.currentOccupancy / venue.capacity) * 100);

            return (
              <div
                key={venue.id}
                onClick={() => setSelectedVenue(venue)}
                className={`rail-card p-5 rounded-2xl cursor-pointer transition-all border ${
                  isSelected
                    ? "glass-panel border-cyan-500/50 shadow-glow-cyan"
                    : "glass-soft border-white/5 hover:border-white/20 hover:-translate-y-0.5"
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center space-x-2.5">
                      <h3 className="text-base font-bold text-white">{venue.name}</h3>
                      {venue.status === "disrupted" && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase bg-rose-500/20 text-rose-300 border border-rose-500/40 flex items-center space-x-1">
                          <AlertTriangle className="w-3 h-3" />
                          <span>OUTAGE</span>
                        </span>
                      )}
                      {venue.status === "active" && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center space-x-1">
                          <CheckCircle2 className="w-3 h-3" />
                          <span>IN SERVICE</span>
                        </span>
                      )}
                      {venue.status === "standby" && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase bg-slate-800 text-slate-300 border border-white/10">
                          AVAILABLE STANDBY
                        </span>
                      )}
                    </div>
                    <div className="flex items-center space-x-2 text-xs text-slate-400 mt-1">
                      <MapPin className="w-3.5 h-3.5 text-cyan-400" />
                      <span>{venue.campus} • {venue.building}</span>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="text-lg font-black text-white">{venue.capacity}</div>
                    <div className="text-[10px] uppercase font-semibold text-slate-500">Max Seats</div>
                  </div>
                </div>

                {venue.disruptionReason && (
                  <div className="mt-3.5 p-2.5 rounded-xl bg-rose-950/40 border border-rose-500/30 text-xs text-rose-200">
                    {venue.disruptionReason}
                  </div>
                )}

                {/* Occupancy bar */}
                <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between text-xs">
                  <div className="flex items-center space-x-4 text-slate-400">
                    <span>Staff Required: <strong className="text-slate-200">{venue.requiredStaff.stageLead + venue.requiredStaff.avTechnicians + venue.requiredStaff.volunteers + venue.requiredStaff.security} Pax</strong></span>
                    <span>AV Rigs: <strong className="text-slate-200">{venue.equipmentInventory.length} Items</strong></span>
                  </div>

                  {venue.currentOccupancy > 0 && (
                    <div className="flex items-center space-x-2">
                      <span className="text-slate-400">{venue.currentOccupancy} Occupied</span>
                      <span className="font-bold text-cyan-400">({occupancyPct}%)</span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Selected Venue Deep Inspector (5 cols) */}
        <div className="lg:col-span-5">
          {selectedVenue ? (
            <div className="glass-panel p-6 rounded-2xl sticky top-24 space-y-6">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-cyan-400">
                    {selectedVenue.type}
                  </span>
                  <span className="font-mono text-[11px] text-slate-500">
                    ID: {selectedVenue.id}
                  </span>
                </div>
                <h2 className="text-xl font-black text-white mt-1">{selectedVenue.name}</h2>
                <p className="text-xs text-slate-400 mt-1">{selectedVenue.campus} • {selectedVenue.building}</p>
              </div>

              {/* Weather Sensor Tag (if outdoor) */}
              {selectedVenue.weatherSensors && (
                <div className="p-3.5 rounded-xl bg-cyan-950/30 border border-cyan-500/30 space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-semibold text-cyan-300">
                    <span className="flex items-center space-x-1.5">
                      <CloudRain className="w-4 h-4" />
                      <span>Live Weather Station Sensor</span>
                    </span>
                    <span className="text-emerald-400 font-bold">MONITORED</span>
                  </div>
                  <div className="grid grid-cols-3 gap-2 pt-1 text-center text-xs">
                    <div className="p-1.5 rounded-lg bg-slate-900/80">
                      <div className="text-[10px] text-slate-500">Temp</div>
                      <div className="font-bold text-white">{selectedVenue.weatherSensors.temp}</div>
                    </div>
                    <div className="p-1.5 rounded-lg bg-slate-900/80">
                      <div className="text-[10px] text-slate-500">Precip Risk</div>
                      <div className="font-bold text-cyan-400">{selectedVenue.weatherSensors.rainRisk}</div>
                    </div>
                    <div className="p-1.5 rounded-lg bg-slate-900/80">
                      <div className="text-[10px] text-slate-500">Wind</div>
                      <div className="font-bold text-white">{selectedVenue.weatherSensors.windSpeed}</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Staffing Allocation Requirements */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2.5 flex items-center space-x-1.5">
                  <Users className="w-4 h-4 text-indigo-400" />
                  <span>Mandatory Staffing Roster</span>
                </h4>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="p-2.5 rounded-xl bg-slate-900/80 border border-white/5 flex justify-between">
                    <span className="text-slate-400">Stage Leads</span>
                    <span className="font-bold text-white">{selectedVenue.requiredStaff.stageLead} Pax</span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-900/80 border border-white/5 flex justify-between">
                    <span className="text-slate-400">AV Technicians</span>
                    <span className="font-bold text-cyan-400">{selectedVenue.requiredStaff.avTechnicians} Pax</span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-900/80 border border-white/5 flex justify-between">
                    <span className="text-slate-400">Volunteer Crew</span>
                    <span className="font-bold text-white">{selectedVenue.requiredStaff.volunteers} Pax</span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-900/80 border border-white/5 flex justify-between">
                    <span className="text-slate-400">Security Gate</span>
                    <span className="font-bold text-white">{selectedVenue.requiredStaff.security} Pax</span>
                  </div>
                </div>
              </div>

              {/* Equipment Inventory */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2.5 flex items-center space-x-1.5">
                  <Tv className="w-4 h-4 text-cyan-400" />
                  <span>Installed Equipment Inventory</span>
                </h4>
                <div className="space-y-1.5">
                  {selectedVenue.equipmentInventory.map((eq, i) => (
                    <div
                      key={i}
                      className="px-3 py-2 rounded-xl bg-slate-900/80 border border-white/5 text-xs text-slate-200 flex items-center space-x-2"
                    >
                      <Zap className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                      <span>{eq}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Power & Infrastructure Details */}
              <div className="p-3.5 rounded-xl bg-slate-900/80 border border-white/5 space-y-1 text-xs">
                <div className="text-[10px] font-bold uppercase text-slate-500">Power & Backup Resiliency</div>
                <div className="text-slate-300 font-medium">{selectedVenue.powerBackup}</div>
              </div>
            </div>
          ) : (
            <div className="glass-panel p-12 text-center text-slate-500 text-xs">
              Select a venue to inspect full hardware specifications.
            </div>
          )}
        </div>
      </Reveal>
    </div>
  );
};
