import React, { useState } from 'react';

export interface MapMarker {
  id: string;
  name: string;
  type: 'venue' | 'shuttle' | 'gate' | 'crowd_zone';
  status: 'normal' | 'disrupted' | 'warning' | 'surge';
  lat: number;
  lng: number;
  capacity?: number;
  currentCount?: number;
  details: string;
  source: string;
  timestamp: string;
}

export const CampusMapView: React.FC = () => {
  const [selectedMarker, setSelectedMarker] = useState<MapMarker | null>(null);
  const [filter, setFilter] = useState<'all' | 'venues' | 'mobility' | 'crowd'>('all');

  const markers: MapMarker[] = [
    {
      id: 'm_ven_main_aud',
      name: 'Main Auditorium (Campus 6)',
      type: 'venue',
      status: 'disrupted',
      lat: 20.3542,
      lng: 85.8182,
      capacity: 1600,
      currentCount: 0,
      details: 'Disrupted: AC ceiling leak. 4 sessions relocated.',
      source: 'ESTATE_OFFICE_NOTION_SYNC',
      timestamp: '08:00 AM (Fresh)',
    },
    {
      id: 'm_ven_oat',
      name: 'Open Air Theatre (Campus 6)',
      type: 'venue',
      status: 'surge',
      lat: 20.3550,
      lng: 85.8190,
      capacity: 600,
      currentCount: 570,
      details: 'Active: Opening Ceremony & Valedictory relocated here.',
      source: 'ATTENDANCE_QR_INGEST',
      timestamp: '08:55 AM (Fresh)',
    },
    {
      id: 'm_ven_aud_c7',
      name: 'Auditorium (Campus 7)',
      type: 'venue',
      status: 'normal',
      lat: 20.3585,
      lng: 85.8214,
      capacity: 250,
      currentCount: 140,
      details: 'Active: Keynote AI Session relocated here.',
      source: 'ATTENDANCE_QR_INGEST',
      timestamp: '08:50 AM (Fresh)',
    },
    {
      id: 'm_shuttle_02',
      name: 'Electric Shuttle 2',
      type: 'shuttle',
      status: 'disrupted',
      lat: 20.3545,
      lng: 85.8185,
      capacity: 30,
      details: 'Battery fault: Replaced by Coach Bus A (Bay 4).',
      source: 'TRANSPORT_TELEMETRY_ENGINE',
      timestamp: '11:15 AM (Fresh)',
    },
    {
      id: 'm_bus_standby_a',
      name: 'Coach Bus A (Active Standby)',
      type: 'shuttle',
      status: 'normal',
      lat: 20.3560,
      lng: 85.8200,
      capacity: 50,
      currentCount: 30,
      details: 'Covering Campus 6 -> 7 Link route.',
      source: 'TRANSPORT_DISPATCH_QUEUE',
      timestamp: '11:20 AM (Fresh)',
    },
    {
      id: 'm_corridor_c6_c7',
      name: 'Campus 6-7 Covered Walkway',
      type: 'crowd_zone',
      status: 'warning',
      lat: 20.3565,
      lng: 85.8195,
      capacity: 300,
      currentCount: 270,
      details: 'High bottleneck (90% capacity). Gate 2 reroute active.',
      source: 'ANONYMOUS_GATE_COUNT_FEED',
      timestamp: '08:52 AM (Fresh)',
    },
    {
      id: 'm_gate_1',
      name: 'Gate 1 Main Entry',
      type: 'gate',
      status: 'warning',
      lat: 20.3538,
      lng: 85.8178,
      capacity: 60,
      currentCount: 55,
      details: 'High incoming flow rate (55/min). Diverting to Gate 2.',
      source: 'GATE_FLOW_TELEMETRY',
      timestamp: '08:54 AM (Fresh)',
    },
  ];

  const filteredMarkers = markers.filter(m => {
    if (filter === 'all') return true;
    if (filter === 'venues') return m.type === 'venue';
    if (filter === 'mobility') return m.type === 'shuttle';
    if (filter === 'crowd') return m.type === 'crowd_zone' || m.type === 'gate';
    return true;
  });

  const getStatusColor = (status: MapMarker['status']) => {
    switch (status) {
      case 'disrupted': return '#ef4444';
      case 'surge': return '#dc2626';
      case 'warning': return '#f59e0b';
      case 'normal': return '#10b981';
      default: return '#3b82f6';
    }
  };

  return (
    <div style={{ backgroundColor: '#0f172a', padding: '20px', borderRadius: '12px', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div>
          <h2 style={{ margin: 0, fontSize: '1.3rem', color: '#38bdf8' }}>🗺️ Live KIIT Campus Mobility & Crowd Map</h2>
          <p style={{ margin: '4px 0 0', fontSize: '0.85rem', color: '#94a3b8' }}>
            Real-time visual twin of campus venues, transit corridors, shuttles, and bottleneck gates.
          </p>
        </div>

        {/* Filter controls */}
        <div style={{ display: 'flex', gap: '8px' }}>
          {(['all', 'venues', 'mobility', 'crowd'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setFilter(tab)}
              style={{
                padding: '6px 14px',
                borderRadius: '6px',
                border: '1px solid #334155',
                backgroundColor: filter === tab ? '#0284c7' : '#1e293b',
                color: '#fff',
                cursor: 'pointer',
                fontSize: '0.85rem',
                textTransform: 'capitalize',
                fontWeight: 600,
              }}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Map visualization canvas container */}
      <div
        style={{
          height: '420px',
          backgroundColor: '#1e293b',
          borderRadius: '10px',
          border: '1px solid #334155',
          position: 'relative',
          overflow: 'hidden',
          backgroundImage: 'radial-gradient(#334155 1px, transparent 1px)',
          backgroundSize: '24px 24px',
        }}
      >
        {/* Campus sector labels */}
        <div style={{ position: 'absolute', top: 16, left: 20, color: '#64748b', fontSize: '0.8rem', fontWeight: 'bold' }}>
          CAMPUS 6 (CENTRAL)
        </div>
        <div style={{ position: 'absolute', top: 16, right: 30, color: '#64748b', fontSize: '0.8rem', fontWeight: 'bold' }}>
          CAMPUS 7 (NORTH-EAST)
        </div>
        <div style={{ position: 'absolute', bottom: 20, right: 30, color: '#64748b', fontSize: '0.8rem', fontWeight: 'bold' }}>
          CAMPUS 13 (SOUTH-EAST)
        </div>

        {/* Transit path lines */}
        <svg style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none' }}>
          <line x1="180" y1="180" x2="480" y2="120" stroke="#0284c7" strokeWidth="3" strokeDasharray="6,6" opacity="0.6" />
          <line x1="180" y1="180" x2="600" y2="340" stroke="#f59e0b" strokeWidth="3" strokeDasharray="6,6" opacity="0.6" />
        </svg>

        {/* Dynamic Markers */}
        {filteredMarkers.map((marker, index) => {
          // Layout positions on the virtual campus grid
          const positions: Record<string, { top: number; left: number }> = {
            m_ven_main_aud: { top: 130, left: 100 },
            m_ven_oat: { top: 220, left: 160 },
            m_ven_aud_c7: { top: 100, left: 490 },
            m_shuttle_02: { top: 155, left: 240 },
            m_bus_standby_a: { top: 135, left: 340 },
            m_corridor_c6_c7: { top: 175, left: 290 },
            m_gate_1: { top: 280, left: 90 },
          };
          const pos = positions[marker.id] || { top: 150 + index * 40, left: 200 + index * 40 };

          return (
            <div
              key={marker.id}
              onClick={() => setSelectedMarker(marker)}
              style={{
                position: 'absolute',
                top: `${pos.top}px`,
                left: `${pos.left}px`,
                backgroundColor: getStatusColor(marker.status),
                color: '#fff',
                padding: '6px 12px',
                borderRadius: '20px',
                fontSize: '0.8rem',
                fontWeight: 'bold',
                cursor: 'pointer',
                boxShadow: '0 4px 12px rgba(0,0,0,0.4)',
                transform: selectedMarker?.id === marker.id ? 'scale(1.1)' : 'scale(1.0)',
                transition: 'transform 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              <span>{marker.type === 'shuttle' ? '🚌' : marker.type === 'gate' ? '🚪' : marker.type === 'crowd_zone' ? '👥' : '🏛️'}</span>
              <span>{marker.name.split('(')[0]}</span>
            </div>
          );
        })}
      </div>

      {/* Selected Marker Detail Drawer */}
      {selectedMarker && (
        <div style={{ marginTop: '16px', backgroundColor: '#1e293b', padding: '16px', borderRadius: '8px', border: '1px solid #475569' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ margin: 0, color: '#38bdf8', fontSize: '1.05rem' }}>{selectedMarker.name}</h3>
            <span style={{ fontSize: '0.75rem', backgroundColor: getStatusColor(selectedMarker.status), color: '#fff', padding: '3px 8px', borderRadius: '4px', textTransform: 'uppercase' }}>
              {selectedMarker.status}
            </span>
          </div>
          <p style={{ margin: '8px 0', fontSize: '0.88rem', color: '#cbd5e1' }}>{selectedMarker.details}</p>
          <div style={{ display: 'flex', gap: '20px', fontSize: '0.8rem', color: '#94a3b8', borderTop: '1px solid #334155', paddingTop: '8px' }}>
            <div>Capacity: <strong>{selectedMarker.capacity || 'N/A'}</strong></div>
            <div>Source: <code>{selectedMarker.source}</code></div>
            <div>Freshness: <strong>{selectedMarker.timestamp}</strong></div>
          </div>
        </div>
      )}
    </div>
  );
};
