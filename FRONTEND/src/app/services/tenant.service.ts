import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { apiUrl, API } from '../core/api';
import { Paged, unwrap } from '../core/models/paged.model';

@Injectable({ providedIn: 'root' })
export class TenantService {
  private base = apiUrl(API.tenants);

  constructor(private http: HttpClient) {}

  getTenants(): Observable<any[]> {
    return this.http.get<any[] | Paged<any>>(this.base).pipe(unwrap<any>());
  }

  getTenant(id: number | string): Observable<any> {
    return this.http.get<any>(`${this.base}${id}/`);
  }

  createTenant(data: any): Observable<any> {
    return this.http.post<any>(this.base, data);
  }

  updateTenant(id: number | string, data: any): Observable<any> {
    return this.http.put<any>(`${this.base}${id}/`, data);
  }

  patchTenant(id: number | string, data: any): Observable<any> {
    return this.http.patch<any>(`${this.base}${id}/`, data);
  }

  deleteTenant(id: number | string): Observable<any> {
    return this.http.delete<any>(`${this.base}${id}/`);
  }
}
