import { Injectable } from '@angular/core';

/**
 * Deriva el centro (tenant) a partir del subdominio del navegador.
 *  - `localhost` / `127.0.0.1`            → dominio público (login de superadmin)
 *  - `sanamente.localhost`               → tenant "sanamente"
 *  - `sanamente.sigepsi.app`             → tenant "sanamente"
 * El backend (django-tenants / TenantMainMiddleware) resuelve el schema por el
 * `Host`, así que aquí solo se usa para la UI (títulos, textos del login).
 */
@Injectable({ providedIn: 'root' })
export class TenantContextService {
  get hostname(): string {
    return window.location.hostname;
  }

  get subdomain(): string | null {
    const host = this.hostname;
    if (host === 'localhost' || host === '127.0.0.1' || host === '0.0.0.0') {
      return null;
    }
    const parts = host.split('.');
    if (parts.length >= 2 && parts[parts.length - 1] === 'localhost') {
      return parts[0];
    }
    // Producción: <centro>.dominio.tld  (3+ segmentos)
    return parts.length > 2 ? parts[0] : null;
  }

  get isPublicDomain(): boolean {
    return this.subdomain === null;
  }

  /** Nombre "bonito" del centro a partir del slug del subdominio. */
  get prettyName(): string {
    const sub = this.subdomain;
    if (!sub) return 'Plataforma SIGEPSI';
    return sub
      .split(/[-_]/)
      .filter(Boolean)
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(' ');
  }
}
