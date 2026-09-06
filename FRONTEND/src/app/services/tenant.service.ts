import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class TenantService {
  private apiUrl = 'http://localhost:8000/api/tenants/';

  constructor(private http: HttpClient) { }

  getTenants(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl);
  }

  createTenant(data: any): Observable<any> {
    return this.http.post<any>(this.apiUrl, data);
  }
}
