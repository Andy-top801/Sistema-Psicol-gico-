import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { apiUrl, API } from '../core/api';
import { Paged, unwrap } from '../core/models/paged.model';

@Injectable({ providedIn: 'root' })
export class UserService {
  private base = apiUrl(API.usuarios);

  constructor(private http: HttpClient) {}

  getUsers(): Observable<any[]> {
    return this.http.get<any[] | Paged<any>>(this.base).pipe(unwrap<any>());
  }

  getUser(id: string): Observable<any> {
    return this.http.get<any>(`${this.base}${id}/`);
  }

  createUser(user: any): Observable<any> {
    return this.http.post<any>(this.base, user);
  }

  updateUser(id: string, user: any): Observable<any> {
    return this.http.put<any>(`${this.base}${id}/`, user);
  }

  patchUser(id: string, data: any): Observable<any> {
    return this.http.patch<any>(`${this.base}${id}/`, data);
  }

  deleteUser(id: string): Observable<any> {
    return this.http.delete<any>(`${this.base}${id}/`);
  }
}
