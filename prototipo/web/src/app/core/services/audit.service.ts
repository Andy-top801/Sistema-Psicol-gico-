import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { AuditEvent } from '../models';

@Injectable({ providedIn: 'root' })
export class AuditService {
  private readonly apiUrl = `${environment.apiUrl}/audit/logs/`;

  constructor(private http: HttpClient) {}

  getLogs(date = '', tenant = ''): Observable<AuditEvent[]> {
    let params = new HttpParams();
    if (date) params = params.set('date', date);
    if (tenant.trim()) params = params.set('tenant', tenant.trim());
    return this.http.get<AuditEvent[]>(this.apiUrl, { params });
  }
}
