import React, { useState } from 'react';
import { ParticipantNotice, ParticipantScheduleItem, QueuedOfflineScan } from './types';
import { OfflineScanQueueManager } from './OfflineScanQueue';

export const ParticipantApp: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'schedule' | 'notices' | 'pass'>('schedule');
  const [offlineQueueManager] = useState(() => new OfflineScanQueueManager());
  const [queuedCount, setQueuedCount] = useState(() => offlineQueueManager.getQueue().length);
  const [checkedInSessions, setCheckedInSessions] = useState<Record<string, boolean>>({});

  const schedule: ParticipantScheduleItem[] = [
    {
      sessionId: 'ses_opening',
      title: 'Opening Ceremony & Keynote',
      venueName: 'Open Air Theatre (Campus 6)',
      building: 'Campus 6',
      timeWindow: '09:00 AM - 11:00 AM',
      isRelocated: true,
      checkedIn: !!checkedInSessions['ses_opening'],
    },
    {
      sessionId: 'ses_keynote_ai',
      title: 'AI in Event Operations',
      venueName: 'Auditorium (Campus 7)',
      building: 'Campus 7',
      timeWindow: '11:30 AM - 01:00 PM',
      isRelocated: true,
      checkedIn: !!checkedInSessions['ses_keynote_ai'],
    },
    {
      sessionId: 'ses_panel_tech',
      title: 'Future of Tech Panel',
      venueName: 'Conference Hall (Campus 13)',
      building: 'Campus 13',
      timeWindow: '02:00 PM - 03:30 PM',
      isRelocated: true,
      checkedIn: !!checkedInSessions['ses_panel_tech'],
    },
  ];

  const notices: ParticipantNotice[] = [
    {
      noticeId: 'notif_01',
      sessionTitle: 'Opening Ceremony & Keynote',
      oldVenue: 'Main Auditorium (Campus 6)',
      newVenue: 'Open Air Theatre (Campus 6)',
      effectiveTime: '09:00 AM',
      actionRequired: 'Please proceed directly to Open Air Theatre (Gate 1 entry).',
      timestamp: '08:05 AM',
    },
    {
      noticeId: 'notif_02',
      sessionTitle: 'AI in Event Operations',
      oldVenue: 'Main Auditorium (Campus 6)',
      newVenue: 'Auditorium (Campus 7)',
      effectiveTime: '11:30 AM',
      actionRequired: 'Take Campus Shuttle 1 or 5-minute walkway to Campus 7 Auditorium.',
      timestamp: '08:10 AM',
    },
  ];

  const handleSimulateCheckIn = (sessionId: string) => {
    setCheckedInSessions(prev => ({ ...prev, [sessionId]: true }));
    const scan: QueuedOfflineScan = {
      scanId: `scn_${Date.now()}`,
      token: `token_part_op_001_${sessionId}`,
      sessionId,
      venueId: 'ven_oat',
      timestamp: new Date().toISOString(),
      idempotencyKey: `idem_pwa_part_001_${sessionId}`,
    };
    offlineQueueManager.enqueueScan(scan);
    setQueuedCount(offlineQueueManager.getQueue().length);
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '16px', color: '#f8fafc', fontFamily: 'sans-serif' }}>
      <header style={{ marginBottom: '16px', borderBottom: '1px solid #334155', paddingBottom: '12px' }}>
        <h1 style={{ margin: 0, fontSize: '1.4rem', color: '#38bdf8' }}>KoreX Participant Pass</h1>
        <p style={{ margin: '4px 0 0', fontSize: '0.85rem', color: '#94a3b8' }}>
          Live Event Companion · KIIT KBC 2026
        </p>
      </header>

      {/* Navigation tabs */}
      <nav aria-label="Participant Tabs" style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
        <button
          onClick={() => setActiveTab('schedule')}
          style={{
            flex: 1,
            padding: '8px 12px',
            backgroundColor: activeTab === 'schedule' ? '#0284c7' : '#1e293b',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: 600,
          }}
        >
          Schedule
        </button>
        <button
          onClick={() => setActiveTab('notices')}
          style={{
            flex: 1,
            padding: '8px 12px',
            backgroundColor: activeTab === 'notices' ? '#0284c7' : '#1e293b',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: 600,
            position: 'relative',
          }}
        >
          Notices {notices.length > 0 && <span style={{ marginLeft: '4px', background: '#ef4444', borderRadius: '10px', padding: '2px 6px', fontSize: '0.75rem' }}>{notices.length}</span>}
        </button>
        <button
          onClick={() => setActiveTab('pass')}
          style={{
            flex: 1,
            padding: '8px 12px',
            backgroundColor: activeTab === 'pass' ? '#0284c7' : '#1e293b',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: 600,
          }}
        >
          QR Pass
        </button>
      </nav>

      {/* Schedule View */}
      {activeTab === 'schedule' && (
        <div>
          <h2 style={{ fontSize: '1.1rem', marginBottom: '12px' }}>Your Personalized Schedule</h2>
          {schedule.map(item => (
            <div
              key={item.sessionId}
              style={{
                backgroundColor: '#1e293b',
                padding: '12px 16px',
                borderRadius: '8px',
                marginBottom: '10px',
                borderLeft: item.isRelocated ? '4px solid #f59e0b' : '4px solid #3b82f6',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <strong style={{ fontSize: '0.95rem' }}>{item.title}</strong>
                {item.isRelocated && (
                  <span style={{ fontSize: '0.75rem', background: '#78350f', color: '#fde68a', padding: '2px 6px', borderRadius: '4px' }}>
                    Relocated
                  </span>
                )}
              </div>
              <div style={{ fontSize: '0.85rem', color: '#cbd5e1', marginTop: '6px' }}>
                📍 {item.venueName} · 🕒 {item.timeWindow}
              </div>
              <div style={{ marginTop: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.8rem', color: item.checkedIn ? '#4ade80' : '#94a3b8' }}>
                  {item.checkedIn ? '✓ Checked In' : 'Not Checked In'}
                </span>
                {!item.checkedIn && (
                  <button
                    onClick={() => handleSimulateCheckIn(item.sessionId)}
                    style={{
                      padding: '4px 10px',
                      backgroundColor: '#3b82f6',
                      color: '#fff',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '0.8rem',
                    }}
                  >
                    Quick Check-In
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Notices View */}
      {activeTab === 'notices' && (
        <div>
          <h2 style={{ fontSize: '1.1rem', marginBottom: '12px' }}>Operational Alerts & Venue Updates</h2>
          {notices.map(notice => (
            <div
              key={notice.noticeId}
              style={{
                backgroundColor: '#1e293b',
                padding: '14px',
                borderRadius: '8px',
                marginBottom: '12px',
                border: '1px solid #475569',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', color: '#f59e0b', fontWeight: 600, fontSize: '0.9rem' }}>
                <span>⚠️ {notice.sessionTitle}</span>
                <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{notice.timestamp}</span>
              </div>
              <div style={{ fontSize: '0.85rem', marginTop: '8px', lineHeight: '1.4' }}>
                <div><strong>Previous Venue:</strong> {notice.oldVenue}</div>
                <div><strong>New Venue:</strong> {notice.newVenue}</div>
                <div><strong>Effective Time:</strong> {notice.effectiveTime}</div>
                <div style={{ marginTop: '6px', color: '#38bdf8' }}><strong>Action:</strong> {notice.actionRequired}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* QR Pass View */}
      {activeTab === 'pass' && (
        <div style={{ textAlign: 'center', backgroundColor: '#1e293b', padding: '24px', borderRadius: '12px' }}>
          <h2 style={{ fontSize: '1.1rem', margin: '0 0 12px' }}>Participant Digital Pass</h2>
          <div style={{ background: '#fff', width: '180px', height: '180px', margin: '0 auto 16px', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#000', fontWeight: 'bold' }}>
            [QR CODE: part_001]
          </div>
          <div style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
            ID: <code style={{ color: '#38bdf8' }}>part_op_001</code>
          </div>
          <div style={{ fontSize: '0.8rem', color: '#cbd5e1', marginTop: '8px' }}>
            Offline Queued Scans: <strong>{queuedCount}</strong>
          </div>
        </div>
      )}
    </div>
  );
};
