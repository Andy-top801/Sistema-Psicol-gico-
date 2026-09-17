// ==============================================================================
// MÓDULO: historia-clinica-list.component.ts
// CAPA BCE: BOUNDARY (Interfaz de Usuario) — IU_ListadoHistoriasClinicas
// CASOS DE USO: CU15: Apertura y Gestión de Expediente Psicológico Electrónico (HU-25)
// ==============================================================================
import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ClinicaSprint2Service } from '../../core/services/clinica-sprint2.service';
import { ClinicaService } from '../../core/services/clinica.service';
import { HistoriaClinica } from '../../core/models/clinica-sprint2.model';
import { Paciente } from '../../core/models';

@Component({
  selector: 'app-historia-clinica-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="ehr-list-container">
      <!-- Encabezado Principal -->
      <div class="page-header glass-panel mb-4">
        <div class="header-info">
          <h1 class="page-title">
            <i class="fa-solid fa-notes-medical text-primary"></i>
            Historias Clínicas Electrónicas (EHR)
          </h1>
          <p class="page-subtitle">
            Expedientes psicológicos con codificación CIE-10, notas evolutivas longitudinales y control de acceso ético (Sprint 2 - HU-25, HU-26).
          </p>
        </div>
        <div class="header-actions">
          <button class="btn btn-primary" (click)="abrirModalApertura()">
            <i class="fa-solid fa-folder-plus"></i> Apertura de Expediente
          </button>
        </div>
      </div>

      <!-- Barra de Búsqueda y Filtros -->
      <div class="filters-bar glass-panel mb-4">
        <div class="search-box">
          <i class="fa-solid fa-magnifying-glass"></i>
          <input
            type="text"
            [(ngModel)]="terminoBusqueda"
            (ngModelChange)="buscar()"
            placeholder="Buscar por N° de Historia (HC-...), CI o nombre del paciente..."
            class="form-control search-input"
          />
        </div>
      </div>

      <!-- Estado de Carga -->
      <div *ngIf="cargando()" class="loading-state glass-panel">
        <i class="fa-solid fa-spinner fa-spin fa-2x text-primary mb-3"></i>
        <span>Cargando historias clínicas electrónicas...</span>
      </div>

      <!-- Estado Vacío -->
      <div *ngIf="!cargando() && historias().length === 0" class="empty-state glass-panel text-center p-5">
        <i class="fa-solid fa-file-shield fa-3x text-dim mb-3"></i>
        <h3>No se encontraron historias clínicas</h3>
        <p class="text-muted">Inicie la apertura del primer expediente clínico para registrar la anamnesis del paciente.</p>
        <button class="btn btn-primary mt-2" (click)="abrirModalApertura()">
          <i class="fa-solid fa-folder-plus"></i> Abrir Expediente Ahora
        </button>
      </div>

      <!-- Tabla de Historias Clínicas -->
      <div class="table-responsive glass-panel" *ngIf="!cargando() && historias().length > 0">
        <table class="custom-table">
          <thead>
            <tr>
              <th>N° Historia</th>
              <th>Paciente</th>
              <th>Psicólogo Cabecera</th>
              <th>Fecha Apertura</th>
              <th>Diagnósticos CIE-10</th>
              <th>Actividad Clínica</th>
              <th class="text-end">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let hc of historias()" class="table-row-hover" (click)="verDetalle(hc.id)">
              <td>
                <span class="hc-badge">
                  <i class="fa-solid fa-hashtag"></i> {{ hc.numero_historia }}
                </span>
              </td>
              <td>
                <div class="patient-cell">
                  <div class="avatar-circle">{{ (hc.paciente_nombre || 'P').charAt(0) }}</div>
                  <div>
                    <strong class="patient-name">{{ hc.paciente_nombre }}</strong>
                    <small class="d-block text-muted">ID: {{ hc.paciente }}</small>
                  </div>
                </div>
              </td>
              <td>
                <div class="doctor-cell">
                  <i class="fa-solid fa-user-doctor text-primary me-1"></i>
                  <span>{{ hc.psicologo_nombre || 'Psicólogo Asignado' }}</span>
                </div>
              </td>
              <td>
                <span class="text-muted">{{ hc.fecha_apertura | date:'dd/MM/yyyy' }}</span>
              </td>
              <td>
                <div class="diagnosticos-chips">
                  <span *ngIf="!hc.diagnosticos || hc.diagnosticos.length === 0" class="badge-empty">
                    Sin diagnóstico activo
                  </span>
                  <span *ngFor="let d of hc.diagnosticos.slice(0, 2)" class="badge-cie" [title]="d.descripcion">
                    <strong>{{ d.codigo_cie10 }}</strong> - {{ d.tipo }}
                  </span>
                  <span *ngIf="hc.diagnosticos && hc.diagnosticos.length > 2" class="badge-more">
                    +{{ hc.diagnosticos.length - 2 }} más
                  </span>
                </div>
              </td>
              <td>
                <div class="stats-row">
                  <span class="stat-pill" title="Sesiones registradas">
                    <i class="fa-solid fa-calendar-check text-success"></i> {{ hc.total_sesiones || 0 }}
                  </span>
                  <span class="stat-pill" title="Tareas asignadas">
                    <i class="fa-solid fa-list-check text-info"></i> {{ hc.total_tareas || 0 }}
                  </span>
                  <span *ngIf="(hc.alertas_recaida || 0) > 0" class="stat-pill stat-alert" title="Alertas de crisis / recaída">
                    <i class="fa-solid fa-triangle-exclamation text-danger"></i> {{ hc.alertas_recaida }}
                  </span>
                </div>
              </td>
              <td class="text-end" (click)="$event.stopPropagation()">
                <button class="btn btn-sm btn-outline-primary" (click)="verDetalle(hc.id)">
                  <i class="fa-solid fa-arrow-right-to-bracket"></i> Abrir Expediente
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- MODAL: APERTURA DE HISTORIA CLÍNICA (HU-25) -->
      <div *ngIf="mostrarModalApertura" class="modal-backdrop-custom" (click)="mostrarModalApertura = false">
        <div class="modal-dialog-custom glass-card-modal modal-lg" (click)="$event.stopPropagation()">
          <div class="modal-header-custom">
            <h2 class="modal-title">
              <i class="fa-solid fa-folder-plus text-primary me-2"></i>
              Apertura de Expediente Psicológico Electrónico
            </h2>
            <button class="btn-close-custom" (click)="mostrarModalApertura = false">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>

          <div class="modal-body-custom">
            <div *ngIf="errorApertura()" class="alert alert-danger mb-3">
              <i class="fa-solid fa-circle-exclamation me-1"></i> {{ errorApertura() }}
            </div>

            <div class="row g-3">
              <div class="col-md-12">
                <label class="form-label">Seleccionar Paciente *</label>
                <select class="form-select" [(ngModel)]="nuevaHistoria.paciente">
                  <option value="" disabled selected>-- Seleccione un paciente del padrón --</option>
                  <option *ngFor="let p of pacientesDisponibles()" [value]="p.id">
                    {{ p.usuario.nombre }} {{ p.usuario.apellido }} (CI: {{ p.ci }}, Exp: {{ p.codigo_expediente }})
                  </option>
                </select>
                <small class="text-muted">Solo se muestran pacientes sin historia clínica activa.</small>
              </div>

              <div class="col-md-12">
                <label class="form-label">Motivo de Consulta Inicial *</label>
                <textarea class="form-control" [(ngModel)]="nuevaHistoria.motivo_consulta_inicial" rows="3"
                          placeholder="Descripción detallada de la demanda psicológica planteada por el consultante..."></textarea>
              </div>

              <div class="col-md-6">
                <label class="form-label">Antecedentes Personales</label>
                <textarea class="form-control" [(ngModel)]="nuevaHistoria.antecedentes_personales" rows="3"
                          placeholder="Historial médico, tratamientos previos, eventos vitales significativos..."></textarea>
              </div>

              <div class="col-md-6">
                <label class="form-label">Antecedentes Familiares</label>
                <textarea class="form-control" [(ngModel)]="nuevaHistoria.antecedentes_familiares" rows="3"
                          placeholder="Dinámica familiar, antecedentes de salud mental en primer grado..."></textarea>
              </div>

              <div class="col-md-12">
                <label class="form-label">Examen del Estado Mental (EEM) Inicial</label>
                <textarea class="form-control" [(ngModel)]="nuevaHistoria.examen_estado_mental" rows="3"
                          placeholder="Orientación alopsíquica/autopsíquica, porte y actitud, curso del pensamiento, afectividad, juicio crítico..."></textarea>
              </div>

              <div class="col-md-12">
                <label class="form-label">Plan Terapéutico Propuesto</label>
                <textarea class="form-control" [(ngModel)]="nuevaHistoria.plan_terapeutico" rows="2"
                          placeholder="Enfoque psicoterapéutico (ej. TCC, Sistémico, Gestáltico), frecuencia estimada..."></textarea>
              </div>
            </div>
          </div>

          <div class="modal-footer-custom">
            <button class="btn btn-secondary" (click)="mostrarModalApertura = false">Cancelar</button>
            <button class="btn btn-primary" [disabled]="!nuevaHistoria.paciente || !nuevaHistoria.motivo_consulta_inicial" (click)="guardarApertura()">
              <i class="fa-solid fa-check me-1"></i> Confirmar Apertura de Historia
            </button>
          </div>
        </div>
      </div>

    </div>
  `,
  styles: [`
    .ehr-list-container { max-width: 1300px; margin: 0 auto; }
    .page-header {
      padding: 1.5rem 2rem;
      border-radius: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #ffffff;
      border: 1px solid #e2e8f0;
    }
    .page-title { font-size: 1.5rem; font-weight: 700; color: #0f172a; margin: 0 0 0.25rem 0; }
    .page-subtitle { font-size: 0.88rem; color: #64748b; margin: 0; }
    
    .filters-bar { padding: 0.75rem 1rem; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; }
    .search-box { display: flex; align-items: center; gap: 0.75rem; color: #94a3b8; }
    .search-input { border: none; box-shadow: none; padding: 0.4rem 0; font-size: 0.95rem; }
    .search-input:focus { outline: none; }

    .custom-table { width: 100%; border-collapse: collapse; background: #ffffff; border-radius: 12px; overflow: hidden; }
    .custom-table th {
      background: #f8fafc; padding: 1rem; font-size: 0.75rem; font-weight: 700;
      text-transform: uppercase; color: #64748b; border-bottom: 1px solid #e2e8f0;
    }
    .custom-table td { padding: 1rem; font-size: 0.85rem; color: #1e293b; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }
    .table-row-hover:hover { background-color: #f8fafc; cursor: pointer; }

    .hc-badge {
      font-family: monospace; font-weight: 700; color: #0284c7; background: #e0f2fe;
      padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.85rem;
    }
    .patient-cell { display: flex; align-items: center; gap: 0.75rem; }
    .avatar-circle {
      width: 36px; height: 36px; border-radius: 50%; background: #e0e7ff; color: #4338ca;
      font-weight: 700; display: flex; align-items: center; justify-content: center;
    }
    .patient-name { color: #0f172a; }

    .diagnosticos-chips { display: flex; flex-wrap: wrap; gap: 0.35rem; }
    .badge-cie {
      font-size: 0.72rem; background: #f1f5f9; color: #334155; padding: 0.2rem 0.5rem;
      border-radius: 4px; border: 1px solid #cbd5e1;
    }
    .badge-empty { font-size: 0.75rem; color: #94a3b8; font-style: italic; }
    .badge-more { font-size: 0.7rem; color: #0284c7; font-weight: 600; padding: 0.2rem 0.4rem; }

    .stats-row { display: flex; gap: 0.5rem; }
    .stat-pill {
      font-size: 0.75rem; font-weight: 600; background: #f8fafc; padding: 0.2rem 0.5rem;
      border-radius: 6px; border: 1px solid #e2e8f0; display: flex; align-items: center; gap: 0.3rem;
    }
    .stat-alert { background: #fee2e2; border-color: #fca5a5; color: #991b1b; }

    .modal-backdrop-custom {
      position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
      background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px); z-index: 1050;
      display: flex; align-items: center; justify-content: center; padding: 1.5rem;
    }
    .modal-dialog-custom {
      width: 100%; max-width: 850px; background: #ffffff; border-radius: 16px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); max-height: 90vh;
      display: flex; flex-direction: column; overflow: hidden;
    }
    .modal-header-custom {
      padding: 1.25rem 1.5rem; border-bottom: 1px solid #e2e8f0;
      display: flex; align-items: center; justify-content: space-between;
    }
    .modal-body-custom { padding: 1.25rem 1.5rem; overflow-y: auto; flex: 1; }
    .modal-footer-custom {
      padding: 1rem 1.5rem; border-top: 1px solid #e2e8f0; background: #f8fafc;
      display: flex; justify-content: flex-end; gap: 0.75rem;
    }
  `]
})
export class HistoriaClinicaListComponent implements OnInit {
  cargando = signal<boolean>(true);
  historias = signal<HistoriaClinica[]>([]);
  pacientesDisponibles = signal<Paciente[]>([]);
  terminoBusqueda = '';
  mostrarModalApertura = false;
  errorApertura = signal<string | null>(null);

  nuevaHistoria = {
    paciente: '',
    motivo_consulta_inicial: '',
    antecedentes_personales: '',
    antecedentes_familiares: '',
    examen_estado_mental: '',
    plan_terapeutico: ''
  };

  constructor(
    private clinicaSprint2: ClinicaSprint2Service,
    private clinicaSprint1: ClinicaService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.cargarHistorias();
  }

  cargarHistorias(): void {
    this.cargando.set(true);
    this.clinicaSprint2.getHistoriasClinicas(this.terminoBusqueda).subscribe({
      next: (data) => {
        this.historias.set(data);
        this.cargando.set(false);
      },
      error: () => this.cargando.set(false)
    });
  }

  buscar(): void {
    this.cargarHistorias();
  }

  verDetalle(id: string): void {
    this.router.navigate(['/historias-clinicas', id]);
  }

  abrirModalApertura(): void {
    this.errorApertura.set(null);
    this.nuevaHistoria = {
      paciente: '',
      motivo_consulta_inicial: '',
      antecedentes_personales: '',
      antecedentes_familiares: '',
      examen_estado_mental: '',
      plan_terapeutico: ''
    };

    // Load patients
    this.clinicaSprint1.getPacientes().subscribe({
      next: (pacs) => {
        // Filter out patients who already have an open EHR
        const idsConHistoria = new Set(this.historias().map(h => typeof h.paciente === 'string' ? h.paciente : (h.paciente as any)?.id));
        this.pacientesDisponibles.set(pacs.filter(p => !idsConHistoria.has(p.id)));
        this.mostrarModalApertura = true;
      }
    });
  }

  guardarApertura(): void {
    if (!this.nuevaHistoria.paciente || !this.nuevaHistoria.motivo_consulta_inicial) return;

    this.clinicaSprint2.crearHistoriaClinica(this.nuevaHistoria).subscribe({
      next: (creada) => {
        this.mostrarModalApertura = false;
        this.verDetalle(creada.id);
      },
      error: (err) => {
        this.errorApertura.set(err?.error?.error || 'Error al aperturar la historia clínica.');
      }
    });
  }
}
