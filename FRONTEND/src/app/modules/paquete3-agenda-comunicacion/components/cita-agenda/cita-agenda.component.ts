import { Component, OnInit } from '@angular/core';
import { CitaService, Cita } from '../../../../services/cita.service';
import { PacienteService, Paciente } from '../../../../services/paciente.service';
import { PsicologoService, Psicologo } from '../../../../services/psicologo.service';

@Component({
  selector: 'app-cita-agenda',
  standalone: false,
  templateUrl: './cita-agenda.component.html',
  styleUrls: ['./cita-agenda.component.css'],
})
export class CitaAgendaComponent implements OnInit {
  citas: Cita[] = [];
  pacientes: Paciente[] = [];
  psicologos: Psicologo[] = [];
  isLoading = true;
  loadError = false;

  filtroEstado = 'all';
  filtroFecha = '';

  citasHoy = 0;
  citasConfirmadas = 0;
  citasPendientes = 0;
  inasistencias = 0;

  // Modal nueva cita
  showCreateModal = false;
  newPacienteId = '';
  newPsicologoId = '';
  newFecha = '';
  newHora = '09:00';
  newDuracion = 60;
  newModalidad: 'presencial' | 'virtual' = 'presencial';
  newMotivo = '';
  createError = '';
  createSuccess = '';
  saving = false;

  // Modal reprogramar
  showReprogramarModal = false;
  selectedCita: Cita | null = null;
  reprogramarFecha = '';
  reprogramarHora = '10:00';
  reprogramarError = '';
  reprogramando = false;

  constructor(
    private citaService: CitaService,
    private pacienteService: PacienteService,
    private psicologoService: PsicologoService
  ) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.isLoading = true;
    this.loadError = false;
    this.citaService.getCitas().subscribe({
      next: (data) => {
        this.citas = data ?? [];
        this.calculateStats();
        this.isLoading = false;
      },
      error: () => {
        this.loadError = true;
        this.isLoading = false;
      },
    });

    this.pacienteService.getPacientes().subscribe({
      next: (pats) => (this.pacientes = pats ?? []),
      error: () => {},
    });
    this.psicologoService.getPsicologos().subscribe({
      next: (psis) => (this.psicologos = psis ?? []),
      error: () => {},
    });
  }

  calculateStats(): void {
    const today = new Date().toISOString().slice(0, 10);
    this.citasHoy = this.citas.filter((c) => c.fecha_hora?.startsWith(today)).length;
    this.citasConfirmadas = this.citas.filter((c) => c.estado === 'confirmada').length;
    this.citasPendientes = this.citas.filter((c) => c.estado === 'reservada').length;
    this.inasistencias = this.citas.filter((c) => c.estado === 'inasistencia').length;
  }

  get filteredCitas(): Cita[] {
    return this.citas.filter((c) => {
      const matchEstado = this.filtroEstado === 'all' || c.estado === this.filtroEstado;
      const matchFecha = !this.filtroFecha || (c.fecha_hora ?? '').startsWith(this.filtroFecha);
      return matchEstado && matchFecha;
    });
  }

  confirmar(cita: Cita): void {
    this.citaService.confirmarCita(cita.id).subscribe({
      next: (updated) => {
        Object.assign(cita, updated);
        this.calculateStats();
      },
    });
  }

  cancelar(cita: Cita): void {
    this.citaService.cancelarCita(cita.id).subscribe({
      next: (updated) => {
        Object.assign(cita, updated);
        this.calculateStats();
      },
    });
  }

  marcarInasistencia(cita: Cita): void {
    this.citaService.patchCita(cita.id, { estado: 'inasistencia' }).subscribe({
      next: (updated) => {
        Object.assign(cita, updated);
        this.calculateStats();
      },
      error: () => {
        // Si la validación bloquea el PATCH, al menos refleja el estado local.
        cita.estado = 'inasistencia';
        this.calculateStats();
      },
    });
  }

  openReprogramar(cita: Cita): void {
    this.selectedCita = cita;
    this.reprogramarFecha = (cita.fecha_hora ?? '').split('T')[0];
    this.reprogramarHora = '10:00';
    this.reprogramarError = '';
    this.showReprogramarModal = true;
  }

  closeReprogramar(): void {
    this.showReprogramarModal = false;
    this.selectedCita = null;
  }

  confirmarReprogramacion(): void {
    if (!this.selectedCita || !this.reprogramarFecha || !this.reprogramarHora) {
      this.reprogramarError = 'Selecciona nueva fecha y hora.';
      return;
    }
    this.reprogramando = true;
    this.reprogramarError = '';
    const nuevaFechaHora = `${this.reprogramarFecha}T${this.reprogramarHora}:00`;
    const cita = this.selectedCita;
    this.citaService.reprogramarCita(cita.id, nuevaFechaHora).subscribe({
      next: (updated) => {
        Object.assign(cita, updated);
        this.calculateStats();
        this.reprogramando = false;
        this.closeReprogramar();
      },
      error: (err) => {
        this.reprogramando = false;
        this.reprogramarError = this.parseError(err);
      },
    });
  }

  openCreate(): void {
    this.showCreateModal = true;
    this.newFecha = new Date().toISOString().split('T')[0];
    this.newPacienteId = '';
    this.newPsicologoId = '';
    this.newHora = '09:00';
    this.newDuracion = 60;
    this.newModalidad = 'presencial';
    this.newMotivo = '';
    this.createError = '';
    this.createSuccess = '';
  }

  closeCreate(): void {
    this.showCreateModal = false;
  }

  saveCita(): void {
    if (!this.newPacienteId || !this.newPsicologoId || !this.newFecha || !this.newHora) {
      this.createError = 'Completa paciente, psicólogo, fecha y hora.';
      return;
    }
    this.saving = true;
    this.createError = '';
    const payload: Partial<Cita> = {
      paciente: this.newPacienteId,
      psicologo: this.newPsicologoId,
      fecha_hora: `${this.newFecha}T${this.newHora}:00`,
      duracion_minutos: Number(this.newDuracion),
      modalidad: this.newModalidad,
      motivo: this.newMotivo,
      estado: 'reservada',
    };
    this.citaService.createCita(payload).subscribe({
      next: (created) => {
        this.citas.unshift(created);
        this.calculateStats();
        this.createSuccess = 'Cita agendada correctamente.';
        this.saving = false;
        setTimeout(() => this.closeCreate(), 1200);
      },
      error: (err) => {
        this.saving = false;
        this.createError = this.parseError(err);
      },
    });
  }

  private parseError(err: any): string {
    const body = err?.error;
    if (body && typeof body === 'object') {
      const firstKey = Object.keys(body)[0];
      const val = body[firstKey];
      if (Array.isArray(val)) return val[0];
      if (typeof val === 'string') return val;
    }
    return 'La operación no se pudo completar. Intenta de nuevo.';
  }
}
