import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { AppRole } from '../models/user.model';

/**
 * Exige que el usuario tenga al menos uno de los roles en `route.data.roles`.
 * Si no cumple, lo redirige a su pantalla de inicio según su rol.
 */
export const roleGuard: CanActivateFn = (route) => {
  const auth = inject(AuthService);
  const router = inject(Router);
  const allowed = (route.data?.['roles'] as AppRole[] | undefined) ?? [];
  if (allowed.length === 0 || auth.hasAnyRole(allowed)) return true;
  return router.createUrlTree([auth.homePathForRole()]);
};
