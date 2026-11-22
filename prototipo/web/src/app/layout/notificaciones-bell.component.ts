/**
 * ═══════════════════════════════════════════════════════════════════════════
 * CU12 / HU-43 — IU_CentroNotificaciones (Web)
 * Recepción de recordatorios automáticos de citas y notificaciones push (FCM).
 *
 *  Paciente:
 *    (a) Al iniciar sesión registra el token del navegador en comunicacion_tokenfcm.
 *    (b) Recibe los avisos 'Recordatorio de Consulta' (24 h y 1 h antes de la cita
 *        confirmada) como notificación emergente del navegador + toast + campanita.
 *    (c) Al presionar la notificación navega al detalle de la cita o a la teleconsulta.
 *  Personal del centro:
 *    Bitácora del despacho (ENVIADO / PENDIENTE / FALLIDO) y ejecución manual
 *    del Mensaje 1 "ejecutar_despacho_recordatorios()".
 * ═══════════════════════════════════════════════════════════════════════════
 */
import { Component, HostListener, OnDestroy, OnInit, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AgendaService, NotificacionCita, NotificacionesResponse, ResumenDespacho } from '../core/services/agenda.service';
import { AuthService } from '../core/services/auth.service';

const TOKEN_KEY = 'sigepsi_fcm_web_token';
const POLL_MS = 30000;

