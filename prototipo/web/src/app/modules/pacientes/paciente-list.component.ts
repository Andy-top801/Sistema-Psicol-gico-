import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ClinicaService } from '../../core/services/clinica.service';
import { Paciente, CrearPacienteDTO } from '../../core/models';

@Component({
  selector: 'app-paciente-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="pacientes-container">
      <!-- Header de Sección -->
      <div class="page-header glass-panel mb-4">
        <div>
          <h1 class="page-title">
            <i class="fa-solid fa-folder-open text-primary"></i> Expedientes de Pacientes
          </h1>
          <p class="page-subtitle">
            Padrón clínico de pacientes, expedientes sociodemográficos y validación de minoría de edad con tutor legal (Sprint 1 - HU-13, HU-14).
          </p>
        </div>
        <div class="header-actions">
          <button class="btn btn-primary" (click)="openCreateModal()">
            <i class="fa-solid fa-user-plus"></i> Registrar Paciente
          </button>
        </div>
      </div>

      <!-- Barra de Búsqueda -->
      <div class="filters-bar glass-panel mb-4">
        <div class="search-box">
          <i class="fa-solid fa-magnifying-glass"></i>
          <input 
            type="text" 
            [(ngModel)]="searchTerm" 
            (ngModelChange)="buscarPacientes()"
            placeholder="Buscar por Carnet de Identidad (CI), nombre, apellido o código de expediente..."
            class="form-control"
          />
        </div>
      </div>

      <!-- Estado de Carga -->
      <div *ngIf="loading()" class="loading-state glass-panel">
        <i class="fa-solid fa-spinner fa-spin"></i>
        <span>Cargando expedientes clínicos...</span>
      </div>

      <!-- Estado Vacío -->
      <div *ngIf="!loading() && pacientes().length === 0" class="empty-state glass-panel">
        <i class="fa-solid fa-hospital-user fa-3x text-dim mb-3"></i>
        <h3>No se encontraron pacientes registrados</h3>
        <p class="text-muted">Inicia registrando el primer paciente para este centro psicológico.</p>
      </div>

      <!-- Tabla de Pacientes -->
      <div *ngIf="!loading() && pacientes().length > 0" class="glass-panel table-container">
        <table class="custom-table">
          <thead>
            <tr>
              <th>Expediente</th>
              <th>Paciente</th>
              <th>CI</th>
              <th>Edad / Género</th>
              <th>Contacto Emergencia</th>
              <th>Tutor Legal (Menores)</th>
              <th>Fecha Registro</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let p of pacientes()">
              <td>
                <span class="badge badge-info">
                  <i class="fa-solid fa-hashtag"></i> {{ p.codigo_expediente }}
                </span>
              </td>
              <td>
                <div class="paciente-cell">
                  <div class="avatar-sm">
                    {{ (p.usuario.nombre.charAt(0) || 'P') }}
                  </div>
                  <div>
                    <strong>{{ p.usuario.nombre }} {{ p.usuario.apellido }}</strong>
                    <span class="text-dim text-sm d-block">{{ p.usuario.email }}</span>
                  </div>
                </div>
              </td>
              <td>
                <span class="ci-badge">{{ p.ci }}</span>
              </td>
              <td>
                <div>
                  <strong>{{ calcularEdad(p.fecha_nacimiento) }} años</strong>
                  <span class="badge badge-primary ms-2" [ngClass]="p.genero === 'M' ? 'badge-primary' : (p.genero === 'F' ? 'badge-info' : 'badge-warning')">
                    {{ p.genero === 'M' ? 'Masc' : (p.genero === 'F' ? 'Fem' : 'Otro') }}
                  </span>
                </div>
                <small class="text-dim">{{ p.fecha_nacimiento }}</small>
              </td>
              <td>
                <div *ngIf="p.contacto_emergencia_nombre">
                  <span>{{ p.contacto_emergencia_nombre }}</span>
                  <small class="text-dim d-block"><i class="fa-solid fa-phone"></i> {{ p.contacto_emergencia_telf || 'S/N' }}</small>
                </div>
                <span *ngIf="!p.contacto_emergencia_nombre" class="text-dim text-sm">No registrado</span>
              </td>
              <td>
                <div *ngIf="p.tutor_legal_nombre">
                  <span class="badge badge-warning">
                    <i class="fa-solid fa-user-shield"></i> {{ p.tutor_legal_nombre }}
                  </span>
                  <small class="text-dim d-block">CI: {{ p.tutor_legal_ci || 'N/A' }}</small>
                </div>
                <span *ngIf="!p.tutor_legal_nombre" class="text-dim text-sm">Mayor de edad</span>
              </td>
              <td>
                <span class="text-dim text-sm">{{ p.fecha_registro }}</span>
              </td>
              <td>
                <button class="btn btn-outline-primary btn-sm" (click)="openEditModal(p)" title="Editar Expediente">
                  <i class="fa-solid fa-user-pen"></i> Editar
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- ==================================================================== -->
      <!-- MODAL: REGISTRO DE PACIENTE (CU7 - HU-13, HU-14)                     -->
      <!-- ==================================================================== -->
      <div *ngIf="showCreateModal" class="modal-overlay">
        <div class="modal-content modal-lg">
          <div class="modal-header">
            <div>
              <h2 class="modal-title">
                <i class="fa-solid" [ngClass]="editingPacienteId ? 'fa-user-pen text-info' : 'fa-user-plus text-primary'"></i>
                {{ editingPacienteId ? 'Editar Expediente de Paciente' : 'Alta de Expediente de Paciente' }}
              </h2>
              <p class="modal-subtitle">
                {{ editingPacienteId ? 'Actualiza los datos sociodemográficos y contactos del paciente.' : 'Ingresa los datos sociodemográficos. Si el paciente es menor de 18 años, el tutor legal es obligatorio.' }}
              </p>
            </div>
            <button class="btn-close" (click)="closeCreateModal()">&times;</button>
          </div>

          <form (ngSubmit)="guardarPacienteCU7()" class="modal-body">
            <!-- Datos Personales -->
            <div class="form-row">
              <div class="form-group col">
                <label class="form-label">Nombre(s) *</label>
                <input type="text" [(ngModel)]="nuevoPaciente.nombre" name="nombre" class="form-control" required placeholder="Ej: Sofía" />
              </div>
              <div class="form-group col">
                <label class="form-label">Apellido(s) *</label>
                <input type="text" [(ngModel)]="nuevoPaciente.apellido" name="apellido" class="form-control" required placeholder="Ej: Rojas Valdivia" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group col">
                <label class="form-label">Cédula de Identidad (CI) *</label>
                <input type="text" [(ngModel)]="nuevoPaciente.ci" name="ci" class="form-control" required placeholder="Ej: 9876543" />
              </div>
              <div class="form-group col">
                <label class="form-label">Fecha de Nacimiento *</label>
                <input 
                  type="date" 
                  [(ngModel)]="nuevoPaciente.fecha_nacimiento" 
                  (ngModelChange)="onFechaNacimientoChange()" 
                  name="fecha_nac" 
                  class="form-control" 
                  required 
                />
              </div>
              <div class="form-group col-sm">
                <label class="form-label">Género *</label>
                <select [(ngModel)]="nuevoPaciente.genero" name="genero" class="form-select">
                  <option value="F">Femenino</option>
                  <option value="M">Masculino</option>
                  <option value="O">Otro</option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group col">
                <label class="form-label">Correo Electrónico (Acceso Web/Móvil) *</label>
                <input type="email" [(ngModel)]="nuevoPaciente.email" name="email" class="form-control" required placeholder="sofia.rojas@gmail.com" />
              </div>
              <div class="form-group col">
                <label class="form-label">{{ editingPacienteId ? 'Cambiar Contraseña (Opcional)' : 'Contraseña Inicial *' }}</label>
                <input type="password" [(ngModel)]="nuevoPaciente.password" name="password" class="form-control" [required]="!editingPacienteId" [placeholder]="editingPacienteId ? 'Dejar vacío para conservar actual' : 'Mínimo 8 caracteres'" />
              </div>
              <div class="form-group col">
                <label class="form-label">Teléfono / WhatsApp</label>
                <input type="text" [(ngModel)]="nuevoPaciente.telefono" name="telefono" class="form-control" placeholder="+591 71234567" />
              </div>
            </div>

            <!-- Indicador de Edad Calculada -->
            <div *ngIf="edadCalculada !== null" class="edad-indicator mb-2">
              <i class="fa-solid fa-calendar-check"></i>
              <span>Edad calculada: <strong>{{ edadCalculada }} años</strong></span>
              <span *ngIf="esMenorDeEdad" class="badge badge-warning ms-2">
                <i class="fa-solid fa-triangle-exclamation"></i> Menor de edad - Requiere Tutor Legal
              </span>
              <span *ngIf="!esMenorDeEdad" class="badge badge-success ms-2">
                <i class="fa-solid fa-circle-check"></i> Mayor de edad
              </span>
            </div>

            <!-- Sección: Tutor Legal (Condicionalmente Obligatorio si < 18) -->
            <div class="tutor-section" [class.highlight-tutor]="esMenorDeEdad">
              <h4 class="section-subheading">
                <i class="fa-solid fa-user-shield"></i> Datos del Tutor Legal Responsable
                <span *ngIf="esMenorDeEdad" class="text-danger">* (Obligatorio por ley para menores de 18 años)</span>
              </h4>
              <div class="form-row">
                <div class="form-group col">
                  <label class="form-label">Nombre Completo del Tutor</label>
                  <input 
                    type="text" 
                    [(ngModel)]="nuevoPaciente.tutor_legal_nombre" 
                    name="tutor_nombre" 
                    class="form-control" 
                    [required]="esMenorDeEdad"
                    placeholder="Ej: Carmen Valdivia de Rojas (Madre)" 
                  />
                </div>
                <div class="form-group col">
                  <label class="form-label">CI del Tutor</label>
                  <input 
                    type="text" 
                    [(ngModel)]="nuevoPaciente.tutor_legal_ci" 
                    name="tutor_ci" 
                    class="form-control" 
                    [required]="esMenorDeEdad"
                    placeholder="Ej: 4321987 SC" 
                  />
                </div>
              </div>
            </div>

            <!-- Contacto de Emergencia -->
            <div class="form-row mt-2">
              <div class="form-group col">
                <label class="form-label">Nombre Contacto de Emergencia</label>
                <input type="text" [(ngModel)]="nuevoPaciente.contacto_emergencia_nombre" name="contacto_emergencia_nombre" class="form-control" placeholder="Ej: Juan Carlos Rojas (Padre/Hermano)" />
              </div>
              <div class="form-group col">
                <label class="form-label">Teléfono de Emergencia</label>
                <input type="text" [(ngModel)]="nuevoPaciente.contacto_emergencia_telf" name="contacto_emergencia_telf" class="form-control" placeholder="+591 79998888" />
              </div>
            </div>

            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" (click)="closeCreateModal()">Cancelar</button>
              <button type="submit" class="btn btn-primary" [disabled]="savingPaciente">
                <i class="fa-solid fa-floppy-disk" *ngIf="!savingPaciente"></i>
                <i class="fa-solid fa-spinner fa-spin" *ngIf="savingPaciente"></i>
                {{ savingPaciente ? 'Guardando...' : (editingPacienteId ? 'Guardar Cambios' : 'Dar de Alta Expediente') }}
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
    .pacientes-container {
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
      border-radius: 14px;
    }
    .search-box {
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
      padding: 12px 0;
      width: 100%;
    }
    .paciente-cell {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .avatar-sm {
      width: 36px;
      height: 36px;
      border-radius: 10px;
      background: #e6f5ed;
      color: #19734e;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
    }
    .ci-badge {
      font-family: var(--font-mono);
      font-weight: 600;
      color: var(--text-muted);
    }
    .loading-state, .empty-state {
      padding: 50px 20px;
      text-align: center;
      border-radius: 16px;
    }
    .modal-lg {
      max-width: 760px;
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
    .form-row {
      display: flex;
      gap: 14px;
    }
    .col { flex: 1; }
    .col-sm { flex: 0.6; }
    .d-block { display: block; }
    .ms-2 { margin-left: 8px; }
    .edad-indicator {
      display: flex;
      align-items: center;
      background: #f8faf9;
      border: 1px solid var(--border-light);
      padding: 8px 14px;
      border-radius: 8px;
      font-size: 0.85rem;
    }
    .tutor-section {
      background: #fdfaf6;
      border: 1px dashed #d5e3dc;
      border-radius: 12px;
      padding: 14px;
    }
    .tutor-section.highlight-tutor {
      border-color: #fde68a;
      background: #fffbeb;
    }
    .section-subheading {
      font-size: 0.88rem;
      font-weight: 700;
      color: var(--text-muted);
      margin-bottom: 10px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .text-danger { color: #f87171; }
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
      .form-row {
        flex-direction: column;
        gap: 12px;
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
export class PacienteListComponent implements OnInit {
  pacientes = signal<Paciente[]>([]);
  loading = signal<boolean>(true);
  searchTerm = '';

  // Modal Registro / Edición
  showCreateModal = false;
  editingPacienteId: string | null = null;
  savingPaciente = false;
  edadCalculada: number | null = null;
  esMenorDeEdad = false;

  nuevoPaciente: CrearPacienteDTO = {
    nombre: '',
    apellido: '',
    email: '',
    password: '',
    telefono: '',
    ci: '',
    fecha_nacimiento: '',
    genero: 'F',
    contacto_emergencia_nombre: '',
    contacto_emergencia_telf: '',
    tutor_legal_nombre: '',
    tutor_legal_ci: ''
  };

  // Toast
  toastMsg = '';
  toastType: 'success' | 'error' = 'success';

  constructor(private clinicaService: ClinicaService) {}

  ngOnInit(): void {
    this.cargarPacientes();
  }

  cargarPacientes(): void {
    this.loading.set(true);
    this.clinicaService.getPacientes(this.searchTerm).subscribe({
      next: (res) => {
        this.pacientes.set(res);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Error al cargar pacientes', err);
        this.loading.set(false);
      }
    });
  }

  buscarPacientes(): void {
    this.cargarPacientes();
  }

  calcularEdad(fechaNacStr: string): number {
    if (!fechaNacStr) return 0;
    const dob = new Date(fechaNacStr);
    const diff = Date.now() - dob.getTime();
    const ageDt = new Date(diff);
    return Math.abs(ageDt.getUTCFullYear() - 1970);
  }

  onFechaNacimientoChange(): void {
    if (!this.nuevoPaciente.fecha_nacimiento) {
      this.edadCalculada = null;
      this.esMenorDeEdad = false;
      return;
    }
    this.edadCalculada = this.calcularEdad(this.nuevoPaciente.fecha_nacimiento);
    this.esMenorDeEdad = this.edadCalculada < 18;
  }

  openCreateModal(): void {
    this.editingPacienteId = null;
    this.nuevoPaciente = {
      nombre: '',
      apellido: '',
      email: '',
      password: '',
      telefono: '',
      ci: '',
      fecha_nacimiento: '',
      genero: 'F',
      contacto_emergencia_nombre: '',
      contacto_emergencia_telf: '',
      tutor_legal_nombre: '',
      tutor_legal_ci: ''
    };
    this.edadCalculada = null;
    this.esMenorDeEdad = false;
    this.showCreateModal = true;
  }

  openEditModal(p: Paciente): void {
    this.editingPacienteId = p.id;
    this.nuevoPaciente = {
      nombre: p.usuario?.nombre || '',
      apellido: p.usuario?.apellido || '',
      email: p.usuario?.email || '',
      password: '',
      telefono: p.usuario?.telefono || '',
      ci: p.ci || '',
      fecha_nacimiento: p.fecha_nacimiento || '',
      genero: (p.genero as any) || 'F',
      contacto_emergencia_nombre: p.contacto_emergencia_nombre || '',
      contacto_emergencia_telf: p.contacto_emergencia_telf || '',
      tutor_legal_nombre: p.tutor_legal_nombre || '',
      tutor_legal_ci: p.tutor_legal_ci || ''
    };
    this.onFechaNacimientoChange();
    this.showCreateModal = true;
  }

  closeCreateModal(): void {
    this.showCreateModal = false;
    this.editingPacienteId = null;
  }

  /**
   * ═══════════════════════════════════════════════════════════════════════════
   * CU7: Guardar / Editar Expediente de Paciente
   * Diagrama de Comunicación – Pasos del Flujo:
   *   Actor  → Paciente / Recepcionista / Administrador
   *   IU     → IU_RegistroPaciente (PacienteListComponent)
   *   CTR    → CTR_PacienteService (Django REST)
   *   CE     → CE_Paciente_y_Usuario (PostgreSQL)
   * ═══════════════════════════════════════════════════════════════════════════
   */
  guardarPacienteCU7(): void {
    // --- Paso 1: Actor ingresa datos personales en IU_RegistroPaciente ---
    // Validación síncrona en cliente de tutor legal si es menor de edad
    if (this.esMenorDeEdad && (!this.nuevoPaciente.tutor_legal_nombre || !this.nuevoPaciente.tutor_legal_ci)) {
      this.mostrarToast('Por ser menor de edad (<18 años), los datos del Tutor Legal son obligatorios.', 'error');
      return;
    }

    this.savingPaciente = true;

    const payload: any = { ...this.nuevoPaciente };
    if (!payload.password || payload.password.trim() === '') {
      delete payload.password;
    }

    // --- Paso 2: POST / PUT /api/clinica/pacientes/ + Header X-Tenant-ID ---
    const action$ = this.editingPacienteId
      ? this.clinicaService.updatePaciente(this.editingPacienteId, payload)
      : this.clinicaService.createPaciente(payload);

    action$.subscribe({
      // --- Paso 9: 201 Created / 200 OK {paciente_id, codigo_expediente} ---
      next: (res) => {
        this.savingPaciente = false;
        this.closeCreateModal();
        // --- Paso 10: Confirmar "Expediente de paciente creado" en IU_RegistroPaciente ---
        const msg = this.editingPacienteId
          ? 'Expediente actualizado exitosamente.'
          : `Expediente creado exitosamente con código ${res.codigo_expediente}.`;
        this.mostrarToast(msg, 'success');
        this.cargarPacientes();
      },
      error: (err) => {
        this.savingPaciente = false;
        let msg = 'Error al dar de alta al paciente';
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
