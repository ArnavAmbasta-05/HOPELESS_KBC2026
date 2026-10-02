import { QueuedOfflineScan } from './types';

export class OfflineScanQueueManager {
  private queueKey = 'korex_participant_offline_scans';

  public getQueue(): QueuedOfflineScan[] {
    try {
      const raw = localStorage.getItem(this.queueKey);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  }

  public enqueueScan(scan: QueuedOfflineScan): void {
    const queue = this.getQueue();
    // Dedup check in local queue
    if (!queue.some(s => s.idempotencyKey === scan.idempotencyKey)) {
      queue.push(scan);
      localStorage.setItem(this.queueKey, JSON.stringify(queue));
    }
  }

  public clearQueue(): void {
    localStorage.removeItem(this.queueKey);
  }
}
