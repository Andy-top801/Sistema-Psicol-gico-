// ==============================================================================
// MÓDULO: intake-config.component.ts
// CAPA BCE: BOUNDARY (Interfaz de Usuario) — IU_IntakeDigital
// CASOS DE USO: CU14: Configuración y Revisión de Cuestionarios Pre-Consulta (HU-23, HU-24)
//              HU-35: Asistente Piloto de Preconsulta con IA (Supervisión Humana)
// ==============================================================================
import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ClinicaSprint2Service } from '../../core/services/clinica-sprint2.service';
import { FormularioPreConsulta, RespuestaPreConsulta } from '../../core/models/clinica-sprint2.model';
import { IaAsistenteModalComponent } from './ia-asistente-modal.component';

@Component({
  selector: 'app-intake-config',
  standalone: true,
  imports: [CommonModule, FormsModule, IaAsistenteModalComponent],
  template: `
    <div class="intake-container">
      <!-- Encabezado Principal -->
      <div class="page-header glass-panel mb-4">
        <div class="header-content">
          <h1 class="page-title">
            <i class="fa-solid fa-clipboard-question text-primary"></i>
            Intake Digital & Cuestionarios Pre-Consulta
          </h1>
          <p class="page-subtitle">
            Instrumentos psicométricos y cuestionarios anamnésicos previos a la primera cita.
            Procesamiento clínico con motor de IA supervisada (Sprint 2 - HU-23, HU-24, HU-35).
          </p>
        </div>
        <div class="header-actions">
          <button class="btn btn-outline-primary me-2" (click)="activeTab = 'respuestas'">
            <i class="fa-solid fa-inbox"></i> Respuestas Pacientes ({{ respuestas().length }})
          </button>
          <button class="btn btn-primary" (click)="openCreateModal()">
            <i class="fa-solid fa-plus"></i> Nuevo Cuestionario
          </button>
        </div>
      </div>

      <!-- Navegación por Pestañas -->
      <div class="tabs-bar glass-panel mb-4">
        <button class="tab-btn" [class.active]="activeTab === 'formularios'" (click)="activeTab = 'formularios'">
          <i class="fa-solid fa-file-lines"></i>
          Plantillas de Cuestionarios ({{ formularios().length }})
        </button>
        <button class="tab-btn" [class.active]="activeTab === 'respuestas'" (click)="activeTab = 'respuestas'">
          <i class="fa-solid fa-clipboard-check"></i>
          Respuestas Recibidas de Pacientes ({{ respuestas().length }})
        </button>
      </div>

      <!-- Notificación Flotante -->
      <div *ngIf="mensajeExito()" class="alert alert-success d-flex align-items-center mb-4">
        <i class="fa-solid fa-circle-check me-2"></i>
        <span>{{ mensajeExito() }}</span>
      </div>

      <!-- TAB 1: PLANTILLAS DE FORMULARIOS -->
      <div *ngIf="activeTab === 'formularios'">
        <div *ngIf="cargando()" class="loading-state glass-panel">
          <i class="fa-solid fa-spinner fa-spin fa-2x text-primary mb-3"></i>
          <span>Cargando plantillas de cuestionarios...</span>
        </div>

        <div *ngIf="!cargando() && formularios().length === 0" class="empty-state glass-panel text-center p-5">
          <i class="fa-solid fa-file-circle-plus fa-3x text-dim mb-3"></i>
          <h3>No hay cuestionarios pre-consulta configurados</h3>
          <p class="text-muted">Cree el primer formulario pre-consulta para que los pacientes respondan antes de su cita.</p>
          <button class="btn btn-primary mt-2" (click)="openCreateModal()">
            <i class="fa-solid fa-plus"></i> Configurar Cuestionario
          </button>
        </div>

        <div class="cards-grid" *ngIf="!cargando() && formularios().length > 0">
          <div class="questionnaire-card glass-panel" *ngFor="let form of formularios()">
            <div class="card-header-row">
              <div class="version-badge">v{{ form.version }}.0</div>
              <span class="status-pill" [class.active]="form.activo">
                {{ form.activo ? 'ACTIVO' : 'INACTIVO' }}
              </span>
            </div>
            <h3 class="form-title">{{ form.titulo }}</h3>
            <p class="form-desc">{{ form.descripcion || 'Sin descripción clínica.' }}</p>
            
            <div class="form-meta">
              <span><i class="fa-solid fa-list-check"></i> {{ form.preguntas_json.length }} preguntas</span>
              <span><i class="fa-solid fa-calendar"></i> {{ form.fecha_creacion | date:'dd/MM/yyyy' }}</span>
            </div>

            <div class="questions-preview">
              <span class="preview-label">Muestra de preguntas:</span>
              <ul>
                <li *ngFor="let q of form.preguntas_json.slice(0, 3)">
                  {{ q.texto }} <span class="badge-type">({{ q.tipo }})</span>
                </li>
              </ul>
            </div>

            <div class="card-actions">
              <button class="btn btn-sm btn-outline-secondary" (click)="verDetalleFormulario(form)">
                <i class="fa-solid fa-eye"></i> Ver Preguntas
              </button>
              <button class="btn btn-sm btn-outline-primary" (click)="duplicarOEditar(form)">
                <i class="fa-solid fa-pen"></i> Editar
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB 2: RESPUESTAS RECIBIDAS -->
      <div *ngIf="activeTab === 'respuestas'">
        <div *ngIf="cargando()" class="loading-state glass-panel">
          <i class="fa-solid fa-spinner fa-spin fa-2x text-primary mb-3"></i>
          <span>Cargando respuestas de pacientes...</span>
        </div>

        <div *ngIf="!cargando() && respuestas().length === 0" class="empty-state glass-panel text-center p-5">
          <i class="fa-solid fa-inbox fa-3x text-dim mb-3"></i>
          <h3>No se han recibido respuestas de pre-consulta</h3>
          <p class="text-muted">Cuando los pacientes completen el intake previo a su cita, aparecerán aquí para revisión.</p>
        </div>

        <div class="table-responsive glass-panel" *ngIf="!cargando() && respuestas().length > 0">
          <table class="custom-table">
            <thead>
              <tr>
                <th>Paciente</th>
                <th>Cuestionario</th>
                <th>Fecha Respuesta</th>
                <th>Consentimiento IA</th>
                <th>Estado</th>
                <th class="text-end">Acciones Clínicas</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let r of respuestas()">
                <td>
                  <div class="patient-cell">
                    <div class="patient-avatar">{{ (r.paciente_nombre || 'P').charAt(0) }}</div>
                    <div>
                      <strong>{{ r.paciente_nombre || 'Paciente Registrado' }}</strong>
                      <small class="d-block text-muted">ID Cita: {{ (r.cita || '').toString().substring(0, 8) }}...</small>
                    </div>
                  </div>
                </td>
                <td>{{ r.formulario_titulo || 'Intake Psicológico Inicial' }}</td>
                <td>{{ (r.fecha_respuesta || '') | date:'dd/MM/yyyy HH:mm' }}</td>
                <td>
                  <span class="badge" [class.badge-success]="r.consentimiento_ia_procesamiento" [class.badge-secondary]="!r.consentimiento_ia_procesamiento">
                    <i class="fa-solid" [class.fa-check]="r.consentimiento_ia_procesamiento" [class.fa-ban]="!r.consentimiento_ia_procesamiento"></i>
                    {{ r.consentimiento_ia_procesamiento ? 'Otorgado' : 'No autorizado' }}
                  </span>
                </td>
                <td>
                  <span class="status-pill active">
                    <i class="fa-solid fa-check-double"></i> Completado
                  </span>
                </td>
                <td class="text-end">
                  <button class="btn btn-sm btn-info text-white me-2" (click)="verDetalleRespuesta(r)" title="Ver respuestas del paciente">
                    <i class="fa-solid fa-file-lines"></i> Ver Datos
                  </button>
                  <button 
                    class="btn btn-sm btn-ai-gradient" 
                    [disabled]="!r.consentimiento_ia_procesamiento"
                    (click)="abrirAsistenteIA(r)"
                    title="Ejecutar Asistente de IA (Reglas Romero)">
                    <i class="fa-solid fa-brain"></i> Asistente IA (HU-35)
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- MODAL: CREAR / EDITAR CUESTIONARIO -->
      <div *ngIf="mostrarModalForm" class="modal-backdrop-custom" (click)="mostrarModalForm = false">
        <div class="modal-dialog-custom glass-card-modal modal-lg" (click)="$event.stopPropagation()">
          <div class="modal-header-custom">
            <h2 class="modal-title">
              <i class="fa-solid fa-clipboard-question text-primary me-2"></i>
              Configurar Cuestionario Pre-Consulta (Intake)
            </h2>
            <button class="btn-close-custom" (click)="mostrarModalForm = false">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>

          <div class="modal-body-custom">
            <div class="row g-3 mb-3">
              <div class="col-md-8">
                <label class="form-label">Título del Instrumento / Cuestionario *</label>
                <input type="text" class="form-control" [(ngModel)]="nuevoFormulario.titulo" 
                       placeholder="Ej. Cuestionario de Sintomatología Inicial y Motivo de Consulta" />
              </div>
              <div class="col-md-4">
                <label class="form-label">Estado</label>
                <div class="form-check form-switch mt-2">
                  <input class="form-check-input" type="checkbox" [(ngModel)]="nuevoFormulario.activo" id="activoCheck" />
                  <label class="form-check-label" for="activoCheck">Publicado y Activo</label>
                </div>
              </div>
              <div class="col-12">
                <label class="form-label">Instrucciones o Descripción</label>
                <textarea class="form-control" [(ngModel)]="nuevoFormulario.descripcion" rows="2"
                          placeholder="Instrucciones para el paciente antes de responder..."></textarea>
              </div>
            </div>

            <!-- Editor de Preguntas Dinámicas -->
            <div class="questions-builder-panel glass-panel p-3 mb-3">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h4 class="m-0"><i class="fa-solid fa-list-ol text-primary me-2"></i>Banco de Preguntas</h4>
                <button class="btn btn-sm btn-outline-primary" (click)="agregarPregunta()">
                  <i class="fa-solid fa-plus"></i> Añadir Pregunta
                </button>
              </div>

              <div *ngFor="let p of nuevoFormulario.preguntas_json; let idx = index" class="question-row-card mb-2 p-2">
                <div class="d-flex align-items-center gap-2 mb-2">
                  <span class="badge bg-secondary">#{{ idx + 1 }}</span>
                  <input type="text" class="form-control form-control-sm flex-grow-1" [(ngModel)]="p.texto" 
                         placeholder="Escriba la pregunta o ítem clínico..." />
                  
                  <select class="form-select form-select-sm" [(ngModel)]="p.tipo" style="width: 170px;">
                    <option value="texto">Texto Libre</option>
                    <option value="escala_1_5">Escala Likert (1 - 5)</option>
                    <option value="booleano">Sí / No</option>
                    <option value="opcion_multiple">Opción Múltiple</option>
                  </select>

                  <div class="form-check form-check-inline m-0">
                    <input class="form-check-input" type="checkbox" [(ngModel)]="p.requerido" [id]="'req_' + idx">
                    <label class="form-check-label small" [for]="'req_' + idx">Obligatoria</label>
                  </div>

                  <button class="btn btn-sm btn-outline-danger" (click)="eliminarPregunta(idx)">
                    <i class="fa-solid fa-trash"></i>
                  </button>
                </div>

                <div *ngIf="p.tipo === 'opcion_multiple'" class="ps-4">
                  <input type="text" class="form-control form-control-sm" 
                         [ngModel]="(p.opciones || []).join(', ')"
                         (ngModelChange)="actualizarOpcionesPregunta(p, $event)"
                         placeholder="Opciones separadas por coma (ej. Casi nunca, A veces, Siempre)" />
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer-custom">
            <button class="btn btn-secondary" (click)="mostrarModalForm = false">Cancelar</button>
            <button class="btn btn-primary" [disabled]="!nuevoFormulario.titulo" (click)="guardarFormulario()">
              <i class="fa-solid fa-save me-1"></i> Guardar Cuestionario
            </button>
          </div>
        </div>
      </div>

      <!-- MODAL: VER DETALLES DE RESPUESTA DE PACIENTE -->
      <div *ngIf="respuestaSeleccionada" class="modal-backdrop-custom" (click)="respuestaSeleccionada = null">
        <div class="modal-dialog-custom glass-card-modal modal-lg" (click)="$event.stopPropagation()">
          <div class="modal-header-custom">
            <h2 class="modal-title">
              <i class="fa-solid fa-clipboard-user text-primary me-2"></i>
              Respuestas de {{ respuestaSeleccionada.paciente_nombre }}
            </h2>
            <button class="btn-close-custom" (click)="respuestaSeleccionada = null">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>

          <div class="modal-body-custom">
            <div class="patient-info-strip glass-panel p-3 mb-3 d-flex justify-content-between align-items-center">
              <div>
                <strong>Fecha de Envío:</strong> {{ respuestaSeleccionada.fecha_respuesta | date:'medium' }}
              </div>
              <div>
                <strong>Consentimiento IA:</strong> 
                <span class="badge ms-1" [class.bg-success]="respuestaSeleccionada.consentimiento_ia_procesamiento" [class.bg-secondary]="!respuestaSeleccionada.consentimiento_ia_procesamiento">
                  {{ respuestaSeleccionada.consentimiento_ia_procesamiento ? 'Autorizado' : 'Rechazado' }}
                </span>
              </div>
            </div>

            <div class="answers-container">
              <div *ngFor="let item of parseRespuestas(respuestaSeleccionada.respuestas_json)" class="answer-item p-3 mb-2 glass-panel">
                <div class="text-muted small mb-1"><i class="fa-solid fa-circle-question me-1"></i> {{ item.pregunta }}</div>
                <div class="fw-bold text-dark fs-6">{{ item.respuesta }}</div>
              </div>
            </div>
          </div>

          <div class="modal-footer-custom">
            <button class="btn btn-secondary" (click)="respuestaSeleccionada = null">Cerrar</button>
            <button 
              *ngIf="respuestaSeleccionada.consentimiento_ia_procesamiento"
              class="btn btn-ai-gradient"
              (click)="abrirAsistenteIA(respuestaSeleccionada)">
              <i class="fa-solid fa-brain me-1"></i> Analizar con Asistente IA
            </button>
          </div>
        </div>
      </div>

      <!-- MODAL HU-35: ASISTENTE IA DE PRECONSULTA -->
      <app-ia-asistente-modal
        *ngIf="mostrarModalIA"
        [respuestaId]="respuestaIdParaIA"
        (cerrar)="mostrarModalIA = false"
        (decisionRegistrada)="onDecisionIARegistrada($event)">
      </app-ia-asistente-modal>

    </div>
  `,
  styles: [`
    .intake-container {
      max-width: 1300px;
      margin: 0 auto;
    }

    .page-header {
      padding: 1.5rem 2rem;
      border-radius: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #ffffff;
      border: 1px solid #e2e8f0;
    }

    .page-title {
      font-size: 1.5rem;
      font-weight: 700;
      color: #0f172a;
      margin: 0 0 0.25rem 0;
    }

    .page-subtitle {
      font-size: 0.88rem;
      color: #64748b;
      margin: 0;
    }

    .tabs-bar {
      display: flex;
      gap: 0.5rem;
      padding: 0.5rem;
      background: #f1f5f9;
      border-radius: 12px;
    }

    .tab-btn {
      padding: 0.65rem 1.25rem;
      border: none;
      background: transparent;
      color: #64748b;
      font-weight: 600;
      font-size: 0.9rem;
      border-radius: 8px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      transition: all 0.2s ease;
    }

    .tab-btn.active {
      background: #ffffff;
      color: #0284c7;
      box-shadow: 0 2px 4px rgba(0,0,0,0.06);
    }

    .cards-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 1.25rem;
    }

    .questionnaire-card {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 16px;
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      transition: transform 0.2s, box-shadow 0.2s;
    }
    .questionnaire-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 15px -3px rgba(0,0,0,0.08);
    }

    .card-header-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.75rem;
    }

    .version-badge {
      font-size: 0.75rem;
      font-weight: 700;
      background: #e0f2fe;
      color: #0284c7;
      padding: 0.2rem 0.5rem;
      border-radius: 6px;
    }

    .status-pill {
      font-size: 0.72rem;
      font-weight: 700;
      padding: 0.2rem 0.6rem;
      border-radius: 9999px;
      background: #f1f5f9;
      color: #64748b;
    }
    .status-pill.active {
      background: #dcfce7;
      color: #166534;
    }

    .form-title {
      font-size: 1.1rem;
      font-weight: 700;
      color: #0f172a;
      margin: 0 0 0.5rem 0;
    }

    .form-desc {
      font-size: 0.85rem;
      color: #64748b;
      margin: 0 0 1rem 0;
      line-height: 1.4;
      flex: 1;
    }

    .form-meta {
      display: flex;
      gap: 1rem;
      font-size: 0.8rem;
      color: #64748b;
      padding: 0.5rem 0;
      border-top: 1px solid #f1f5f9;
      border-bottom: 1px solid #f1f5f9;
      margin-bottom: 0.75rem;
    }

    .questions-preview {
      background: #f8fafc;
      padding: 0.75rem;
      border-radius: 8px;
      margin-bottom: 1rem;
    }

    .preview-label {
      font-size: 0.72rem;
      font-weight: 700;
      color: #94a3b8;
      text-transform: uppercase;
    }

    .questions-preview ul {
      margin: 0.35rem 0 0 0;
      padding-left: 1.25rem;
      font-size: 0.8rem;
      color: #334155;
    }

    .badge-type {
      font-size: 0.68rem;
      color: #0284c7;
      font-weight: 600;
    }

    .card-actions {
      display: flex;
      gap: 0.5rem;
      justify-content: flex-end;
    }

    .custom-table {
      width: 100%;
      border-collapse: collapse;
      background: #ffffff;
      border-radius: 12px;
      overflow: hidden;
    }

    .custom-table th {
      background: #f8fafc;
      padding: 1rem;
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      color: #64748b;
      border-bottom: 1px solid #e2e8f0;
    }

    .custom-table td {
      padding: 1rem;
      font-size: 0.85rem;
      color: #1e293b;
      border-bottom: 1px solid #f1f5f9;
      vertical-align: middle;
    }

    .patient-cell {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }

    .patient-avatar {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: #e0e7ff;
      color: #4338ca;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .btn-ai-gradient {
      background: linear-gradient(135deg, #0284c7, #6366f1);
      color: #ffffff;
      border: none;
      box-shadow: 0 2px 4px rgba(99, 102, 241, 0.2);
    }
    .btn-ai-gradient:hover:not(:disabled) {
      background: linear-gradient(135deg, #0369a1, #4f46e5);
      color: #ffffff;
    }

    .modal-backdrop-custom {
      position: fixed;
      top: 0; left: 0; width: 100vw; height: 100vh;
      background: rgba(15, 23, 42, 0.6);
      backdrop-filter: blur(4px);
      z-index: 1050;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1.5rem;
    }

    .modal-dialog-custom {
      width: 100%;
      background: #ffffff;
      border-radius: 16px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
      display: flex;
      flex-direction: column;
      max-height: 90vh;
      overflow: hidden;
    }
    .modal-lg { max-width: 850px; }

    .modal-header-custom {
      padding: 1.25rem 1.5rem;
      border-bottom: 1px solid #e2e8f0;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .modal-body-custom {
      padding: 1.25rem 1.5rem;
      overflow-y: auto;
      flex: 1;
    }

    .modal-footer-custom {
      padding: 1rem 1.5rem;
      border-top: 1px solid #e2e8f0;
      display: flex;
      justify-content: flex-end;
      gap: 0.75rem;
      background: #f8fafc;
    }

    .question-row-card {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
    }
  `]
})
export class IntakeConfigComponent implements OnInit {
  activeTab: 'formularios' | 'respuestas' = 'formularios';
  cargando = signal<boolean>(true);
  formularios = signal<FormularioPreConsulta[]>([]);
  respuestas = signal<RespuestaPreConsulta[]>([]);
  mensajeExito = signal<string | null>(null);

