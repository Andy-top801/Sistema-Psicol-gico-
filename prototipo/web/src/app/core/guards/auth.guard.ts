import { inject } from '@angular/core';
import { Router, CanActivateFn, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = (route: ActivatedRouteSnapshot, state: RouterStateSnapshot) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated()) {
    return true;
  }

  router.navigate(['/login']);
  return false;
};

export const superAdminGuard: CanActivateFn = (route: ActivatedRouteSnapshot, state: RouterStateSnapshot) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated() && authService.isSuperAdmin()) {
    return true;
  }

  router.navigate(['/dashboard']);
  return false;
};

export const adminCentroGuard: CanActivateFn = (route: ActivatedRouteSnapshot, state: RouterStateSnapshot) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated() && (authService.isAdminCentro() || authService.isSuperAdmin())) {
    return true;
  }

  router.navigate(['/dashboard']);
  return false;
};

/**
 * ═══════════════════════════════════════════════════════════════════════════
 * Guard Clínico (Sprint 2 – HU-26: RBAC Clínico)
 * Permite acceso únicamente a personal clínico autorizado:
 * SuperAdmin, Admin Centro, Coordinador Clínico y Psicólogo.
 * Bloquea a Pacientes y Recepcionistas de las rutas clínicas protegidas
 * (Historias Clínicas, Notas SOAP, Derivaciones).
 * ═══════════════════════════════════════════════════════════════════════════
 */
export const clinicalStaffGuard: CanActivateFn = (route: ActivatedRouteSnapshot, state: RouterStateSnapshot) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated() && authService.canAccessHistoriasClinicas()) {
    return true;
  }

  router.navigate(['/dashboard']);
  return false;
};

/**
 * ═══════════════════════════════════════════════════════════════════════════
 * Guard que excluye a Recepcionistas (Sprint 2 – HU-29: Tareas Terapéuticas)
 * Permite acceso a todos los roles autenticados EXCEPTO Recepcionista,
 * ya que las tareas terapéuticas son exclusivas de la relación
 * Psicólogo–Paciente y supervisión administrativa.
 * ═══════════════════════════════════════════════════════════════════════════
 */
export const excludeRecepcionistaGuard: CanActivateFn = (route: ActivatedRouteSnapshot, state: RouterStateSnapshot) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated() && !authService.isRecepcionista()) {
    return true;
  }

  router.navigate(['/dashboard']);
  return false;
};
