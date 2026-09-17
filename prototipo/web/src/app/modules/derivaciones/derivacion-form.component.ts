// ==============================================================================
// MÓDULO: derivacion-form.component.ts
// CAPA BCE: BOUNDARY (Interfaz de Usuario) — IU_CierreYDerivacionCaso
// CASOS DE USO: CU19: Protocolo de Cierre e Interconsulta Médica/Psiquiátrica (HU-33, HU-34)
// DESCRIPCIÓN: Formulario formal para emisión de orden de derivación médica/psiquiátrica,
//              protocolo de alta terapéutica, bloqueo de agenda y descarga de orden en PDF.
// ==============================================================================
import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ClinicaSprint2Service } from '../../core/services/clinica-sprint2.service';
import { DerivacionCaso, HistoriaClinica } from '../../core/models/clinica-sprint2.model';

@Component({
  selector: 'app-derivacion-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="derivacion-container">
      
      <!-- Encabezado -->
      <div class="page-header glass-panel mb-4">
        <div>
          <h1 class="page-title">
            <i class="fa-solid fa-share-from-square text-primary"></i> Cierre de Caso y Órdenes de Derivación
          </h1>
          <p class="page-subtitle">
            Emisión de órdenes de interconsulta psiquiátrica/médica, alta formal y bloqueo preventivo de citas (Sprint 2 - HU-33, HU-34).
          </p>
        </div>
        <div class="header-actions">
          <button class="btn btn-primary" (click)="abrirModalNuevaDerivacion()">
            <i class="fa-solid fa-file-medical"></i> Registrar Cierre / Derivación
          </button>
        </div>
      </div>

      <!-- Banner de Feedback -->
      <div *ngIf="mensajeAviso()" class="alert alert-success d-flex align-items-center mb-4">
        <i class="fa-solid fa-circle-check me-2"></i>
        <span>{{ mensajeAviso() }}</span>
      </div>

      <!-- Estado de Carga -->
      <div *ngIf="cargando()" class="loading-state glass-panel text-center p-5">
        <i class="fa-solid fa-spinner fa-spin fa-2x text-primary mb-3"></i>
        <p class="text-muted">Cargando registros de derivación y cierre...</p>
      </div>

      <!-- Estado Vacío -->
      <div *ngIf="!cargando() && derivaciones().length === 0" class="empty-state glass-panel text-center p-5">
        <i class="fa-solid fa-notes-medical fa-3x text-dim mb-3"></i>
        <h3>No hay derivaciones ni cierres de caso registrados</h3>
        <p class="text-muted">Cuando un caso concluya o requiera interconsulta psiquiátrica externa, aparecerá registrado aquí.</p>
      </div>

      <!-- Tabla de Derivaciones y Cierres -->
      <div class="table-responsive glass-panel" *ngIf="!cargando() && derivaciones().length > 0">
        <table class="custom-table">
          <thead>
            <tr>
              <th>Paciente</th>
              <th>Tipo de Cierre</th>
              <th>Destino / Especialidad</th>
              <th>Fecha de Registro</th>
              <th>Bloqueo de Citas</th>
              <th>Psicólogo Emisor</th>
              <th class="text-end">Orden PDF</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let d of derivaciones()">
              <td>
                <strong>{{ d.paciente_nombre }}</strong>
              </td>
              <td>
                <span class="badge" [ngClass]="getTipoCierreBadge(d.tipo_cierre)">
                  {{ d.tipo_cierre }}
                </span>
              </td>
              <td>
                <div *ngIf="d.especialidad_destino">
                  <strong>{{ d.especialidad_destino }}</strong>
                  <div class="small text-muted">{{ d.profesional_o_institucion_destino || 'No especificado' }}</div>
                </div>
                <div *ngIf="!d.especialidad_destino" class="text-muted small">N/A (Cierre Interno)</div>
              </td>
              <td>{{ d.fecha_registro | date:'dd/MM/yyyy HH:mm' }}</td>
              <td>
                <span class="badge" [class.bg-danger]="d.bloquear_citas_subsecuentes" [class.bg-light]="!d.bloquear_citas_subsecuentes" [class.text-dark]="!d.bloquear_citas_subsecuentes">
                  <i class="fa-solid" [class.fa-lock]="d.bloquear_citas_subsecuentes" [class.fa-lock-open]="!d.bloquear_citas_subsecuentes"></i>
                  {{ d.bloquear_citas_subsecuentes ? 'Agenda Bloqueada' : 'Permitidas' }}
                </span>
              </td>
              <td>{{ d.psicologo_nombre }}</td>
              <td class="text-end">
                <button class="btn btn-sm btn-outline-danger" (click)="descargarPdf(d.id)" title="Descargar Orden Médica en PDF">
                  <i class="fa-solid fa-file-pdf me-1"></i> Orden Médica
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- MODAL NUEVO CIERRE / DERIVACIÓN -->
      <div *ngIf="mostrarModal" class="modal-backdrop-custom" (click)="mostrarModal = false">
        <div class="modal-dialog-custom glass-card-modal modal-lg" (click)="$event.stopPropagation()">
          <div class="modal-header-custom">
            <h2 class="modal-title">
              <i class="fa-solid fa-share-from-square text-primary me-2"></i>
              Emitir Protocolo de Cierre o Interconsulta
            </h2>
            <button class="btn-close-custom" (click)="mostrarModal = false"><i class="fa-solid fa-xmark"></i></button>
          </div>

          <div class="modal-body-custom p-4">
            <div class="row g-3 mb-3">
              <div class="col-md-6">
                <label class="form-label">Historia Clínica del Paciente *</label>
                <select class="form-select" [(ngModel)]="nuevaDerivacion.historia_clinica">
                  <option value="" disabled selected>-- Seleccione expediente --</option>
                  <option *ngFor="let h of historias()" [value]="h.id">
                    {{ h.numero_historia }} - {{ h.paciente_nombre }}
                  </option>
                </select>
              </div>

              <div class="col-md-6">
                <label class="form-label">Tipo de Cierre o Derivación *</label>
                <select class="form-select" [(ngModel)]="nuevaDerivacion.tipo_cierre">
                  <option value="DERIVACION_PSIQUIATRIA">Derivación a Psiquiatría (Interconsulta)</option>
                  <option value="DERIVACION_MEDICA">Derivación Médica General / Neurología</option>
                  <option value="ALTA_TERAPEUTICA">Alta Terapéutica (Objetivos Cumplidos)</option>
                  <option value="ABANDONO">Cierre por Deserción / Abandono</option>
                  <option value="ADMINISTRATIVO">Cierre Administrativo</option>
                </select>
              </div>
            </div>

            <!-- Campos condicionales si es Derivación Médica o Psiquiátrica -->
            <div class="row g-3 mb-3" *ngIf="nuevaDerivacion.tipo_cierre.startsWith('DERIVACION')">
              <div class="col-md-6">
                <label class="form-label">Especialidad de Destino *</label>
                <input type="text" class="form-control" [(ngModel)]="nuevaDerivacion.especialidad_destino"
                       placeholder="Ej. Psiquiatría General, Paidopsiquiatría, Neurología..." />
              </div>
              <div class="col-md-6">
                <label class="form-label">Profesional o Institución Receptora</label>
                <input type="text" class="form-control" [(ngModel)]="nuevaDerivacion.profesional_o_institucion_destino"
                       placeholder="Ej. Hospital Psiquiátrico / Dr. Gómez" />
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label">Motivo de la Derivación o Cierre *</label>
              <textarea class="form-control" rows="2" [(ngModel)]="nuevaDerivacion.motivo_derivacion"
                        placeholder="Fundamentación clínica del motivo de la derivación o circunstancias del cierre..."></textarea>
            </div>

            <div class="mb-3">
              <label class="form-label">Resumen de la Evolución Psicológica *</label>
              <textarea class="form-control" rows="3" [(ngModel)]="nuevaDerivacion.resumen_evolucion"
                        placeholder="Síntesis de sesiones realizadas, respuesta al tratamiento e hipótesis diagnósticas trabajadas..."></textarea>
            </div>

            <div class="mb-3">
              <label class="form-label">Recomendaciones y Sugerencias de Tratamiento</label>
              <textarea class="form-control" rows="2" [(ngModel)]="nuevaDerivacion.recomendaciones_tratamiento"
                        placeholder="Pautas sugeridas para el equipo receptor (ej. valoración psicofarmacológica complementaria)..."></textarea>
            </div>

            <!-- HU-33: Bloqueo de Citas Subsecuentes -->
            <div class="form-check form-switch p-3 rounded glass-panel mb-2">
              <input class="form-check-input ms-0 me-2" type="checkbox" [(ngModel)]="nuevaDerivacion.bloquear_citas_subsecuentes" id="chkBloqueo" />
              <label class="form-check-label fw-bold text-dark" for="chkBloqueo">
                Bloquear reserva de citas subsecuentes en la agenda (HU-33)
              </label>
              <div class="small text-muted ms-4">
                Impide que el paciente o recepcionista agenden nuevas sesiones estándar tras el alta o derivación definitiva.
              </div>
            </div>

          </div>

          <div class="modal-footer-custom p-3">
            <button class="btn btn-secondary" (click)="mostrarModal = false">Cancelar</button>
            <button class="btn btn-primary" [disabled]="!nuevaDerivacion.historia_clinica || !nuevaDerivacion.motivo_derivacion" (click)="guardarDerivacion()">
              <i class="fa-solid fa-file-medical me-1"></i> Generar Orden Oficial & Sellar Cierre
            </button>
          </div>
        </div>
      </div>

    </div>
  `,
  styles: [`
    .derivacion-container { max-width: 1300px; margin: 0 auto; }
    .page-header {
      padding: 1.5rem 2rem; border-radius: 16px; background: #ffffff;
      border: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center;
    }
    .page-title { font-size: 1.5rem; font-weight: 700; color: #0f172a; margin: 0 0 0.25rem 0; }
    .page-subtitle { font-size: 0.88rem; color: #64748b; margin: 0; }

    .custom-table { width: 100%; border-collapse: collapse; background: #ffffff; border-radius: 12px; }
    .custom-table th { background: #f8fafc; padding: 0.85rem 1rem; font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; }
    .custom-table td { padding: 0.85rem 1rem; font-size: 0.85rem; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }

    .modal-backdrop-custom {
      position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
      background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px); z-index: 1050;
      display: flex; align-items: center; justify-content: center; padding: 1.5rem;
    }
    .modal-dialog-custom {
      width: 100%; max-width: 800px; background: #ffffff; border-radius: 16px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); overflow: hidden;
    }
    .modal-header-custom { padding: 1.25rem 1.5rem; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
    .modal-footer-custom { border-top: 1px solid #e2e8f0; background: #f8fafc; display: flex; justify-content: flex-end; gap: 0.75rem; }
  `]
})
export class DerivacionFormComponent implements OnInit {
  cargando = signal<boolean>(true);
  derivaciones = signal<DerivacionCaso[]>([]);
  historias = signal<HistoriaClinica[]>([]);
  mensajeAviso = signal<string | null>(null);

  mostrarModal = false;
  nuevaDerivacion = {
    historia_clinica: '',
    tipo_cierre: 'DERIVACION_PSIQUIATRIA',
    especialidad_destino: 'Psiquiatría General',
    profesional_o_institucion_destino: '',
    motivo_derivacion: '',
    resumen_evolucion: '',
    recomendaciones_tratamiento: '',
    bloquear_citas_subsecuentes: true
  };

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private clinicaService: ClinicaSprint2Service
  ) {}

  ngOnInit(): void {
    this.cargarDatos();

    this.route.queryParams.subscribe(q => {
      if (q['historia']) {
        this.nuevaDerivacion.historia_clinica = q['historia'];
        this.mostrarModal = true;
      }
    });
  }

  cargarDatos(): void {
    this.cargando.set(true);
    this.clinicaService.getDerivaciones().subscribe({
      next: (ds) => {
        this.derivaciones.set(ds);
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

  abrirModalNuevaDerivacion(): void {
    this.nuevaDerivacion = {
      historia_clinica: this.historias().length > 0 ? this.historias()[0].id : '',
      tipo_cierre: 'DERIVACION_PSIQUIATRIA',
      especialidad_destino: 'Psiquiatría General',
      profesional_o_institucion_destino: '',
      motivo_derivacion: '',
      resumen_evolucion: '',
      recomendaciones_tratamiento: '',
      bloquear_citas_subsecuentes: true
    };
    this.mostrarModal = true;
  }

  guardarDerivacion(): void {
    this.clinicaService.crearDerivacion(this.nuevaDerivacion).subscribe({
      next: (d) => {
        this.mostrarModal = false;
        this.mostrarFeedback(`Orden de derivación ${d.id.substring(0, 8)} generada con éxito`);
        this.cargarDatos();
      }
    });
  }

  descargarPdf(derivacionId: string): void {
    this.clinicaService.descargarOrdenDerivacionPdf(derivacionId).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Orden_Derivacion_${derivacionId.substring(0, 8)}.pdf`;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    });
  }

  getTipoCierreBadge(tipo: string): string {
    switch (tipo) {
      case 'DERIVACION_PSIQUIATRIA': return 'bg-danger text-white';
      case 'DERIVACION_MEDICA': return 'bg-warning text-dark';
      case 'ALTA_TERAPEUTICA': return 'bg-success text-white';
      default: return 'bg-secondary text-white';
    }
  }

  mostrarFeedback(msg: string): void {
    this.mensajeAviso.set(msg);
    setTimeout(() => this.mensajeAviso.set(null), 4000);
  }
}
