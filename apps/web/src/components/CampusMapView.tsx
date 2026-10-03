import React, { useState } from "react";
import {
  MapPin,
  ExternalLink,
  Navigation,
  Footprints,
  Bus,
  AlertTriangle,
  Building2,
  Radio,
  Layers,
  Sparkles,
} from "lucide-react";

export interface GISMarker {
  id: string;
  name: string;
  campus: string;
  category: "auditorium" | "oat" | "shuttle" | "gate" | "corridor";
  status: "disrupted" | "active" | "standby" | "warning";
  lat: number;
  lng: number;
  capacity?: number;
  currentCount?: number;
  details: string;
  googleMapsUrl: string;
  googleMapsDirectionsUrl: string;
  walkingDistanceMetersFromMainAud: number;
  walkingTimeMinutesFromMainAud: number;
  shuttleTimeMinutesFromMainAud: number;
}

export const KIIT_GIS_LOCATIONS: GISMarker[] = [
  {
    id: "ven_main_aud",
    name: "Main Auditorium (Campus 6)",
    campus: "Campus 6 — International Convention Wing",
    category: "auditorium",
    status: "disrupted",
    lat: 20.3540,
    lng: 85.8180,
    capacity: 500,
    currentCount: 0,
    details: "Outage: Ceiling AC leak reported by Estate Office (08:00 IST). 4 sessions displaced.",
    googleMapsUrl: "https://www.google.com/maps/search/?api=1&query=Auditorium+Campus+6+KIIT+Bhubaneswar",
    googleMapsDirectionsUrl: "https://www.google.com/maps/dir/?api=1&destination=20.3540,85.8180",
    walkingDistanceMetersFromMainAud: 0,
    walkingTimeMinutesFromMainAud: 0,
    shuttleTimeMinutesFromMainAud: 0,
  },
  {
    id: "ven_open_air",
    name: "Open Air Theatre (OAT)",
    campus: "Campus 6 — Rose Garden Complex",
    category: "oat",
    status: "active",
    lat: 20.3552,
    lng: 85.8188,
    capacity: 600,
    currentCount: 570,
    details: "Relocated destination for Opening Ceremony & Valedictory. Weather canopy rig on standby.",
    googleMapsUrl: "https://www.google.com/maps/search/?api=1&query=Open+Air+Theatre+KIIT+Campus+6+Bhubaneswar",
    googleMapsDirectionsUrl: "https://www.google.com/maps/dir/?api=1&origin=20.3540,85.8180&destination=20.3552,85.8188",
    walkingDistanceMetersFromMainAud: 120,
    walkingTimeMinutesFromMainAud: 1.5,
    shuttleTimeMinutesFromMainAud: 1,
  },
  {
    id: "ven_seminar",
    name: "Campus 7 Auditorium / Seminar Hall",
    campus: "Campus 7 — Technology Core",
    category: "auditorium",
    status: "active",
    lat: 20.3582,
    lng: 85.8210,
    capacity: 250,
    currentCount: 180,
    details: "Relocated destination for Keynote AI in FinTech. Bose F1 array active.",
    googleMapsUrl: "https://www.google.com/maps/search/?api=1&query=Campus+7+Auditorium+KIIT+Bhubaneswar",
    googleMapsDirectionsUrl: "https://www.google.com/maps/dir/?api=1&origin=20.3540,85.8180&destination=20.3582,85.8210",
    walkingDistanceMetersFromMainAud: 450,
    walkingTimeMinutesFromMainAud: 5.0,
    shuttleTimeMinutesFromMainAud: 2,
  },
  {
    id: "ven_ksac_chintan",
    name: "Chintan Auditorium (KSAC)",
    campus: "Campus 15 — Student Activity Centre",
    category: "auditorium",
    status: "standby",
    lat: 20.3620,
    lng: 85.8242,
    capacity: 200,
    currentCount: 95,
    details: "Standby contingency hall with hybrid live streaming setup.",
    googleMapsUrl: "https://www.google.com/maps/search/?api=1&query=KIIT+Student+Activity+Centre+KSAC+Bhubaneswar",
    googleMapsDirectionsUrl: "https://www.google.com/maps/dir/?api=1&origin=20.3540,85.8180&destination=20.3620,85.8242",
    walkingDistanceMetersFromMainAud: 850,
    walkingTimeMinutesFromMainAud: 9.0,
    shuttleTimeMinutesFromMainAud: 3,
  },
  {
    id: "ven_multipurpose",
    name: "Multipurpose Hall (Campus 6)",
    campus: "Campus 6 — Indoor Sports Block",
    category: "auditorium",
    status: "standby",
    lat: 20.3548,
    lng: 85.8172,
    capacity: 350,
    currentCount: 0,
    details: "Indoor weather fallback stage configured for evening lightning contingencies.",
    googleMapsUrl: "https://www.google.com/maps/search/?api=1&query=Campus+6+Indoor+Stadium+KIIT+Bhubaneswar",
    googleMapsDirectionsUrl: "https://www.google.com/maps/dir/?api=1&origin=20.3540,85.8180&destination=20.3548,85.8172",
    walkingDistanceMetersFromMainAud: 110,
    walkingTimeMinutesFromMainAud: 1.0,
    shuttleTimeMinutesFromMainAud: 1,
  },
  {
    id: "ven_campus3_conf",
    name: "Campus 3 Conference Hall",
    campus: "Campus 3 — Civil / Mechanical Wing",
    category: "auditorium",
    status: "active",
    lat: 20.3518,
    lng: 85.8145,
    capacity: 150,
    currentCount: 110,
    details: "Hosting academic breakout sessions and speaker green rooms.",
    googleMapsUrl: "https://www.google.com/maps/search/?api=1&query=KIIT+Campus+3+Bhubaneswar",
    googleMapsDirectionsUrl: "https://www.google.com/maps/dir/?api=1&destination=20.3518,85.8145",
    walkingDistanceMetersFromMainAud: 650,
    walkingTimeMinutesFromMainAud: 7.0,
    shuttleTimeMinutesFromMainAud: 3,
  },
  {
    id: "m_shuttle_1",
    name: "EV Shuttle Loop #1 (Campus 6 <-> 7)",
    campus: "Main Transit Loop",
    category: "shuttle",
    status: "active",
    lat: 20.3560,
    lng: 85.8195,
    capacity: 25,
    currentCount: 18,
    details: "High-frequency 3-minute transit link connecting displaced attendees between Campus 6 and 7.",
    googleMapsUrl: "https://www.google.com/maps/search/?api=1&query=KIIT+Road+Campus+6+Bhubaneswar",
    googleMapsDirectionsUrl: "https://www.google.com/maps/dir/?api=1&destination=20.3560,85.8195",
    walkingDistanceMetersFromMainAud: 250,
    walkingTimeMinutesFromMainAud: 3.0,
    shuttleTimeMinutesFromMainAud: 1,
  },
  {
    id: "m_bus_standby",
    name: "Coach Bus A (Active Dispatch)",
    campus: "KIIT Road — Bay 4 Terminal",
    category: "shuttle",
    status: "active",
    lat: 20.3570,
    lng: 85.8205,
    capacity: 50,
    currentCount: 32,
    details: "Active emergency transit between KP-6 Hostels, Campus 6 and Campus 7.",
    googleMapsUrl: "https://www.google.com/maps/search/?api=1&query=KIIT+Campus+7+Bhubaneswar",
    googleMapsDirectionsUrl: "https://www.google.com/maps/dir/?api=1&destination=20.3570,85.8205",
    walkingDistanceMetersFromMainAud: 350,
    walkingTimeMinutesFromMainAud: 4.0,
    shuttleTimeMinutesFromMainAud: 1,
  },
  {
    id: "m_gate_1",
    name: "Gate 1 (Campus 6 Main VIP Gate)",
    campus: "Campus 6 — Main Entry",
    category: "gate",
    status: "active",
    lat: 20.3535,
    lng: 85.8175,
    details: "Optical attendee counters active: 380 scanned for Opening Ceremony.",
    googleMapsUrl: "https://www.google.com/maps/search/?api=1&query=KIIT+Campus+6+Gate+1+Bhubaneswar",
    googleMapsDirectionsUrl: "https://www.google.com/maps/dir/?api=1&destination=20.3535,85.8175",
    walkingDistanceMetersFromMainAud: 80,
    walkingTimeMinutesFromMainAud: 1.0,
    shuttleTimeMinutesFromMainAud: 1,
  },
];

