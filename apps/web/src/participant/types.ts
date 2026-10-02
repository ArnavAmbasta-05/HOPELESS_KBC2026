export interface ParticipantScheduleItem {
  sessionId: string;
  title: string;
  venueName: string;
  building: string;
  timeWindow: string;
  isRelocated: boolean;
  checkedIn: boolean;
}

export interface ParticipantNotice {
  noticeId: string;
  sessionTitle: string;
  oldVenue: string;
  newVenue: string;
  effectiveTime: string;
  actionRequired: string;
  timestamp: string;
}

export interface QueuedOfflineScan {
  scanId: string;
  token: string;
  sessionId: string;
  venueId: string;
  timestamp: string;
  idempotencyKey: string;
}
