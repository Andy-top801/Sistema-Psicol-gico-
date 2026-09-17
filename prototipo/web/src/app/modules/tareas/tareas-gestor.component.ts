// ==============================================================================
// MÓDULO: tareas-gestor.component.ts
// CAPA BCE: BOUNDARY (Interfaz de Usuario) — IU_GestionTareasTerapeuticas
// CASOS DE USO: CU17: Tareas Terapéuticas Inter-Sesión y Adherencia (HU-29, HU-30)
// ==============================================================================
import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ClinicaSprint2Service } from '../../core/services/clinica-sprint2.service';
import { TareaTerapeutica, HistoriaClinica } from '../../core/models/clinica-sprint2.model';

@Component({
  selector: 'app-tareas-gestor',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="tareas-container">
      
      <!-- Header -->
      <div class="page-header glass-panel mb-4">
        <div>
          <h1 class="page-title">
            <i class="fa-solid fa-list-check text-primary"></i> Tareas Terapéuticas Inter-Sesión
          </h1>
          <p class="page-subtitle">
            Prescripción de actividades conductuales, auto-registros cognitivos y evaluación de adherencia entre sesiones (Sprint 2 - HU-29, HU-30).
          </p>
        </div>
        <div class="header-actions">
          <button class="btn btn-primary" (click)="abrirModalNuevaTarea()">
            <i class="fa-solid fa-plus"></i> Prescribir Tarea
          </button>
        </div>
      </div>

      <!-- Filtros -->
      <div class="filters-bar glass-panel mb-4">
        <div class="d-flex gap-2 align-items-center">
          <span class="small fw-bold text-muted">Filtrar por estado:</span>
          <button class="btn btn-sm" [class.btn-primary]="filtroEstado === 'TODOS'" [class.btn-light]="filtroEstado !== 'TODOS'" (click)="filtroEstado = 'TODOS'">Todos</button>
          <button class="btn btn-sm" [class.btn-primary]="filtroEstado === 'PENDIENTE'" [class.btn-light]="filtroEstado !== 'PENDIENTE'" (click)="filtroEstado = 'PENDIENTE'">Pendientes</button>
          <button class="btn btn-sm" [class.btn-primary]="filtroEstado === 'COMPLETADA'" [class.btn-light]="filtroEstado !== 'COMPLETADA'" (click)="filtroEstado = 'COMPLETADA'">Completadas</button>
          <button class="btn btn-sm" [class.btn-primary]="filtroEstado === 'REVISADA'" [class.btn-light]="filtroEstado !== 'REVISADA'" (click)="filtroEstado = 'REVISADA'">Revisadas</button>
        </div>
      </div>

      <!-- Feedback Banner -->
      <div *ngIf="mensajeFeedback()" class="alert alert-success d-flex align-items-center mb-4">
        <i class="fa-solid fa-circle-check me-2"></i>
        <span>{{ mensajeFeedback() }}</span>
      </div>

      <!-- Estado de Carga -->
      <div *ngIf="cargando()" class="loading-state glass-panel text-center p-5">
        <i class="fa-solid fa-spinner fa-spin fa-2x text-primary mb-3"></i>
        <p class="text-muted">Cargando tareas terapéuticas...</p>
      </div>

      <!-- Estado Vacío -->
      <div *ngIf="!cargando() && tareasFiltradas().length === 0" class="empty-state glass-panel text-center p-5">
        <i class="fa-solid fa-clipboard-check fa-3x text-dim mb-3"></i>
        <h3>No hay tareas terapéuticas registradas</h3>
        <p class="text-muted">Prescriba la primera tarea para el trabajo inter-sesión del paciente.</p>
      </div>

      <!-- Grilla de Tareas -->
      <div class="tareas-grid" *ngIf="!cargando() && tareasFiltradas().length > 0">
        <div class="tarea-card glass-panel" *ngFor="let t of tareasFiltradas()">
          
          <div class="tarea-card-header">
            <span class="category-pill" [ngClass]="'cat-' + t.categoria.toLowerCase()">
              {{ getCategoriaNombre(t.categoria) }}
            </span>
            <span class="status-pill" [ngClass]="'status-' + t.estado.toLowerCase()">
              {{ t.estado }}
            </span>
          </div>

          <h3 class="tarea-title">{{ t.titulo }}</h3>
          <p class="tarea-instrucciones">{{ t.instrucciones }}</p>

          <div class="tarea-meta-row">
            <span><i class="fa-solid fa-calendar-xmark text-danger me-1"></i> Vence: {{ t.fecha_limite | date:'dd/MM/yyyy' }}</span>
            <span><i class="fa-solid fa-paperclip text-info me-1"></i> {{ t.evidencias.length || 0 }} Evidencias</span>
          </div>

          <!-- Feedback del Psicólogo si existe -->
          <div *ngIf="t.feedback_psicologo" class="feedback-box mt-2 p-2 rounded small">
            <i class="fa-solid fa-comment-medical text-primary me-1"></i>
            <strong>Devolución del terapeuta:</strong> {{ t.feedback_psicologo }}
          </div>

          <!-- Acciones de la Tarea -->
          <div class="tarea-actions-footer mt-3">
            <!-- Acción de Paciente (Demo / Test) -->
            <button class="btn btn-sm btn-outline-secondary" *ngIf="t.estado === 'PENDIENTE'" (click)="abrirModalEvidencia(t)">
              <i class="fa-solid fa-upload"></i> Subir Evidencia
            </button>

            <!-- Acción de Terapeuta -->
            <button class="btn btn-sm btn-primary" *ngIf="t.estado === 'COMPLETADA' || (t.evidencias && t.evidencias.length > 0)" (click)="abrirModalRevisar(t)">
              <i class="fa-solid fa-user-check"></i> Revisar y Dar Feedback
            </button>
          </div>

        </div>
      </div>

      <!-- MODAL NUEVA TAREA -->
      <div *ngIf="mostrarModalCrear" class="modal-backdrop-custom" (click)="mostrarModalCrear = false">
        <div class="modal-dialog-custom glass-card-modal modal-md" (click)="$event.stopPropagation()">
          <div class="modal-header-custom">
            <h2 class="modal-title"><i class="fa-solid fa-plus-circle text-primary me-2"></i>Nueva Tarea Terapéutica</h2>
            <button class="btn-close-custom" (click)="mostrarModalCrear = false"><i class="fa-solid fa-xmark"></i></button>
          </div>
          <div class="modal-body-custom p-4">
            <div class="mb-3">
              <label class="form-label">Historia Clínica del Paciente *</label>
              <select class="form-select" [(ngModel)]="nuevaTarea.historia_clinica">
                <option value="" disabled selected>-- Seleccione el expediente --</option>
                <option *ngFor="let h of historias()" [value]="h.id">
                  {{ h.numero_historia }} - {{ h.paciente_nombre }}
                </option>
              </select>
            </div>

            <div class="mb-3">
              <label class="form-label">Título de la Tarea *</label>
              <input type="text" class="form-control" [(ngModel)]="nuevaTarea.titulo" placeholder="Ej. Registro de pensamientos automáticos" />
            </div>

            <div class="row g-3 mb-3">
              <div class="col-md-6">
                <label class="form-label">Categoría</label>
                <select class="form-select" [(ngModel)]="nuevaTarea.categoria">
                  <option value="REGISTRO_PENSAMIENTOS">Registro de Pensamientos</option>
                  <option value="CONDUCTUAL">Activación Conductual</option>
                  <option value="MINDFULNESS">Mindfulness / Relajación</option>
                  <option value="LECTURA">Psicoeducación</option>
                  <option value="OTRO">Otro</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label">Fecha Límite *</label>
                <input type="date" class="form-control" [(ngModel)]="nuevaTarea.fecha_limite" />
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label">Instrucciones Clínicas *</label>
              <textarea class="form-control" [(ngModel)]="nuevaTarea.instrucciones" rows="3" placeholder="Pautas detalladas para el paciente..."></textarea>
            </div>
          </div>
          <div class="modal-footer-custom p-3">
            <button class="btn btn-secondary" (click)="mostrarModalCrear = false">Cancelar</button>
            <button class="btn btn-primary" [disabled]="!nuevaTarea.historia_clinica || !nuevaTarea.titulo" (click)="guardarNuevaTarea()">
              Prescribir Tarea
            </button>
          </div>
        </div>
      </div>

      <!-- MODAL SUBIR EVIDENCIA (PACIENTE) -->
      <div *ngIf="tareaParaEvidencia" class="modal-backdrop-custom" (click)="tareaParaEvidencia = null">
        <div class="modal-dialog-custom glass-card-modal modal-md" (click)="$event.stopPropagation()">
          <div class="modal-header-custom">
            <h2 class="modal-title"><i class="fa-solid fa-upload text-info me-2"></i>Completar Tarea: {{ tareaParaEvidencia.titulo }}</h2>
            <button class="btn-close-custom" (click)="tareaParaEvidencia = null"><i class="fa-solid fa-xmark"></i></button>
          </div>
          <div class="modal-body-custom p-4">
            <div class="mb-3">
              <label class="form-label">Reflexión o Respuestas del Paciente *</label>
              <textarea class="form-control" [(ngModel)]="evidenciaForm.reflexion_paciente" rows="4"
                        placeholder="Escriba lo experimentado, pensamientos identificados o conclusiones de la tarea..."></textarea>
            </div>

            <div class="mb-3">
              <label class="form-label">Nivel de Dificultad Percibido (1 = Muy fácil, 5 = Muy difícil): <strong>{{ evidenciaForm.nivel_dificultad_percibido }} / 5</strong></label>
              <input type="range" class="form-range" min="1" max="5" step="1" [(ngModel)]="evidenciaForm.nivel_dificultad_percibido" />
              <div class="d-flex justify-content-between small text-muted">
                <span>1 - Muy Fácil</span>
                <span>3 - Moderado</span>
                <span>5 - Muy Difícil</span>
              </div>
            </div>
          </div>
          <div class="modal-footer-custom p-3">
            <button class="btn btn-secondary" (click)="tareaParaEvidencia = null">Cancelar</button>
            <button class="btn btn-success" [disabled]="!evidenciaForm.reflexion_paciente" (click)="enviarEvidencia()">
              <i class="fa-solid fa-check me-1"></i> Enviar Cumplimiento
            </button>
          </div>
        </div>
      </div>

      <!-- MODAL REVISAR TAREA Y FEEDBACK (PSICÓLOGO) -->
      <div *ngIf="tareaParaRevisar" class="modal-backdrop-custom" (click)="tareaParaRevisar = null">
        <div class="modal-dialog-custom glass-card-modal modal-lg" (click)="$event.stopPropagation()">
          <div class="modal-header-custom">
            <h2 class="modal-title"><i class="fa-solid fa-clipboard-check text-primary me-2"></i>Revisión de Tarea: {{ tareaParaRevisar.titulo }}</h2>
            <button class="btn-close-custom" (click)="tareaParaRevisar = null"><i class="fa-solid fa-xmark"></i></button>
          </div>
          <div class="modal-body-custom p-4">
            <h4 class="small fw-bold text-muted text-uppercase mb-2">Evidencias Enviadas por el Paciente</h4>
            
            <div *ngIf="!tareaParaRevisar.evidencias || tareaParaRevisar.evidencias.length === 0" class="text-muted small p-3 bg-light rounded mb-3">
              Sin evidencias adjuntas aún.
            </div>

            <div *ngFor="let ev of tareaParaRevisar.evidencias" class="evidence-card glass-panel p-3 mb-3">
              <div class="d-flex justify-content-between mb-2">
                <span class="small text-muted"><i class="fa-solid fa-clock me-1"></i> {{ ev.fecha_registro | date:'medium' }}</span>
                <span class="badge bg-info text-dark">Dificultad: {{ ev.nivel_dificultad_percibido }}/5</span>
              </div>
              <p class="m-0 text-dark">{{ ev.reflexion_paciente }}</p>
            </div>

            <div class="mt-4">
              <label class="form-label fw-bold">Devolución / Feedback del Psicólogo *</label>
              <textarea class="form-control" [(ngModel)]="feedbackTexto" rows="3"
                        placeholder="Escriba el reforzamiento positivo o aclaración técnica para el paciente..."></textarea>
            </div>
          </div>
          <div class="modal-footer-custom p-3">
            <button class="btn btn-secondary" (click)="tareaParaRevisar = null">Cerrar</button>
            <button class="btn btn-primary" [disabled]="!feedbackTexto" (click)="guardarFeedback()">
              <i class="fa-solid fa-check-double me-1"></i> Marcar como Revisada & Enviar Feedback
            </button>
          </div>
        </div>
      </div>

    </div>
  `,
  styles: [`
    .tareas-container { max-width: 1300px; margin: 0 auto; }
    .page-header {
      padding: 1.5rem 2rem; border-radius: 16px; background: #ffffff;
      border: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center;
    }
    .page-title { font-size: 1.5rem; font-weight: 700; color: #0f172a; margin: 0 0 0.25rem 0; }
    .page-subtitle { font-size: 0.88rem; color: #64748b; margin: 0; }

    .filters-bar { padding: 0.75rem 1rem; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; }

    .tareas-grid {
      display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 1.25rem;
    }
    .tarea-card {
      background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 1.25rem;
      display: flex; flex-direction: column; transition: transform 0.2s;
    }
    .tarea-card:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.06); }

    .tarea-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
    .category-pill { font-size: 0.72rem; font-weight: 700; padding: 0.2rem 0.6rem; border-radius: 6px; }
    .cat-registro_pensamientos { background: #e0f2fe; color: #0369a1; }
    .cat-conductual { background: #dcfce7; color: #166534; }
    .cat-mindfulness { background: #f3e8ff; color: #7e22ce; }
    .cat-lectura { background: #fef9c3; color: #854d0e; }
    .cat-otro { background: #f1f5f9; color: #475569; }

    .status-pill { font-size: 0.72rem; font-weight: 700; padding: 0.2rem 0.6rem; border-radius: 9999px; }
    .status-pendiente { background: #fef9c3; color: #854d0e; }
    .status-completada { background: #e0f2fe; color: #0369a1; }
    .status-revisada { background: #dcfce7; color: #166534; }
    .status-vencida { background: #fee2e2; color: #991b1b; }

    .tarea-title { font-size: 1.05rem; font-weight: 700; color: #0f172a; margin: 0 0 0.4rem 0; }
    .tarea-instrucciones { font-size: 0.85rem; color: #64748b; margin: 0 0 1rem 0; flex: 1; line-height: 1.4; }
    .tarea-meta-row { display: flex; justify-content: space-between; font-size: 0.78rem; color: #64748b; border-top: 1px solid #f1f5f9; padding-top: 0.5rem; }
    .feedback-box { background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; }
    .tarea-actions-footer { display: flex; justify-content: flex-end; gap: 0.5rem; }

    .modal-backdrop-custom {
      position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
      background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px); z-index: 1050;
      display: flex; align-items: center; justify-content: center; padding: 1.5rem;
    }
    .modal-dialog-custom {
      width: 100%; background: #ffffff; border-radius: 16px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); overflow: hidden;
    }
    .modal-md { max-width: 600px; }
    .modal-lg { max-width: 800px; }
    .modal-header-custom { padding: 1.25rem 1.5rem; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
    .modal-footer-custom { border-top: 1px solid #e2e8f0; background: #f8fafc; display: flex; justify-content: flex-end; gap: 0.75rem; }
  `]
})
export class TareasGestorComponent implements OnInit {
  cargando = signal<boolean>(true);
  tareas = signal<TareaTerapeutica[]>([]);
  historias = signal<HistoriaClinica[]>([]);
  filtroEstado = 'TODOS';
  mensajeFeedback = signal<string | null>(null);

  // Modal Nueva Tarea
  mostrarModalCrear = false;
  nuevaTarea = {
    historia_clinica: '',
    titulo: '',
    instrucciones: '',
    categoria: 'REGISTRO_PENSAMIENTOS',
    fecha_limite: ''
  };

  // Modal Evidencia
  tareaParaEvidencia: TareaTerapeutica | null = null;
  evidenciaForm = {
    reflexion_paciente: '',
    nivel_dificultad_percibido: 3
  };

  // Modal Revisar
  tareaParaRevisar: TareaTerapeutica | null = null;
  feedbackTexto = '';

  constructor(private clinicaService: ClinicaSprint2Service) {}

  ngOnInit(): void {
    this.cargarDatos();
  }

  cargarDatos(): void {
    this.cargando.set(true);
    this.clinicaService.getTareas().subscribe({
      next: (ts) => {
        this.tareas.set(ts);
        this.clinicaService.getHistoriasClinicas().subscribe({
          next: (hs) => {
            this.historias.set(hs);
            this.cargando.set(false);
          },
          error: () => this.cargando.set(false)
        });
      },
      error: () => this.cargando.set(false)
    });
  }

  tareasFiltradas(): TareaTerapeutica[] {
    if (this.filtroEstado === 'TODOS') return this.tareas();
    return this.tareas().filter(t => t.estado === this.filtroEstado);
  }

  getCategoriaNombre(cat: string): string {
    switch (cat) {
      case 'REGISTRO_PENSAMIENTOS': return 'Registro TCC';
      case 'CONDUCTUAL': return 'Conductual';
      case 'MINDFULNESS': return 'Mindfulness';
      case 'LECTURA': return 'Psicoeducación';
      default: return 'General';
    }
  }

  abrirModalNuevaTarea(): void {
    const d = new Date();
    d.setDate(d.getDate() + 7);
    this.nuevaTarea = {
      historia_clinica: this.historias().length > 0 ? this.historias()[0].id : '',
      titulo: '',
      instrucciones: '',
      categoria: 'REGISTRO_PENSAMIENTOS',
      fecha_limite: d.toISOString().substring(0, 10)
    };
    this.mostrarModalCrear = true;
  }

  guardarNuevaTarea(): void {
    this.clinicaService.crearTarea(this.nuevaTarea).subscribe({
      next: () => {
        this.mostrarModalCrear = false;
        this.mostrarAviso('Tarea terapéutica prescrita correctamente');
        this.cargarDatos();
      }
    });
  }

  abrirModalEvidencia(t: TareaTerapeutica): void {
    this.tareaParaEvidencia = t;
    this.evidenciaForm = { reflexion_paciente: '', nivel_dificultad_percibido: 3 };
  }

  enviarEvidencia(): void {
    if (!this.tareaParaEvidencia) return;
    this.clinicaService.subirEvidenciaTarea(this.tareaParaEvidencia.id, this.evidenciaForm).subscribe({
      next: () => {
        this.tareaParaEvidencia = null;
        this.mostrarAviso('Evidencia de cumplimiento registrada');
        this.cargarDatos();
      }
    });
  }

  abrirModalRevisar(t: TareaTerapeutica): void {
    this.tareaParaRevisar = t;
    this.feedbackTexto = t.feedback_psicologo || '';
  }

  guardarFeedback(): void {
    if (!this.tareaParaRevisar) return;
    this.clinicaService.revisarTarea(this.tareaParaRevisar.id, this.feedbackTexto).subscribe({
      next: () => {
        this.tareaParaRevisar = null;
        this.mostrarAviso('Tarea revisada y feedback remitido al paciente');
        this.cargarDatos();
      }
    });
  }

  mostrarAviso(msg: string): void {
    this.mensajeFeedback.set(msg);
    setTimeout(() => this.mensajeFeedback.set(null), 3500);
  }
}