export const CampusMapView: React.FC = () => {
  const [selectedLocation, setSelectedLocation] = useState<GISMarker | null>(KIIT_GIS_LOCATIONS[0]);
  const [activeFilter, setActiveFilter] = useState<string>("all");
  const [mapStyle, setMapStyle] = useState<"satellite" | "streets">("streets");

  const filteredLocations = KIIT_GIS_LOCATIONS.filter((loc) => {
    if (activeFilter === "all") return true;
    return loc.category === activeFilter;
  });

  const googleMapsEmbedUrl = `https://maps.google.com/maps?q=${encodeURIComponent(
    selectedLocation
      ? `${selectedLocation.name}, KIIT University, Bhubaneswar`
      : "KIIT University Campus 6 Bhubaneswar"
  )}&t=${mapStyle === "satellite" ? "k" : "m"}&z=17&ie=UTF8&iwloc=&output=embed`;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="font-display text-2xl md:text-[28px] font-bold text-white tracking-tight">
              KIIT Campus <span className="text-cyan-400">Interactive Google Map</span>
            </h1>
            <span className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span>Google Maps Live</span>
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Live interactive Google Maps with venue auto-focus, satellite switch, and turn-by-turn routing.
          </p>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center space-x-1 overflow-x-auto bg-slate-900/90 p-1.5 rounded-2xl border border-white/10">
          {[
            { id: "all", label: "All Assets" },
            { id: "auditorium", label: "Auditoriums" },
            { id: "oat", label: "OAT" },
            { id: "shuttle", label: "Shuttles" },
            { id: "gate", label: "Gates" },
          ].map((f) => (
            <button
              key={f.id}
              onClick={() => setActiveFilter(f.id)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                activeFilter === f.id
                  ? "bg-slate-800 text-cyan-300 border border-cyan-500/40 shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Split: Interactive Real Map (7 cols) + Real Distance Matrix (5 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Main Map Display (7 cols) */}
        <div className="lg:col-span-7 space-y-3">
          <div className="glass-panel p-2 rounded-3xl overflow-hidden border border-white/10 relative shadow-2xl">
            {/* Real Google Maps Embed Container */}
            <div className="relative w-full h-[540px] rounded-2xl overflow-hidden bg-slate-950">
              <iframe
                title="Google Maps Live KIIT Campus View"
                src={googleMapsEmbedUrl}
                className="w-full h-full border-0 rounded-2xl"
                loading="lazy"
                allowFullScreen
              />

              {/* Focus Overlay Badge */}
              <div className="absolute top-4 left-4 z-10 px-3.5 py-2 rounded-xl bg-slate-950/95 backdrop-blur-md border border-white/10 shadow-xl flex items-center space-x-2 text-xs">
                <MapPin className="w-4 h-4 text-cyan-400" />
                <span className="font-bold text-white">
                  {selectedLocation ? selectedLocation.name : "KIIT University Campus"}
                </span>
                <span className="text-[10px] text-cyan-300 font-mono">
                  ({selectedLocation ? `${selectedLocation.lat.toFixed(4)}, ${selectedLocation.lng.toFixed(4)}` : "Live GPS"})
                </span>
              </div>

              {/* Map Type Switcher for Google Maps */}
              <div className="absolute top-4 right-4 z-10 flex items-center space-x-1.5 p-1 rounded-xl bg-slate-950/95 backdrop-blur-md border border-white/10 shadow-xl text-xs">
                <button
                  onClick={() => setMapStyle("streets")}
                  className={`px-3 py-1 rounded-lg font-bold text-[11px] transition-all ${
                    mapStyle !== "satellite"
                      ? "bg-cyan-500/30 text-cyan-300 border border-cyan-500/50 shadow-sm"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  Google Map
                </button>
                <button
                  onClick={() => setMapStyle("satellite")}
                  className={`px-3 py-1 rounded-lg font-bold text-[11px] transition-all ${
                    mapStyle === "satellite"
                      ? "bg-cyan-500/30 text-cyan-300 border border-cyan-500/50 shadow-sm"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  Google Satellite
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Right: Selected Venue Real Coordinates, Google Maps Links & Transit Matrix (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          {selectedLocation ? (
            <div className="glass-panel p-6 rounded-3xl space-y-5 border border-white/10 shadow-xl">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-500/30">
                    {selectedLocation.category}
                  </span>
                  <span className="font-mono text-[11px] text-slate-400">
                    {selectedLocation.lat.toFixed(4)}° N, {selectedLocation.lng.toFixed(4)}° E
                  </span>
                </div>
                <h2 className="text-xl font-bold text-white mt-2">{selectedLocation.name}</h2>
                <p className="text-xs text-slate-400 mt-0.5">{selectedLocation.campus}</p>
              </div>

              {/* Status & Details */}
              <div
                className={`p-4 rounded-2xl border text-xs leading-relaxed ${
                  selectedLocation.status === "disrupted"
                    ? "bg-rose-950/30 border-rose-500/40 text-rose-200"
                    : "bg-slate-900/80 border-white/5 text-slate-200"
                }`}
              >
                {selectedLocation.details}
              </div>

              {/* Real Walking & Transit Distances from Main Auditorium */}
              <div>
                <div className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2.5 flex items-center space-x-1.5">
                  <Navigation className="w-4 h-4 text-cyan-400" />
                  <span>Real Transit Distance from Main Aud (Campus 6)</span>
                </div>

                <div className="grid grid-cols-3 gap-2 text-center text-xs">
                  <div className="p-3 rounded-2xl bg-slate-900/80 border border-white/5">
                    <span className="text-[10px] text-slate-400 flex items-center justify-center space-x-1">
                      <Footprints className="w-3 h-3 text-cyan-400" />
                      <span>Walking Dist</span>
                    </span>
                    <div className="font-bold text-white mt-1">
                      {selectedLocation.walkingDistanceMetersFromMainAud} Meters
                    </div>
                  </div>

                  <div className="p-3 rounded-2xl bg-slate-900/80 border border-white/5">
                    <span className="text-[10px] text-slate-400">Walk Time</span>
                    <div className="font-bold text-cyan-300 mt-1">
                      {selectedLocation.walkingTimeMinutesFromMainAud} Min
                    </div>
                  </div>

                  <div className="p-3 rounded-2xl bg-slate-900/80 border border-white/5">
                    <span className="text-[10px] text-slate-400 flex items-center justify-center space-x-1">
                      <Bus className="w-3 h-3 text-indigo-400" />
                      <span>Shuttle Time</span>
                    </span>
                    <div className="font-bold text-indigo-300 mt-1">
                      {selectedLocation.shuttleTimeMinutesFromMainAud} Min
                    </div>
                  </div>
                </div>
              </div>

              {/* Real Google Maps Navigation Links */}
              <div className="space-y-2 pt-2 border-t border-white/10">
                <a
                  href={selectedLocation.googleMapsUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-bold text-xs flex items-center justify-center space-x-2 transition-all shadow-lg shadow-cyan-500/20"
                >
                  <MapPin className="w-3.5 h-3.5" />
                  <span>Open Exact Pin on Google Maps</span>
                  <ExternalLink className="w-3 h-3" />
                </a>

                <a
                  href={selectedLocation.googleMapsDirectionsUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full py-2.5 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 border border-white/10 text-slate-300 font-semibold text-xs flex items-center justify-center space-x-2 transition-all"
                >
                  <Navigation className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Get Live Turn-by-Turn Directions</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
          ) : (
            <div className="glass-panel p-12 text-center text-slate-500 text-xs">
              Click any pin on the map to inspect real distance and GPS data.
            </div>
          )}

          {/* Quick List of All KIIT Campuses */}
          <div className="glass-panel p-4 rounded-3xl space-y-2 max-h-56 overflow-y-auto border border-white/5">
            <div className="text-[10px] font-bold uppercase text-slate-400 tracking-wider">
              Filtered Campus Pins ({filteredLocations.length})
            </div>
            {filteredLocations.map((loc) => (
              <div
                key={loc.id}
                onClick={() => setSelectedLocation(loc)}
                className={`p-3 rounded-2xl border cursor-pointer flex items-center justify-between text-xs transition-all ${
                  selectedLocation?.id === loc.id
                    ? "bg-cyan-950/50 border-cyan-500/40 shadow-sm"
                    : "bg-slate-900/60 hover:bg-slate-800/80 border-white/5"
                }`}
              >
                <div>
                  <div className="font-semibold text-white truncate">{loc.name}</div>
                  <div className="text-[10px] text-slate-400">{loc.walkingDistanceMetersFromMainAud}m from Main Aud</div>
                </div>
                <span className="text-cyan-400 text-xs font-bold font-mono">Focus →</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
