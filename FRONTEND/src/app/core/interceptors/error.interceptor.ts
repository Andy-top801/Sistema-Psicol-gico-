import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { AuthService } from '../../services/auth.service';

/**
 * Ante un 401 (token vencido/ inválido) cierra la sesión y manda al login.
 * No intercepta el propio endpoint de login para no ocultar el error de
 * credenciales.
 */
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const router = inject(Router);
  return next(req).pipe(
    catchError((err: HttpErrorResponse) => {
      const isAuthCall = req.url.includes('/auth/login') || req.url.includes('/auth/refresh');
      if (err.status === 401 && !isAuthCall) {
        auth.logout();
        router.navigate(['/login']);
      }
      return throwError(() => err);
    })
  );
};
