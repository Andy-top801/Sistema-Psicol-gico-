import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { apiUrl, API } from '../core/api';
import { Paged, unwrap } from '../core/models/paged.model';

@Injectable({ providedIn: 'root' })
export class RoleService {
  private rolesUrl = apiUrl(API.roles);
  private permisosUrl = apiUrl(API.permisos);

  constructor(private http: HttpClient) {}

  getRoles(): Observable<any[]> {
    return this.http.get<any[] | Paged<any>>(this.rolesUrl).pipe(unwrap<any>());
  }

  getRole(id: string): Observable<any> {
    return this.http.get<any>(`${this.rolesUrl}${id}/`);
  }

  createRole(role: any): Observable<any> {
    return this.http.post<any>(this.rolesUrl, role);
  }

  getPermisos(): Observable<any[]> {
    return this.http
      .get<any[] | Paged<any>>(this.permisosUrl)
      .pipe(unwrap<any>());
  }
}