  mostrarModalForm = false;
  respuestaSeleccionada: RespuestaPreConsulta | null = null;

  // HU-35 AI Modal State
  mostrarModalIA = false;
  respuestaIdParaIA = '';

  nuevoFormulario: {
    id: string;
    titulo: string;
    descripcion: string;
    activo: boolean;
    preguntas_json: Array<{
      id: string;
      texto: string;
      tipo: 'texto' | 'opcion_multiple' | 'escala_1_5' | 'booleano';
      opciones?: string[];
      requerido: boolean;
    }>;
  } = {
    id: '',
    titulo: '',
    descripcion: '',
    activo: true,
    preguntas_json: [
      { id: 'motivo_1', texto: '¿Cuál es el motivo principal por el que solicita atención psicológica?', tipo: 'texto', requerido: true },
      { id: 'tiempo_1', texto: '¿Desde hace cuánto tiempo experimenta estos síntomas?', tipo: 'texto', requerido: true },
      { id: 'animo_1', texto: 'En las últimas 2 semanas, ¿con qué frecuencia se ha sentido decaído o sin esperanzas?', tipo: 'escala_1_5', requerido: true },
      { id: 'ansiedad_1', texto: '¿Ha experimentado ataques repentinos de pánico o palpitaciones?', tipo: 'booleano', requerido: true },
      { id: 'alerta_1', texto: '¿Ha tenido pensamientos de que preferiría estar muerto o autolesionarse?', tipo: 'booleano', requerido: true }
    ]
  };

