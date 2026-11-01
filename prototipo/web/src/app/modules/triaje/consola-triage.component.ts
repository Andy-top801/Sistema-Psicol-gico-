// ==============================================================================
// MÓDULO: consola-triage.component.ts
// CAPA BCE: BOUNDARY (Interfaz de Usuario Web – Angular 17) — IU_ConsolaTriageIAView
// CASOS DE USO: CU21 (Clasificación Asistida por IA) y CU22 (Matching con HITL)
// HISTORIAS DE USUARIO: HU-47, HU-48
// DESCRIPCIÓN: Consola web para el Coordinador Clínico que presenta el triaje automatizado
//              con categorización, banderas rojas de crisis vital, y motor de emparejamiento
//              multivariable con supervisión humana obligatoria (Human-in-the-Loop).
// ==============================================================================
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TriajeIAService, ClasificacionIA, SugerenciaMatching } from '../../core/services/triaje-ia.service';

@Component({
  selector: 'app-consola-triage',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="container-fluid py-4 px-4">
      
      <!-- Encabezado de la Consola -->
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 class="h3 fw-bold text-slate-800 mb-1">
            <i class="fa-solid fa-brain text-teal me-2"></i>Consola de Triaje Clínico y Matching Asistido por IA
          </h1>
          <p class="text-muted small mb-0">
            Sprint 3 • Clasificación Lingüística, Detección de Crisis Vital (CU21) y Emparejamiento Multivariable con Supervisión Humana HITL (CU22)
          </p>
        </div>
        <div class="d-flex gap-2">
          <button class="btn btn-outline-secondary btn-sm" (click)="cargarDatos()">
            <i class="fa-solid fa-arrows-rotate me-1"></i> Actualizar
          </button>
        </div>
      </div>

      <!-- BANNER DE ALERTA ROJA: CRISIS VITAL Y RIESGO AUTOLÍTICO (CP-M11 / CU21) -->
      <div *ngIf="alertasCrisis.length > 0" class="alert-crisis-box mb-4 p-3 rounded-3 shadow-sm border border-danger">
        <div class="d-flex align-items-center justify-content-between">
          <div class="d-flex align-items-center gap-3">
            <div class="pulse-crisis-icon">
              <i class="fa-solid fa-triangle-exclamation fa-2x text-danger"></i>
            </div>
            <div>
              <h5 class="fw-bold text-danger mb-0">
                ¡ALERTA DE TRIAJE PRIORITARIO: CRISIS VITAL DETECTADA! ({{ alertasCrisis.length }})
              </h5>
              <p class="text-danger small mb-0">
                Se han detectado patrones de ideación autolítica o sufrimiento agudo que requieren intervención inmediata del Coordinador Clínico.
              </p>
            </div>
          </div>
          <span class="badge bg-danger fs-6 px-3 py-2">SEVERIDAD CRÍTICA</span>
        </div>
      </div>

      <!-- Pestañas o Layout en 2 Columnas -->
      <div class="row g-4">
        
        <!-- Columna Izquierda: Casos Clasificados por IA (CU21 / HU-47) -->
        <div class="col-lg-6">
          <div class="card shadow-sm border-0 rounded-3 h-100">
            <div class="card-header bg-white py-3 border-bottom d-flex justify-content-between align-items-center">
              <h5 class="fw-bold mb-0 text-slate-700">
                <i class="fa-solid fa-stethoscope text-primary me-2"></i>Evaluaciones de Intake e IA (CU21)
              </h5>
              <span class="badge bg-light text-dark">{{ clasificaciones.length }} Registros</span>
            </div>
            <div class="card-body p-0">
              <div *ngIf="cargando" class="text-center py-5">
                <div class="spinner-border text-primary" role="status"></div>
                <p class="small text-muted mt-2">Cargando inferencias clínicas...</p>
              </div>

              <div *ngIf="!cargando && clasificaciones.length === 0" class="text-center py-5">
                <i class="fa-regular fa-folder-open fa-2x text-muted mb-2"></i>
                <p class="text-muted small">No hay evaluaciones de intake registradas.</p>
              </div>

              <div class="list-group list-group-flush" *ngIf="!cargando && clasificaciones.length > 0">
                <div *ngFor="let c of clasificaciones" 
                     class="list-group-item p-3 list-group-item-action cursor-pointer"
                     [class.border-start-crisis]="c.alerta_crisis"
                     [class.bg-selected]="casoSeleccionado?.id === c.id"
                     (click)="seleccionarCaso(c)">
                  
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <div>
                      <h6 class="fw-bold mb-1">{{ c.paciente_nombre || 'Paciente en Evaluación' }}</h6>
                      <span class="badge me-1" [ngClass]="getCategoriaBadgeClass(c.categoria_principal)">
                        {{ getCategoriaLabel(c.categoria_principal) }}
                      </span>
                      <span class="badge" [ngClass]="getSeveridadBadgeClass(c.nivel_severidad)">
                        {{ c.nivel_severidad }}
                      </span>
                    </div>
                    <div class="text-end">
                      <span class="badge bg-info bg-opacity-10 text-info border border-info border-opacity-25">
                        Confianza: {{ (c.confianza_score * 100) | number:'1.0-0' }}%
                      </span>
                      <div class="text-muted font-monospace small mt-1" style="font-size: 0.7rem;">
                        SHA: {{ c.hash_trazabilidad_sha256.substring(0, 10) }}...
                      </div>
                    </div>
                  </div>

                  <p class="small text-muted mb-2">{{ c.explicacion_heuristica }}</p>

                  <!-- Palabras clave sanitizadas -->
                  <div class="d-flex flex-wrap gap-1">
                    <span *ngFor="let kw of c.palabras_clave_detectadas" class="badge bg-secondary bg-opacity-10 text-secondary border">
                      #{{ kw }}
                    </span>
                  </div>

                  <div *ngIf="c.alerta_crisis" class="mt-2 text-danger small fw-bold">
                    <i class="fa-solid fa-circle-exclamation me-1"></i> Bandera Roja Autolítica Activada
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Columna Derecha: Motor de Matching Multivariable y HITL (CU22 / HU-48) -->
        <div class="col-lg-6">
          <div class="card shadow-sm border-0 rounded-3 h-100">
            <div class="card-header bg-white py-3 border-bottom d-flex justify-content-between align-items-center">
              <h5 class="fw-bold mb-0 text-slate-700">
                <i class="fa-solid fa-user-doctor text-success me-2"></i>Emparejamiento Terapéutico (CU22)
              </h5>
              <button class="btn btn-primary btn-sm" [disabled]="!casoSeleccionado || procesandoMatching" (click)="generarSugerenciasTop3()">
                <i class="fa-solid fa-wand-magic-sparkles me-1"></i>
                {{ procesandoMatching ? 'Calculando...' : 'Generar Top 3 IA' }}
              </button>
            </div>
            
            <div class="card-body p-3">
              <div *ngIf="!casoSeleccionado" class="text-center py-5">
                <i class="fa-solid fa-hand-pointer fa-2x text-muted mb-2"></i>
                <p class="text-muted small">Seleccione un caso de la lista izquierda para ejecutar el emparejamiento de psicólogos.</p>
              </div>

              <!-- Top 3 Recomendaciones -->
              <div *ngIf="casoSeleccionado">
                
                <div class="bg-light p-2 rounded-2 mb-3 small d-flex justify-content-between">
                  <div>
                    <strong>Paciente:</strong> {{ casoSeleccionado.paciente_nombre }}<br>
                    <strong>Especialidad Requerida:</strong> {{ getCategoriaLabel(casoSeleccionado.categoria_principal) }}
                  </div>
                  <div class="text-end">
                    <span class="badge bg-secondary">Modalidad: Mixta / Virtual</span>
                  </div>
                </div>

                <div *ngIf="sugerencias.length === 0 && !procesandoMatching" class="text-center py-4 text-muted small">
                  Presione <strong>'Generar Top 3 IA'</strong> para calcular afinidad según especialidad (40%), disponibilidad (30%), balanceo de carga (20%) y modalidad (10%).
                </div>

                <!-- Tarjetas del Top 3 -->
                <div *ngFor="let sug of sugerencias; let idx = index" class="card mb-3 border" [class.border-success]="idx === 0">
                  <div class="card-body p-3">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                      <div>
                        <span class="badge me-2" [ngClass]="idx === 0 ? 'bg-success' : 'bg-secondary'">
                          #{{ idx + 1 }} Recomendación
                        </span>
                        <h6 class="fw-bold d-inline">{{ sug.psicologo_nombre || 'Lic. Especialista' }}</h6>
                        <span class="text-muted small ms-2" *ngIf="sug.numero_colegiado">({{ sug.numero_colegiado }})</span>
                      </div>
                      <div class="text-end">
                        <span class="fs-5 fw-bold text-success">{{ sug.score_afinidad | number:'1.1-1' }}%</span>
                        <div class="small text-muted">Afinidad Global</div>
                      </div>
                    </div>

                    <!-- Desglose de factores ponderados -->
                    <div class="row g-2 small text-muted my-2 py-1 bg-light rounded">
                      <div class="col-6 col-md-3">
                        <i class="fa-solid fa-ribbon me-1 text-primary"></i>Esp (40%): 
                        <strong>{{ sug.factores_ponderacion.afinidad_especialidad }}%</strong>
                      </div>
                      <div class="col-6 col-md-3">
                        <i class="fa-solid fa-calendar-check me-1 text-info"></i>Disp (30%): 
                        <strong>{{ sug.factores_ponderacion.disponibilidad_horaria }}%</strong>
                      </div>
                      <div class="col-6 col-md-3">
                        <i class="fa-solid fa-scale-balanced me-1 text-warning"></i>Carga (20%): 
                        <strong>{{ sug.factores_ponderacion.balance_carga }}%</strong>
                      </div>
                      <div class="col-6 col-md-3">
                        <i class="fa-solid fa-laptop me-1 text-secondary"></i>Mod (10%): 
                        <strong>{{ sug.factores_ponderacion.preferencia_modalidad }}%</strong>
                      </div>
                    </div>

                    <!-- Botón de Asignación Humana Obligatoria (HITL) -->
                    <div class="d-flex justify-content-between align-items-center mt-3 pt-2 border-top">
                      <span class="badge bg-warning bg-opacity-10 text-warning border border-warning border-opacity-25" *ngIf="sug.estado_decision === 'PENDIENTE_VALIDACION'">
                        <i class="fa-solid fa-shield-halved me-1"></i>Pendiente Validación Humana
                      </span>
                      <span class="badge bg-success" *ngIf="sug.estado_decision === 'APROBADO'">
                        <i class="fa-solid fa-circle-check me-1"></i>Asignación Aprobada
                      </span>

                      <button class="btn btn-outline-success btn-sm" 
                              *ngIf="sug.estado_decision === 'PENDIENTE_VALIDACION'"
                              (click)="abrirModalHITL(sug)">
                        <i class="fa-solid fa-user-check me-1"></i> Aprobar Asignación (HITL)
                      </button>
                    </div>

                  </div>
                </div>

              </div>

            </div>
          </div>
        </div>

      </div>

      <!-- MODAL DE SUPERVISIÓN HUMANA OBLIGATORIA (HITL) -->
      <div *ngIf="sugerenciaSeleccionada" class="modal-backdrop-custom">
        <div class="modal-dialog-custom glass-card p-4">
          <div class="d-flex justify-content-between align-items-center mb-3 border-bottom pb-2">
            <h5 class="fw-bold mb-0 text-success">
              <i class="fa-solid fa-user-shield me-2"></i>Validación y Supervisión Humana (HITL)
            </h5>
            <button class="btn-close" (click)="sugerenciaSeleccionada = null"></button>
          </div>

          <div class="alert alert-info py-2 small">
            <i class="fa-solid fa-circle-info me-1"></i>
            Conforme a la normativa ético-clínica, la asignación definitiva del terapeuta es responsabilidad exclusiva del Coordinador Humano.
          </div>

          <div class="mb-3">
            <p class="mb-1"><strong>Paciente:</strong> {{ casoSeleccionado?.paciente_nombre }}</p>
            <p class="mb-1"><strong>Psicólogo Sugerido:</strong> {{ sugerenciaSeleccionada.psicologo_nombre }}</p>
            <p class="mb-2"><strong>Score de Afinidad:</strong> {{ sugerenciaSeleccionada.score_afinidad }}%</p>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold small">Justificación Clínica de la Asignación *</label>
            <textarea class="form-control form-control-sm" rows="3" [(ngModel)]="justificacionClinica"
                      placeholder="Ingrese fundamentación profesional para el expediente (ej. Terapeuta idóneo para abordaje cognitivo-conductual)..."></textarea>
          </div>

          <div class="d-flex justify-content-end gap-2">
            <button class="btn btn-secondary btn-sm" (click)="sugerenciaSeleccionada = null">Cancelar</button>
            <button class="btn btn-success btn-sm" [disabled]="!justificacionClinica.trim() || confirmandoHITL" (click)="confirmarAsignacionHITL()">
              <i class="fa-solid fa-check me-1"></i>
              {{ confirmandoHITL ? 'Asignando...' : 'Confirmar y Asignar Terapeuta' }}
            </button>
          </div>
        </div>
      </div>

    </div>
  `,
  styles: [`
    .text-teal { color: #0d9488; }
    .cursor-pointer { cursor: pointer; }
    .bg-selected { background-color: #f0fdf4 !important; border-left: 4px solid #10b981 !important; }
    .border-start-crisis { border-left: 4px solid #ef4444 !important; background-color: #fff5f5; }
    .alert-crisis-box { background-color: #fef2f2; }
    .pulse-crisis-icon { animation: pulse 1.5s infinite; }
    @keyframes pulse {
      0% { transform: scale(1); }
      50% { transform: scale(1.15); }
      100% { transform: scale(1); }
    }
    .modal-backdrop-custom {
      position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
      background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px); z-index: 1050;
      display: flex; align-items: center; justify-content: center; padding: 1.5rem;
    }
    .modal-dialog-custom {
      width: 100%; max-width: 520px; background: #ffffff; border-radius: 16px;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
    }
  `]
})
export class ConsolaTriageComponent implements OnInit {
  clasificaciones: ClasificacionIA[] = [];
  alertasCrisis: ClasificacionIA[] = [];
  casoSeleccionado: ClasificacionIA | null = null;
  sugerencias: SugerenciaMatching[] = [];
  sugerenciaSeleccionada: SugerenciaMatching | null = null;
  justificacionClinica: string = 'Aprobado conforme al perfil sintomático y disponibilidad horaria del profesional.';

  cargando: boolean = true;
  procesandoMatching: boolean = false;
  confirmandoHITL: boolean = false;

  constructor(private triajeService: TriajeIAService) {}

  ngOnInit(): void {
    this.cargarDatos();
  }

  cargarDatos(): void {
    this.cargando = true;
    this.triajeService.getClasificaciones().subscribe({
      next: (data) => {
        this.clasificaciones = data;
        this.alertasCrisis = data.filter(c => c.alerta_crisis || c.nivel_severidad === 'CRITICA');
        if (data.length > 0 && !this.casoSeleccionado) {
          this.seleccionarCaso(data[0]);
        }
        this.cargando = false;
      },
      error: () => {
        this.cargando = false;
      }
    });
  }

  seleccionarCaso(caso: ClasificacionIA): void {
    this.casoSeleccionado = caso;
    this.sugerencias = [];
  }

  generarSugerenciasTop3(): void {
    if (!this.casoSeleccionado) return;
    this.procesandoMatching = true;

    // Se asume que el ID del paciente se obtiene desde la evaluación
    const pacienteId = this.casoSeleccionado.id;
    this.triajeService.generarMatching(
      pacienteId,
      this.casoSeleccionado.categoria_principal,
      'MIXTA'
    ).subscribe({
      next: (top3) => {
        this.sugerencias = top3;
        this.procesandoMatching = false;
      },
      error: () => {
        this.procesandoMatching = false;
      }
    });
  }

  abrirModalHITL(sug: SugerenciaMatching): void {
    this.sugerenciaSeleccionada = sug;
  }

  confirmarAsignacionHITL(): void {
    if (!this.sugerenciaSeleccionada || !this.casoSeleccionado) return;
    this.confirmandoHITL = true;

    this.triajeService.asignarPsicologoHITL(
      this.sugerenciaSeleccionada.id,
      this.sugerenciaSeleccionada.paciente,
      this.sugerenciaSeleccionada.psicologo_sugerido,
      this.justificacionClinica
    ).subscribe({
      next: () => {
        this.sugerenciaSeleccionada!.estado_decision = 'APROBADO';
        this.confirmandoHITL = false;
        this.sugerenciaSeleccionada = null;
      },
      error: () => {
        this.confirmandoHITL = false;
      }
    });
  }

  getCategoriaLabel(code: string): string {
    const map: Record<string, string> = {
      'ANSIEDAD_FOBIAS': 'Ansiedad y Fobias',
      'DEPRESION_ANIMO': 'Depresión y Estado de Ánimo',
      'PAREJA_FAMILIA': 'Pareja y Dinámica Familiar',
      'INFANTO_JUVENIL': 'Infanto-Juvenil',
      'DUELO_PERDIDA': 'Duelo y Pérdida Afectiva'
    };
    return map[code] || code;
  }

  getCategoriaBadgeClass(code: string): string {
    return 'bg-primary bg-opacity-10 text-primary border border-primary border-opacity-25';
  }

  getSeveridadBadgeClass(sev: string): string {
    switch (sev) {
      case 'CRITICA': return 'bg-danger text-white';
      case 'SEVERO': return 'bg-warning text-dark';
      case 'MODERADO': return 'bg-info bg-opacity-25 text-dark';
      default: return 'bg-success bg-opacity-10 text-success';
    }
  }
}
