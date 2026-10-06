import { HttpInterceptorFn, HttpRequest, HttpHandlerFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

export const authInterceptor: HttpInterceptorFn = (req: HttpRequest<unknown>, next: HttpHandlerFn) => {
  const authService = inject(AuthService);
  const token = authService.accessToken();
  const tenantId = authService.getTenantId();

  let headers = req.headers;

  const isPublicAuthOrTenantList = req.url.includes('/api/tenants/public/') || req.url.includes('/api/auth/login/');

  if (token && !isPublicAuthOrTenantList) {
    headers = headers.set('Authorization', `Bearer ${token}`);
  }

  if (tenantId) {
    headers = headers.set('X-Tenant-ID', tenantId);
  }

  const authReq = req.clone({ headers });
  return next(authReq).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401 && !isPublicAuthOrTenantList) {
        authService.clearSession();
      }
      return throwError(() => error);
    })
  );
};