  constructor(private clinicaService: ClinicaSprint2Service) {}

  ngOnInit(): void {
    this.cargarDatos();
  }

  cargarDatos(): void {
    this.cargando.set(true);
    this.clinicaService.getFormulariosPreconsulta().subscribe({
      next: (forms) => {
        this.formularios.set(forms);
        this.clinicaService.getRespuestasPreconsulta().subscribe({
          next: (resps) => {
            this.respuestas.set(resps);
            this.cargando.set(false);
          },
          error: () => this.cargando.set(false)
        });
      },
      error: () => this.cargando.set(false)
    });
  }

  openCreateModal(): void {
    this.nuevoFormulario = {
      id: '',
      titulo: 'Cuestionario de Preconsulta Psicológica General',
      descripcion: 'Complete este cuestionario antes de su primera sesión para orientar a su terapeuta.',
      activo: true,
      preguntas_json: [
        { id: 'motivo_1', texto: '¿Cuál es el motivo principal por el que solicita atención psicológica?', tipo: 'texto', requerido: true },
        { id: 'tiempo_1', texto: '¿Desde hace cuánto tiempo experimenta estos síntomas?', tipo: 'texto', requerido: true },
        { id: 'animo_1', texto: 'En las últimas 2 semanas, ¿con qué frecuencia se ha sentido decaído o sin esperanzas? (1=Nunca, 5=Todos los días)', tipo: 'escala_1_5', requerido: true },
        { id: 'ansiedad_1', texto: '¿Ha experimentado crisis de ansiedad aguda o palpitaciones?', tipo: 'booleano', requerido: true },
        { id: 'alerta_1', texto: '¿Ha tenido pensamientos de muerte o deseos de desaparecer?', tipo: 'booleano', requerido: true }
      ]
    };
    this.mostrarModalForm = true;
  }

