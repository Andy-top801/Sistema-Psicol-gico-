/**
 * CU21 / HU-47 (c) — Notificación prioritaria inmediata al Coordinador Clínico.
 * Consulta /triaje/alertas/ cada 30 s, muestra cuántos casos de crisis siguen sin psicólogo
 * asignado y lanza una notificación del navegador por cada alerta nueva. Al pulsar, abre la consola.
 */
import { Component, OnDestroy, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';
import { TriajeIAService } from '../core/services/triaje-ia.service';

const POLL_MS = 30000;
const VISTAS_KEY = 'sigepsi_alertas_crisis_vistas';

@Component({
  selector: 'app-alertas-crisis-badge',
  standalone: true,
  imports: [CommonModule],
  template: `
    <button type="button" class="crisis-btn" [class.activa]="pendientes() > 0" (click)="abrirConsola()"
            [attr.aria-label]="pendientes() ? pendientes() + ' alertas de crisis sin asignar' : 'Sin alertas de crisis'"
            title="Alertas de crisis (CU21)">
      <i aria-hidden="true" class="fa-solid fa-triangle-exclamation"></i>
      <span class="crisis-badge" *ngIf="pendientes() > 0">{{ pendientes() > 9 ? '9+' : pendientes() }}</span>
    </button>
  `,
  styles: [`
    .crisis-btn {
      position: relative; width: 40px; height: 40px; border-radius: 12px;
      border: 1px solid var(--border-light, #e2e8f0); background: #fff; color: #94a3b8;
      display: inline-flex; align-items: center; justify-content: center; font-size: 1.05rem; cursor: pointer;
    }
    .crisis-btn.activa { color: #dc2626; border-color: #fca5a5; background: #fef2f2; animation: latido 1.6s infinite; }
    @media (prefers-reduced-motion: reduce) { .crisis-btn.activa { animation: none; } }
    @keyframes latido { 0%, 100% { box-shadow: 0 0 0 0 rgba(220, 38, 38, .35); } 50% { box-shadow: 0 0 0 6px rgba(220, 38, 38, 0); } }
    .crisis-badge {
      position: absolute; top: -6px; right: -6px; min-width: 20px; height: 20px; padding: 0 5px;
      border-radius: 10px; background: #dc2626; color: #fff; font-size: .7rem; font-weight: 800;
      display: flex; align-items: center; justify-content: center; border: 2px solid #fff;
    }
  `]
})
export class AlertasCrisisBadgeComponent implements OnInit, OnDestroy {
  pendientes = signal(0);
  private timer?: ReturnType<typeof setInterval>;
  private vistas = new Set<string>(this.leerVistas());

  constructor(private triaje: TriajeIAService, private router: Router) {}

  ngOnInit(): void {
    if (typeof Notification !== 'undefined' && Notification.permission === 'default') {
      Notification.requestPermission().catch(() => {});
    }
    this.consultar();
    this.timer = setInterval(() => this.consultar(), POLL_MS);
  }

  ngOnDestroy(): void {
    clearInterval(this.timer);
  }

  abrirConsola(): void {
    this.router.navigate(['/triaje-ia']);
  }

  private consultar(): void {
    this.triaje.getAlertasCrisis().subscribe({
      next: alertas => {
        const sinAsignar = alertas.filter(a => !a.psicologo_asignado_nombre);
        this.pendientes.set(sinAsignar.length);
        const nuevas = sinAsignar.filter(a => !this.vistas.has(a.id));
        nuevas.forEach(a => this.vistas.add(a.id));
        if (nuevas.length) {
          this.guardarVistas();
          this.notificar(nuevas.length, nuevas[0].paciente_nombre);
        }
      },
      error: (err: HttpErrorResponse) => {
        if (err.status === 401 || err.status === 403) clearInterval(this.timer);  // sin permiso: no insistir
      }
    });
  }

  private notificar(cantidad: number, paciente: string): void {
    if (typeof Notification === 'undefined' || Notification.permission !== 'granted') return;
    try {
      const n = new Notification('ALERTA DE CRISIS — atención prioritaria', {
        body: cantidad > 1 ? `${cantidad} casos nuevos con riesgo vital.` : `Caso nuevo con riesgo vital: ${paciente}.`,
        tag: 'sigepsi-crisis', requireInteraction: true, icon: '/favicon.ico',
      });
      n.onclick = () => { window.focus(); this.abrirConsola(); n.close(); };
    } catch {}
  }

  private leerVistas(): string[] {
    try { return JSON.parse(localStorage.getItem(VISTAS_KEY) || '[]'); } catch { return []; }
  }

  private guardarVistas(): void {
    try { localStorage.setItem(VISTAS_KEY, JSON.stringify([...this.vistas].slice(-200))); } catch {}
  }
}
