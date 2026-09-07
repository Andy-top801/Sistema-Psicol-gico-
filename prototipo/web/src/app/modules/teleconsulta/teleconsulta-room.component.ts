import { Component, OnInit, OnDestroy, ElementRef, ViewChild, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { AgendaService } from '../../core/services/agenda.service';
import { TeleconsultaAccess } from '../../core/models';

declare const JitsiMeetExternalAPI: any;

@Component({
  selector: 'app-teleconsulta-room',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="teleconsulta-container">
      <!-- Barra Superior de la Videoconsulta -->
      <div class="teleconsulta-header glass-panel">
        <div class="room-info">
          <div class="live-dot"></div>
          <div>
            <h2 class="room-title">
              <i class="fa-solid fa-video text-primary"></i> Sala de Teleconsulta Clínica
            </h2>
            <p class="room-subtitle" *ngIf="accessData">
              Sesión con <strong>{{ accessData.display_name }}</strong> &bull; Sala: <code>{{ accessData.room_name }}</code>
              <span *ngIf="accessData.is_moderator" class="badge badge-warning ms-2">
                <i class="fa-solid fa-crown"></i> Moderador (Psicólogo)
              </span>
            </p>
          </div>
        </div>

        <div class="header-controls">
          <!-- Cronómetro de la Sesión -->
          <div class="timer-badge">
            <i class="fa-solid fa-stopwatch text-primary"></i>
            <span class="timer-display">{{ tiempoFormateado }}</span>
          </div>

          <!-- Botón de Salir / Finalizar -->
          <button class="btn btn-danger btn-sm" (click)="finalizarSesion()" [disabled]="finalizando">
            <i class="fa-solid fa-phone-slash"></i>
            {{ finalizando ? 'Cerrando...' : (accessData?.is_moderator ? 'Finalizar Consulta' : 'Salir de la Sala') }}
          </button>
        </div>
      </div>

      <!-- Contenedor del Iframe de Jitsi Meet -->
      <div class="video-wrapper glass-panel">
        <div *ngIf="cargando" class="loading-overlay">
          <i class="fa-solid fa-spinner fa-spin fa-3x text-primary mb-3"></i>
          <h3>Estableciendo conexión WebRTC cifrada...</h3>
          <p class="text-muted">Obteniendo token de acceso y conectando con el cluster Jitsi Meet.</p>
        </div>

        <div *ngIf="errorMsg" class="error-overlay">
          <i class="fa-solid fa-triangle-exclamation fa-3x text-danger mb-3"></i>
          <h3>Error al conectar a la Teleconsulta</h3>
          <p class="text-muted">{{ errorMsg }}</p>
          <button class="btn btn-secondary mt-3" (click)="volverAAgenda()">
            <i class="fa-solid fa-arrow-left"></i> Volver a la Agenda
          </button>
        </div>

        <!-- Elemento ancla para el iframe Jitsi -->
        <div #jitsiContainer class="jitsi-frame-container" [hidden]="cargando || errorMsg"></div>
      </div>
    </div>
  `,
  styles: [`
    .teleconsulta-container {
      display: flex;
      flex-direction: column;
      gap: 16px;
      height: calc(100vh - 120px);
    }
    .teleconsulta-header {
      padding: 14px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-radius: 14px;
    }
    .room-info {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .live-dot {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: #ef4444;
      box-shadow: 0 0 12px #ef4444;
      animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
      0% { transform: scale(0.95); opacity: 0.8; }
      50% { transform: scale(1.2); opacity: 1; }
      100% { transform: scale(0.95); opacity: 0.8; }
    }
    .room-title {
      font-size: 1.2rem;
      font-weight: 800;
      margin: 0;
    }
    .room-subtitle {
      font-size: 0.82rem;
      color: var(--text-muted);
      margin: 2px 0 0;
    }
    .room-subtitle code {
      font-family: var(--font-mono);
      background: rgba(0,0,0,0.3);
      padding: 2px 6px;
      border-radius: 4px;
      color: #38bdf8;
    }
    .header-controls {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    .timer-badge {
      display: flex;
      align-items: center;
      gap: 8px;
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid var(--border-glass);
      padding: 6px 14px;
      border-radius: 8px;
      font-family: var(--font-mono);
      font-size: 1.05rem;
      font-weight: 700;
      color: var(--text-main);
    }
    .video-wrapper {
      flex: 1;
      position: relative;
      border-radius: 16px;
      overflow: hidden;
      display: flex;
    }
    .jitsi-frame-container {
      width: 100%;
      height: 100%;
      border: none;
      background: #000;
    }
    .loading-overlay, .error-overlay {
      position: absolute;
      top: 0; left: 0; right: 0; bottom: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: rgba(11, 15, 25, 0.95);
      z-index: 10;
      padding: 20px;
      text-align: center;
    }
    .ms-2 { margin-left: 8px; }
    .mt-3 { margin-top: 14px; }

    @media (max-width: 640px) {
      .teleconsulta-header {
        flex-direction: column;
        align-items: stretch;
        gap: 12px;
        padding: 12px;
      }
      .header-controls {
        justify-content: space-between;
      }
      .room-title {
        font-size: 1.1rem;
      }
    }
  `]
})
export class TeleconsultaRoomComponent implements OnInit, OnDestroy {
  @ViewChild('jitsiContainer', { static: false }) jitsiContainer!: ElementRef<HTMLDivElement>;

  citaId: string = '';
  accessData: TeleconsultaAccess | null = null;
  cargando = true;
  errorMsg = '';
  finalizando = false;

  // Temporizador de Videoconsulta
  segundosTranscurridos = 0;
  timerInterval: any = null;
  jitsiApi: any = null;

  get tiempoFormateado(): string {
    const hrs = Math.floor(this.segundosTranscurridos / 3600);
    const mins = Math.floor((this.segundosTranscurridos % 3600) / 60);
    const secs = this.segundosTranscurridos % 60;
    return `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  }

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private agendaService: AgendaService
  ) {}

  ngOnInit(): void {
    this.citaId = this.route.snapshot.paramMap.get('id') || '';
    if (!this.citaId) {
      this.errorMsg = 'Identificador de cita no especificado.';
      this.cargando = false;
      return;
    }

    this.conectarTeleconsultaCU13();
  }

  ngOnDestroy(): void {
    this.detenerTimer();
    if (this.jitsiApi) {
      this.jitsiApi.dispose();
    }
  }

  /**
   * ═══════════════════════════════════════════════════════════════════════════
   * CU13: Teleconsulta y Videoconferencias Jitsi Meet
   * Diagrama de Comunicación – Pasos del Flujo:
   *   Actor  → Paciente / Terapeuta
   *   IU     → IU_Teleconsulta (TeleconsultaRoomComponent)
   *   CTR    → CTR_TeleconsultaService (Django REST)
   *   CE     → CE_Teleconsulta_y_Cita (PostgreSQL)
   *   SRV    → SRV_JitsiServer (WebRTC Cluster meet.jit.si)
   * ═══════════════════════════════════════════════════════════════════════════
   */
  conectarTeleconsultaCU13(): void {
    // --- Paso 1: Actor ingresa y hace clic en 'Unirse a Videoconsulta' en IU_Teleconsulta ---
    this.cargando = true;

    // --- Paso 2: GET /api/agenda/teleconsulta/{cita_id}/access/ + Bearer JWT ---
    this.agendaService.getTeleconsultaAccess(this.citaId).subscribe({
      // --- Paso 7: 200 OK {room_name, jwt_token, domain, is_moderator} ---
      next: (access) => {
        this.accessData = access;
        this.cargarScriptJitsiYMontar(access);
      },
      error: (err) => {
        this.cargando = false;
        this.errorMsg = err.error?.error || 'No fue posible acceder a la sala de teleconsulta. Verifica el estado y horario de la cita.';
      }
    });
  }

  private cargarScriptJitsiYMontar(access: TeleconsultaAccess): void {
    if ((window as any).JitsiMeetExternalAPI) {
      this.iniciarJitsiMeet(access);
      return;
    }

    const script = document.createElement('script');
    script.src = `https://${access.domain || 'meet.jit.si'}/external_api.js`;
    script.async = true;
    script.onload = () => {
      this.iniciarJitsiMeet(access);
    };
    script.onerror = () => {
      this.cargando = false;
      this.errorMsg = 'Error al cargar la librería externa de videoconferencia Jitsi Meet.';
    };
    document.body.appendChild(script);
  }

  private iniciarJitsiMeet(access: TeleconsultaAccess): void {
    setTimeout(() => {
      if (!this.jitsiContainer) return;

      const domain = access.domain || 'meet.jit.si';
      const options: any = {
        roomName: access.room_name,
        width: '100%',
        height: '100%',
        parentNode: this.jitsiContainer.nativeElement,
        userInfo: {
          displayName: access.display_name,
          email: access.email
        },
        configOverwrite: {
          startWithAudioMuted: false,
          startWithVideoMuted: false,
          prejoinPageEnabled: false,
          disableDeepLinking: true
        },
        interfaceConfigOverwrite: {
          TOOLBAR_BUTTONS: [
            'microphone', 'camera', 'closedcaptions', 'desktop', 'fullscreen',
            'fodeviceselection', 'hangup', 'profile', 'chat', 'recording',
            'livestreaming', 'etherpad', 'sharedvideo', 'settings', 'raisehand',
            'videoquality', 'filmstrip', 'feedback', 'stats', 'shortcuts',
            'tileview', 'videobackgroundblur', 'download', 'help', 'mute-everyone'
          ],
          SHOW_JITSI_WATERMARK: false,
          SHOW_WATERMARK_FOR_GUESTS: false
        }
      };

      if (access.jwt_token) {
        options.jwt = access.jwt_token;
      }

      // --- Paso 8: IU_Teleconsulta establece conexión WebRTC con SRV_JitsiServer ---
      this.jitsiApi = new JitsiMeetExternalAPI(domain, options);

      // --- Paso 9: Flujo bidireccional de audio y video activo ---
      // --- Paso 10: Cargar sala de video interactiva en pantalla con temporizador ---
      this.cargando = false;
      this.iniciarTimer();

      this.jitsiApi.addEventListeners({
        readyToClose: () => {
          this.finalizarSesion();
        },
        videoConferenceLeft: () => {
          this.finalizarSesion();
        }
      });
    }, 100);
  }

  iniciarTimer(): void {
    this.segundosTranscurridos = 0;
    this.timerInterval = setInterval(() => {
      this.segundosTranscurridos++;
    }, 1000);
  }

  detenerTimer(): void {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
      this.timerInterval = null;
    }
  }

  finalizarSesion(): void {
    this.detenerTimer();
    this.finalizando = true;

    // Si es psicólogo, registrar fin y duración en PostgreSQL
    this.agendaService.finishTeleconsulta(this.citaId, this.segundosTranscurridos).subscribe({
      next: () => {
        this.volverAAgenda();
      },
      error: () => {
        this.volverAAgenda();
      }
    });
  }

  volverAAgenda(): void {
    this.router.navigate(['/agenda']);
  }
}