  agregarPregunta(): void {
    const idx = this.nuevoFormulario.preguntas_json.length + 1;
    this.nuevoFormulario.preguntas_json.push({
      id: `pregunta_${idx}`,
      texto: '',
      tipo: 'texto',
      requerido: true
    });
  }

  eliminarPregunta(index: number): void {
    this.nuevoFormulario.preguntas_json.splice(index, 1);
  }

  actualizarOpcionesPregunta(p: any, valor: string): void {
    p.opciones = valor.split(',').map(s => s.trim()).filter(s => !!s);
  }

  guardarFormulario(): void {
    if (this.nuevoFormulario.id) {
      this.clinicaService.actualizarFormularioPreconsulta(this.nuevoFormulario.id, this.nuevoFormulario).subscribe({
        next: () => {
          this.mostrarModalForm = false;
          this.mostrarFeedback('Cuestionario actualizado correctamente');
          this.cargarDatos();
        }
      });
    } else {
      this.clinicaService.crearFormularioPreconsulta(this.nuevoFormulario).subscribe({
        next: () => {
          this.mostrarModalForm = false;
          this.mostrarFeedback('Cuestionario creado y publicado con éxito');
          this.cargarDatos();
        }
      });
    }
  }

  verDetalleFormulario(form: FormularioPreConsulta): void {
    this.nuevoFormulario = {
      id: form.id,
      titulo: form.titulo,
      descripcion: form.descripcion || '',
      activo: form.activo,
      preguntas_json: JSON.parse(JSON.stringify(form.preguntas_json))
    };
    this.mostrarModalForm = true;
  }

  duplicarOEditar(form: FormularioPreConsulta): void {
    this.verDetalleFormulario(form);
  }

  verDetalleRespuesta(r: RespuestaPreConsulta): void {
    this.respuestaSeleccionada = r;
  }

  parseRespuestas(respuestasJson: any): Array<{ pregunta: string; respuesta: any }> {
    if (!respuestasJson) return [];
    return Object.keys(respuestasJson).map(k => ({
      pregunta: k,
      respuesta: typeof respuestasJson[k] === 'boolean' ? (respuestasJson[k] ? 'Sí' : 'No') : respuestasJson[k]
    }));
  }

  abrirAsistenteIA(r: RespuestaPreConsulta): void {
    this.respuestaIdParaIA = r.id;
    this.mostrarModalIA = true;
  }

  onDecisionIARegistrada(evento: { decision: string; resumen: string }): void {
    this.mostrarFeedback(`Decisión humana registrada en auditoría: ${evento.decision}`);
    this.cargarDatos();
  }

  mostrarFeedback(msg: string): void {
    this.mensajeExito.set(msg);
    setTimeout(() => this.mensajeExito.set(null), 4000);
  }
}
