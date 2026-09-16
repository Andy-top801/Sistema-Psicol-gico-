export interface AuditEvent {
  timestamp: string;
  ip: string | null;
  user_id: string | null;
  user: string;
  tenant: string | null;
  method: string;
  path: string;
  action: string;
  status_code: number;
  error: string | null;
}
