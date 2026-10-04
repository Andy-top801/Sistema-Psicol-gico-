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
        
        <!-- Header del Modal: Simétrico y Formal -->
        <div class="modal-header-ia">
          <div class="header-left">
            <div class="ai-badge-pulse">
              <i class="fa-solid fa-brain"></i>
            </div>
            <div>
              <h2 class="modal-title">Asistente IA de Preconsulta</h2>
              <p class="modal-subtitle">
                Motor Clínico de Soporte Basado en Reglas (Dr. Romero) · Supervisión Humana Obligatoria
              </p>
            </div>
          </div>
          <button class="btn-close-custom" (click)="onCerrar()" title="Cerrar ventana">
            <i class="fa-solid fa-xmark"></i>
          </button>
        </div>

        <!-- Banner de Salvaguarda Deontológica y Legal -->
        <div class="safety-banner">
          <div class="safety-icon-box">
            <i class="fa-solid fa-shield-halved"></i>
          </div>
          <div class="banner-text">
            <div class="banner-title">
              <i class="fa-solid fa-triangle-exclamation me-1"></i>
              SALVAGUARDA ÉTICA Y DEONTOLÓGICA CLÍNICA (HU-35)
            </div>
            <p class="banner-desc">
              Este módulo sintetiza las respuestas del paciente para asistir al profesional en la preparación de la consulta.
              <strong>En ningún caso prescribe diagnósticos CIE-10 ni planes de tratamiento definitivos</strong>.
              Cualquier inferencia debe ser ratificada o descartada por el psicólogo tratante.
            </p>
          </div>
        </div>

        <!-- Estado de Carga -->
        <div *ngIf="cargando()" class="loading-state">
          <i class="fa-solid fa-circle-notch fa-spin fa-2x text-primary mb-3"></i>
          <p>Analizando respuestas con el motor de reglas Romero y sanitizando PII...</p>
        </div>

        <!-- Error / Consent Safeguard State -->
        <div *ngIf="errorMensaje()" class="alert-error-custom m-4 p-3 rounded" [class.alert-warning-custom]="esConsentimientoPendiente">
          <div class="d-flex align-items-center gap-2 mb-1">
            <i class="fa-solid fa-shield-halved text-warning" *ngIf="esConsentimientoPendiente"></i>
            <i class="fa-solid fa-circle-exclamation text-danger" *ngIf="!esConsentimientoPendiente"></i>
            <strong>{{ esConsentimientoPendiente ? 'Salvaguarda Ética y Legal (HU-35):' : 'Aviso del Sistema:' }}</strong>
          </div>
          <p class="mb-2 text-sm">{{ errorMensaje() }}</p>
          <div *ngIf="esConsentimientoPendiente" class="mt-2 text-end">
            <button class="btn btn-sm btn-outline-primary" (click)="onCerrar()">
              <i class="fa-solid fa-clipboard-check me-1"></i> Continuar con Revisión Manual
            </button>
          </div>
        </div>

        <!-- Contenido del Análisis IA -->
        <div *ngIf="!cargando() && analisis()" class="modal-body-ia">
          
          <!-- Metadatos de Severidad, Alerta y Trazabilidad (3 Tarjetas Simétricas) -->
          <div class="summary-cards-grid">
            <!-- Card 1: Severidad -->
            <div class="metric-card">
              <div class="metric-card-top">
                <span class="metric-label">SEVERIDAD CALCULADA</span>
                <i class="fa-solid fa-chart-line metric-icon text-primary"></i>
              </div>
              <div class="metric-value-row">
                <span class="metric-number">{{ analisis()?.puntuacion_severidad }}</span>
                <span class="metric-scale">/ 100</span>
              </div>
              <div class="progress-bar-bg">
                <div class="progress-bar-fill" [style.width.%]="analisis()?.puntuacion_severidad"
                     [ngClass]="getSeveridadClass(analisis()?.puntuacion_severidad || 0)"></div>
              </div>
              <span class="metric-footer-note">Puntaje escala heurística Romero</span>
            </div>

            <!-- Card 2: Alerta Clínica -->
            <div class="metric-card">
              <div class="metric-card-top">
                <span class="metric-label">NIVEL DE ALERTA</span>
                <i class="fa-solid fa-shield-heart metric-icon text-success"></i>
              </div>
              <div class="alert-badge-container">
                <span class="badge-alerta" [ngClass]="getAlertaBadgeClass(analisis()?.nivel_alerta)">
                  <i class="fa-solid fa-shield-halved me-1"></i>
                  {{ analisis()?.nivel_alerta }}
                </span>
              </div>
              <span class="metric-footer-note">
                {{ getAlertaDescription(analisis()?.nivel_alerta) }}
              </span>
            </div>

            <!-- Card 3: Criptografía Forense -->
            <div class="metric-card">
              <div class="metric-card-top">
                <span class="metric-label">SELLO DE AUDITORÍA</span>
                <i class="fa-solid fa-fingerprint metric-icon text-info"></i>
              </div>
              <div class="hash-box" [title]="analisis()?.sha256_verificacion">
                <code class="hash-code">{{ (analisis()?.sha256_verificacion || '').substring(0, 18) }}...</code>
              </div>
              <span class="metric-footer-note">
                <i class="fa-solid fa-lock text-success me-1"></i> Integridad SHA-256 verificada
              </span>
            </div>
          </div>

          <!-- Reglas Romero Disparadas con Evidencia -->
          <div class="section-container">
            <h3 class="section-title">
              <i class="fa-solid fa-diagram-project text-teal"></i>
              Reglas Clínicas Detectadas ({{ analisis()?.reglas_disparadas?.length || 0 }})
            </h3>
            
            <div *ngIf="(analisis()?.reglas_disparadas?.length || 0) === 0" class="empty-rules">
              <i class="fa-solid fa-circle-check text-success me-2"></i>
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
                  <i class="fa-solid fa-quote-left text-dim me-1"></i>
                  <span>{{ regla.evidencia }}</span>
                </div>
                <div *ngIf="regla.explicacion" class="rule-expl small text-muted mt-1">
                  <i class="fa-solid fa-circle-info text-primary me-1"></i>
                  {{ regla.explicacion }}
                </div>
              </div>
            </div>
          </div>

          <!-- Resumen Clínico Sugerido: Estructurado y Ordenado -->
          <div class="section-container">
            <div class="section-header-action">
              <h3 class="section-title">
                <i class="fa-solid fa-file-lines text-teal"></i>
                Resumen Clínico Sugerido para la Anamnesis
              </h3>
              <button class="btn btn-sm btn-outline-secondary" (click)="modoEdicion = !modoEdicion">
                <i class="fa-solid" [ngClass]="modoEdicion ? 'fa-eye' : 'fa-pen-to-square'"></i>
                {{ modoEdicion ? 'Vista previa estructurada' : 'Editar texto' }}
              </button>
            </div>

            <!-- Vista Previa Estructurada en Líneas Médicas Limpias -->
            <div *ngIf="!modoEdicion" class="summary-preview-card">
              <div class="summary-field-row" *ngFor="let line of getSummaryLines()">
                <div class="field-indicator"><i class="fa-solid fa-circle-check text-success"></i></div>
                <div class="field-content">
                  <span class="field-key" *ngIf="line.key">{{ line.key }}</span>
                  <span class="field-val">{{ line.val }}</span>
                </div>
              </div>
            </div>

            <!-- Modo de Edición Profesional -->
            <div *ngIf="modoEdicion" class="summary-edit-box">
              <textarea [(ngModel)]="resumenEditado" rows="5" class="form-control"
                        placeholder="Edite o complemente el resumen sugerido por el asistente..."></textarea>
              <small class="text-muted mt-1 d-block">
                <i class="fa-solid fa-circle-info me-1 text-primary"></i>
                El texto modificado se registrará en la bitácora de auditoría médica bajo estado "EDITADO".
              </small>
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
                <i class="fa-solid fa-arrow-right text-teal me-2"></i>
                <span>{{ pregunta }}</span>
              </li>
            </ul>
          </div>

          <!-- Formulario de Motivo si se decide Descartar -->
          <div *ngIf="mostrarDescarte" class="discard-reason-panel glass-panel mt-3">
            <label class="form-label fw-semibold">
              <i class="fa-solid fa-comment-slash text-warning me-1"></i>
              Motivo del descarte clínico (requerido para bitácora forense):
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

        <!-- Footer con Acciones de Decisión Humana (Perfectamente Alineado y Simétrico) -->
        <div class="modal-footer-ia">
          <div class="footer-left">
            <div class="footer-audit-pill">
              <i class="fa-solid fa-fingerprint text-primary"></i>
              <span>Supervisión Humana Obligatoria · Trazabilidad Forense</span>
            </div>
          </div>

          <div class="footer-actions" *ngIf="!cargando() && analisis()">
            <button type="button" class="btn btn-action-discard" (click)="solicitarDescarte()" [disabled]="mostrarDescarte" title="Descartar inferencia de la IA">
              <i class="fa-solid fa-ban me-1"></i> Descartar
            </button>
            <button type="button" class="btn btn-action-edit" *ngIf="modoEdicion" (click)="aceptarConEdicion()">
              <i class="fa-solid fa-pen-nib me-1"></i> Guardar Editado
            </button>
            <button type="button" class="btn btn-action-accept" (click)="modoEdicion ? aceptarConEdicion() : aceptarOriginal()">
              <i class="fa-solid fa-circle-check me-1"></i> Aceptar Sugerencia
            </button>
          </div>
        </div>

      </div>
    </div>
  `,
  styles: [`
    .modal-backdrop-custom {
      position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
      background: rgba(15, 23, 42, 0.72); backdrop-filter: blur(6px); z-index: 1050;
      display: flex; align-items: center; justify-content: center; padding: 1.5rem;
    }
    .modal-dialog-custom {
      width: 100%; max-width: 900px; max-height: 92vh; background: #ffffff;
      border-radius: 20px; display: flex; flex-direction: column;
      box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.25), 0 0 0 1px rgba(226, 232, 240, 0.9);
      overflow: hidden; animation: modalFadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes modalFadeIn {
      from { opacity: 0; transform: scale(0.97) translateY(8px); }
      to { opacity: 1; transform: scale(1) translateY(0); }
    }
    .modal-header-ia {
      padding: 1.25rem 1.75rem; border-bottom: 1px solid #e2e8f0;
      display: flex; align-items: center; justify-content: space-between; background: #f8fafc;
    }
    .header-left { display: flex; align-items: center; gap: 1rem; }
    .ai-badge-pulse {
      width: 46px; height: 46px; border-radius: 12px;
      background: linear-gradient(135deg, #0d9488, #0284c7);
      color: #fff; display: flex; align-items: center; justify-content: center;
      font-size: 1.3rem; box-shadow: 0 4px 12px rgba(13, 148, 136, 0.3);
    }
    .modal-title { font-size: 1.25rem; font-weight: 700; color: #0f172a; margin: 0; }
    .modal-subtitle { font-size: 0.82rem; color: #64748b; margin: 0.15rem 0 0 0; }
    .btn-close-custom {
      background: #f1f5f9; border: none; width: 34px; height: 34px; border-radius: 50%;
      font-size: 1.1rem; color: #64748b; cursor: pointer; display: flex; align-items: center;
      justify-content: center; transition: all 0.15s ease;
    }
    .btn-close-custom:hover { background: #fee2e2; color: #ef4444; }

    /* Banner Ético */
    .safety-banner {
      background: #fffdf5; border-bottom: 1px solid #fef3c7; border-left: 5px solid #f59e0b;
      padding: 0.9rem 1.75rem; display: flex; align-items: flex-start; gap: 1rem;
    }
    .safety-icon-box {
      width: 36px; height: 36px; border-radius: 8px; background: #fef3c7; color: #b45309;
      display: flex; align-items: center; justify-content: center; font-size: 1.1rem; flex-shrink: 0;
    }
    .banner-text { flex: 1; }
    .banner-title { font-size: 0.8rem; font-weight: 800; color: #92400e; letter-spacing: 0.03em; margin-bottom: 0.2rem; }
    .banner-desc { font-size: 0.82rem; color: #78350f; margin: 0; line-height: 1.45; }

    /* Cuerpo del Modal */
    .modal-body-ia {
      padding: 1.5rem 1.75rem; overflow-y: auto; flex: 1; display: flex; flex-direction: column; gap: 1.25rem;
    }

    /* Grid de Métricas Simétricas */
    .summary-cards-grid {
      display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;
    }
    .metric-card {
      background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 1.1rem;
      display: flex; flex-direction: column; justify-content: space-between; min-height: 125px;
      transition: box-shadow 0.2s ease;
    }
    .metric-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.04); }
    .metric-card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem; }
    .metric-label { font-size: 0.72rem; font-weight: 700; color: #64748b; letter-spacing: 0.05em; }
    .metric-icon { font-size: 0.95rem; }
    .metric-value-row { display: flex; align-items: baseline; gap: 0.3rem; margin: 0.2rem 0; }
    .metric-number { font-size: 1.9rem; font-weight: 800; color: #0f172a; line-height: 1; }
    .metric-scale { font-size: 0.9rem; font-weight: 600; color: #94a3b8; }
    .progress-bar-bg { height: 6px; background: #e2e8f0; border-radius: 4px; overflow: hidden; margin-top: 0.35rem; }
    .progress-bar-fill { height: 100%; border-radius: 4px; transition: width 0.4s ease; }
    .metric-footer-note { font-size: 0.76rem; color: #64748b; line-height: 1.35; margin-top: 0.4rem; }

    .badge-alerta {
      display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.35rem 0.85rem;
      border-radius: 9999px; font-size: 0.82rem; font-weight: 700;
    }
    .alerta-normal { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
    .alerta-moderada { background: #fef9c3; color: #854d0e; border: 1px solid #fef08a; }
    .alerta-alta { background: #ffedd5; color: #9a3412; border: 1px solid #fed7aa; }
    .alerta-critica { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }

    .hash-box {
      background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px;
      padding: 0.4rem 0.65rem; display: flex; align-items: center; justify-content: center;
    }
    .hash-code { font-family: ui-monospace, monospace; font-size: 0.82rem; color: #0284c7; font-weight: 700; }

    /* Secciones */
    .section-container {
      background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 1.15rem 1.35rem;
    }
    .section-title {
      font-size: 0.95rem; font-weight: 700; color: #0f172a; margin: 0 0 0.85rem 0;
      display: flex; align-items: center; gap: 0.5rem;
    }
    .section-header-action {
      display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.85rem;
    }
    .section-header-action .section-title { margin-bottom: 0; }

    /* Reglas Clínicas */
    .rules-list { display: flex; flex-direction: column; gap: 0.65rem; }
    .rule-card {
      background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #cbd5e1;
      border-radius: 10px; padding: 0.85rem 1.15rem;
    }
    .border-critica { border-left-color: #ef4444; background: #fff5f5; }
    .border-alta { border-left-color: #f97316; background: #fffaf0; }
    .border-media { border-left-color: #eab308; background: #fefce8; }
    .border-baja { border-left-color: #0d9488; background: #f0fdfa; }
    .rule-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.35rem; }
    .rule-name { font-weight: 700; font-size: 0.88rem; color: #0f172a; font-family: ui-monospace, monospace; }
    .rule-severity-pill { font-size: 0.7rem; font-weight: 700; padding: 0.2rem 0.6rem; border-radius: 9999px; text-transform: uppercase; }
    .pill-critica { background: #fee2e2; color: #991b1b; }
    .pill-alta { background: #ffedd5; color: #9a3412; }
    .pill-media { background: #fef9c3; color: #854d0e; }
    .pill-baja { background: #ccfbf1; color: #0f766e; }
    .rule-evidence { font-size: 0.85rem; color: #334155; display: flex; align-items: flex-start; gap: 0.5rem; }

    /* Resumen Clínico Estructurado */
    .summary-preview-card {
      background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px;
      padding: 0.9rem 1.15rem; display: flex; flex-direction: column; gap: 0.55rem;
    }
    .summary-field-row {
      display: flex; align-items: flex-start; gap: 0.65rem; font-size: 0.88rem; line-height: 1.45;
    }
    .field-indicator { margin-top: 3px; font-size: 0.65rem; }
    .field-content { flex: 1; }
    .field-key { font-weight: 700; color: #1e293b; margin-right: 0.35rem; }
    .field-val { color: #334155; }
    .summary-edit-box textarea {
      border: 1.5px solid #0d9488; border-radius: 10px; padding: 0.85rem; font-size: 0.9rem;
    }

    .questions-list {
      list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.5rem;
    }
    .questions-list li {
      font-size: 0.85rem; color: #334155; display: flex; align-items: center; gap: 0.6rem;
      background: #f0fdf4; padding: 0.5rem 0.75rem; border-radius: 6px;
    }

    /* Footer y Botones */
    .modal-footer-ia {
      padding: 1.1rem 1.75rem; border-top: 1px solid #e2e8f0; background: #f8fafc;
      display: flex; align-items: center; justify-content: space-between; gap: 1rem;
    }
    .footer-left { display: flex; align-items: center; }
    .footer-audit-pill {
      font-size: 0.8rem; color: #64748b; display: inline-flex; align-items: center; gap: 0.5rem;
      background: #ffffff; border: 1px solid #e2e8f0; padding: 0.35rem 0.8rem; border-radius: 9999px;
    }
    .footer-actions {
      display: flex; align-items: center; gap: 0.75rem; flex-wrap: nowrap;
    }
    .btn-action-discard {
      height: 42px; padding: 0 1.15rem; font-weight: 600; font-size: 0.88rem; border-radius: 10px;
      background: #ffffff; border: 1px solid #cbd5e1; color: #64748b; transition: all 0.2s ease; cursor: pointer;
    }
    .btn-action-discard:hover:not(:disabled) {
      background: #fee2e2; border-color: #fca5a5; color: #dc2626;
    }
    .btn-action-edit {
      height: 42px; padding: 0 1.25rem; font-weight: 600; font-size: 0.88rem; border-radius: 10px;
      background: #ffffff; border: 1.5px solid #0284c7; color: #0284c7; transition: all 0.2s ease; cursor: pointer;
    }
    .btn-action-edit:hover { background: #f0f9ff; }
    .btn-action-accept {
      height: 42px; padding: 0 1.35rem; font-weight: 600; font-size: 0.88rem; border-radius: 10px;
      background: #0d9488; border: 1px solid #0d9488; color: #ffffff;
      box-shadow: 0 2px 6px rgba(13, 148, 136, 0.25); transition: all 0.2s ease; cursor: pointer;
    }
    .btn-action-accept:hover {
      background: #0f766e; border-color: #0f766e; transform: translateY(-1px);
    }

    .loading-state { padding: 3rem; text-align: center; color: #64748b; }
    .alert-error-custom {
      background: #fee2e2; border: 1px solid #fca5a5; color: #991b1b;
      padding: 0.75rem 1rem; border-radius: 8px; display: flex; align-items: center; gap: 0.5rem;
    }
    .discard-reason-panel {
      padding: 1rem; background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px;
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
  esConsentimientoPendiente = false;

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
    this.esConsentimientoPendiente = false;

    this.clinicaService.analizarRespuestaConIA(this.respuestaId).subscribe({
      next: (data) => {
        this.analisis.set(data);
        this.resumenEditado = data.resumen_clinico_sugerido || '';
        this.cargando.set(false);
      },
      error: (err) => {
        this.esConsentimientoPendiente = !!(err?.status === 403 && err?.error?.modo_manual_requerido);
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

  getSummaryLines(): { key: string; val: string }[] {
    if (!this.resumenEditado) return [];
    return this.resumenEditado
      .split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0)
      .map(line => {
        const colonIdx = line.indexOf(':');
        if (colonIdx !== -1) {
          return {
            key: line.substring(0, colonIdx + 1),
            val: line.substring(colonIdx + 1).trim()
          };
        }
        return { key: '', val: line };
      });
  }

  onCerrar(): void {
    this.cerrar.emit();
  }
}