@Component({
  selector: 'app-notificaciones-bell',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="bell-wrap">
      <button type="button" class="bell-btn" [class.active]="abierto()" (click)="toggle($event)"
              [attr.aria-label]="'Notificaciones' + (badge() ? ', ' + badge() + ' nuevas' : '')"
              title="Centro de Notificaciones (CU12)">
        <i class="fa-solid fa-bell" [class.ring]="animarCampana()"></i>
        <span class="bell-badge" *ngIf="badge() > 0">{{ badge() > 9 ? '9+' : badge() }}</span>
      </button>

      <!-- ═══ PANEL DESPLEGABLE ═══ -->
      <div class="panel" *ngIf="abierto()" (click)="$event.stopPropagation()" role="dialog" aria-label="Centro de Notificaciones">
        <div class="panel-head">
          <div class="head-icon"><i class="fa-solid fa-bell"></i></div>
          <div class="head-text">
            <h3>Centro de Notificaciones</h3>
            <p>Recordatorios automáticos de citas · CU12</p>
          </div>
          <button *ngIf="esPaciente() && noLeidas() > 0" class="link-btn" (click)="leerTodas()">
            <i class="fa-solid fa-check-double"></i> Marcar leídas
          </button>
        </div>

        <!-- ─── Vista PERSONAL: estado del despacho ─── -->
        <ng-container *ngIf="!esPaciente()">
          <div class="stats">
            <div class="stat ok">
              <span class="stat-num">{{ resumen().enviadas_24h ?? 0 }}</span>
              <span class="stat-lbl"><i class="fa-solid fa-paper-plane"></i> Enviados 24 h</span>
            </div>
            <div class="stat wait">
              <span class="stat-num">{{ resumen().pendientes ?? 0 }}</span>
              <span class="stat-lbl"><i class="fa-regular fa-clock"></i> Pendientes</span>
            </div>
            <div class="stat bad">
              <span class="stat-num">{{ resumen().fallidas ?? 0 }}</span>
              <span class="stat-lbl"><i class="fa-solid fa-triangle-exclamation"></i> Fallidos</span>
            </div>
          </div>

          <div class="dispatch-bar">
            <button class="btn-dispatch" (click)="despachar()" [disabled]="despachando()">
              <i class="fa-solid" [ngClass]="despachando() ? 'fa-spinner fa-spin' : 'fa-satellite-dish'"></i>
              {{ despachando() ? 'Despachando…' : 'Ejecutar despacho ahora' }}
            </button>
            <span class="auto-hint"><i class="fa-solid fa-rotate"></i> Automático: 24 h y 1 h antes</span>
          </div>

          <div class="dispatch-result" *ngIf="ultimoDespacho() as r">
            <i class="fa-solid fa-circle-check"></i>
            <span>
              <strong>{{ r.total_enviadas }}</strong> enviado(s),
              <strong>{{ r.total_fallidas }}</strong> fallido(s) de {{ r.total_evaluadas }} evaluado(s)
            </span>
            <span class="mode-pill">FCM {{ r.modo_fcm === 'REAL' ? 'real' : 'sandbox' }}</span>
          </div>
        </ng-container>

        <!-- ─── LISTA ─── -->
        <div class="list">
          <div class="loading" *ngIf="cargando() && !items().length">
            <i class="fa-solid fa-spinner fa-spin"></i> Cargando notificaciones…
          </div>

          <div class="empty" *ngIf="!cargando() && !items().length">
            <div class="empty-icon"><i class="fa-regular fa-bell-slash"></i></div>
            <strong>{{ esPaciente() ? 'No tienes notificaciones' : 'Aún no hay recordatorios despachados' }}</strong>
            <span>
              {{ esPaciente()
                ? 'Te avisaremos 24 h y 1 h antes de cada cita confirmada.'
                : 'Las citas CONFIRMADAS generan recordatorios 24 h y 1 h antes de su inicio.' }}
            </span>
          </div>

          <!-- Paciente: notificaciones recibidas -->
          <ng-container *ngIf="esPaciente()">
            <button type="button" class="item" *ngFor="let n of items(); trackBy: trackId"
                    [class.unread]="!n.leida" (click)="abrir(n)">
              <span class="item-icon" [ngClass]="claseIcono(n)"><i class="fa-solid" [ngClass]="icono(n)"></i></span>
              <span class="item-body">
                <span class="item-top">
                  <span class="item-title">{{ n.titulo }}</span>
                  <span class="item-time">{{ haceCuanto(n.fecha_envio) }}</span>
                </span>
                <span class="item-text">{{ n.cuerpo }}</span>
                <span class="chips">
                  <span class="chip" [ngClass]="n.tipo_evento === 'RECORDATORIO_1H' ? 'chip-amber' : 'chip-green'">
                    {{ n.tipo_evento === 'RECORDATORIO_1H' ? 'En 1 hora' : '24 h antes' }}
                  </span>
                  <span class="chip chip-soft">
                    <i class="fa-solid" [ngClass]="n.modalidad === 'VIRTUAL' ? 'fa-video' : 'fa-location-dot'"></i>
                    {{ n.modalidad === 'VIRTUAL' ? 'Teleconsulta' : 'Presencial' }}
                  </span>
                  <span class="chip-go">{{ n.modalidad === 'VIRTUAL' && salaHabilitada(n) ? 'Unirse' : 'Ver cita' }} <i class="fa-solid fa-arrow-right"></i></span>
                </span>
              </span>
              <span class="dot" *ngIf="!n.leida"></span>
            </button>
          </ng-container>

          <!-- Personal: bitácora de despacho -->
          <ng-container *ngIf="!esPaciente()">
            <div class="item log" *ngFor="let n of items(); trackBy: trackId" (click)="abrir(n)">
              <span class="item-icon" [ngClass]="claseIcono(n)"><i class="fa-solid" [ngClass]="icono(n)"></i></span>
              <span class="item-body">
                <span class="item-top">
                  <span class="item-title">{{ n.paciente_nombre }}</span>
                  <span class="estado" [ngClass]="'estado-' + n.estado.toLowerCase()">{{ etiquetaEstado(n.estado) }}</span>
                </span>
                <span class="item-text">
                  {{ n.tipo_evento === 'RECORDATORIO_1H' ? 'Recordatorio 1 h' : 'Recordatorio 24 h' }} ·
                  Cita {{ n.fecha_cita | date:'dd/MM' }} {{ n.hora_cita }} ·
                  {{ n.modalidad === 'VIRTUAL' ? 'Teleconsulta' : 'Presencial' }} · {{ n.psicologo_nombre }}
                </span>
                <span class="item-error" *ngIf="n.estado === 'FALLIDO' && n.error_log">
                  <i class="fa-solid fa-circle-info"></i> {{ n.error_log }} (intento {{ n.intentos_entrega }}/3)
                </span>
                <span class="item-meta" *ngIf="n.fecha_envio">
                  <i class="fa-regular fa-clock"></i> Enviado {{ haceCuanto(n.fecha_envio) }}
                </span>
              </span>
            </div>
          </ng-container>
        </div>

        <div class="panel-foot" *ngIf="esPaciente()">
          <i class="fa-solid" [ngClass]="permisoNavegador() === 'granted' ? 'fa-circle-check ok' : 'fa-circle-info'"></i>
          <span *ngIf="permisoNavegador() === 'granted'">Este navegador recibe tus recordatorios.</span>
          <span *ngIf="permisoNavegador() !== 'granted'">
            Activa las alertas del navegador para recibir avisos emergentes.
            <button class="link-btn" *ngIf="permisoNavegador() === 'default'" (click)="pedirPermiso()">Activar</button>
          </span>
        </div>
      </div>
    </div>

    <!-- ═══ TOAST tipo push (llegada de una nueva notificación) ═══ -->
    <div class="toast" *ngIf="toast() as t" (click)="abrir(t); toast.set(null)" role="alert">
      <span class="toast-logo">Ψ</span>
      <span class="toast-body">
        <span class="toast-app">SIGEPSI · ahora</span>
        <strong>{{ t.titulo }}</strong>
        <span>{{ t.cuerpo }}</span>
      </span>
      <button class="toast-x" (click)="$event.stopPropagation(); toast.set(null)" aria-label="Cerrar">
        <i class="fa-solid fa-xmark"></i>
      </button>
    </div>
  `,
  styles: [`
    :host { position: relative; display: inline-flex; }
    .bell-wrap { position: relative; }

    .bell-btn {
      position: relative; width: 40px; height: 40px; border-radius: 12px;
      border: 1px solid var(--border-light); background: #fff; color: var(--text-main);
      display: inline-flex; align-items: center; justify-content: center; font-size: 1.05rem;
      cursor: pointer; box-shadow: var(--shadow-sm); transition: var(--transition);
    }
    .bell-btn:hover, .bell-btn.active { border-color: var(--primary); color: var(--primary); background: var(--primary-light); }
    .bell-btn:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
    .bell-badge {
      position: absolute; top: -6px; right: -6px; min-width: 20px; height: 20px; padding: 0 5px;
      border-radius: 10px; background: var(--danger); color: #fff; font-size: 0.7rem; font-weight: 800;
      display: flex; align-items: center; justify-content: center; border: 2px solid #fff;
    }
    .ring { animation: ring 0.9s ease-in-out 2; transform-origin: 50% 0; }
    @keyframes ring {
      0%,100% { transform: rotate(0); } 15% { transform: rotate(16deg); } 30% { transform: rotate(-14deg); }
      45% { transform: rotate(10deg); } 60% { transform: rotate(-8deg); } 75% { transform: rotate(4deg); }
    }

    .panel {
      position: absolute; top: calc(100% + 12px); right: 0; width: 420px; max-width: calc(100vw - 24px);
      max-height: min(640px, calc(100vh - 100px)); display: flex; flex-direction: column;
      background: #fff; border: 1px solid var(--border-light); border-radius: 18px;
      box-shadow: 0 24px 60px -12px rgba(15, 41, 34, 0.28); overflow: hidden; z-index: 200;
      animation: drop 0.18s ease-out;
    }
    @keyframes drop { from { opacity: 0; transform: translateY(-6px); } to { opacity: 1; transform: none; } }

    .panel-head {
      display: flex; align-items: center; gap: 12px; padding: 16px 18px;
      background: linear-gradient(135deg, #0f2922 0%, #19734e 100%); color: #fff;
    }
    .head-icon {
      width: 38px; height: 38px; border-radius: 11px; background: rgba(255,255,255,0.14);
      display: flex; align-items: center; justify-content: center; flex-shrink: 0;
    }
    .head-text { flex: 1; min-width: 0; }
    .head-text h3 { margin: 0; font-size: 1rem; font-weight: 700; color: #fff; }
    .head-text p { margin: 2px 0 0; font-size: 0.76rem; color: #b6dccb; }
    .panel-head .link-btn { color: #d6f5e6; }

    .link-btn {
      background: none; border: none; color: var(--primary); font-weight: 700; font-size: 0.78rem;
      cursor: pointer; padding: 4px 6px; border-radius: 6px; white-space: nowrap;
    }
    .link-btn:hover { text-decoration: underline; }

    .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; padding: 14px 16px 6px; }
    .stat { border-radius: 12px; padding: 10px; display: flex; flex-direction: column; gap: 2px; border: 1px solid transparent; }
    .stat-num { font-size: 1.35rem; font-weight: 800; line-height: 1.1; }
    .stat-lbl { font-size: 0.7rem; font-weight: 600; display: flex; gap: 4px; align-items: center; }
    .stat.ok { background: var(--success-bg); color: #166534; border-color: #bbe5cc; }
    .stat.wait { background: #f1f5f3; color: var(--text-muted); border-color: var(--border-light); }
    .stat.bad { background: var(--danger-bg); color: #991b1b; border-color: #fbc7c7; }

    .dispatch-bar { display: flex; align-items: center; gap: 10px; padding: 8px 16px; flex-wrap: wrap; }
    .btn-dispatch {
      display: inline-flex; align-items: center; gap: 8px; border: none; cursor: pointer;
      background: var(--primary); color: #fff; font-weight: 700; font-size: 0.82rem;
      padding: 9px 14px; border-radius: 10px; box-shadow: 0 4px 12px var(--primary-glow); transition: var(--transition);
    }
    .btn-dispatch:hover:not(:disabled) { background: var(--primary-hover); }
    .btn-dispatch:disabled { opacity: 0.7; cursor: wait; }
    .auto-hint { font-size: 0.74rem; color: var(--text-dim); display: inline-flex; gap: 5px; align-items: center; }
    .dispatch-result {
      margin: 4px 16px 6px; padding: 9px 12px; border-radius: 10px; background: var(--accent-light);
      border: 1px solid #c4ecd9; color: #14532d; font-size: 0.8rem; display: flex; gap: 8px; align-items: center;
    }
    .mode-pill {
      margin-left: auto; font-size: 0.66rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.04em;
      background: #fff; border: 1px solid #c4ecd9; padding: 2px 7px; border-radius: 20px; white-space: nowrap;
    }

    .list { overflow-y: auto; padding: 8px; flex: 1; }
    .loading, .empty {
      display: flex; flex-direction: column; align-items: center; gap: 6px; text-align: center;
      padding: 32px 20px; color: var(--text-muted); font-size: 0.84rem;
    }
    .empty strong { color: var(--text-main); font-size: 0.92rem; }
    .empty-icon {
      width: 54px; height: 54px; border-radius: 50%; background: var(--primary-light); color: var(--primary);
      display: flex; align-items: center; justify-content: center; font-size: 1.3rem; margin-bottom: 4px;
    }

    .item {
      width: 100%; text-align: left; font: inherit; color: inherit; background: none; border: none;
      display: flex; gap: 12px; padding: 12px; border-radius: 12px; cursor: pointer; position: relative;
      transition: background 0.15s;
    }
    .item + .item { margin-top: 2px; }
    .item:hover { background: var(--bg-card-hover); }
    .item.unread { background: #f1faf5; }
    .item.unread:hover { background: #e7f6ee; }
    .item:focus-visible { outline: 2px solid var(--primary); outline-offset: -2px; }
    .item-icon {
      width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center;
      flex-shrink: 0; font-size: 0.98rem;
    }
    .ic-green { background: var(--success-bg); color: var(--primary); }
    .ic-amber { background: var(--warning-bg); color: var(--warning); }
    .ic-blue { background: var(--info-bg); color: var(--info); }
    .ic-red { background: var(--danger-bg); color: var(--danger); }
    .item-body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 4px; }
    .item-top { display: flex; align-items: baseline; gap: 8px; }
    .item-title { font-weight: 700; font-size: 0.88rem; color: var(--text-main); flex: 1; min-width: 0; }
    .item-time { font-size: 0.72rem; color: var(--text-dim); white-space: nowrap; }
    .item-text { font-size: 0.81rem; color: var(--text-body); line-height: 1.4; }
    .item-meta { font-size: 0.72rem; color: var(--text-dim); display: flex; gap: 5px; align-items: center; }
    .item-error { font-size: 0.74rem; color: #991b1b; display: flex; gap: 5px; align-items: flex-start; }
    .dot { position: absolute; top: 16px; right: 12px; width: 8px; height: 8px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 0 3px #d5f3e4; }
    .item.unread .item-top { padding-right: 14px; }

    .chips { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; margin-top: 2px; }
    .chip { font-size: 0.69rem; font-weight: 700; padding: 3px 8px; border-radius: 20px; display: inline-flex; gap: 4px; align-items: center; }
    .chip-green { background: var(--success-bg); color: #166534; }
    .chip-amber { background: var(--warning-bg); color: #9a5b06; }
    .chip-soft { background: #f1f5f3; color: var(--text-muted); }
    .chip-go { margin-left: auto; font-size: 0.74rem; font-weight: 700; color: var(--primary); display: inline-flex; gap: 4px; align-items: center; }

    .estado { font-size: 0.66rem; font-weight: 800; padding: 3px 8px; border-radius: 20px; letter-spacing: 0.03em; white-space: nowrap; }
    .estado-enviado { background: var(--success-bg); color: #166534; }
    .estado-pendiente { background: #f1f5f3; color: var(--text-muted); }
    .estado-fallido { background: var(--danger-bg); color: #991b1b; }

    .panel-foot {
      border-top: 1px solid var(--border-light); padding: 10px 16px; font-size: 0.76rem; color: var(--text-muted);
      display: flex; gap: 8px; align-items: center; background: #fafcfb;
    }
    .panel-foot .ok { color: var(--success); }

    .toast {
      position: fixed; top: 18px; right: 18px; z-index: 1000; width: 360px; max-width: calc(100vw - 24px);
      display: flex; gap: 12px; align-items: flex-start; padding: 14px; cursor: pointer;
      background: rgba(255,255,255,0.97); backdrop-filter: blur(12px); border: 1px solid var(--border-light);
      border-left: 4px solid var(--accent); border-radius: 14px; box-shadow: 0 18px 44px -10px rgba(15,41,34,0.35);
      animation: slideIn 0.3s cubic-bezier(0.2, 0.9, 0.3, 1.2);
    }
    @keyframes slideIn { from { opacity: 0; transform: translateX(40px); } to { opacity: 1; transform: none; } }
    .toast-logo {
      width: 36px; height: 36px; border-radius: 10px; flex-shrink: 0; background: var(--primary); color: #fff;
      display: flex; align-items: center; justify-content: center; font-weight: 800;
    }
    .toast-body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; font-size: 0.8rem; color: var(--text-body); }
    .toast-body strong { color: var(--text-main); font-size: 0.88rem; }
    .toast-app { font-size: 0.68rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; }
    .toast-x { background: none; border: none; color: var(--text-dim); cursor: pointer; padding: 2px; }

    @media (max-width: 640px) {
      .panel { position: fixed; top: 64px; left: 12px; right: 12px; width: auto; max-width: none; }
      .toast { left: 12px; right: 12px; width: auto; }
    }
  `]
})
export class NotificacionesBellComponent implements OnInit, OnDestroy {
  abierto = signal(false);
  cargando = signal(false);
  despachando = signal(false);
  animarCampana = signal(false);
  items = signal<NotificacionCita[]>([]);
  resumen = signal<NotificacionesResponse['resumen']>({});
  ultimoDespacho = signal<ResumenDespacho | null>(null);
  toast = signal<NotificacionCita | null>(null);
  permisoNavegador = signal<NotificationPermission | 'unsupported'>(
    typeof Notification !== 'undefined' ? Notification.permission : 'unsupported'
  );

  esPaciente = computed(() => this.authService.isPaciente());
  noLeidas = computed(() => this.resumen().no_leidas ?? 0);
  badge = computed(() => this.esPaciente() ? this.noLeidas() : (this.resumen().enviadas_24h ?? 0));

  private timer: any;
  private toastTimer: any;
  private idsConocidos: Set<string> | null = null;

  constructor(
    private agendaService: AgendaService,
    public authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    if (this.esPaciente()) this.registrarDispositivo();
    this.cargar();
    this.timer = setInterval(() => this.cargar(), POLL_MS);
  }

  ngOnDestroy(): void {
    clearInterval(this.timer);
    clearTimeout(this.toastTimer);
  }

  @HostListener('document:click')
  cerrarAlClickFuera() { this.abierto.set(false); }

  @HostListener('document:keydown.escape')
  cerrarConEsc() { this.abierto.set(false); }

  toggle(ev: Event) {
    ev.stopPropagation();
    this.abierto.update(v => !v);
    if (this.abierto()) this.cargar();
  }

  /** Criterio (a): token del navegador registrado en comunicacion_tokenfcm (plataforma WEB). */
  private registrarDispositivo() {
    let token: string | null = null;
    try { token = localStorage.getItem(TOKEN_KEY); } catch {}
    if (!token) {
      const rnd = (crypto as any)?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(36).slice(2)}`;
      token = `web-sandbox-${rnd}`;
      try { localStorage.setItem(TOKEN_KEY, token); } catch {}
    }
    this.agendaService.registrarTokenFCM(token, 'WEB').subscribe({ error: () => {} });
  }

  cargar() {
    this.cargando.set(true);
    this.agendaService.getNotificaciones().subscribe({
      next: (res) => {
        this.cargando.set(false);
        this.detectarNuevas(res.resultados);
        this.items.set(res.resultados);
        this.resumen.set(res.resumen);
      },
      error: () => this.cargando.set(false)
    });
  }

  /** Criterio (b): una notificación recién llegada se muestra como push emergente. */
  private detectarNuevas(lista: NotificacionCita[]) {
    const ids = new Set(lista.map(n => n.id));
    if (this.idsConocidos && this.esPaciente()) {
      const nuevas = lista.filter(n => !this.idsConocidos!.has(n.id) && !n.leida);
      if (nuevas.length) {
        this.mostrarPush(nuevas[0]);
        this.animarCampana.set(true);
        setTimeout(() => this.animarCampana.set(false), 1900);
      }
    }
    this.idsConocidos = ids;
  }

  private mostrarPush(n: NotificacionCita) {
    this.toast.set(n);
    clearTimeout(this.toastTimer);
    this.toastTimer = setTimeout(() => this.toast.set(null), 9000);

    if (this.permisoNavegador() === 'granted') {
      try {
        const nativa = new Notification(n.titulo, { body: n.cuerpo, tag: n.id, icon: '/favicon.ico' });
        nativa.onclick = () => { window.focus(); this.abrir(n); nativa.close(); };
      } catch {}
    }
  }

  pedirPermiso() {
    if (typeof Notification === 'undefined') return;
    Notification.requestPermission().then(p => this.permisoNavegador.set(p));
  }

  /** Criterio (c): abre la teleconsulta (VIRTUAL) o el detalle de la cita (PRESENCIAL). */
  abrir(n: NotificacionCita) {
    this.abierto.set(false);
    if (this.esPaciente() && !n.leida) {
      n.leida = true;
      this.resumen.update(r => ({ ...r, no_leidas: Math.max(0, (r.no_leidas ?? 1) - 1) }));
      this.agendaService.marcarNotificacionLeida(n.id).subscribe({ error: () => {} });
    }
    if (n.modalidad === 'VIRTUAL' && this.esPaciente() && this.salaHabilitada(n)) {
      this.router.navigate(['/teleconsulta', n.cita_id]);
    } else {
      this.router.navigate(['/agenda'], { queryParams: { cita: n.cita_id } });
    }
  }

  /** Regla CU13: la sala Jitsi se habilita 10 min antes del inicio de la cita. */
  salaHabilitada(n: NotificacionCita): boolean {
    const inicio = new Date(`${n.fecha_cita}T${n.hora_cita}:00`).getTime();
    return !isNaN(inicio) && Date.now() >= inicio - 10 * 60 * 1000;
  }

  leerTodas() {
    this.agendaService.marcarTodasLeidas().subscribe(() => {
      this.items.update(l => l.map(n => ({ ...n, leida: true })));
      this.resumen.update(r => ({ ...r, no_leidas: 0 }));
    });
  }

  despachar() {
    this.despachando.set(true);
    this.agendaService.ejecutarDespachoRecordatorios().subscribe({
      next: (r) => { this.ultimoDespacho.set(r); this.despachando.set(false); this.cargar(); },
      error: () => this.despachando.set(false)
    });
  }

  icono(n: NotificacionCita): string {
    if (n.estado === 'FALLIDO') return 'fa-triangle-exclamation';
    if (n.modalidad === 'VIRTUAL') return 'fa-video';
    return n.tipo_evento === 'RECORDATORIO_1H' ? 'fa-hourglass-half' : 'fa-calendar-check';
  }

  claseIcono(n: NotificacionCita): string {
    if (n.estado === 'FALLIDO') return 'ic-red';
    if (n.modalidad === 'VIRTUAL') return 'ic-blue';
    return n.tipo_evento === 'RECORDATORIO_1H' ? 'ic-amber' : 'ic-green';
  }

  etiquetaEstado(e: string): string {
    return e === 'ENVIADO' ? 'Enviado' : e === 'FALLIDO' ? 'Fallido' : 'Pendiente';
  }

  haceCuanto(iso: string | null): string {
    if (!iso) return '';
    const seg = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
    if (seg < 60) return 'ahora';
    if (seg < 3600) return `hace ${Math.floor(seg / 60)} min`;
    if (seg < 86400) return `hace ${Math.floor(seg / 3600)} h`;
    return `hace ${Math.floor(seg / 86400)} d`;
  }

  trackId = (_: number, n: NotificacionCita) => n.id;
}
