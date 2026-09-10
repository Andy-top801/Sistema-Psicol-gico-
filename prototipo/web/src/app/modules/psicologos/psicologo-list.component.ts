// ==============================================================================
// MÓDULO: psicologo-list.component.ts
// CAPA BCE: BOUNDARY (Interfaz de Usuario) — IU_GestionPsicologos, IU_PerfilDisponibilidad
// CASOS DE USO: CU6 (Gestión de Psicólogos y Perfiles), CU8 (Gestión de Disponibilidad)
// DESCRIPCIÓN: Componente Angular interactivo que captura los datos de alta/edición
//              de profesionales y la configuración de franjas horarias semanales.
//              Implementa los pasos 1, 2, 7 y 8 de los Diagramas de Comunicación BCE.
// ==============================================================================
import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ClinicaService } from '../../core/services/clinica.service';
import { Especialidad, Psicologo, Disponibilidad, CrearPsicologoDTO } from '../../core/models';

@Component({
  selector: 'app-psicologo-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="psicologos-container">
      <!-- Header de Sección -->
      <div class="page-header glass-panel mb-4">
        <div>
          <h1 class="page-title">
            <i class="fa-solid fa-user-doctor text-primary"></i> Directorio de Psicólogos y Terapeutas
          </h1>
          <p class="page-subtitle">
            Gestión del plantel profesional, colegiatura acreditada, aranceles y franjas de disponibilidad semanal (Sprint 1 - HU-11, HU-12).
          </p>
        </div>
        <div class="header-actions">
          <button class="btn btn-primary" (click)="openCreateModal()">
            <i class="fa-solid fa-user-plus"></i> Registrar Psicólogo
          </button>
        </div>
      </div>

      <!-- Filtros y Búsqueda -->
      <div class="filters-bar glass-panel mb-4">
        <div class="search-box">
          <i class="fa-solid fa-magnifying-glass"></i>
          <input 
            type="text" 
            [(ngModel)]="searchTerm" 
            (ngModelChange)="aplicarFiltros()"
            placeholder="Buscar por nombre, apellido o número de colegiado..."
            class="form-control"
          />
        </div>

        <div class="select-group">
          <select [(ngModel)]="selectedEspecialidad" (ngModelChange)="aplicarFiltros()" class="form-select">
            <option value="">Todas las Especialidades</option>
            <option *ngFor="let esp of especialidades()" [value]="esp.nombre">{{ esp.nombre }}</option>
          </select>

          <select [(ngModel)]="selectedModalidad" (ngModelChange)="aplicarFiltros()" class="form-select">
            <option value="">Todas las Modalidades</option>
            <option value="PRESENCIAL">Presencial</option>
            <option value="VIRTUAL">Virtual</option>
            <option value="MIXTA">Mixta (Presencial/Virtual)</option>
          </select>
        </div>
      </div>

      <!-- Grid de Tarjetas de Psicólogos -->
      <div *ngIf="loading()" class="loading-state glass-panel">
        <i class="fa-solid fa-spinner fa-spin"></i>
        <span>Cargando directorio profesional...</span>
      </div>

      <div *ngIf="!loading() && psicologosFiltrados().length === 0" class="empty-state glass-panel">
        <i class="fa-solid fa-user-doctor fa-3x text-dim mb-3"></i>
        <h3>No se encontraron profesionales registrados</h3>
        <p class="text-muted">Ajusta los filtros o registra un nuevo psicólogo en este centro.</p>
      </div>

      <div *ngIf="!loading() && psicologosFiltrados().length > 0" class="psicologos-grid">
        <div *ngFor="let p of psicologosFiltrados()" class="psicologo-card glass-panel">
          <!-- Card Top -->
          <div class="card-header-flex">
            <div class="avatar-box">
              {{ (p.usuario.nombre.charAt(0) || 'P') }}{{ (p.usuario.apellido ? p.usuario.apellido.charAt(0) : '') }}
            </div>
            <div class="status-indicator">
              <span class="badge" [ngClass]="p.activo ? 'badge-success' : 'badge-danger'">
                {{ p.activo ? 'Activo' : 'Inactivo' }}
              </span>
            </div>
          </div>

          <!-- Info Principal -->
          <div class="card-body-info">
            <h3 class="psico-nombre">{{ p.usuario.nombre }} {{ p.usuario.apellido }}</h3>
            <div class="colegiatura-chip">
              <i class="fa-solid fa-id-card"></i> Colegiado: <strong>{{ p.numero_colegiado }}</strong>
            </div>

            <p class="psico-bio" *ngIf="p.biografia">
              "{{ p.biografia.slice(0, 110) }}{{ p.biografia.length > 110 ? '...' : '' }}"
            </p>

            <!-- Modalidad y Tarifa -->
            <div class="meta-row">
              <div class="meta-item">
                <span class="meta-label">Modalidad</span>
                <span class="badge badge-info">
                  <i class="fa-solid" [ngClass]="p.modalidad === 'VIRTUAL' ? 'fa-video' : (p.modalidad === 'PRESENCIAL' ? 'fa-building' : 'fa-arrows-split-up-and-left')"></i>
                  {{ p.modalidad }}
                </span>
              </div>
              <div class="meta-item">
                <span class="meta-label">Arancel Base</span>
                <span class="tarifa-value">BOB {{ p.tarifa_base }}</span>
              </div>
            </div>

            <!-- Especialidades -->
            <div class="especialidades-wrapper">
              <span class="meta-label">Especialidades</span>
              <div class="tags-container">
                <span *ngFor="let esp of p.especialidades" class="badge badge-primary">
                  {{ esp.nombre }}
                </span>
                <span *ngIf="!p.especialidades || p.especialidades.length === 0" class="text-dim text-sm">
                  Sin especialidades asignadas
                </span>
              </div>
            </div>
          </div>

          <!-- Card Actions -->
          <div class="card-footer-actions d-flex gap-2">
            <button class="btn btn-secondary btn-sm flex-1" (click)="openDisponibilidadModal(p)">
              <i class="fa-solid fa-calendar-days text-primary"></i> Horarios
            </button>
            <button class="btn btn-outline-primary btn-sm flex-1" (click)="openEditModal(p)">
              <i class="fa-solid fa-user-pen text-info"></i> Editar
            </button>
          </div>
        </div>
      </div>

      <!-- ==================================================================== -->
      <!-- MODAL: CONFIGURACIÓN DE DISPONIBILIDAD SEMANAL (CU6 / CU8)            -->
      <!-- ==================================================================== -->
      <div *ngIf="showDisponibilidadModal" class="modal-overlay">
        <div class="modal-content modal-lg">
          <div class="modal-header">
            <div>
              <h2 class="modal-title">
                <i class="fa-solid fa-clock text-primary"></i> Disponibilidad Semanal
              </h2>
              <p class="modal-subtitle">
                Terapeuta: <strong>{{ selectedPsicologo?.usuario?.nombre }} {{ selectedPsicologo?.usuario?.apellido }}</strong> (Col. {{ selectedPsicologo?.numero_colegiado }})
              </p>
            </div>
            <button class="btn-close" (click)="closeDisponibilidadModal()">&times;</button>
          </div>

          <div class="modal-body">
            <div *ngIf="dispModalError()" class="alert-box alert-error mb-3">
              <i class="fa-solid fa-triangle-exclamation"></i>
              <span>{{ dispModalError() }}</span>
            </div>

            <div class="info-alert mb-3">
              <i class="fa-solid fa-circle-info"></i>
              Configura las franjas de atención por día. Los bloques de consulta se dividen automáticamente en slots de 50 minutos para evitar colisiones.
            </div>

            <!-- Tabla de Franjas Horarias -->
            <div class="table-container mb-3">
              <table class="custom-table">
                <thead>
                  <tr>
                    <th>Día</th>
                    <th>Hora Inicio</th>
                    <th>Hora Fin</th>
                    <th>Duración Bloque</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr *ngFor="let f of tempDisponibilidades; let i = index">
                    <td>
                      <select [(ngModel)]="f.dia_semana" class="form-select form-select-sm">
                        <option [value]="1">Lunes</option>
                        <option [value]="2">Martes</option>
                        <option [value]="3">Miércoles</option>
                        <option [value]="4">Jueves</option>
                        <option [value]="5">Viernes</option>
                        <option [value]="6">Sábado</option>
                        <option [value]="0">Domingo</option>
                      </select>
                    </td>
                    <td>
                      <input type="time" [(ngModel)]="f.hora_inicio" class="form-control form-control-sm" />
                    </td>
                    <td>
                      <input type="time" [(ngModel)]="f.hora_fin" class="form-control form-control-sm" />
                    </td>
                    <td>
                      <span class="badge badge-info">{{ f.duracion_bloque_min }} min</span>
                    </td>
                    <td>
                      <button class="btn btn-danger btn-sm" (click)="removerFranja(i)" title="Eliminar franja">
                        <i class="fa-solid fa-trash"></i>
                      </button>
                    </td>
                  </tr>
                  <tr *ngIf="tempDisponibilidades.length === 0">
                    <td colspan="5" class="text-center text-muted py-3">
                      No hay horarios configurados. Haz clic en "Añadir Franja Horaria".
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <button class="btn btn-secondary btn-sm" (click)="agregarFranja()">
              <i class="fa-solid fa-plus"></i> Añadir Franja Horaria
            </button>
          </div>

          <div class="modal-footer">
            <button class="btn btn-secondary" (click)="closeDisponibilidadModal()">Cancelar</button>
            <button class="btn btn-primary" [disabled]="savingDisponibilidad" (click)="guardarDisponibilidadCU6CU8()">
              <i class="fa-solid fa-floppy-disk" *ngIf="!savingDisponibilidad"></i>
              <i class="fa-solid fa-spinner fa-spin" *ngIf="savingDisponibilidad"></i>
              {{ savingDisponibilidad ? 'Guardando...' : 'Guardar Horario Semanal' }}
            </button>
          </div>
        </div>
      </div>

      <!-- ==================================================================== -->
      <!-- MODAL: REGISTRO DE PSICÓLOGO                                         -->
      <!-- ==================================================================== -->
      <div *ngIf="showCreateModal" class="modal-overlay">
        <div class="modal-content">
          <div class="modal-header">
            <h2 class="modal-title">
              <i class="fa-solid" [ngClass]="editingPsicologoId ? 'fa-user-pen text-info' : 'fa-user-plus text-primary'"></i>
              {{ editingPsicologoId ? 'Editar Terapeuta' : 'Registrar Terapeuta' }}
            </h2>
            <button class="btn-close" (click)="closeCreateModal()">&times;</button>
          </div>

          <form (ngSubmit)="guardarPsicologo()" class="modal-body">
            <div *ngIf="modalError()" class="alert-box alert-error mb-3">
              <i class="fa-solid fa-triangle-exclamation"></i>
              <span>{{ modalError() }}</span>
            </div>

            <div class="form-row">
              <div class="form-group col">
                <label class="form-label">Nombre</label>
                <input type="text" [(ngModel)]="nuevoPsico.nombre" name="nombre" class="form-control" required placeholder="Ej: Dr. Roberto" />
              </div>
              <div class="form-group col">
                <label class="form-label">Apellido</label>
                <input type="text" [(ngModel)]="nuevoPsico.apellido" name="apellido" class="form-control" required placeholder="Ej: Méndez" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group col">
                <label class="form-label">Correo Electrónico</label>
                <input type="email" [(ngModel)]="nuevoPsico.email" name="email" class="form-control" required placeholder="roberto@sigepsi.com" />
              </div>
              <div class="form-group col">
                <label class="form-label">{{ editingPsicologoId ? 'Cambiar Contraseña (Opcional)' : 'Contraseña Temporal *' }}</label>
                <input type="password" [(ngModel)]="nuevoPsico.password" name="password" class="form-control" [required]="!editingPsicologoId" [placeholder]="editingPsicologoId ? 'Dejar vacío para conservar actual' : 'Mínimo 8 caracteres'" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group col">
                <label class="form-label">Nro. Colegiado Profesional</label>
                <input type="text" [(ngModel)]="nuevoPsico.numero_colegiado" name="colegiado" class="form-control" required placeholder="Ej: COL-PSI-7788" />
              </div>
              <div class="form-group col">
                <label class="form-label">Teléfono</label>
                <input type="text" [(ngModel)]="nuevoPsico.telefono" name="telefono" class="form-control" placeholder="+591 70012345" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group col">
                <label class="form-label">Modalidad de Atención</label>
                <select [(ngModel)]="nuevoPsico.modalidad" name="modalidad" class="form-select">
                  <option value="MIXTA">Mixta (Presencial / Virtual)</option>
                  <option value="PRESENCIAL">Sólo Presencial</option>
                  <option value="VIRTUAL">Sólo Virtual (Teleconsulta)</option>
                </select>
              </div>
              <div class="form-group col">
                <label class="form-label">Tarifa Base por Sesión (BOB)</label>
                <input type="number" [(ngModel)]="nuevoPsico.tarifa_base" name="tarifa" class="form-control" min="0" required />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Especialidades Acreditadas</label>
              <div class="checkbox-grid">
                <label *ngFor="let esp of especialidades()" class="checkbox-item">
                  <input 
                    type="checkbox" 
                    [checked]="isEspecialidadSelected(esp.id)" 
                    (change)="toggleEspecialidad(esp.id)"
                  />
                  <span>{{ esp.nombre }}</span>
                </label>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Breve Biografía Profesional</label>
              <textarea [(ngModel)]="nuevoPsico.biografia" name="bio" rows="2" class="form-control" placeholder="Formación de posgrado, años de experiencia clínica..."></textarea>
            </div>

            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" (click)="closeCreateModal()">Cancelar</button>
              <button type="submit" class="btn btn-primary" [disabled]="savingPsicologo">
                <i class="fa-solid fa-floppy-disk" *ngIf="!savingPsicologo"></i>
                <i class="fa-solid fa-spinner fa-spin" *ngIf="savingPsicologo"></i>
                {{ savingPsicologo ? 'Guardando...' : (editingPsicologoId ? 'Guardar Cambios' : 'Crear Psicólogo') }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Toast Feedback -->
      <div *ngIf="toastMsg" class="toast" [ngClass]="toastType === 'success' ? 'toast-success' : 'toast-error'">
        <i class="fa-solid" [ngClass]="toastType === 'success' ? 'fa-circle-check' : 'fa-triangle-exclamation'"></i>
        <span>{{ toastMsg }}</span>
      </div>
    </div>
  `,
  styles: [`
    .psicologos-container {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    .page-header {
      padding: 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-radius: 16px;
    }
    .page-title {
      font-size: 1.5rem;
      font-weight: 800;
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .page-subtitle {
      font-size: 0.9rem;
      color: var(--text-muted);
      margin-top: 4px;
    }
    .filters-bar {
      padding: 16px 20px;
      display: flex;
      justify-content: space-between;
      gap: 16px;
      border-radius: 14px;
      flex-wrap: wrap;
    }
    .search-box {
      flex: 1;
      min-width: 280px;
      display: flex;
      align-items: center;
      gap: 10px;
      background: var(--bg-input);
      border: 1px solid var(--border-glass);
      border-radius: 10px;
      padding: 0 14px;
    }
    .search-box i {
      color: var(--text-dim);
    }
    .search-box input {
      border: none;
      background: transparent;
      padding: 10px 0;
    }
    .select-group {
      display: flex;
      gap: 12px;
    }
    .psicologos-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 20px;
    }
    .psicologo-card {
      padding: 22px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 16px;
      border-radius: 16px;
    }
    .card-header-flex {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
    }
    .avatar-box {
      width: 52px;
      height: 52px;
      border-radius: 14px;
      background: #e6f5ed;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.25rem;
      font-weight: 800;
      color: #19734e;
      border: 1px solid #c7e6d7;
      box-shadow: 0 2px 8px rgba(25, 115, 78, 0.08);
    }
    .psico-nombre {
      font-size: 1.15rem;
      font-weight: 700;
      margin-bottom: 4px;
    }
    .colegiatura-chip {
      font-size: 0.8rem;
      color: var(--text-dim);
      margin-bottom: 10px;
    }
    .colegiatura-chip strong {
      color: var(--text-muted);
    }
    .psico-bio {
      font-size: 0.84rem;
      color: var(--text-muted);
      font-style: italic;
      line-height: 1.4;
      margin-bottom: 12px;
    }
    .meta-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 0;
      border-top: 1px solid var(--border-glass);
      border-bottom: 1px solid var(--border-glass);
      margin-bottom: 12px;
    }
    .meta-item {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .meta-label {
      font-size: 0.72rem;
      font-weight: 700;
      color: var(--text-dim);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .tarifa-value {
      font-size: 1rem;
      font-weight: 800;
      color: var(--success);
    }
    .especialidades-wrapper {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .tags-container {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }
    .card-footer-actions {
      border-top: 1px solid var(--border-glass);
      padding-top: 14px;
    }
    .w-100 { width: 100%; }
    .loading-state, .empty-state {
      padding: 50px 20px;
      text-align: center;
      border-radius: 16px;
    }
    .modal-lg {
      max-width: 700px;
    }
    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 20px;
      border-bottom: 1px solid var(--border-glass);
      padding-bottom: 14px;
    }
    .modal-title {
      font-size: 1.3rem;
      font-weight: 800;
    }
    .modal-subtitle {
      font-size: 0.85rem;
      color: var(--text-muted);
    }
    .btn-close {
      background: transparent;
      border: none;
      color: var(--text-dim);
      font-size: 1.5rem;
      cursor: pointer;
    }
    .modal-body {
      display: flex;
      flex-direction: column;
      gap: 14px;
    }
    .info-alert {
      background: rgba(14, 165, 233, 0.1);
      border: 1px solid rgba(14, 165, 233, 0.25);
      border-radius: 10px;
      padding: 10px 14px;
      font-size: 0.84rem;
      color: #7dd3fc;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .form-row {
      display: flex;
      gap: 14px;
    }
    .col { flex: 1; }
    .checkbox-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
      background: var(--bg-input);
      padding: 12px;
      border-radius: 10px;
      border: 1px solid var(--border-glass);
    }
    .checkbox-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.86rem;
      color: var(--text-muted);
      cursor: pointer;
    }
    .modal-footer {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      margin-top: 20px;
      padding-top: 16px;
      border-top: 1px solid var(--border-glass);
    }

    @media (max-width: 768px) {
      .page-header {
        flex-direction: column;
        align-items: stretch;
        gap: 14px;
        padding: 18px;
      }
      .header-actions .btn {
        width: 100%;
        justify-content: center;
      }
      .page-title {
        font-size: 1.25rem;
      }
      .filters-bar {
        flex-direction: column;
        gap: 12px;
      }
      .select-group {
        flex-direction: column;
        gap: 10px;
      }
      .modal-footer {
        flex-direction: column-reverse;
      }
      .modal-footer .btn {
        width: 100%;
        justify-content: center;
      }
    }
  `]
})
export class PsicologoListComponent implements OnInit {
  psicologos = signal<Psicologo[]>([]);
  psicologosFiltrados = signal<Psicologo[]>([]);
  especialidades = signal<Especialidad[]>([]);
  loading = signal<boolean>(true);

  // Filtros
  searchTerm = '';
  selectedEspecialidad = '';
  selectedModalidad = '';

  // Modal Disponibilidad (CU6/CU8)
  showDisponibilidadModal = false;
  selectedPsicologo: Psicologo | null = null;
  tempDisponibilidades: Disponibilidad[] = [];
  savingDisponibilidad = false;
  dispModalError = signal<string | null>(null);

  // Modal Registro / Edición
  showCreateModal = false;
  editingPsicologoId: string | null = null;
  savingPsicologo = false;
  modalError = signal<string | null>(null);
  nuevoPsico: CrearPsicologoDTO = {
    nombre: '',
    apellido: '',
    email: '',
    password: '',
    telefono: '',
    numero_colegiado: '',
    biografia: '',
    modalidad: 'MIXTA',
    tarifa_base: 150.00,
    especialidad_ids: []
  };

  // Toast
  toastMsg = '';
  toastType: 'success' | 'error' = 'success';

  constructor(private clinicaService: ClinicaService) {}

  ngOnInit(): void {
    this.cargarDatos();
  }

  cargarDatos(): void {
    this.loading.set(true);
    this.clinicaService.getEspecialidades().subscribe({
      next: (esps) => this.especialidades.set(esps),
      error: (err) => console.error('Error cargando especialidades', err)
    });

    this.clinicaService.getPsicologos().subscribe({
      next: (res) => {
        this.psicologos.set(res);
        this.aplicarFiltros();
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Error cargando psicólogos', err);
        this.loading.set(false);
      }
    });
  }

  aplicarFiltros(): void {
    const term = this.searchTerm.toLowerCase().trim();
    const filtrados = this.psicologos().filter(p => {
      const matchSearch = !term || 
        p.usuario?.nombre?.toLowerCase().includes(term) ||
        p.usuario?.apellido?.toLowerCase().includes(term) ||
        p.numero_colegiado?.toLowerCase().includes(term);
      
      const matchEsp = !this.selectedEspecialidad ||
        p.especialidades?.some(e => e.nombre === this.selectedEspecialidad);
      
      const matchMod = !this.selectedModalidad || p.modalidad === this.selectedModalidad;

      return matchSearch && matchEsp && matchMod;
    });

    this.psicologosFiltrados.set(filtrados);
  }

  // --------------------------------------------------------------------------
  // DISPONIBILIDAD SEMANAL (CU6 / CU8 - HU-11, HU-12)
  // --------------------------------------------------------------------------
  openDisponibilidadModal(psico: Psicologo): void {
    this.selectedPsicologo = psico;
    this.dispModalError.set(null);
    this.showDisponibilidadModal = true;
    this.clinicaService.getDisponibilidad(psico.id).subscribe({
      next: (disps) => {
        this.tempDisponibilidades = disps && disps.length > 0 ? [...disps] : [
          { dia_semana: 1, hora_inicio: '08:00', hora_fin: '12:00', duracion_bloque_min: 50 },
          { dia_semana: 1, hora_inicio: '14:00', hora_fin: '18:00', duracion_bloque_min: 50 }
        ];
      },
      error: () => {
        this.tempDisponibilidades = [
          { dia_semana: 1, hora_inicio: '08:00', hora_fin: '12:00', duracion_bloque_min: 50 }
        ];
      }
    });
  }

  closeDisponibilidadModal(): void {
    this.showDisponibilidadModal = false;
    this.selectedPsicologo = null;
    this.tempDisponibilidades = [];
    this.dispModalError.set(null);
  }

  agregarFranja(): void {
    this.dispModalError.set(null);
    this.tempDisponibilidades.push({
      dia_semana: 1,
      hora_inicio: '09:00',
      hora_fin: '13:00',
      duracion_bloque_min: 50
    });
  }

  removerFranja(index: number): void {
    this.dispModalError.set(null);
    this.tempDisponibilidades.splice(index, 1);
  }

  /**
   * ═══════════════════════════════════════════════════════════════════════════
   * CU6 / CU8: Guardar Disponibilidad Horaria Semanal
   * Diagrama de Comunicación – Pasos del Flujo:
   *   Actor  → Administrador / Psicólogo
   *   IU     → IU_PerfilDisponibilidad (PsicologoListComponent)
   *   CTR    → CTR_PsicologoService (Django REST)
   *   CE     → CE_Psicologo_y_Horario (PostgreSQL)
   * ═══════════════════════════════════════════════════════════════════════════
   */
  guardarDisponibilidadCU6CU8(): void {
    this.dispModalError.set(null);
    if (!this.selectedPsicologo) return;

    if (!this.tempDisponibilidades || this.tempDisponibilidades.length === 0) {
      this.dispModalError.set('Debe configurar al menos una franja horaria para el terapeuta.');
      return;
    }

    // Validación de cada franja (HU-12 / TP-30)
    for (let i = 0; i < this.tempDisponibilidades.length; i++) {
      const f = this.tempDisponibilidades[i];
      if (!f.hora_inicio || !f.hora_fin) {
        this.dispModalError.set(`Franja #${i + 1}: Complete la hora de inicio y fin.`);
        return;
      }
      if (f.hora_fin <= f.hora_inicio) {
        this.dispModalError.set(`Franja #${i + 1}: Hora de fin debe ser posterior a la de inicio (${f.hora_inicio} - ${f.hora_fin}).`);
        return;
      }
      if (!f.duracion_bloque_min || Number(f.duracion_bloque_min) <= 0) {
        this.dispModalError.set(`Franja #${i + 1}: La duración de bloque debe ser mayor a 0 minutos.`);
        return;
      }
    }

    // Validación de solapamiento entre franjas del mismo día
    for (let i = 0; i < this.tempDisponibilidades.length; i++) {
      for (let j = i + 1; j < this.tempDisponibilidades.length; j++) {
        const a = this.tempDisponibilidades[i];
        const b = this.tempDisponibilidades[j];
        if (Number(a.dia_semana) === Number(b.dia_semana)) {
          if (a.hora_inicio < b.hora_fin && b.hora_inicio < a.hora_fin) {
            const dias = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
            const diaNom = dias[Number(a.dia_semana)] || 'Día ' + a.dia_semana;
            this.dispModalError.set(`Conflicto de horario en ${diaNom}: Las franjas ${a.hora_inicio}-${a.hora_fin} y ${b.hora_inicio}-${b.hora_fin} se solapan.`);
            return;
          }
        }
      }
    }

    // --- Paso 1: Configurar franjas semanales y duración bloque en IU_PerfilDisponibilidad > ---
    this.savingDisponibilidad = true;

    // --- Paso 2: POST /api/clinica/disponibilidad/ + JWT > ---
    this.clinicaService.guardarDisponibilidad(this.selectedPsicologo.id, this.tempDisponibilidades).subscribe({
      // --- Paso 7: 200 OK {franjas_configuradas, slots_generados} < ---
      next: (res) => {
        this.savingDisponibilidad = false;
        this.closeDisponibilidadModal();
        // --- Paso 8: Mostrar 'Horario laboral actualizado' en IU_PerfilDisponibilidad < ---
        this.mostrarToast(`Horario laboral actualizado correctamente (${res.count || this.tempDisponibilidades.length} franjas).`, 'success');
      },
      error: (err) => {
        this.savingDisponibilidad = false;
        const msg = err.error?.error || err.error?.detail || 'Error al guardar la disponibilidad horaria';
        this.dispModalError.set(msg);
        this.mostrarToast(msg, 'error');
      }
    });
  }

  // --------------------------------------------------------------------------
  // REGISTRO Y EDICIÓN DE PSICÓLOGO
  // --------------------------------------------------------------------------
  openCreateModal(): void {
    this.editingPsicologoId = null;
    this.modalError.set(null);
    this.nuevoPsico = {
      nombre: '',
      apellido: '',
      email: '',
      password: '',
      telefono: '',
      numero_colegiado: '',
      biografia: '',
      modalidad: 'MIXTA',
      tarifa_base: 150.00,
      especialidad_ids: []
    };
    this.showCreateModal = true;
  }

  openEditModal(p: Psicologo): void {
    this.editingPsicologoId = p.id;
    this.modalError.set(null);
    this.nuevoPsico = {
      nombre: p.usuario?.nombre || '',
      apellido: p.usuario?.apellido || '',
      email: p.usuario?.email || '',
      password: '',
      telefono: p.usuario?.telefono || '',
      numero_colegiado: p.numero_colegiado || '',
      biografia: p.biografia || '',
      modalidad: p.modalidad || 'MIXTA',
      tarifa_base: Number(p.tarifa_base) || 150.00,
      especialidad_ids: (p.especialidades || []).map(e => e.id)
    };
    this.showCreateModal = true;
  }

  closeCreateModal(): void {
    this.showCreateModal = false;
    this.editingPsicologoId = null;
    this.modalError.set(null);
  }

  isEspecialidadSelected(id: number): boolean {
    return this.nuevoPsico.especialidad_ids.includes(id);
  }

  toggleEspecialidad(id: number): void {
    const idx = this.nuevoPsico.especialidad_ids.indexOf(id);
    if (idx > -1) {
      this.nuevoPsico.especialidad_ids.splice(idx, 1);
    } else {
      this.nuevoPsico.especialidad_ids.push(id);
    }
  }

  /**
   * ═══════════════════════════════════════════════════════════════════════════
   * CU6: Gestión de Psicólogos y Perfiles Profesionales (HU-11)
   * Diagrama de Comunicación – Pasos del Flujo:
   *   Actor  → Administrador del Centro
   *   IU     → IU_GestionPsicologos (PsicologoListComponent)
   *   CTR    → CTR_PsicologoService (Django REST - clinica/views.py)
   *   CE     → CE_Psicologo_y_Especialidad (PostgreSQL)
   * ═══════════════════════════════════════════════════════════════════════════
   */
  guardarPsicologo(): void {
    this.modalError.set(null);

    // --- Paso 1: Ingresar datos de Psicólogo en IU_GestionPsicologos ---
    // Validaciones frontend de campos obligatorios y formatos (HU-11 / TP-27 / TP-28)
    if (!this.nuevoPsico.nombre || this.nuevoPsico.nombre.trim() === '') {
      this.modalError.set('El nombre del psicólogo es obligatorio.');
      return;
    }
    if (!this.nuevoPsico.apellido || this.nuevoPsico.apellido.trim() === '') {
      this.modalError.set('El apellido del psicólogo es obligatorio.');
      return;
    }
    if (!this.nuevoPsico.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.nuevoPsico.email.trim())) {
      this.modalError.set('Ingrese un correo electrónico válido para el psicólogo.');
      return;
    }
    if (!this.editingPsicologoId) {
      if (!this.nuevoPsico.password || this.nuevoPsico.password.length < 8) {
        this.modalError.set('La contraseña inicial es requerida y debe tener al menos 8 caracteres.');
        return;
      }
    }
    if (!this.nuevoPsico.numero_colegiado || this.nuevoPsico.numero_colegiado.trim() === '') {
      this.modalError.set('El número de colegiado profesional es obligatorio.');
      return;
    }
    if (this.nuevoPsico.tarifa_base === null || this.nuevoPsico.tarifa_base === undefined || Number(this.nuevoPsico.tarifa_base) <= 0) {
      this.modalError.set('La tarifa debe ser mayor a cero.');
      return;
    }
    if (!this.nuevoPsico.especialidad_ids || this.nuevoPsico.especialidad_ids.length === 0) {
      this.modalError.set('Debe seleccionar al menos una especialidad acreditada.');
      return;
    }

    this.savingPsicologo = true;
    const payload: any = {
      ...this.nuevoPsico,
      especialidad_ids: this.nuevoPsico.especialidad_ids,
      especialidades_ids: this.nuevoPsico.especialidad_ids
    };

    if (this.editingPsicologoId && !payload.password) {
      delete payload.password;
    }

    // --- Paso 2: POST /api/clinica/psicologos/ > ---
    // IU_GestionPsicologos envía los datos del terapeuta al CTR_PsicologoService
    const action$ = this.editingPsicologoId
      ? this.clinicaService.updatePsicologo(this.editingPsicologoId, payload)
      : this.clinicaService.createPsicologo(payload);

    action$.subscribe({
      // --- Paso 7: 201 Created < ---
      // CTR_PsicologoService confirma la creación de usuario, perfil y disponibilidad
      next: () => {
        this.savingPsicologo = false;
        // --- Paso 8: Mostrar confirmación en IU_GestionPsicologos < ---
        const msg = this.editingPsicologoId
          ? 'Psicólogo actualizado exitosamente.'
          : 'Psicólogo registrado exitosamente en el directorio.';
        this.closeCreateModal();
        this.mostrarToast(msg, 'success');
        this.cargarDatos();
      },
      error: (err) => {
        this.savingPsicologo = false;
        let msg = 'Error al registrar el profesional';
        if (err.error) {
          if (typeof err.error === 'string') msg = err.error;
          else if (err.error.error) msg = err.error.error;
          else {
            const parts: string[] = [];
            for (const k of Object.keys(err.error)) {
              const v = err.error[k];
              parts.push(`${k}: ${Array.isArray(v) ? v.join(', ') : v}`);
            }
            if (parts.length > 0) msg = parts.join(' | ');
          }
        }
        this.modalError.set(msg);
        this.mostrarToast(msg, 'error');
      }
    });
  }

  private mostrarToast(msg: string, type: 'success' | 'error'): void {
    this.toastMsg = msg;
    this.toastType = type;
    setTimeout(() => {
      this.toastMsg = '';
    }, 4000);
  }
}
