// ==============================================================================
// MÓDULO: calendario-agenda.component.ts
// CAPA BCE: BOUNDARY (Interfaz de Usuario) — IU_AgendaCitas
// CASOS DE USO: CU11: Programación, Reserva y Gestión de Citas (HU-15, HU-16, HU-17, HU-22)
// DESCRIPCIÓN: Componente Angular interactivo con cuadrícula de calendario mensual,
//              selección de slots libres, reserva concurrente y cancelación con anticipación.
//              Implementa los pasos 1, 2, 7 y 8 del Diagrama de Comunicación BCE.
// ==============================================================================
import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AgendaService } from '../../core/services/agenda.service';
import { ClinicaService } from '../../core/services/clinica.service';
import { Cita, SlotDisponible, Psicologo, Paciente } from '../../core/models';

interface DiaCalendario {
  fecha: Date;
  fechaStr: string;
  esMesActual: boolean;
  esHoy: boolean;
  citas: Cita[];
}

@Component({
  selector: 'app-calendario-agenda',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="agenda-container">
      <!-- Header de Sección -->
      <div class="page-header glass-panel mb-4">
        <div>
          <h1 class="page-title">
            <i class="fa-solid fa-calendar-check text-primary"></i> Agenda y Calendario de Citas
          </h1>
          <p class="page-subtitle">
            Programación concurrente de consultas clínicas, visualización por estados y telemedicina WebRTC (Sprint 1 - HU-15, HU-16, HU-17, HU-22).
          </p>
        </div>
        <div class="header-actions">
          <button class="btn btn-primary" (click)="openNuevaCitaModal()">
            <i class="fa-solid fa-calendar-plus"></i> Agendar Nueva Cita
          </button>
        </div>
      </div>

      <!-- Barra de Navegación y Filtros del Calendario -->
      <div class="calendar-controls glass-panel mb-4">
        <div class="nav-date-group">
          <button class="btn btn-secondary btn-sm" (click)="cambiarMes(-1)">
            <i class="fa-solid fa-chevron-left"></i>
          </button>
          <button class="btn btn-secondary btn-sm" (click)="irAHoy()">Hoy</button>
          <button class="btn btn-secondary btn-sm" (click)="cambiarMes(1)">
            <i class="fa-solid fa-chevron-right"></i>
          </button>
          <h3 class="mes-titulo">{{ nombreMesActual }} {{ anioActual }}</h3>
        </div>

        <div class="filters-group">
          <!-- Filtro por Terapeuta -->
          <select [(ngModel)]="filtroPsicologoId" (ngModelChange)="cargarCitas()" class="form-select form-select-sm">
            <option value="">Todos los Terapeutas</option>
            <option *ngFor="let psi of psicologos()" [value]="psi.id">
              {{ psi.usuario.nombre }} {{ psi.usuario.apellido }}
            </option>
          </select>

          <!-- Filtro por Estado -->
          <select [(ngModel)]="filtroEstado" (ngModelChange)="filtrarCitas()" class="form-select form-select-sm">
            <option value="">Todos los Estados</option>
            <option value="PROGRAMADA">Programada</option>
            <option value="CONFIRMADA">Confirmada</option>
            <option value="REALIZADA">Realizada</option>
            <option value="CANCELADA">Cancelada</option>
            <option value="INASISTENCIA">Inasistencia</option>
          </select>

          <!-- Selector de Vista (Mes / Semana / Lista) -->
          <div class="view-toggle">
            <button class="btn btn-sm" [ngClass]="vistaActual === 'mes' ? 'btn-primary' : 'btn-secondary'" (click)="vistaActual = 'mes'">
              <i class="fa-solid fa-table-cells"></i> Mes
            </button>
            <button class="btn btn-sm" [ngClass]="vistaActual === 'lista' ? 'btn-primary' : 'btn-secondary'" (click)="vistaActual = 'lista'">
              <i class="fa-solid fa-list-ul"></i> Lista
            </button>
          </div>
        </div>
      </div>

      <!-- ==================================================================== -->
      <!-- VISTA: GRILLA MENSUAL DE CALENDARIO                                  -->
      <!-- ==================================================================== -->
      <div *ngIf="vistaActual === 'mes'" class="calendar-grid-wrapper glass-panel">
        <!-- Encabezados de Días de la Semana -->
        <div class="weekdays-grid">
          <div class="weekday-col">Dom</div>
          <div class="weekday-col">Lun</div>
          <div class="weekday-col">Mar</div>
          <div class="weekday-col">Mié</div>
          <div class="weekday-col">Jue</div>
          <div class="weekday-col">Vie</div>
          <div class="weekday-col">Sáb</div>
        </div>

        <!-- Celdas de Días -->
        <div class="month-cells-grid">
          <div 
            *ngFor="let dia of diasCalendario" 
            class="day-cell"
            [class.outside-month]="!dia.esMesActual"
            [class.today]="dia.esHoy"
          >
            <div class="day-header">
              <span class="day-number">{{ dia.fecha.getDate() }}</span>
              <button class="btn-add-quick" (click)="agendarEnDia(dia.fechaStr)" title="Agendar en este día">
                <i class="fa-solid fa-plus"></i>
              </button>
            </div>

            <!-- Chips de Citas del Día -->
            <div class="day-citas-container">
              <div 
                *ngFor="let cita of dia.citas" 
                class="cita-chip"
                [ngClass]="'chip-' + cita.estado.toLowerCase()"
                (click)="verDetalleCita(cita)"
                [title]="cita.motivo_consulta || 'Consulta clínica'"
              >
                <span class="chip-time">{{ cita.hora_inicio.slice(0, 5) }}</span>
                <span class="chip-paciente">{{ cita.paciente_nombre }}</span>
                <i *ngIf="cita.modalidad === 'VIRTUAL'" class="fa-solid fa-video chip-icon" title="Teleconsulta"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ==================================================================== -->
      <!-- VISTA: TABLA LISTA DETALLADA DE CITAS                                -->
      <!-- ==================================================================== -->
      <div *ngIf="vistaActual === 'lista'" class="table-container glass-panel">
        <table class="custom-table">
          <thead>
            <tr>
              <th>Fecha y Hora</th>
              <th>Paciente</th>
              <th>Terapeuta</th>
              <th>Modalidad</th>
              <th>Estado</th>
              <th>Arancel</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let c of citasFiltradas()">
              <td>
                <strong>{{ c.fecha }}</strong>
                <span class="d-block text-dim text-sm">{{ c.hora_inicio.slice(0, 5) }} - {{ c.hora_fin.slice(0, 5) }}</span>
              </td>
              <td>
                <strong>{{ c.paciente_nombre }}</strong>
                <span class="d-block text-dim text-sm">Exp: {{ c.paciente_expediente }}</span>
              </td>
              <td>
                <span>{{ c.psicologo_nombre }}</span>
              </td>
              <td>
                <span class="badge" [ngClass]="c.modalidad === 'VIRTUAL' ? 'badge-info' : 'badge-primary'">
                  <i class="fa-solid" [ngClass]="c.modalidad === 'VIRTUAL' ? 'fa-video' : 'fa-building'"></i>
                  {{ c.modalidad }}
                </span>
              </td>
              <td>
                <span class="badge" [ngClass]="getEstadoBadgeClass(c.estado)">
                  {{ c.estado }}
                </span>
              </td>
              <td>
                <span class="tarifa-text">BOB {{ c.costo }}</span>
              </td>
              <td>
                <div class="actions-flex">
                  <button 
                    *ngIf="c.modalidad === 'VIRTUAL' && (c.estado === 'PROGRAMADA' || c.estado === 'CONFIRMADA')"
                    class="btn btn-primary btn-sm" 
                    (click)="irATeleconsulta(c.id)"
                    title="Unirse a la sala de Teleconsulta Jitsi"
                  >
                    <i class="fa-solid fa-video"></i> Sala WebRTC
                  </button>
                  <button class="btn btn-secondary btn-sm" (click)="verDetalleCita(c)">
                    <i class="fa-solid fa-eye"></i> Detalle
                  </button>
                </div>
              </td>
            </tr>
            <tr *ngIf="citasFiltradas().length === 0">
              <td colspan="7" class="text-center text-muted py-4">
                No hay citas programadas para los filtros seleccionados.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- ==================================================================== -->
      <!-- MODAL: AGENDAR NUEVA CITA (CU11 - HU-15, HU-16, HU-17, HU-22)        -->
      <!-- ==================================================================== -->
      <div *ngIf="showNuevaCitaModal" class="modal-overlay">
        <div class="modal-content modal-lg">
          <div class="modal-header">
            <div>
              <h2 class="modal-title">
                <i class="fa-solid fa-calendar-plus text-primary"></i> Programar Cita Clínica
              </h2>
              <p class="modal-subtitle">
                Reserva atómica con bloqueo pesimista en PostgreSQL para evitar solapamientos concurrentes.
              </p>
            </div>
            <button class="btn-close" (click)="closeNuevaCitaModal()">&times;</button>
          </div>

          <form (ngSubmit)="guardarCitaCU11()" class="modal-body">
            <div *ngIf="modalError()" class="alert-box alert-error mb-3">
              <i class="fa-solid fa-triangle-exclamation"></i>
              <span>{{ modalError() }}</span>
            </div>

            <!-- Selección de Paciente y Psicólogo -->
            <div class="form-row">
              <div class="form-group col">
                <label class="form-label">Paciente *</label>
                <select [(ngModel)]="nuevaCita.paciente" name="paciente" class="form-select" required>
                  <option value="">-- Seleccionar Paciente --</option>
                  <option *ngFor="let pac of pacientes()" [value]="pac.id">
                    {{ pac.usuario.nombre }} {{ pac.usuario.apellido }} ({{ pac.codigo_expediente }} - CI: {{ pac.ci }})
                  </option>
                </select>
              </div>

              <div class="form-group col">
                <label class="form-label">Psicólogo / Terapeuta *</label>
                <select 
                  [(ngModel)]="nuevaCita.psicologo" 
                  name="psicologo" 
                  class="form-select" 
                  required
                  (ngModelChange)="onPsicologoOFechaChange()"
                >
                  <option value="">-- Seleccionar Profesional --</option>
                  <option *ngFor="let psi of psicologos()" [value]="psi.id">
                    {{ psi.usuario.nombre }} {{ psi.usuario.apellido }} (BOB {{ psi.tarifa_base }})
                  </option>
                </select>
              </div>
            </div>

            <!-- Fecha y Modalidad -->
            <div class="form-row">
              <div class="form-group col">
                <label class="form-label">Fecha de la Cita *</label>
                <input 
                  type="date" 
                  [(ngModel)]="nuevaCita.fecha" 
                  name="fecha" 
                  class="form-control" 
                  required
                  (ngModelChange)="onPsicologoOFechaChange()"
                />
              </div>

              <div class="form-group col">
                <label class="form-label">Modalidad *</label>
                <select [(ngModel)]="nuevaCita.modalidad" name="modalidad" class="form-select">
                  <option value="PRESENCIAL">Presencial en Consultorio</option>
                  <option value="VIRTUAL">Virtual (Teleconsulta Jitsi Meet)</option>
                </select>
              </div>
            </div>

            <!-- Selección de Slots Disponibles en Tiempo Real -->
            <div class="form-group">
              <label class="form-label">
                Horarios Libres Disponibles *
                <span class="text-dim text-sm" *ngIf="cargandoSlots">(Consultando disponibilidad...)</span>
              </label>

              <div *ngIf="!nuevaCita.psicologo || !nuevaCita.fecha" class="alert-hint">
                <i class="fa-solid fa-circle-info"></i> Selecciona terapeuta y fecha para consultar los bloques libres.
              </div>

              <div *ngIf="nuevaCita.psicologo && nuevaCita.fecha && !cargandoSlots && slotsDisponibles.length === 0" class="alert-hint alert-warning">
                <i class="fa-solid fa-triangle-exclamation"></i> El terapeuta no cuenta con franjas libres configuradas para esta fecha (o el día no es hábil).
              </div>

              <div *ngIf="slotsDisponibles.length > 0" class="slots-grid">
                <div 
                  *ngFor="let s of slotsDisponibles" 
                  class="slot-btn"
                  [class.selected]="nuevaCita.hora_inicio === s.hora_inicio"
                  [class.disabled]="!s.disponible"
                  (click)="seleccionarSlot(s)"
                >
                  <i class="fa-solid fa-clock"></i>
                  <span>{{ s.hora_inicio }} - {{ s.hora_fin }}</span>
                  <small *ngIf="!s.disponible" class="slot-badge-busy">Ocupado</small>
                </div>
              </div>
            </div>

            <!-- Motivo de Consulta -->
            <div class="form-group">
              <label class="form-label">Motivo de Consulta Clínica</label>
              <textarea 
                [(ngModel)]="nuevaCita.motivo_consulta" 
                name="motivo" 
                rows="2" 
                class="form-control" 
                placeholder="Ansiedad, derivación escolar, sesión de seguimiento, etc."
              ></textarea>
            </div>

            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" (click)="closeNuevaCitaModal()">Cancelar</button>
              <button 
                type="submit" 
                class="btn btn-primary" 
                [disabled]="savingCita || !nuevaCita.hora_inicio || !nuevaCita.paciente || !nuevaCita.psicologo"
              >
                <i class="fa-solid fa-check" *ngIf="!savingCita"></i>
                <i class="fa-solid fa-spinner fa-spin" *ngIf="savingCita"></i>
                {{ savingCita ? 'Bloqueando Slot y Reservando...' : 'Confirmar Reserva de Cita' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- ==================================================================== -->
      <!-- MODAL: DETALLE Y ACCIONES DE CITA                                    -->
      <!-- ==================================================================== -->
      <div *ngIf="showDetalleModal && citaSeleccionada" class="modal-overlay">
        <div class="modal-content">
          <div class="modal-header">
            <h2 class="modal-title">
              <i class="fa-solid fa-notes-medical text-primary"></i> Detalle de Sesión Clínica
            </h2>
            <button class="btn-close" (click)="closeDetalleModal()">&times;</button>
          </div>

          <div class="modal-body">
            <div class="cita-detail-grid">
              <div class="detail-item">
                <span class="detail-label">Paciente</span>
                <span class="detail-val">{{ citaSeleccionada.paciente_nombre }}</span>
                <small class="text-dim">Expediente: {{ citaSeleccionada.paciente_expediente }}</small>
              </div>
              <div class="detail-item">
                <span class="detail-label">Terapeuta Asignado</span>
                <span class="detail-val">{{ citaSeleccionada.psicologo_nombre }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Fecha y Horario</span>
                <span class="detail-val">{{ citaSeleccionada.fecha }}</span>
                <span class="text-primary">{{ citaSeleccionada.hora_inicio.slice(0, 5) }} a {{ citaSeleccionada.hora_fin.slice(0, 5) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Modalidad y Estado</span>
                <div class="d-flex gap-2 align-center mt-1">
                  <span class="badge" [ngClass]="citaSeleccionada.modalidad === 'VIRTUAL' ? 'badge-info' : 'badge-primary'">
                    {{ citaSeleccionada.modalidad }}
                  </span>
                  <span class="badge" [ngClass]="getEstadoBadgeClass(citaSeleccionada.estado)">
                    {{ citaSeleccionada.estado }}
                  </span>
                </div>
              </div>
              <div class="detail-item full-width" *ngIf="citaSeleccionada.motivo_consulta">
                <span class="detail-label">Motivo de Consulta</span>
                <p class="motivo-box">{{ citaSeleccionada.motivo_consulta }}</p>
              </div>
            </div>

            <!-- Acciones según Estado y Modalidad -->
            <div class="modal-actions-box mt-3">
              <!-- Enlace a Teleconsulta Jitsi -->
              <button 
                *ngIf="citaSeleccionada.modalidad === 'VIRTUAL' && (citaSeleccionada.estado === 'PROGRAMADA' || citaSeleccionada.estado === 'CONFIRMADA')"
                class="btn btn-primary w-100 mb-2"
                (click)="irATeleconsulta(citaSeleccionada.id)"
              >
                <i class="fa-solid fa-video"></i> Entrar a Sala de Teleconsulta (Jitsi Meet)
              </button>

              <!-- Cancelar Cita -->
              <div *ngIf="citaSeleccionada.estado === 'PROGRAMADA' || citaSeleccionada.estado === 'CONFIRMADA'" class="cancel-box">
                <div *ngIf="cancelError()" class="alert-box alert-error mb-2">
                  <i class="fa-solid fa-triangle-exclamation"></i>
                  <span>{{ cancelError() }}</span>
                </div>
                <input 
                  type="text" 
                  [(ngModel)]="motivoCancelacion" 
                  placeholder="Motivo de la cancelación (mínimo 5 caracteres y 2 hrs de anticipación)..."
                  class="form-control mb-2" 
                />
                <button class="btn btn-danger w-100" (click)="cancelarCita()">
                  <i class="fa-solid fa-ban"></i> Cancelar Cita
                </button>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn btn-secondary" (click)="closeDetalleModal()">Cerrar</button>
          </div>
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
    .agenda-container {
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
    .calendar-controls {
      padding: 16px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-radius: 14px;
      flex-wrap: wrap;
      gap: 16px;
    }
    .nav-date-group {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .mes-titulo {
      font-size: 1.2rem;
      font-weight: 800;
      margin-left: 10px;
      min-width: 180px;
    }
    .filters-group {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }
    .view-toggle {
      display: flex;
      gap: 6px;
    }
    .calendar-grid-wrapper {
      padding: 16px;
      border-radius: 16px;
    }
    .weekdays-grid {
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      text-align: center;
      font-weight: 700;
      color: var(--text-dim);
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--border-glass);
    }
    .month-cells-grid {
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      border-left: 1px solid var(--border-glass);
      border-top: 1px solid var(--border-glass);
    }
    .day-cell {
      min-height: 120px;
      padding: 8px;
      border-right: 1px solid var(--border-light);
      border-bottom: 1px solid var(--border-light);
      background: #ffffff;
      display: flex;
      flex-direction: column;
      gap: 6px;
      transition: var(--transition);
    }
    .day-cell:hover {
      background: #f8fbf9;
    }
    .day-cell.outside-month {
      opacity: 0.55;
      background: #f3f6f4;
    }
    .day-cell.today {
      border: 1.5px solid var(--primary);
      background: #f0f9f4;
    }
    .day-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .day-number {
      font-size: 0.85rem;
      font-weight: 700;
      color: var(--text-main);
    }
    .btn-add-quick {
      background: transparent;
      border: none;
      color: var(--text-dim);
      font-size: 0.75rem;
      cursor: pointer;
      opacity: 0;
      transition: var(--transition);
    }
    .day-cell:hover .btn-add-quick {
      opacity: 1;
      color: var(--primary);
    }
    .day-citas-container {
      display: flex;
      flex-direction: column;
      gap: 4px;
      overflow-y: auto;
      max-height: 90px;
    }
    .cita-chip {
      padding: 3px 6px;
      border-radius: 6px;
      font-size: 0.74rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      transition: var(--transition);
    }
    .cita-chip:hover {
      transform: translateX(2px);
    }
    .chip-time {
      font-weight: 700;
    }
    .chip-paciente {
      overflow: hidden;
      text-overflow: ellipsis;
      flex: 1;
    }
    .chip-icon {
      font-size: 0.7rem;
    }
    .chip-programada { background: #e0f2fe; color: #0369a1; border-left: 3px solid #0284c7; }
    .chip-confirmada { background: #e6f7ee; color: #15803d; border-left: 3px solid #16a34a; }
    .chip-realizada { background: #ede9fe; color: #6d28d9; border-left: 3px solid #7c3aed; }
    .chip-cancelada { background: #fee2e2; color: #b91c1c; border-left: 3px solid #dc2626; }
    .chip-inasistencia { background: #fef3c7; color: #b45309; border-left: 3px solid #d97706; }

    .slots-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
      gap: 8px;
      max-height: 180px;
      overflow-y: auto;
      padding: 4px;
    }
    .slot-btn {
      padding: 8px 10px;
      border-radius: 8px;
      background: var(--bg-input);
      border: 1px solid var(--border-light);
      font-size: 0.8rem;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 4px;
      cursor: pointer;
      transition: var(--transition);
      color: var(--text-body);
    }
    .slot-btn:hover:not(.disabled) {
      border-color: var(--primary);
      color: var(--primary);
      background: #e6f5ed;
    }
    .slot-btn.selected {
      background: #19734e;
      color: white;
      border-color: #135d3e;
      box-shadow: 0 2px 8px var(--primary-glow);
    }
    .slot-btn.disabled {
      opacity: 0.4;
      cursor: not-allowed;
      background: #f8faf9;
      border-color: #e3ebe6;
    }
    .slot-badge-busy {
      font-size: 0.65rem;
      color: #dc2626;
    }
    .alert-hint {
      background: #f8faf9;
      border: 1px dashed var(--border-light);
      border-radius: 8px;
      padding: 10px;
      font-size: 0.82rem;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .alert-hint.alert-warning {
      color: #92400e;
      background: #fffbeb;
      border-color: #fde68a;
    }
    .cita-detail-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 14px;
    }
    .detail-item {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .detail-item.full-width {
      grid-column: span 2;
    }
    .detail-label {
      font-size: 0.75rem;
      font-weight: 700;
      color: var(--text-dim);
      text-transform: uppercase;
    }
    .detail-val {
      font-size: 0.95rem;
      font-weight: 700;
    }
    .motivo-box {
      background: var(--bg-input);
      border-radius: 8px;
      padding: 10px;
      font-size: 0.86rem;
      color: var(--text-muted);
    }
    .tarifa-text {
      font-weight: 700;
      color: var(--success);
    }
    .actions-flex {
      display: flex;
      gap: 6px;
    }
    .modal-lg { max-width: 720px; }
    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 20px;
      border-bottom: 1px solid var(--border-glass);
      padding-bottom: 14px;
    }
    .modal-title { font-size: 1.3rem; font-weight: 800; }
    .modal-subtitle { font-size: 0.85rem; color: var(--text-muted); }
    .btn-close { background: transparent; border: none; color: var(--text-dim); font-size: 1.5rem; cursor: pointer; }
    .modal-body { display: flex; flex-direction: column; gap: 14px; }
    .form-row { display: flex; gap: 14px; }
    .col { flex: 1; }
    .modal-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--border-glass); }
    .w-100 { width: 100%; }
    .mb-2 { margin-bottom: 8px; }
    .mt-3 { margin-top: 14px; }
    .align-center { align-items: center; }
    .d-flex { display: flex; }
    .gap-2 { gap: 8px; }

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
      .calendar-controls {
        flex-direction: column;
        align-items: stretch;
        gap: 12px;
        padding: 14px;
      }
      .nav-date-group {
        justify-content: space-between;
      }
      .mes-titulo {
        font-size: 1.05rem;
        min-width: auto;
      }
      .filters-group {
        flex-direction: column;
        align-items: stretch;
        gap: 8px;
      }
      .calendar-grid-wrapper {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
      }
      .weekdays-grid, .month-cells-grid {
        min-width: 620px;
      }
      .form-row {
        flex-direction: column;
        gap: 10px;
      }
      .cita-detail-grid {
        grid-template-columns: 1fr;
      }
      .detail-item.full-width {
        grid-column: span 1;
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
export class CalendarioAgendaComponent implements OnInit {
  citas = signal<Cita[]>([]);
  citasFiltradas = signal<Cita[]>([]);
  psicologos = signal<Psicologo[]>([]);
  pacientes = signal<Paciente[]>([]);

  // Vistas y Navegación
  vistaActual: 'mes' | 'lista' = 'mes';
  fechaReferencia = new Date();
  diasCalendario: DiaCalendario[] = [];

  // Filtros
  filtroPsicologoId = '';
  filtroEstado = '';

  // Modal Agendar Cita (CU11)
  showNuevaCitaModal = false;
  savingCita = false;
  cargandoSlots = false;
  slotsDisponibles: SlotDisponible[] = [];
  modalError = signal<string | null>(null);

  nuevaCita = {
    paciente: '',
    psicologo: '',
    fecha: '',
    hora_inicio: '',
    hora_fin: '',
    modalidad: 'PRESENCIAL' as 'PRESENCIAL' | 'VIRTUAL',
    motivo_consulta: '',
    costo: 150.00
  };

  // Modal Detalle
  showDetalleModal = false;
  citaSeleccionada: Cita | null = null;
  motivoCancelacion = '';
  cancelError = signal<string | null>(null);

  // Toast
  toastMsg = '';
  toastType: 'success' | 'error' = 'success';

  get anioActual(): number {
    return this.fechaReferencia.getFullYear();
  }

  get nombreMesActual(): string {
    const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
    return meses[this.fechaReferencia.getMonth()];
  }

  constructor(
    private agendaService: AgendaService,
    private clinicaService: ClinicaService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.cargarDatosMaestros();
    this.cargarCitas();
  }

  cargarDatosMaestros(): void {
    this.clinicaService.getPsicologos().subscribe({
      next: (res) => this.psicologos.set(res)
    });

    this.clinicaService.getPacientes().subscribe({
      next: (res) => this.pacientes.set(res)
    });
  }

  cargarCitas(): void {
    this.agendaService.getCitas({ psicologo_id: this.filtroPsicologoId || undefined }).subscribe({
      next: (res) => {
        this.citas.set(res);
        this.filtrarCitas();
        this.construirGrillaMes();
      },
      error: (err) => console.error('Error al cargar citas', err)
    });
  }

  filtrarCitas(): void {
    let list = this.citas();
    if (this.filtroEstado) {
      list = list.filter(c => c.estado === this.filtroEstado);
    }
    this.citasFiltradas.set(list);
    this.construirGrillaMes();
  }

  cambiarMes(delta: number): void {
    this.fechaReferencia = new Date(this.fechaReferencia.getFullYear(), this.fechaReferencia.getMonth() + delta, 1);
    this.construirGrillaMes();
  }

  irAHoy(): void {
    this.fechaReferencia = new Date();
    this.construirGrillaMes();
  }

  construirGrillaMes(): void {
    const year = this.fechaReferencia.getFullYear();
    const month = this.fechaReferencia.getMonth();

    const primerDiaMes = new Date(year, month, 1);
    const ultimoDiaMes = new Date(year, month + 1, 0);

    const inicioSemana = primerDiaMes.getDay(); // 0=Dom
    const totalDiasMes = ultimoDiaMes.getDate();

    const dias: DiaCalendario[] = [];
    const hoyStr = new Date().toISOString().split('T')[0];

    // Días previos del mes anterior
    const mesAnteriorUltimoDia = new Date(year, month, 0).getDate();
    for (let i = inicioSemana - 1; i >= 0; i--) {
      const f = new Date(year, month - 1, mesAnteriorUltimoDia - i);
      const fStr = f.toISOString().split('T')[0];
      dias.push({
        fecha: f,
        fechaStr: fStr,
        esMesActual: false,
        esHoy: fStr === hoyStr,
        citas: this.citasFiltradas().filter(c => c.fecha === fStr)
      });
    }

    // Días del mes actual
    for (let d = 1; d <= totalDiasMes; d++) {
      const f = new Date(year, month, d);
      const y = f.getFullYear();
      const m = String(f.getMonth() + 1).padStart(2, '0');
      const day = String(f.getDate()).padStart(2, '0');
      const fStr = `${y}-${m}-${day}`;
      dias.push({
        fecha: f,
        fechaStr: fStr,
        esMesActual: true,
        esHoy: fStr === hoyStr,
        citas: this.citasFiltradas().filter(c => c.fecha === fStr)
      });
    }

    // Días posteriores para completar la matriz de semanas
    const celdasRestantes = 42 - dias.length; // 6 semanas completas
    for (let d = 1; d <= celdasRestantes; d++) {
      const f = new Date(year, month + 1, d);
      const y = f.getFullYear();
      const m = String(f.getMonth() + 1).padStart(2, '0');
      const day = String(f.getDate()).padStart(2, '0');
      const fStr = `${y}-${m}-${day}`;
      dias.push({
        fecha: f,
        fechaStr: fStr,
        esMesActual: false,
        esHoy: fStr === hoyStr,
        citas: this.citasFiltradas().filter(c => c.fecha === fStr)
      });
    }

    this.diasCalendario = dias;
  }

  // --------------------------------------------------------------------------
  // AGENDAR CITA (CU11 - HU-15, HU-16, HU-17, HU-22)
  // --------------------------------------------------------------------------
  openNuevaCitaModal(): void {
    this.modalError.set(null);
    this.cargarDatosMaestros();
    const hoyStr = new Date().toISOString().split('T')[0];
    this.nuevaCita = {
      paciente: '',
      psicologo: '',
      fecha: hoyStr,
      hora_inicio: '',
      hora_fin: '',
      modalidad: 'PRESENCIAL',
      motivo_consulta: '',
      costo: 150.00
    };
    this.slotsDisponibles = [];
    this.showNuevaCitaModal = true;
  }

  agendarEnDia(fechaStr: string): void {
    this.openNuevaCitaModal();
    this.nuevaCita.fecha = fechaStr;
  }

  closeNuevaCitaModal(): void {
    this.showNuevaCitaModal = false;
    this.modalError.set(null);
  }

  onPsicologoOFechaChange(): void {
    if (!this.nuevaCita.psicologo || !this.nuevaCita.fecha) {
      this.slotsDisponibles = [];
      return;
    }

    this.cargandoSlots = true;
    this.agendaService.getSlotsDisponibles(this.nuevaCita.psicologo, this.nuevaCita.fecha).subscribe({
      next: (slots) => {
        this.slotsDisponibles = slots;
        this.cargandoSlots = false;
      },
      error: () => {
        this.slotsDisponibles = [];
        this.cargandoSlots = false;
      }
    });
  }

  seleccionarSlot(slot: SlotDisponible): void {
    if (!slot.disponible) return;
    this.nuevaCita.hora_inicio = slot.hora_inicio;
    this.nuevaCita.hora_fin = slot.hora_fin;
  }

  /**
   * ═══════════════════════════════════════════════════════════════════════════
   * CU11: Programación y Reserva de Citas
   * Diagrama de Comunicación – Pasos del Flujo:
   *   Actor  → Recepcionista / Paciente / Administrador
   *   IU     → IU_AgendaCitas (CalendarioAgendaComponent)
   *   CTR    → CTR_CitaService (Django REST)
   *   CE     → CE_Cita_y_Disponibilidad (PostgreSQL)
   * ═══════════════════════════════════════════════════════════════════════════
   */
  guardarCitaCU11(): void {
    this.modalError.set(null);

    // Validaciones síncronas en frontend (HU-15 / HU-16 / TP-41)
    if (!this.nuevaCita.paciente) {
      this.modalError.set('Debe seleccionar el paciente para la consulta.');
      return;
    }
    if (!this.nuevaCita.psicologo) {
      this.modalError.set('Debe seleccionar el terapeuta asignado.');
      return;
    }
    if (!this.nuevaCita.fecha) {
      this.modalError.set('Debe seleccionar la fecha de la cita.');
      return;
    }
    const fechaCita = new Date(this.nuevaCita.fecha + 'T00:00:00');
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);
    if (fechaCita < hoy) {
      this.modalError.set('No se pueden programar citas en fechas pasadas.');
      return;
    }
    if (!this.nuevaCita.hora_inicio || !this.nuevaCita.hora_fin) {
      this.modalError.set('Debe seleccionar un bloque horario libre disponible para agendar la cita.');
      return;
    }

    // --- Paso 1: Seleccionar paciente, terapeuta, fecha y slot en IU_AgendaCitas > ---
    this.savingCita = true;

    // --- Paso 2: POST /api/agenda/citas/ {fecha, hora, modalidad} > ---
    // IU_AgendaCitas envía los datos seleccionados al CTR_CitaService
    this.agendaService.createCita({
      paciente: this.nuevaCita.paciente,
      psicologo: this.nuevaCita.psicologo,
      fecha: this.nuevaCita.fecha,
      hora_inicio: this.nuevaCita.hora_inicio,
      hora_fin: this.nuevaCita.hora_fin,
      modalidad: this.nuevaCita.modalidad,
      motivo_consulta: this.nuevaCita.motivo_consulta,
      costo: this.nuevaCita.costo
    }).subscribe({
      // --- Paso 7: 201 Created {cita_id, estado: 'PROGRAMADA'} < ---
      // CTR_CitaService confirma la reserva concurrente con bloqueo pesimista
      next: (res) => {
        this.savingCita = false;
        this.closeNuevaCitaModal();
        // --- Paso 8: Desplegar comprobante de cita confirmada en IU_AgendaCitas < ---
        this.mostrarToast(`Cita programada con éxito para el ${res.fecha} a las ${res.hora_inicio}.`, 'success');
        this.cargarCitas();
      },
      error: (err) => {
        this.savingCita = false;
        const msg = err.error?.error || err.error?.detail || 'Conflicto de horario: el bloque ya fue tomado.';
        this.modalError.set(msg);
        this.mostrarToast(msg, 'error');
      }
    });
  }

  // --------------------------------------------------------------------------
  // DETALLE Y CANCELACIÓN DE CITA (CU11 - Flujo Alternativo Cancelación)
  // --------------------------------------------------------------------------
  verDetalleCita(cita: Cita): void {
    this.citaSeleccionada = cita;
    this.motivoCancelacion = '';
    this.cancelError.set(null);
    this.showDetalleModal = true;
  }

  closeDetalleModal(): void {
    this.showDetalleModal = false;
    this.citaSeleccionada = null;
    this.cancelError.set(null);
  }

  /**
   * CU11 - Cancelación de Citas (HU-17)
   *   Paso 1: Actor ingresa motivo de cancelación en IU_DetalleCita
   *   Paso 2: POST /api/agenda/citas/{id}/cancelar/ {motivo}
   *   (Pasos 3-6: CTR valida anticipación mínima 2h y actualiza estado='CANCELADA')
   *   Paso 7: 200 OK con confirmación de cancelación
   *   Paso 8: Mostrar notificación de cita cancelada y cupo liberado
   */
  cancelarCita(): void {
    this.cancelError.set(null);
    if (!this.citaSeleccionada) return;

    const motivo = this.motivoCancelacion.trim();
    if (!motivo) {
      this.cancelError.set('Por favor describe el motivo de la cancelación.');
      this.mostrarToast('Por favor describe el motivo de la cancelación.', 'error');
      return;
    }
    if (motivo.length < 5) {
      this.cancelError.set('El motivo de la cancelación debe tener al menos 5 caracteres.');
      this.mostrarToast('El motivo de la cancelación debe tener al menos 5 caracteres.', 'error');
      return;
    }

    // Pre-validación de política de 2 horas de anticipación (HU-17 / TP-42)
    try {
      const citaDateTime = new Date(`${this.citaSeleccionada.fecha}T${this.citaSeleccionada.hora_inicio}`);
      const ahora = new Date();
      const diffMs = citaDateTime.getTime() - ahora.getTime();
      const diffHoras = diffMs / (1000 * 60 * 60);
      if (diffHoras < 0) {
        this.cancelError.set('No es posible cancelar una consulta cuya fecha y hora de inicio ya han pasado.');
        return;
      }
    } catch (_) {}

    // --- Paso 2: POST /api/agenda/citas/{id}/cancelar/ > ---
    this.agendaService.cancelarCita(this.citaSeleccionada.id, motivo).subscribe({
      // --- Paso 7: 200 OK < ---
      next: (res) => {
        this.closeDetalleModal();
        // --- Paso 8: Mostrar notificación de cita cancelada < ---
        this.mostrarToast(res.mensaje || 'Cita cancelada correctamente.', 'success');
        this.cargarCitas();
      },
      error: (err) => {
        const msg = err.error?.error || err.error?.detail || 'No es posible cancelar la cita con menos de 2 horas de anticipación.';
        this.cancelError.set(msg);
        this.mostrarToast(msg, 'error');
      }
    });
  }

  irATeleconsulta(citaId: string): void {
    this.closeDetalleModal();
    this.router.navigate(['/teleconsulta', citaId]);
  }

  getEstadoBadgeClass(estado: string): string {
    switch (estado) {
      case 'PROGRAMADA': return 'badge-primary';
      case 'CONFIRMADA': return 'badge-success';
      case 'REALIZADA': return 'badge-info';
      case 'CANCELADA': return 'badge-danger';
      case 'INASISTENCIA': return 'badge-warning';
      default: return 'badge-secondary';
    }
  }

  private mostrarToast(msg: string, type: 'success' | 'error'): void {
    this.toastMsg = msg;
    this.toastType = type;
    setTimeout(() => {
      this.toastMsg = '';
    }, 4000);
  }
}
