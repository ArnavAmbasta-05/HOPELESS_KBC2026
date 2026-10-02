import React, { useEffect, useRef, useState } from "react";
import L from "leaflet";
import {
  MapPin,
  ExternalLink,
  Navigation,
  Footprints,
  Bus,
  AlertTriangle,
  CheckCircle2,
  Building2,
  Radio,
  Layers,
  ArrowRight,
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
    capacity: 1600,
    currentCount: 0,
    details: "Outage: Ceiling AC leak reported by Estate Office (08:00 AM). 4 sessions displaced.",
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
    walkingTimeMinutesFromMainAud: 10.0,
    shuttleTimeMinutesFromMainAud: 3,
  },
  {
    id: "ven_convention_c3",
    name: "Convention Centre Hall (Campus 3)",
    campus: "Campus 3 — Kathajodi / Central Library",
    category: "auditorium",
    status: "standby",
    lat: 20.3482,
    lng: 85.8122,
    capacity: 800,
    currentCount: 0,
    details: "Grand plenary backup hall. 12K projection system.",
    googleMapsUrl: "https://www.google.com/maps/search/?api=1&query=Campus+3+Central+Library+KIIT+Bhubaneswar",
    googleMapsDirectionsUrl: "https://www.google.com/maps/dir/?api=1&origin=20.3540,85.8180&destination=20.3482,85.8122",
    walkingDistanceMetersFromMainAud: 1200,
    walkingTimeMinutesFromMainAud: 14.0,
    shuttleTimeMinutesFromMainAud: 4,
  },
  {
    id: "ven_lh3",
    name: "Lecture Hall Complex LH-3",
    campus: "Campus 12 — Law School Complex",
    category: "auditorium",
    status: "standby",
    lat: 20.3592,
    lng: 85.8172,
    capacity: 150,
    currentCount: 0,
    details: "Digital podium & smart boards on standby.",
    googleMapsUrl: "https://www.google.com/maps/search/?api=1&query=KIIT+School+of+Law+Campus+12+Bhubaneswar",
    googleMapsDirectionsUrl: "https://www.google.com/maps/dir/?api=1&origin=20.3540,85.8180&destination=20.3592,85.8172",
    walkingDistanceMetersFromMainAud: 550,
    walkingTimeMinutesFromMainAud: 6.5,
    shuttleTimeMinutesFromMainAud: 2,
  },
  {
    id: "m_shuttle_02",
    name: "Electric Shuttle 2 (Route 1)",
    campus: "KIIT Road — Campus 6/7 Corridor",
    category: "shuttle",
    status: "disrupted",
    lat: 20.3560,
    lng: 85.8195,
    capacity: 30,
    details: "Battery circuit fault. Replaced by 50-seater Coach Bus A at Bay 4.",
    googleMapsUrl: "https://www.google.com/maps/search/?api=1&query=KIIT+Road+Patia+Bhubaneswar",
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
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const [selectedLocation, setSelectedLocation] = useState<GISMarker | null>(KIIT_GIS_LOCATIONS[0]);
  const [activeFilter, setActiveFilter] = useState<string>("all");

  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      // Initialize Leaflet map centered on KIIT Campus 6 (20.3540, 85.8180)
      const map = L.map(mapContainerRef.current, {
        center: [20.3555, 85.8195],
        zoom: 16,
        zoomControl: true,
      });

      // Dark Matter CartoDB Basemap tiles
      L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: "abcd",
        maxZoom: 20,
      }).addTo(map);

      // Add polyline connecting Campus 6 -> Campus 7 corridor
      const corridorPoints: L.LatLngExpression[] = [
        [20.3540, 85.8180], // Main Aud
        [20.3552, 85.8188], // OAT
        [20.3565, 85.8198], // Walkway
        [20.3582, 85.8210], // Campus 7
      ];

      L.polyline(corridorPoints, {
        color: "#06b6d4",
        weight: 4,
        dashArray: "6, 8",
        opacity: 0.8,
      }).addTo(map);

      mapInstanceRef.current = map;
    }

    const map = mapInstanceRef.current;

    // Clear previous markers
    map.eachLayer((layer) => {
      if (layer instanceof L.Marker) {
        map.removeLayer(layer);
      }
    });

    // Add Markers with customized HTML icons
    KIIT_GIS_LOCATIONS.forEach((loc) => {
      if (activeFilter !== "all" && loc.category !== activeFilter) return;

      const isDisrupted = loc.status === "disrupted";
      const isWarning = loc.status === "warning";
      const markerColor = isDisrupted ? "#f43f5e" : isWarning ? "#f59e0b" : "#06b6d4";

      const customIcon = L.divIcon({
        className: "custom-gis-pin",
        html: `
          <div style="
            background: ${markerColor};
            width: 24px;
            height: 24px;
            border-radius: 50%;
            border: 3px solid #050811;
            box-shadow: 0 0 12px ${markerColor};
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 10px;
            font-weight: 800;
          ">
            ${loc.category === "auditorium" ? "🏛" : loc.category === "shuttle" ? "🚌" : loc.category === "oat" ? "🎪" : "📍"}
          </div>
        `,
        iconSize: [24, 24],
        iconAnchor: [12, 12],
      });

      const marker = L.marker([loc.lat, loc.lng], { icon: customIcon }).addTo(map);

      marker.on("click", () => {
        setSelectedLocation(loc);
      });

      marker.bindPopup(`
        <div style="color: #0f172a; font-family: Inter, sans-serif; padding: 4px;">
          <strong style="font-size: 13px; display: block; margin-bottom: 2px;">${loc.name}</strong>
          <span style="font-size: 11px; color: #64748b;">${loc.campus}</span>
          ${loc.capacity ? `<div style="font-size: 11px; font-weight: bold; margin-top: 4px;">Capacity: ${loc.capacity} seats</div>` : ""}
          <div style="margin-top: 6px;">
            <a href="${loc.googleMapsUrl}" target="_blank" rel="noopener noreferrer" style="color: #0284c7; font-size: 11px; font-weight: bold; text-decoration: underline;">
              View on Google Maps ↗
            </a>
          </div>
        </div>
      `);
    });
  }, [activeFilter]);

  const panToLocation = (loc: GISMarker) => {
    setSelectedLocation(loc);
    if (mapInstanceRef.current) {
      mapInstanceRef.current.flyTo([loc.lat, loc.lng], 17, { duration: 1.2 });
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight">
            KIIT Campus 2.5D Real GIS Digital Twin
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real GPS coordinates, live electric shuttle tracking, gate optical flow counters, and real Google Maps directions.
          </p>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center space-x-2 overflow-x-auto">
          {[
            { id: "all", label: "All GIS Assets" },
            { id: "auditorium", label: "Auditoriums & Halls" },
            { id: "oat", label: "Open Air Theatres" },
            { id: "shuttle", label: "Transit Fleet" },
            { id: "gate", label: "Gate Sensors" },
          ].map((f) => (
            <button
              key={f.id}
              onClick={() => setActiveFilter(f.id)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                activeFilter === f.id
                  ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                  : "text-slate-400 hover:text-slate-200 bg-slate-900/60 border border-white/5"
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Split: Interactive Real Map (7 cols) + Real Distance Matrix (5 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Leaflet Live Map View (7 cols) */}
        <div className="lg:col-span-7 space-y-3">
          <div className="glass-panel p-2 rounded-2xl overflow-hidden border border-white/10 relative shadow-2xl">
            <div
              ref={mapContainerRef}
              className="w-full h-[520px] rounded-xl z-10"
              style={{ background: "#050811" }}
            />

            {/* Map Legend Overlay */}
            <div className="absolute bottom-5 left-5 z-20 p-3 rounded-xl bg-slate-950/90 backdrop-blur-md border border-white/10 text-xs space-y-1.5 shadow-xl">
              <div className="text-[10px] font-bold uppercase text-slate-400">Live Map Legend</div>
              <div className="flex items-center space-x-2 text-[11px] text-slate-300">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
                <span>Outage Venue (Main Aud)</span>
              </div>
              <div className="flex items-center space-x-2 text-[11px] text-slate-300">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
                <span>Active Re-homed / Standby</span>
              </div>
              <div className="flex items-center space-x-2 text-[11px] text-slate-300">
                <span className="w-3 h-0.5 bg-cyan-400 border-dashed" />
                <span>Campus 6-7 Transit Corridor</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right: Selected Venue Real Coordinates, Google Maps Links & Transit Matrix (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          {selectedLocation ? (
            <div className="glass-panel p-6 rounded-2xl space-y-5">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400">
                    {selectedLocation.category}
                  </span>
                  <span className="font-mono text-[11px] text-slate-400">
                    {selectedLocation.lat.toFixed(4)}° N, {selectedLocation.lng.toFixed(4)}° E
                  </span>
                </div>
                <h2 className="text-lg font-black text-white mt-1">{selectedLocation.name}</h2>
                <p className="text-xs text-slate-400 mt-0.5">{selectedLocation.campus}</p>
              </div>

              {/* Status & Details */}
              <div
                className={`p-3.5 rounded-xl border text-xs leading-relaxed ${
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
                  <div className="p-3 rounded-xl bg-slate-900/80 border border-white/5">
                    <span className="text-[10px] text-slate-400 flex items-center justify-center space-x-1">
                      <Footprints className="w-3 h-3 text-cyan-400" />
                      <span>Walking Dist</span>
                    </span>
                    <div className="font-bold text-white mt-1">
                      {selectedLocation.walkingDistanceMetersFromMainAud} Meters
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-900/80 border border-white/5">
                    <span className="text-[10px] text-slate-400">Walk Time</span>
                    <div className="font-bold text-cyan-300 mt-1">
                      {selectedLocation.walkingTimeMinutesFromMainAud} Min
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-900/80 border border-white/5">
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
                  className="w-full py-2.5 px-4 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/40 text-cyan-200 font-bold text-xs flex items-center justify-center space-x-2 transition-all shadow-lg"
                >
                  <MapPin className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Open Exact Pin on Google Maps</span>
                  <ExternalLink className="w-3 h-3" />
                </a>

                <a
                  href={selectedLocation.googleMapsDirectionsUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full py-2 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 border border-white/10 text-slate-300 font-semibold text-xs flex items-center justify-center space-x-2 transition-all"
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
          <div className="glass-panel p-4 rounded-2xl space-y-2 max-h-48 overflow-y-auto">
            <div className="text-[10px] font-bold uppercase text-slate-400">All Patia Campus Pins</div>
            {KIIT_GIS_LOCATIONS.map((loc) => (
              <div
                key={loc.id}
                onClick={() => panToLocation(loc)}
                className="p-2.5 rounded-xl bg-slate-900/60 hover:bg-slate-800/80 border border-white/5 cursor-pointer flex items-center justify-between text-xs"
              >
                <div>
                  <div className="font-semibold text-white truncate">{loc.name}</div>
                  <div className="text-[10px] text-slate-400">{loc.walkingDistanceMetersFromMainAud}m from Main Aud</div>
                </div>
                <span className="text-cyan-400 text-xs font-bold font-mono">Fly To →</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
