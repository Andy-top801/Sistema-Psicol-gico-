// ==============================================================================
// MÓDULO: historia-clinica-detalle.component.ts
// CAPA BCE: BOUNDARY (Interfaz de Usuario) — IU_DetalleHistoriaClinica
// CASOS DE USO: CU15: Codificación CIE-10 y Expediente Psicológico (HU-25, HU-26)
//              CU16: Visualización de Sesiones SOAP vinculadas
//              CU17: Línea de Tiempo Longitudinal y Alertas de Crisis
// ==============================================================================
import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ClinicaSprint2Service } from '../../core/services/clinica-sprint2.service';
import { HistoriaClinica, DiagnosticoCIE, CieItem } from '../../core/models/clinica-sprint2.model';

@Component({
  selector: 'app-historia-clinica-detalle',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <!-- Security Screen for 403 Forbidden Access (HU-26) -->
    <div class="ehr-forbidden-container glass-panel text-center p-5 mx-auto my-5" style="max-width: 650px; background: #ffffff; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05);" *ngIf="accesoRestringido()">
      <div class="security-shield-badge mb-3">
        <i class="fa-solid fa-user-shield fa-4x text-danger"></i>
      </div>
      <h2 class="text-slate-900 fw-bold mb-2">Acceso Clínico Restringido (HU-26)</h2>
      <p class="text-muted mb-4">
        {{ errorMensajeAcceso() }}
      </p>
      <div class="audit-log-pill p-2 mb-4 bg-light rounded text-xs text-muted d-inline-flex align-items-center gap-2">
        <i class="fa-solid fa-fingerprint text-primary"></i>
        <span>Evento de seguridad auditado forensemente en disco con marca de tiempo e IP.</span>
      </div>
      <div>
        <a routerLink="/historias-clinicas" class="btn btn-primary px-4 py-2">
          <i class="fa-solid fa-arrow-left me-2"></i> Volver a Mis Historias Clínicas
        </a>
      </div>
    </div>

    <div class="ehr-detail-container" *ngIf="historia() && !accesoRestringido()">
      
      <!-- Top Banner con Identificación Clínica -->
      <div class="patient-header glass-panel mb-4">
        <div class="patient-header-left">
          <div class="patient-avatar-large">
            {{ (historia()?.paciente_nombre || 'P').charAt(0) }}
          </div>
          <div class="patient-title-info">
            <div class="d-flex align-items-center gap-2">
              <h1 class="patient-name">{{ historia()?.paciente_nombre }}</h1>
              <span class="hc-badge">{{ historia()?.numero_historia }}</span>
              <span class="status-pill active" *ngIf="historia()?.activo">EN TRATAMIENTO</span>
              <span class="status-pill closed" *ngIf="!historia()?.activo">CASO CERRADO</span>
            </div>
            <p class="patient-meta">
              <span><i class="fa-solid fa-user-doctor text-primary"></i> Terapeuta: {{ historia()?.psicologo_nombre }}</span>
              <span><i class="fa-solid fa-calendar-plus text-secondary"></i> Apertura: {{ historia()?.fecha_apertura | date:'dd/MM/yyyy' }}</span>
              <span><i class="fa-solid fa-notes-medical text-info"></i> {{ historia()?.diagnosticos?.length || 0 }} Diagnósticos CIE-10</span>
            </p>
          </div>
        </div>

        <!-- Acciones Rápidas -->
        <div class="header-action-buttons">
          <a [routerLink]="['/notas-soap/nueva']" [queryParams]="{ historia: historia()?.id }" class="btn btn-primary">
            <i class="fa-solid fa-file-signature"></i> Nueva Nota SOAP
          </a>
          <button class="btn btn-outline-primary" (click)="abrirModalTarea()">
            <i class="fa-solid fa-list-check"></i> Asignar Tarea
          </button>
          <a [routerLink]="['/derivaciones/nueva']" [queryParams]="{ historia: historia()?.id }" class="btn btn-outline-secondary">
            <i class="fa-solid fa-share-from-square"></i> Cierre / Derivación
          </a>
          <a routerLink="/historias-clinicas" class="btn btn-light" title="Volver al padrón">
            <i class="fa-solid fa-arrow-left"></i>
          </a>
        </div>
      </div>

      <!-- Pestañas del Expediente -->
      <div class="tabs-nav glass-panel mb-4">
        <button class="tab-item" [class.active]="activeTab === 'anamnesis'" (click)="activeTab = 'anamnesis'">
          <i class="fa-solid fa-book-medical"></i> Anamnesis & EEM
        </button>
        <button class="tab-item" [class.active]="activeTab === 'diagnosticos'" (click)="activeTab = 'diagnosticos'">
          <i class="fa-solid fa-disease"></i> Diagnósticos CIE-10 ({{ historia()?.diagnosticos?.length || 0 }})
        </button>
        <button class="tab-item" [class.active]="activeTab === 'plan'" (click)="activeTab = 'plan'">
          <i class="fa-solid fa-bullseye"></i> Plan Terapéutico
        </button>
        <button class="tab-item" [class.active]="activeTab === 'timeline'" (click)="cambiarATimeline()">
          <i class="fa-solid fa-timeline"></i> Línea de Tiempo Longitudinal
        </button>
      </div>

      <!-- Mensaje de Feedback -->
      <div *ngIf="feedbackMensaje()" class="alert alert-success d-flex align-items-center mb-4">
        <i class="fa-solid fa-circle-check me-2"></i>
        <span>{{ feedbackMensaje() }}</span>
      </div>

      <!-- TAB 1: ANAMNESIS & EXAMEN DE ESTADO MENTAL -->
      <div *ngIf="activeTab === 'anamnesis'" class="tab-content-panel">
        <div class="section-card glass-panel mb-4">
          <div class="section-header">
            <h3 class="section-heading"><i class="fa-solid fa-clipboard-question text-primary me-2"></i>Motivo de Consulta Inicial</h3>
            <button class="btn btn-sm btn-outline-primary" *ngIf="!editandoAnamnesis" (click)="editandoAnamnesis = true">
              <i class="fa-solid fa-pen"></i> Editar
            </button>
            <button class="btn btn-sm btn-success" *ngIf="editandoAnamnesis" (click)="guardarCambiosAnamnesis()">
              <i class="fa-solid fa-check"></i> Guardar Cambios
            </button>
          </div>
          <div *ngIf="!editandoAnamnesis" class="content-block">
            <p>{{ historia()?.motivo_consulta_inicial || 'Sin motivo inicial registrado.' }}</p>
          </div>
          <div *ngIf="editandoAnamnesis">
            <textarea class="form-control" [(ngModel)]="anamnesisForm.motivo_consulta_inicial" rows="3"></textarea>
          </div>
        </div>

        <div class="row g-4 mb-4">
          <div class="col-md-6">
            <div class="section-card glass-panel h-100">
              <h3 class="section-heading"><i class="fa-solid fa-user text-info me-2"></i>Antecedentes Personales</h3>
              <div *ngIf="!editandoAnamnesis" class="content-block">
                <p>{{ historia()?.antecedentes_personales || 'Sin antecedentes personales registrados.' }}</p>
              </div>
              <div *ngIf="editandoAnamnesis">
                <textarea class="form-control" [(ngModel)]="anamnesisForm.antecedentes_personales" rows="4"></textarea>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="section-card glass-panel h-100">
              <h3 class="section-heading"><i class="fa-solid fa-people-roof text-secondary me-2"></i>Antecedentes Familiares</h3>
              <div *ngIf="!editandoAnamnesis" class="content-block">
                <p>{{ historia()?.antecedentes_familiares || 'Sin antecedentes familiares registrados.' }}</p>
              </div>
              <div *ngIf="editandoAnamnesis">
                <textarea class="form-control" [(ngModel)]="anamnesisForm.antecedentes_familiares" rows="4"></textarea>
              </div>
            </div>
          </div>
        </div>

        <div class="section-card glass-panel">
          <h3 class="section-heading"><i class="fa-solid fa-brain text-accent me-2"></i>Examen del Estado Mental (EEM)</h3>
          <div *ngIf="!editandoAnamnesis" class="content-block">
            <p>{{ historia()?.examen_estado_mental || 'Sin examen mental registrado.' }}</p>
          </div>
          <div *ngIf="editandoAnamnesis">
            <textarea class="form-control" [(ngModel)]="anamnesisForm.examen_estado_mental" rows="4"
                      placeholder="Orientación témporo-espacial, atención, afectividad, pensamiento, sensopercepción, juicio..."></textarea>
          </div>
        </div>
      </div>

      <!-- TAB 2: DIAGNÓSTICOS CIE-10 (HU-26) -->
      <div *ngIf="activeTab === 'diagnosticos'" class="tab-content-panel">
        <!-- Buscador Inteligente CIE-10 -->
        <div class="section-card glass-panel mb-4">
          <h3 class="section-heading">
            <i class="fa-solid fa-magnifying-glass-plus text-primary me-2"></i>
            Codificador Diagnóstico CIE-10 / ICD-10 (Salud Mental F00-F99)
          </h3>
          <p class="text-muted small">
            Búsqueda por código o criterio clínico normalizado de acuerdo con la clasificación internacional de la OMS.
          </p>

          <div class="cie-search-panel">
            <!-- Barra de Búsqueda Principal -->
            <div class="cie-search-bar">
              <label class="form-label fw-semibold">Buscar Código o Criterio Diagnóstico CIE-10 / OMS</label>
              <div class="cie-input-group">
                <i class="fa-solid fa-magnifying-glass cie-group-icon"></i>
                <input
                  type="text"
                  class="form-control cie-main-input"
                  [(ngModel)]="busquedaCieQuery"
                  (ngModelChange)="onBuscarCie($event)"
                  placeholder="Escriba aquí para buscar diagnósticos (ej. ansiedad, depresión, F41, estrés, fobia)..."
                />
                <button *ngIf="busquedaCieQuery" type="button" class="btn btn-sm btn-light cie-clear-btn" (click)="limpiarBusquedaCie()">
                  <i class="fa-solid fa-xmark me-1"></i> Borrar
                </button>
              </div>
            </div>

            <!-- LISTA VISIBLE EN PANTALLA: Opciones Encontradas mientras el usuario escribe -->
            <div *ngIf="resultadosCie().length > 0" class="cie-results-card">
              <div class="cie-results-header">
                <div>
                  <i class="fa-solid fa-list-check text-primary me-2"></i>
                  <strong>Opciones diagnósticas encontradas ({{ resultadosCie().length }}):</strong>
                  <span class="text-muted ms-2 small">Haga clic en una opción para seleccionarla</span>
                </div>
                <span class="badge bg-primary">{{ resultadosCie().length }} coincidencias</span>
              </div>
              <div class="cie-results-list">
                <div 
                  *ngFor="let item of resultadosCie()" 
                  class="cie-result-item" 
                  [class.is-selected]="nuevoDiagnostico.codigo_cie10 === item.codigo"
                  (click)="seleccionarCie(item)">
                  <div class="cie-item-content">
                    <span class="cie-code-pill">{{ item.codigo }}</span>
                    <span class="cie-desc-label">{{ item.descripcion }}</span>
                  </div>
                  <button type="button" class="btn btn-sm" [ngClass]="nuevoDiagnostico.codigo_cie10 === item.codigo ? 'btn-success' : 'btn-outline-primary'">
                    <i class="fa-solid" [ngClass]="nuevoDiagnostico.codigo_cie10 === item.codigo ? 'fa-check' : 'fa-hand-pointer'"></i>
                    {{ nuevoDiagnostico.codigo_cie10 === item.codigo ? 'Seleccionado' : 'Elegir' }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Accesos Rápidos Frecuentes (para selección inmediata con 1 clic) -->
            <div class="cie-quick-chips">
              <span class="cie-chips-label"><i class="fa-solid fa-bolt text-warning me-1"></i> Frecuentes:</span>
              <button type="button" class="cie-chip" (click)="seleccionarCieRapido('F41.1', 'Trastorno de ansiedad generalizada (TAG)')">
                <strong>F41.1</strong> Ansiedad Generalizada
              </button>
              <button type="button" class="cie-chip" (click)="seleccionarCieRapido('F32.1', 'Episodio depresivo moderado')">
                <strong>F32.1</strong> Depresión Moderada
              </button>
              <button type="button" class="cie-chip" (click)="seleccionarCieRapido('F43.1', 'Trastorno por estrés postraumático (TEPT)')">
                <strong>F43.1</strong> Estrés Postraumático
              </button>
              <button type="button" class="cie-chip" (click)="seleccionarCieRapido('F42.2', 'Actos y pensamientos obsesivos mixtos (TOC)')">
                <strong>F42.2</strong> TOC Mixto
              </button>
              <button type="button" class="cie-chip" (click)="seleccionarCieRapido('F90.0', 'Perturbación de la actividad y de la atención (TDAH)')">
                <strong>F90.0</strong> TDAH
              </button>
            </div>

            <!-- Panel de Asignación con Diagnóstico Elegido -->
            <div class="cie-assign-panel">
              <div class="row-fields">
                <div class="field-selected">
                  <label class="form-label fw-semibold">Diagnóstico a Asignar</label>
                  <div class="selected-display-box" [class.has-selection]="nuevoDiagnostico.codigo_cie10">
                    <div *ngIf="nuevoDiagnostico.codigo_cie10" class="d-flex align-items-center justify-content-between w-100">
                      <div>
                        <strong class="text-success me-2"><i class="fa-solid fa-circle-check"></i> [{{ nuevoDiagnostico.codigo_cie10 }}]</strong>
                        <span class="fw-semibold text-dark">{{ nuevoDiagnostico.descripcion }}</span>
                      </div>
                      <button type="button" class="btn-clean" (click)="deseleccionarCie()" title="Quitar selección">×</button>
                    </div>
                    <div *ngIf="!nuevoDiagnostico.codigo_cie10" class="text-muted small">
                      <i class="fa-solid fa-arrow-up me-1"></i> Escriba arriba o elija un acceso frecuente para seleccionar el diagnóstico.
                    </div>
                  </div>
                </div>

                <div class="field-hierarchy">
                  <label class="form-label fw-semibold">Jerarquía Diagnóstica</label>
                  <select class="form-select" [(ngModel)]="nuevoDiagnostico.tipo">
                    <option value="PRINCIPAL">Principal</option>
                    <option value="SECUNDARIO">Secundario / Comorbilidad</option>
                    <option value="PRESUNTIVO">Presuntivo / En Estudio</option>
                    <option value="DESCARTADO">Descartado</option>
                  </select>
                </div>

                <div class="field-button">
                  <button 
                    class="btn btn-primary w-100 btn-assign-action" 
                    [disabled]="!nuevoDiagnostico.codigo_cie10"
                    (click)="agregarDiagnostico()">
                    <i class="fa-solid fa-plus-circle me-1"></i> Asignar al Expediente
                  </button>
                </div>
              </div>

              <!-- Notas adicionales / Justificación (Opcional) -->
              <div class="mt-2" *ngIf="nuevoDiagnostico.codigo_cie10">
                <input 
                  type="text" 
                  class="form-control form-control-sm" 
                  [(ngModel)]="nuevoDiagnostico.notas_criterio"
                  placeholder="Notas clínicas de respaldo diagnóstico o criterios DSM-5/CIE-10 observados (opcional)..." 
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Tabla de Diagnósticos Asignados -->
        <div class="section-card glass-panel">
          <h3 class="section-heading mb-3">Diagnósticos Asignados a la Historia</h3>

          <div *ngIf="!historia()?.diagnosticos || historia()?.diagnosticos?.length === 0" class="text-muted p-4 text-center">
            <i class="fa-solid fa-clipboard-check fa-2x text-dim mb-2"></i>
            <p>No se han registrado diagnósticos codificados para este paciente.</p>
          </div>

          <div class="table-responsive" *ngIf="historia()?.diagnosticos && (historia()?.diagnosticos?.length || 0) > 0">
            <table class="custom-table">
              <thead>
                <tr>
                  <th>Código CIE-10</th>
                  <th>Denominación Oficial OMS</th>
                  <th>Jerarquía</th>
                  <th>Fecha Registro</th>
                  <th>Criterios / Notas</th>
                  <th class="text-end">Acción</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let diag of historia()?.diagnosticos">
                  <td><span class="hc-badge">{{ diag.codigo_cie10 }}</span></td>
                  <td><strong>{{ diag.descripcion }}</strong></td>
                  <td>
                    <span class="badge" [ngClass]="getTipoBadge(diag.tipo)">
                      {{ diag.tipo }}
                    </span>
                  </td>
                  <td>{{ diag.fecha_diagnostico | date:'dd/MM/yyyy' }}</td>
                  <td><span class="text-muted small">{{ diag.notas_criterio || 'Sin notas.' }}</span></td>
                  <td class="text-end">
                    <button class="btn btn-sm btn-outline-danger" (click)="removerDiagnostico(diag.id)" title="Remover diagnóstico">
                      <i class="fa-solid fa-trash"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- TAB 3: PLAN TERAPÉUTICO -->
      <div *ngIf="activeTab === 'plan'" class="tab-content-panel">
        <div class="section-card glass-panel mb-4">
          <div class="section-header">
            <h3 class="section-heading"><i class="fa-solid fa-bullseye text-primary me-2"></i>Estrategia y Plan Terapéutico</h3>
            <button class="btn btn-sm btn-outline-primary" *ngIf="!editandoPlan" (click)="editandoPlan = true">
              <i class="fa-solid fa-pen"></i> Editar Plan
            </button>
            <button class="btn btn-sm btn-success" *ngIf="editandoPlan" (click)="guardarCambiosPlan()">
              <i class="fa-solid fa-check"></i> Guardar
            </button>
          </div>
          <div *ngIf="!editandoPlan" class="content-block">
            <p>{{ historia()?.plan_terapeutico || 'Sin plan terapéutico formalizado.' }}</p>
          </div>
          <div *ngIf="editandoPlan">
            <textarea class="form-control" [(ngModel)]="planForm.plan_terapeutico" rows="5"></textarea>
          </div>
        </div>
      </div>

      <!-- TAB 4: LÍNEA DE TIEMPO LONGITUDINAL (CU17 / HU-28) -->
      <div *ngIf="activeTab === 'timeline'" class="tab-content-panel">
        <div class="section-card glass-panel">
          <div class="section-header mb-3">
            <h3 class="section-heading">
              <i class="fa-solid fa-timeline text-primary me-2"></i>
              Evolución Longitudinal del Tratamiento
            </h3>
            <span class="badge bg-light text-dark">{{ timelineEvents().length }} Eventos Registrados</span>
          </div>

          <div *ngIf="cargandoTimeline()" class="text-center p-4">
            <i class="fa-solid fa-spinner fa-spin fa-2x text-primary mb-2"></i>
            <p class="text-muted">Consolidando línea de tiempo clínica...</p>
          </div>

          <div *ngIf="!cargandoTimeline() && timelineEvents().length === 0" class="text-center p-5 text-muted">
            <i class="fa-solid fa-clock-rotate-left fa-3x text-dim mb-3"></i>
            <p>No hay eventos clínicos registrados aún en el expediente.</p>
          </div>

          <div class="timeline-stream" *ngIf="!cargandoTimeline() && timelineEvents().length > 0">
            <div *ngFor="let ev of timelineEvents()" class="timeline-entry" [class.entry-crisis]="ev.alerta">
              <div class="timeline-icon-column">
                <div class="timeline-circle" [ngClass]="getTimelineIconClass(ev.tipo, ev.alerta)">
                  <i class="fa-solid" [ngClass]="getTimelineIcon(ev.tipo, ev.alerta)"></i>
                </div>
                <div class="timeline-line"></div>
              </div>

              <div class="timeline-body glass-panel">
                <div class="d-flex justify-content-between align-items-center mb-1">
                  <div class="d-flex align-items-center gap-2">
                    <span class="timeline-type-badge" [ngClass]="'badge-' + ev.tipo.toLowerCase()">{{ ev.tipo }}</span>
                    <h4 class="timeline-event-title m-0">{{ ev.titulo }}</h4>
                  </div>
                  <span class="timeline-date">{{ ev.fecha | date:'dd/MM/yyyy HH:mm' }}</span>
                </div>

                <p class="timeline-detail mb-2">{{ ev.detalle }}</p>

                <!-- Alerta Roja de Crisis de Recaída (HU-28) -->
                <div *ngIf="ev.alerta" class="crisis-alert-callout p-2 rounded mb-2">
                  <i class="fa-solid fa-triangle-exclamation text-danger me-1"></i>
                  <strong>ALERTA DE RECAÍDA / CRISIS:</strong>
                  <span>{{ ev.metadata?.descripcion_crisis || 'Indicador agudo detectado.' }}</span>
                  <div *ngIf="ev.metadata?.recomendacion_inmediata" class="small text-danger-emphasis mt-1">
                    <i class="fa-solid fa-hand-holding-medical me-1"></i> Plan de contingencia: {{ ev.metadata?.recomendacion_inmediata }}
                  </div>
                </div>

                <div class="timeline-meta small text-muted d-flex gap-3">
                  <span *ngIf="ev.profesional"><i class="fa-solid fa-user-doctor me-1"></i> {{ ev.profesional }}</span>
                  <span *ngIf="ev.metadata?.riesgo"><i class="fa-solid fa-shield-virus me-1"></i> Riesgo: {{ ev.metadata?.riesgo }}</span>
                  <span *ngIf="ev.metadata?.progreso"><i class="fa-solid fa-chart-line me-1"></i> Progreso: {{ ev.metadata?.progreso }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- MODAL ASIGNACIÓN DE TAREA TERAPÉUTICA -->
      <div *ngIf="mostrarModalTarea" class="modal-backdrop-custom" (click)="mostrarModalTarea = false">
        <div class="modal-dialog-custom glass-card-modal" (click)="$event.stopPropagation()">
          <div class="modal-header-custom">
            <h2 class="modal-title">
              <i class="fa-solid fa-list-check text-primary me-2"></i> Asignar Tarea Terapéutica Inter-Sesión
            </h2>
            <button class="btn-close-custom" (click)="mostrarModalTarea = false"><i class="fa-solid fa-xmark"></i></button>
          </div>

          <div class="modal-body-custom">
            <div class="mb-3">
              <label class="form-label">Título de la Tarea *</label>
              <input type="text" class="form-control" [(ngModel)]="nuevaTarea.titulo" 
                     placeholder="Ej. Registro de pensamientos distorsionados triada cognitiva" />
            </div>

            <div class="row g-3 mb-3">
              <div class="col-md-6">
                <label class="form-label">Categoría Terapéutica</label>
                <select class="form-select" [(ngModel)]="nuevaTarea.categoria">
                  <option value="REGISTRO_PENSAMIENTOS">Registro de Pensamientos (TCC)</option>
                  <option value="CONDUCTUAL">Activación Conductual</option>
                  <option value="MINDFULNESS">Mindfulness / Respiración</option>
                  <option value="LECTURA">Psicoeducación / Lectura</option>
                  <option value="OTRO">Otra Intervención</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label">Fecha Límite *</label>
                <input type="date" class="form-control" [(ngModel)]="nuevaTarea.fecha_limite" />
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label">Instrucciones y Pautas para el Paciente *</label>
              <textarea class="form-control" [(ngModel)]="nuevaTarea.instrucciones" rows="3"
                        placeholder="Detalle los pasos concretos que el paciente debe realizar entre sesiones..."></textarea>
            </div>
          </div>

          <div class="modal-footer-custom">
            <button class="btn btn-secondary" (click)="mostrarModalTarea = false">Cancelar</button>
            <button class="btn btn-primary" [disabled]="!nuevaTarea.titulo || !nuevaTarea.fecha_limite" (click)="guardarTarea()">
              <i class="fa-solid fa-paper-plane me-1"></i> Asignar Tarea
            </button>
          </div>
        </div>
      </div>

    </div>
  `,
  styles: [`
    .ehr-detail-container { max-width: 1300px; margin: 0 auto; }
    .patient-header {
      padding: 1.5rem 2rem; border-radius: 16px; background: #ffffff; border: 1px solid #e2e8f0;
      display: flex; justify-content: space-between; align-items: center;
    }
    .patient-header-left { display: flex; align-items: center; gap: 1.25rem; }
    .patient-avatar-large {
      width: 56px; height: 56px; border-radius: 50%; background: #e0e7ff; color: #4338ca;
      font-size: 1.5rem; font-weight: 800; display: flex; align-items: center; justify-content: center;
    }
    .patient-name { font-size: 1.5rem; font-weight: 700; color: #0f172a; margin: 0; }
    .hc-badge {
      font-family: monospace; font-weight: 700; color: #0284c7; background: #e0f2fe;
      padding: 0.2rem 0.6rem; border-radius: 6px; font-size: 0.85rem;
    }
    .status-pill { font-size: 0.72rem; font-weight: 700; padding: 0.2rem 0.6rem; border-radius: 9999px; }
    .status-pill.active { background: #dcfce7; color: #166534; }
    .status-pill.closed { background: #fee2e2; color: #991b1b; }
    .patient-meta { margin: 0.35rem 0 0 0; font-size: 0.85rem; color: #64748b; display: flex; gap: 1.5rem; }
    .header-action-buttons { display: flex; gap: 0.5rem; }

    .tabs-nav {
      display: flex; gap: 0.5rem; padding: 0.5rem; background: #f1f5f9; border-radius: 12px;
    }
    .tab-item {
      padding: 0.65rem 1.25rem; border: none; background: transparent; color: #64748b;
      font-weight: 600; font-size: 0.9rem; border-radius: 8px; cursor: pointer;
      display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s ease;
    }
    .tab-item.active { background: #ffffff; color: #0284c7; box-shadow: 0 2px 4px rgba(0,0,0,0.06); }

    .section-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 1.5rem; }
    .section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
    .section-heading { font-size: 1.1rem; font-weight: 700; color: #0f172a; margin: 0; }
    .content-block { font-size: 0.92rem; color: #334155; line-height: 1.6; white-space: pre-line; }

    /* Buscador y Lista de Resultados CIE-10 (HU-25 / HU-26) */
    .cie-search-panel { display: flex; flex-direction: column; gap: 1rem; width: 100%; }
    .cie-search-bar { width: 100%; }
    .cie-input-group { position: relative; width: 100%; display: flex; align-items: center; }
    .cie-group-icon {
      position: absolute; left: 1.1rem; color: #0d9488; font-size: 1.05rem; pointer-events: none;
    }
    .cie-main-input {
      padding-left: 2.85rem; padding-right: 6rem; height: 46px;
      border: 2px solid #cbd5e1; border-radius: 12px; font-size: 0.95rem; width: 100%;
      background: #ffffff; transition: all 0.2s ease;
    }
    .cie-main-input:focus {
      border-color: #0d9488; box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.15); outline: none;
    }
    .cie-clear-btn {
      position: absolute; right: 0.6rem; border-radius: 8px; font-size: 0.8rem;
    }

    /* Lista Visible de Opciones Encontradas en Flujo Normal */
    .cie-results-card {
      background: #ffffff; border: 2px solid #0d9488; border-radius: 12px;
      box-shadow: 0 8px 16px -4px rgba(13, 148, 136, 0.12); overflow: hidden; width: 100%;
    }
    .cie-results-header {
      background: #f0fdfa; padding: 0.7rem 1.25rem; border-bottom: 1px solid #ccfbf1;
      display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; color: #0f766e;
    }
    .cie-results-list {
      max-height: 240px; overflow-y: auto; display: flex; flex-direction: column;
    }
    .cie-result-item {
      display: flex; justify-content: space-between; align-items: center;
      padding: 0.75rem 1.25rem; border-bottom: 1px solid #f1f5f9; cursor: pointer;
      transition: background 0.15s ease;
    }
    .cie-result-item:last-child { border-bottom: none; }
    .cie-result-item:hover { background: #f8fafc; }
    .cie-result-item.is-selected { background: #ecfdf5; border-left: 4px solid #10b981; }
    .cie-item-content { display: flex; align-items: center; gap: 0.85rem; flex: 1; }
    .cie-code-pill {
      font-family: ui-monospace, monospace; font-weight: 800; color: #0d9488;
      background: #ccfbf1; padding: 0.2rem 0.6rem; border-radius: 6px; font-size: 0.88rem;
    }
    .cie-desc-label { font-size: 0.92rem; font-weight: 600; color: #1e293b; }

    /* Chips de Selección Rápida CIE-10 */
    .cie-quick-chips { display: flex; align-items: center; flex-wrap: wrap; gap: 0.5rem; }
    .cie-chips-label { font-size: 0.82rem; font-weight: 700; color: #64748b; }
    .cie-chip {
      background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 9999px;
      padding: 0.3rem 0.8rem; font-size: 0.8rem; color: #334155; cursor: pointer;
      display: inline-flex; align-items: center; gap: 0.35rem; transition: all 0.15s ease;
    }
    .cie-chip strong { color: #0d9488; }
    .cie-chip:hover { background: #ccfbf1; border-color: #5eead4; color: #0f766e; transform: translateY(-1px); }

    /* Panel de Asignación y Jerarquía */
    .cie-assign-panel {
      background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; width: 100%;
    }
    .row-fields {
      display: flex; gap: 1rem; align-items: flex-end; flex-wrap: wrap;
    }
    .field-selected { flex: 1 1 360px; min-width: 280px; }
    .field-hierarchy { flex: 0 0 220px; }
    .field-button { flex: 0 0 220px; }

    .selected-display-box {
      min-height: 44px; background: #ffffff; border: 1.5px dashed #cbd5e1; border-radius: 10px;
      padding: 0.55rem 1rem; display: flex; align-items: center;
    }
    .selected-display-box.has-selection {
      border: 1.5px solid #10b981; background: #f0fdf4;
    }
    .btn-clean {
      background: none; border: none; font-size: 1.25rem; line-height: 1; cursor: pointer;
      color: #94a3b8; padding: 0 0.3rem;
    }
    .btn-clean:hover { color: #ef4444; }

    .btn-assign-action {
      height: 44px; font-weight: 600; border-radius: 10px;
      display: flex; align-items: center; justify-content: center; gap: 0.5rem;
      background: #0d9488; border-color: #0d9488; color: #ffffff;
      box-shadow: 0 2px 6px rgba(13, 148, 136, 0.25); cursor: pointer; transition: all 0.2s ease;
    }
    .btn-assign-action:hover:not(:disabled) {
      background: #0f766e; border-color: #0f766e; transform: translateY(-1px);
    }
    .btn-assign-action:disabled {
      background: #94a3b8; border-color: #94a3b8; opacity: 0.65; cursor: not-allowed; box-shadow: none;
    }
    .btn-close-sm { background: none; border: none; font-size: 1.25rem; line-height: 1; cursor: pointer; color: #64748b; }

    .custom-table { width: 100%; border-collapse: collapse; }
    .custom-table th { background: #f8fafc; padding: 0.85rem 1rem; font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; }
    .custom-table td { padding: 0.85rem 1rem; font-size: 0.85rem; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }

    .badge-principal { background: #e0f2fe; color: #0369a1; }
    .badge-secundario { background: #f1f5f9; color: #475569; }
    .badge-presuntivo { background: #fef9c3; color: #854d0e; }
    .badge-descartado { background: #fee2e2; color: #991b1b; }

    .timeline-stream { display: flex; flex-direction: column; gap: 1rem; position: relative; padding-left: 1rem; }
    .timeline-entry { display: flex; gap: 1.25rem; position: relative; }
    .timeline-icon-column { display: flex; flex-direction: column; align-items: center; }
    .timeline-circle {
      width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center;
      justify-content: center; font-size: 1rem; z-index: 2;
    }
    .timeline-line { flex: 1; width: 2px; background: #e2e8f0; margin-top: 4px; }
    .timeline-body { flex: 1; padding: 1rem 1.25rem; border-radius: 12px; background: #f8fafc; border: 1px solid #e2e8f0; }
    .entry-crisis .timeline-body { border-color: #fca5a5; background: #fff5f5; }

    .timeline-type-badge { font-size: 0.68rem; font-weight: 700; padding: 0.15rem 0.5rem; border-radius: 4px; text-transform: uppercase; }
    .badge-sesion { background: #e0f2fe; color: #0369a1; }
    .badge-evolucion { background: #dcfce7; color: #166534; }
    .badge-tarea { background: #f3e8ff; color: #6b21a8; }
    .badge-consentimiento { background: #ffedd5; color: #c2410c; }
    .badge-derivacion { background: #fee2e2; color: #991b1b; }

    .crisis-alert-callout { background: #fee2e2; border-left: 4px solid #ef4444; }

    .modal-backdrop-custom {
      position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
      background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px); z-index: 1050;
      display: flex; align-items: center; justify-content: center; padding: 1.5rem;
    }
    .modal-dialog-custom {
      width: 100%; max-width: 650px; background: #ffffff; border-radius: 16px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); display: flex; flex-direction: column; overflow: hidden;
    }
    .modal-header-custom { padding: 1.25rem 1.5rem; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
    .modal-body-custom { padding: 1.25rem 1.5rem; }
    .modal-footer-custom { padding: 1rem 1.5rem; border-top: 1px solid #e2e8f0; background: #f8fafc; display: flex; justify-content: flex-end; gap: 0.75rem; }
  `]
})
export class HistoriaClinicaDetalleComponent implements OnInit {
  historiaId!: string;
  historia = signal<HistoriaClinica | null>(null);
  activeTab: 'anamnesis' | 'diagnosticos' | 'plan' | 'timeline' = 'anamnesis';
  feedbackMensaje = signal<string | null>(null);
  accesoRestringido = signal<boolean>(false);
  errorMensajeAcceso = signal<string>('');

  // Tab 1 Edit
  editandoAnamnesis = false;
  anamnesisForm = {
    motivo_consulta_inicial: '',
    antecedentes_personales: '',
    antecedentes_familiares: '',
    examen_estado_mental: ''
  };

  // Tab 2 CIE-10 Search
  busquedaCieQuery = '';
  resultadosCie = signal<CieItem[]>([]);
  nuevoDiagnostico = {
    codigo_cie10: '',
    descripcion: '',
    tipo: 'PRINCIPAL' as 'PRINCIPAL' | 'SECUNDARIO' | 'PRESUNTIVO' | 'DESCARTADO',
    notas_criterio: ''
  };

  // Tab 3 Plan Edit
  editandoPlan = false;
  planForm = { plan_terapeutico: '' };

  // Tab 4 Timeline
  cargandoTimeline = signal<boolean>(false);
  timelineEvents = signal<any[]>([]);

  // Modal Asignar Tarea
  mostrarModalTarea = false;
  nuevaTarea = {
    titulo: '',
    instrucciones: '',
    categoria: 'REGISTRO_PENSAMIENTOS',
    fecha_limite: ''
  };

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private clinicaService: ClinicaSprint2Service
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.historiaId = params['id'];
      if (this.historiaId) {
        this.cargarHistoria();
      }
    });
  }

  cargarHistoria(): void {
    this.accesoRestringido.set(false);
    this.clinicaService.getHistoriaClinicaById(this.historiaId).subscribe({
      next: (hc) => {
        this.historia.set(hc);
        this.anamnesisForm = {
          motivo_consulta_inicial: hc.motivo_consulta_inicial || '',
          antecedentes_personales: hc.antecedentes_personales || '',
          antecedentes_familiares: hc.antecedentes_familiares || '',
          examen_estado_mental: hc.examen_estado_mental || ''
        };
        this.planForm = { plan_terapeutico: hc.plan_terapeutico || '' };
      },
      error: (err) => {
        if (err.status === 403) {
          this.accesoRestringido.set(true);
          this.errorMensajeAcceso.set(
            err?.error?.detail ||
            err?.error?.message ||
            'Acceso denegado: El expediente clínico está protegido y reservado exclusivamente al psicólogo tratante asignado (HU-26).'
          );
        } else {
          this.router.navigate(['/historias-clinicas']);
        }
      }
    });
  }

  guardarCambiosAnamnesis(): void {
    this.clinicaService.actualizarHistoriaClinica(this.historiaId, this.anamnesisForm).subscribe({
      next: (actualizada) => {
        this.historia.set(actualizada);
        this.editandoAnamnesis = false;
        this.mostrarFeedback('Anamnesis y EEM actualizados correctamente');
      }
    });
  }

  guardarCambiosPlan(): void {
    this.clinicaService.actualizarHistoriaClinica(this.historiaId, this.planForm).subscribe({
      next: (actualizada) => {
        this.historia.set(actualizada);
        this.editandoPlan = false;
        this.mostrarFeedback('Plan terapéutico actualizado con éxito');
      }
    });
  }

  onBuscarCie(query: string): void {
    if (!query || query.trim().length < 2) {
      this.resultadosCie.set([]);
      return;
    }
    this.clinicaService.buscarCIE10(query.trim()).subscribe({
      next: (items) => this.resultadosCie.set(items),
      error: () => this.resultadosCie.set([])
    });
  }

  limpiarBusquedaCie(): void {
    this.busquedaCieQuery = '';
    this.resultadosCie.set([]);
  }

  seleccionarCieRapido(codigo: string, descripcion: string): void {
    this.nuevoDiagnostico.codigo_cie10 = codigo;
    this.nuevoDiagnostico.descripcion = descripcion;
    this.busquedaCieQuery = `${codigo} - ${descripcion}`;
    this.resultadosCie.set([]);
  }

  deseleccionarCie(): void {
    this.nuevoDiagnostico.codigo_cie10 = '';
    this.nuevoDiagnostico.descripcion = '';
    this.nuevoDiagnostico.notas_criterio = '';
    this.busquedaCieQuery = '';
  }

  seleccionarCie(item: CieItem): void {
    this.nuevoDiagnostico.codigo_cie10 = item.codigo;
    this.nuevoDiagnostico.descripcion = item.descripcion;
    this.resultadosCie.set([]);
    this.busquedaCieQuery = `${item.codigo} - ${item.descripcion}`;
  }

  agregarDiagnostico(): void {
    if (!this.nuevoDiagnostico.codigo_cie10) return;
    const codigo = this.nuevoDiagnostico.codigo_cie10;
    this.clinicaService.agregarDiagnostico(this.historiaId, this.nuevoDiagnostico).subscribe({
      next: () => {
        this.mostrarFeedback(`Diagnóstico [${codigo}] asignado exitosamente al expediente`);
        this.nuevoDiagnostico = {
          codigo_cie10: '',
          descripcion: '',
          tipo: 'PRINCIPAL',
          notas_criterio: ''
        };
        this.busquedaCieQuery = '';
        this.cargarHistoria();
      },
      error: (err) => {
        console.error('Error al agregar diagnóstico:', err);
        const detalle = err?.error?.detail || (typeof err?.error === 'object' ? JSON.stringify(err?.error) : '') || 'Error al guardar';
        this.mostrarFeedback(`Error al asignar diagnóstico: ${detalle}`);
      }
    });
  }

  removerDiagnostico(diagId: string): void {
    this.clinicaService.removerDiagnostico(this.historiaId, diagId).subscribe({
      next: () => {
        this.mostrarFeedback('Diagnóstico removido del expediente');
        this.cargarHistoria();
      }
    });
  }

  cambiarATimeline(): void {
    this.activeTab = 'timeline';
    this.cargandoTimeline.set(true);
    this.clinicaService.getTimeline(this.historiaId).subscribe({
      next: (res) => {
        this.timelineEvents.set(res.timeline || []);
        this.cargandoTimeline.set(false);
      },
      error: () => this.cargandoTimeline.set(false)
    });
  }

  abrirModalTarea(): void {
    const d = new Date();
    d.setDate(d.getDate() + 7);
    this.nuevaTarea = {
      titulo: '',
      instrucciones: '',
      categoria: 'REGISTRO_PENSAMIENTOS',
      fecha_limite: d.toISOString().substring(0, 10)
    };
    this.mostrarModalTarea = true;
  }

  guardarTarea(): void {
    const payload = {
      historia_clinica: this.historiaId,
      ...this.nuevaTarea
    };
    this.clinicaService.crearTarea(payload).subscribe({
      next: () => {
        this.mostrarModalTarea = false;
        this.mostrarFeedback('Tarea terapéutica asignada al paciente');
      }
    });
  }

  getTipoBadge(tipo: string): string {
    switch (tipo) {
      case 'PRINCIPAL': return 'badge-principal';
      case 'SECUNDARIO': return 'badge-secundario';
      case 'PRESUNTIVO': return 'badge-presuntivo';
      default: return 'badge-descartado';
    }
  }

  getTimelineIcon(tipo: string, alerta: boolean): string {
    if (alerta) return 'fa-triangle-exclamation';
    switch (tipo) {
      case 'SESION': return 'fa-comment-medical';
      case 'EVOLUCION': return 'fa-chart-line';
      case 'TAREA': return 'fa-list-check';
      case 'CONSENTIMIENTO': return 'fa-file-signature';
      case 'DERIVACION': return 'fa-share-from-square';
      default: return 'fa-circle-dot';
    }
  }

  getTimelineIconClass(tipo: string, alerta: boolean): string {
    if (alerta) return 'bg-danger text-white';
    switch (tipo) {
      case 'SESION': return 'bg-primary text-white';
      case 'EVOLUCION': return 'bg-success text-white';
      case 'TAREA': return 'bg-purple text-white';
      case 'CONSENTIMIENTO': return 'bg-warning text-dark';
      case 'DERIVACION': return 'bg-danger text-white';
      default: return 'bg-secondary text-white';
    }
  }

  mostrarFeedback(msg: string): void {
    this.feedbackMensaje.set(msg);
    setTimeout(() => this.feedbackMensaje.set(null), 3500);
  }
}
