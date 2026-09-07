import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { CentroConfig } from '../models';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class CentroService {
  private apiUrl = `${environment.apiUrl}/centro/config/`;

  constructor(private http: HttpClient) {}

  getConfig(): Observable<CentroConfig> {
    return this.http.get<CentroConfig>(this.apiUrl);
  }

  updateConfig(data: Partial<CentroConfig>): Observable<any> {
    return this.http.put(this.apiUrl, data);
  }
}
