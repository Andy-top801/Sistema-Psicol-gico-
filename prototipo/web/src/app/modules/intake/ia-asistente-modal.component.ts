// ==============================================================================
// MÓDULO: ia-asistente-modal.component.ts
// CAPA BCE: BOUNDARY (Interfaz de Usuario) — IU_AsistenteIAPreconsulta
// CASOS DE USO: HU-35 (SP2-54) Asistente Piloto de Preconsulta con IA
// DESCRIPCIÓN: Modal interactivo para visualización de reglas Romero disparadas,
//              nivel de severidad, resumen clínico sugerido y preguntas guía.
//              Garantiza la supervisión humana estricta: Aceptar, Editar o Descartar.
// ==============================================================================
import { Component, Input, Output, EventEmitter, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ClinicaSprint2Service } from '../../core/services/clinica-sprint2.service';
import { AnalisisIAResponse, ReglaDisparada, RespuestaPreConsulta } from '../../core/models/clinica-sprint2.model';

@Component({
  selector: 'app-ia-asistente-modal',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="modal-backdrop-custom" (click)="onCerrar()">
      <div class="modal-dialog-custom glass-card-modal" (click)="$event.stopPropagation()">
        
        <!-- Header del Modal -->
        <div class="modal-header-ia">
          <div class="header-left">
            <div class="ai-badge-pulse">
              <i class="fa-solid fa-brain"></i>
            </div>
            <div>
              <h2 class="modal-title">Asistente IA de Preconsulta</h2>
              <p class="modal-subtitle">
                Motor de Soporte Clínico Basado en Reglas (Dr. Romero) · Supervisión Humana Requerida
              </p>
            </div>
          </div>
          <button class="btn-close-custom" (click)="onCerrar()" title="Cerrar ventana">
            <i class="fa-solid fa-xmark"></i>
          </button>
        </div>

        <!-- Banner de Advertencia Ética y Clínica Obligatoria -->
        <div class="safety-banner">
          <i class="fa-solid fa-triangle-exclamation alert-icon"></i>
          <div class="banner-text">
            <strong>ADVERTENCIA CLÍNICA OBLIGATORIA (HU-35):</strong>
            <span>
              Este módulo procesa las respuestas del paciente para asistir al profesional en la preparación de la consulta.
              <strong>En ningún caso escribe diagnósticos CIE-10 ni planes de tratamiento definitivos</strong> en el expediente.
              Cualquier inferencia debe ser ratificada o descartada por el psicólogo tratante.
            </span>
          </div>
        </div>

        <!-- Estado de Carga -->
        <div *ngIf="cargando()" class="loading-state">
          <i class="fa-solid fa-circle-notch fa-spin fa-2x text-primary mb-3"></i>
          <p>Analizando respuestas con el motor de reglas Romero y sanitizando PII...</p>
        </div>

        <!-- Error State -->
        <div *ngIf="errorMensaje()" class="alert-error-custom mb-3">
          <i class="fa-solid fa-circle-exclamation"></i>
          <span>{{ errorMensaje() }}</span>
        </div>

        <!-- Contenido del Análisis IA -->
        <div *ngIf="!cargando() && analisis()" class="modal-body-ia">
          
          <!-- Metadatos de Severidad y Alerta -->
          <div class="summary-cards-grid">
            <div class="metric-card">
              <span class="metric-label">PUNTUACIÓN DE SEVERIDAD</span>
              <div class="metric-value-row">
                <span class="metric-number">{{ analisis()?.puntuacion_severidad }}</span>
                <span class="metric-scale">/ 100</span>
              </div>
              <div class="progress-bar-bg">
                <div class="progress-bar-fill" [style.width.%]="analisis()?.puntuacion_severidad"
                     [ngClass]="getSeveridadClass(analisis()?.puntuacion_severidad || 0)"></div>
              </div>
            </div>

            <div class="metric-card">
              <span class="metric-label">NIVEL DE ALERTA CLÍNICA</span>
              <div class="alert-badge-container">
                <span class="badge-alerta" [ngClass]="getAlertaBadgeClass(analisis()?.nivel_alerta)">
                  <i class="fa-solid fa-shield-halved"></i>
                  {{ analisis()?.nivel_alerta }}
                </span>
              </div>
              <span class="metric-subtext">
                {{ getAlertaDescription(analisis()?.nivel_alerta) }}
              </span>
            </div>

            <div class="metric-card">
              <span class="metric-label">SELLO CRIPTOGRÁFICO DE AUDITORÍA</span>
              <div class="hash-box" [title]="analisis()?.sha256_verificacion">
                <i class="fa-solid fa-fingerprint text-accent"></i>
                <code class="hash-code">{{ (analisis()?.sha256_verificacion || '').substring(0, 16) }}...</code>
              </div>
              <span class="metric-subtext">Integridad verificada con SHA-256</span>
            </div>
          </div>

          <!-- Reglas Romero Disparadas con Evidencia -->
          <div class="section-container">
            <h3 class="section-title">
              <i class="fa-solid fa-diagram-project text-primary"></i>
              Reglas Clínicas Detectadas ({{ analisis()?.reglas_disparadas?.length || 0 }})
            </h3>
            
            <div *ngIf="(analisis()?.reglas_disparadas?.length || 0) === 0" class="empty-rules">
              <i class="fa-solid fa-circle-check text-success"></i>
              <span>No se activaron banderas rojas ni indicadores de riesgo clínico agudo.</span>
            </div>

            <div class="rules-list" *ngIf="(analisis()?.reglas_disparadas?.length || 0) > 0">
              <div class="rule-card" *ngFor="let regla of analisis()?.reglas_disparadas"
                   [ngClass]="'border-' + regla.severidad.toLowerCase()">
                <div class="rule-header">
                  <span class="rule-name">{{ regla.regla }}</span>
                  <span class="rule-severity-pill" [ngClass]="'pill-' + regla.severidad.toLowerCase()">
                    {{ regla.severidad }}
                  </span>
                </div>
                <div class="rule-evidence">
                  <i class="fa-solid fa-quote-left text-dim"></i>
                  <span>{{ regla.evidencia }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Resumen Clínico Sugerido (Conmutador Ver / Editar) -->
          <div class="section-container">
            <div class="section-header-action">
              <h3 class="section-title">
                <i class="fa-solid fa-notes-medical text-primary"></i>
                Resumen Clínico Sugerido para la Anamnesis
              </h3>
              <button class="btn btn-sm btn-outline-secondary" (click)="modoEdicion = !modoEdicion">
                <i class="fa-solid" [ngClass]="modoEdicion ? 'fa-eye' : 'fa-pen-to-square'"></i>
                {{ modoEdicion ? 'Vista previa' : 'Editar texto' }}
              </button>
            </div>

            <div *ngIf="!modoEdicion" class="summary-preview-box">
              <p class="summary-text">{{ resumenEditado }}</p>
            </div>

            <div *ngIf="modoEdicion" class="summary-edit-box">
              <textarea [(ngModel)]="resumenEditado" rows="5" class="form-control"
                        placeholder="Edite o complemente el resumen sugerido por el asistente..."></textarea>
              <small class="text-muted">El texto modificado se registrará en la auditoría con estado "EDITADO".</small>
            </div>
          </div>

          <!-- Preguntas de Profundización Recomendadas -->
          <div class="section-container" *ngIf="(analisis()?.preguntas_profundizacion_sugeridas?.length || 0) > 0">
            <h3 class="section-title">
              <i class="fa-solid fa-circle-question text-info"></i>
              Preguntas de Exploración Clínica Sugeridas
            </h3>
            <ul class="questions-list">
              <li *ngFor="let pregunta of analisis()?.preguntas_profundizacion_sugeridas">
                <i class="fa-solid fa-arrow-right text-primary"></i>
                <span>{{ pregunta }}</span>
              </li>
            </ul>
          </div>

          <!-- Formulario de Motivo si se decide Descartar -->
          <div *ngIf="mostrarDescarte" class="discard-reason-panel glass-panel mt-3">
            <label class="form-label">
              <i class="fa-solid fa-comment-slash text-warning"></i>
              Motivo del descarte clínico (requerido para bitácora):
            </label>
            <textarea [(ngModel)]="motivoDescarte" class="form-control" rows="2"
                      placeholder="Explique por qué descarta esta sugerencia (ej. falso positivo en respuestas del paciente)..."></textarea>
            <div class="mt-2 d-flex gap-2 justify-content-end">
              <button class="btn btn-sm btn-secondary" (click)="mostrarDescarte = false">Cancelar</button>
              <button class="btn btn-sm btn-danger" [disabled]="!motivoDescarte.trim()" (click)="confirmarDescarte()">
                Confirmar Descarte
              </button>
            </div>
          </div>

        </div>

        <!-- Footer con Acciones de Decisión Humana (Supervisión Estricta) -->
        <div class="modal-footer-ia">
          <div class="footer-left">
            <span class="text-xs text-muted">
              Auditoría activa · Decisión vinculada al ID de usuario en sesión
            </span>
          </div>

          <div class="footer-actions d-flex gap-2" *ngIf="!cargando() && analisis()">
            <button class="btn btn-secondary" (click)="solicitarDescarte()" [disabled]="mostrarDescarte">
              <i class="fa-solid fa-ban"></i> Descartar
            </button>
            <button class="btn btn-outline-primary" (click)="aceptarConEdicion()">
              <i class="fa-solid fa-pen-nib"></i> Guardar Editado
            </button>
            <button class="btn btn-primary" (click)="aceptarOriginal()">
              <i class="fa-solid fa-check-double"></i> Aceptar Sugerencia
            </button>
          </div>
        </div>

      </div>
    </div>
  `,
  styles: [`
    .modal-backdrop-custom {
      position: fixed;
      top: 0; left: 0; width: 100vw; height: 100vh;
      background: rgba(15, 23, 42, 0.7);
      backdrop-filter: blur(8px);
      z-index: 1050;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1.5rem;
    }

    .modal-dialog-custom {
      width: 100%;
      max-width: 850px;
      max-height: 90vh;
      background: #ffffff;
      border-radius: 16px;
      display: flex;
      flex-direction: column;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
      border: 1px solid rgba(226, 232, 240, 0.8);
      overflow: hidden;
      animation: modalFadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes modalFadeIn {
      from { opacity: 0; transform: scale(0.96) translateY(10px); }
      to { opacity: 1; transform: scale(1) translateY(0); }
    }

    .modal-header-ia {
      padding: 1.25rem 1.5rem;
      border-bottom: 1px solid #e2e8f0;
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #f8fafc;
    }

    .header-left {
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    .ai-badge-pulse {
      width: 44px;
      height: 44px;
      border-radius: 12px;
      background: linear-gradient(135deg, #0284c7, #4f46e5);
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.25rem;
      box-shadow: 0 0 15px rgba(79, 70, 229, 0.35);
    }

    .modal-title {
      font-size: 1.2rem;
      font-weight: 700;
      color: #0f172a;
      margin: 0;
    }

    .modal-subtitle {
      font-size: 0.82rem;
      color: #64748b;
      margin: 0;
    }

    .btn-close-custom {
      background: transparent;
      border: none;
      font-size: 1.25rem;
      color: #94a3b8;
      cursor: pointer;
      padding: 0.25rem;
      transition: color 0.15s;
    }
    .btn-close-custom:hover { color: #0f172a; }

    .safety-banner {
      background: #fffbeb;
      border-left: 4px solid #f59e0b;
      padding: 0.85rem 1.25rem;
      display: flex;
      align-items: flex-start;
      gap: 0.85rem;
      font-size: 0.82rem;
      color: #92400e;
    }

    .safety-banner .alert-icon {
      font-size: 1.1rem;
      color: #f59e0b;
      margin-top: 2px;
    }

    .modal-body-ia {
      padding: 1.25rem 1.5rem;
      overflow-y: auto;
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }

    .summary-cards-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1rem;
    }

    .metric-card {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 1rem;
      display: flex;
      flex-direction: column;
    }

    .metric-label {
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.05em;
      color: #64748b;
      margin-bottom: 0.35rem;
    }

    .metric-value-row {
      display: flex;
      align-items: baseline;
      gap: 0.25rem;
      margin-bottom: 0.5rem;
    }

    .metric-number {
      font-size: 1.8rem;
      font-weight: 800;
      color: #0f172a;
    }

    .metric-scale {
      font-size: 0.9rem;
      color: #94a3b8;
    }

    .progress-bar-bg {
      height: 6px;
      background: #e2e8f0;
      border-radius: 3px;
      overflow: hidden;
    }

    .progress-bar-fill {
      height: 100%;
      border-radius: 3px;
      transition: width 0.4s ease;
    }

    .alert-badge-container {
      margin: 0.4rem 0;
    }

    .badge-alerta {
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      padding: 0.35rem 0.75rem;
      border-radius: 9999px;
      font-size: 0.8rem;
      font-weight: 700;
    }

    .alerta-normal { background: #dcfce7; color: #166534; }
    .alerta-moderada { background: #fef9c3; color: #854d0e; }
    .alerta-alta { background: #ffedd5; color: #9a3412; }
    .alerta-critica { background: #fee2e2; color: #991b1b; animation: pulseRed 1.5s infinite; }

    @keyframes pulseRed {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.04); }
    }

    .metric-subtext {
      font-size: 0.75rem;
      color: #64748b;
    }

    .hash-box {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      background: #ffffff;
      padding: 0.4rem 0.6rem;
      border-radius: 6px;
      border: 1px solid #cbd5e1;
      margin-bottom: 0.4rem;
    }

    .hash-code {
      font-family: monospace;
      font-size: 0.78rem;
      color: #0284c7;
    }

    .section-container {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 1rem 1.25rem;
    }

    .section-title {
      font-size: 0.95rem;
      font-weight: 700;
      color: #1e293b;
      margin: 0 0 0.85rem 0;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .section-header-action {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 0.85rem;
    }
    .section-header-action .section-title { margin-bottom: 0; }

    .rules-list {
      display: flex;
      flex-direction: column;
      gap: 0.65rem;
    }

    .rule-card {
      background: #f8fafc;
      border-left: 4px solid #cbd5e1;
      border-radius: 8px;
      padding: 0.75rem 1rem;
    }

    .border-critica { border-left-color: #ef4444; background: #fff5f5; }
    .border-alta { border-left-color: #f97316; background: #fffaf0; }
    .border-media { border-left-color: #eab308; background: #fefce8; }
    .border-baja { border-left-color: #3b82f6; background: #f0f9ff; }

    .rule-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 0.35rem;
    }

    .rule-name {
      font-weight: 600;
      font-size: 0.88rem;
      color: #0f172a;
    }

    .rule-severity-pill {
      font-size: 0.7rem;
      font-weight: 700;
      padding: 0.15rem 0.5rem;
      border-radius: 9999px;
      text-transform: uppercase;
    }

    .pill-critica { background: #fee2e2; color: #991b1b; }
    .pill-alta { background: #ffedd5; color: #9a3412; }
    .pill-media { background: #fef9c3; color: #854d0e; }
    .pill-baja { background: #e0f2fe; color: #0369a1; }

    .rule-evidence {
      font-size: 0.8rem;
      color: #475569;
      display: flex;
      align-items: flex-start;
      gap: 0.5rem;
    }

    .summary-preview-box {
      background: #f8fafc;
      border: 1px dashed #cbd5e1;
      border-radius: 8px;
      padding: 0.9rem;
    }

    .summary-text {
      margin: 0;
      font-size: 0.88rem;
      line-height: 1.5;
      color: #1e293b;
      white-space: pre-line;
    }

    .questions-list {
      list-style: none;
      padding: 0;
      margin: 0;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    .questions-list li {
      font-size: 0.85rem;
      color: #334155;
      display: flex;
      align-items: center;
      gap: 0.6rem;
      background: #f0fdf4;
      padding: 0.5rem 0.75rem;
      border-radius: 6px;
    }

    .modal-footer-ia {
      padding: 1rem 1.5rem;
      border-top: 1px solid #e2e8f0;
      background: #f8fafc;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .loading-state {
      padding: 3rem;
      text-align: center;
      color: #64748b;
    }

    .alert-error-custom {
      background: #fee2e2;
      border: 1px solid #fca5a5;
      color: #991b1b;
      padding: 0.75rem 1rem;
      border-radius: 8px;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .discard-reason-panel {
      padding: 1rem;
      background: #fffbeb;
      border: 1px solid #fde68a;
      border-radius: 8px;
    }
  `]
})
export class IaAsistenteModalComponent implements OnInit {
  @Input() respuestaId!: string;
  @Input() motivoConsulta?: string;
  @Output() cerrar = new EventEmitter<void>();
  @Output() decisionRegistrada = new EventEmitter<{ decision: string; resumen: string }>();

  cargando = signal<boolean>(true);
  errorMensaje = signal<string | null>(null);
  analisis = signal<AnalisisIAResponse | null>(null);

  modoEdicion = false;
  resumenEditado = '';
  mostrarDescarte = false;
  motivoDescarte = '';

  constructor(private clinicaService: ClinicaSprint2Service) {}

  ngOnInit(): void {
    if (this.respuestaId) {
      this.cargarAnalisisIA();
    } else {
      this.errorMensaje.set('ID de respuesta preconsulta no proporcionado.');
      this.cargando.set(false);
    }
  }

  cargarAnalisisIA(): void {
    this.cargando.set(true);
    this.errorMensaje.set(null);

    this.clinicaService.analizarRespuestaConIA(this.respuestaId).subscribe({
      next: (data) => {
        this.analisis.set(data);
        this.resumenEditado = data.resumen_clinico_sugerido || '';
        this.cargando.set(false);
      },
      error: (err) => {
        const errorMsg = err?.error?.error || 'Error al ejecutar el motor de inferencia clínica de IA.';
        this.errorMensaje.set(errorMsg);
        this.cargando.set(false);
      }
    });
  }

  getSeveridadClass(score: number): string {
    if (score >= 80) return 'bg-danger';
    if (score >= 50) return 'bg-warning';
    if (score >= 25) return 'bg-info';
    return 'bg-success';
  }

  getAlertaBadgeClass(alerta?: string): string {
    switch (alerta) {
      case 'CRITICA': return 'alerta-critica';
      case 'ALTA': return 'alerta-alta';
      case 'MODERADA': return 'alerta-moderada';
      default: return 'alerta-normal';
    }
  }

  getAlertaDescription(alerta?: string): string {
    switch (alerta) {
      case 'CRITICA': return 'Riesgo agudo inminente. Requiere evaluación inmediata.';
      case 'ALTA': return 'Múltiples banderas rojas. Priorizar en primera sesión.';
      case 'MODERADA': return 'Sintomatología clínica presente con impacto funcional.';
      default: return 'Sintomatología dentro de parámetros normales o leves.';
    }
  }

  aceptarOriginal(): void {
    const payload = {
      respuesta_preconsulta_id: this.respuestaId,
      analisis_id: this.analisis()?.analisis_id,
      decision: 'ACEPTADO' as const,
      texto_final_utilizado: this.resumenEditado
    };

    this.clinicaService.registrarDecisionIA(payload).subscribe({
      next: () => {
        this.decisionRegistrada.emit({ decision: 'ACEPTADO', resumen: this.resumenEditado });
        this.onCerrar();
      },
      error: () => {
        // Even if registration emits an error, inform parent
        this.decisionRegistrada.emit({ decision: 'ACEPTADO', resumen: this.resumenEditado });
        this.onCerrar();
      }
    });
  }

  aceptarConEdicion(): void {
    const payload = {
      respuesta_preconsulta_id: this.respuestaId,
      analisis_id: this.analisis()?.analisis_id,
      decision: 'EDITADO' as const,
      texto_final_utilizado: this.resumenEditado
    };

    this.clinicaService.registrarDecisionIA(payload).subscribe({
      next: () => {
        this.decisionRegistrada.emit({ decision: 'EDITADO', resumen: this.resumenEditado });
        this.onCerrar();
      },
      error: () => {
        this.decisionRegistrada.emit({ decision: 'EDITADO', resumen: this.resumenEditado });
        this.onCerrar();
      }
    });
  }

  solicitarDescarte(): void {
    this.mostrarDescarte = true;
  }

  confirmarDescarte(): void {
    const payload = {
      respuesta_preconsulta_id: this.respuestaId,
      analisis_id: this.analisis()?.analisis_id,
      decision: 'DESCARTADO' as const,
      motivo_descarte: this.motivoDescarte
    };

    this.clinicaService.registrarDecisionIA(payload).subscribe({
      next: () => {
        this.decisionRegistrada.emit({ decision: 'DESCARTADO', resumen: '' });
        this.onCerrar();
      },
      error: () => {
        this.decisionRegistrada.emit({ decision: 'DESCARTADO', resumen: '' });
        this.onCerrar();
      }
    });
  }

  onCerrar(): void {
    this.cerrar.emit();
  }
}
