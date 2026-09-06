import { Component, OnInit } from '@angular/core';
import {
  PsicologoService,
  Psicologo,
  Especialidad,
  DisponibilidadSlot,
} from '../../../../services/psicologo.service';

@Component({
  selector: 'app-psicologo-list',
  standalone: false,
  templateUrl: './psicologo-list.component.html',
  styleUrls: ['./psicologo-list.component.css'],
})
export class PsicologoListComponent implements OnInit {
  psicologos: Psicologo[] = [];
  especialidades: Especialidad[] = [];
  isLoading = true;
  loadError = false;
  searchTerm = '';

  totalPsicologos = 0;
  activosCount = 0;

  // Modal disponibilidad (CU8)
  showDisponibilidadModal = false;
  selectedPsicologo: Psicologo | null = null;
  selectedSlots: DisponibilidadSlot[] = [];
  newDiaSemana = 1;
  newHoraInicio = '08:00';
  newHoraFin = '12:00';
  slotError = '';

  // Modal nuevo psicólogo (CU6)
  showCreateModal = false;
  newEmail = '';
  newFirstName = '';
  newLastName = '';
  newPhone = '';
  newPassword = '';
  newModalidad: 'presencial' | 'virtual' | 'mixta' = 'presencial';
  newEspecialidades: string[] = [];
  createError = '';
  createSuccess = '';
  saving = false;

  readonly modalidadLabels: Record<string, string> = {
    presencial: 'Presencial',
    virtual: 'Virtual',
    mixta: 'Mixta',
  };

  readonly diasSemanaLabels: Record<number, string> = {
    1: 'Lunes',
    2: 'Martes',
    3: 'Miércoles',
    4: 'Jueves',
    5: 'Viernes',
    6: 'Sábado',
    7: 'Domingo',
  };

  constructor(private psicologoService: PsicologoService) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.isLoading = true;
    this.loadError = false;
    this.psicologoService.getPsicologos().subscribe({
      next: (data) => {
        this.psicologos = data ?? [];
        this.calculateStats();
        this.isLoading = false;
      },
      error: () => {
        this.loadError = true;
        this.isLoading = false;
      },
    });

    this.psicologoService.getEspecialidades().subscribe({
      next: (esps) => (this.especialidades = esps ?? []),
      error: () => {},
    });
  }

  calculateStats(): void {
    this.totalPsicologos = this.psicologos.length;
    this.activosCount = this.psicologos.filter((p) => p.activo).length;
  }

  get filteredPsicologos(): Psicologo[] {
    if (!this.searchTerm.trim()) return this.psicologos;
    const q = this.searchTerm.toLowerCase();
    return this.psicologos.filter(
      (p) =>
        p.usuario.first_name.toLowerCase().includes(q) ||
        p.usuario.last_name.toLowerCase().includes(q) ||
        p.usuario.email.toLowerCase().includes(q)
    );
  }

  modalidadLabel(m?: string): string {
    return this.modalidadLabels[m ?? ''] ?? m ?? '';
  }

  toggleActivo(p: Psicologo): void {
    const newState = !p.activo;
    p.activo = newState;
    this.psicologoService.patchPsicologo(p.id, { activo: newState }).subscribe({
      next: () => this.calculateStats(),
      error: () => (p.activo = !newState),
    });
  }

  // ── Nuevo psicólogo ──────────────────────────────────────────
  openCreate(): void {
    this.newEmail = '';
    this.newFirstName = '';
    this.newLastName = '';
    this.newPhone = '';
    this.newPassword = '';
    this.newModalidad = 'presencial';
    this.newEspecialidades = [];
    this.createError = '';
    this.createSuccess = '';
    this.showCreateModal = true;
  }

  closeCreate(): void {
    this.showCreateModal = false;
  }

  toggleEspecialidad(id: string): void {
    const i = this.newEspecialidades.indexOf(id);
    if (i >= 0) this.newEspecialidades.splice(i, 1);
    else this.newEspecialidades.push(id);
  }

  saveNewPsicologo(): void {
    if (!this.newEmail || !this.newFirstName || !this.newLastName || !this.newPassword) {
      this.createError = 'Completa correo, nombre, apellido y contraseña.';
      return;
    }
    this.saving = true;
    this.createError = '';
    this.psicologoService
      .createPsicologo({
        email: this.newEmail,
        password: this.newPassword,
        first_name: this.newFirstName,
        last_name: this.newLastName,
        phone: this.newPhone,
        modalidad_atencion: this.newModalidad,
        especialidades: this.newEspecialidades,
      })
      .subscribe({
        next: (created) => {
          this.psicologos.unshift(created);
          this.calculateStats();
          this.createSuccess = 'Psicólogo registrado con éxito.';
          this.saving = false;
          setTimeout(() => this.closeCreate(), 1200);
        },
        error: (err) => {
          this.saving = false;
          this.createError = this.parseError(err);
        },
      });
  }

  // ── Disponibilidad (CU8) ─────────────────────────────────────
  openDisponibilidad(p: Psicologo): void {
    this.selectedPsicologo = p;
    this.selectedSlots = [];
    this.slotError = '';
    this.showDisponibilidadModal = true;
    this.loadSlots(p.id);
  }

  closeDisponibilidad(): void {
    this.showDisponibilidadModal = false;
    this.selectedPsicologo = null;
  }

  loadSlots(psicologoId: string): void {
    this.psicologoService.getDisponibilidades(psicologoId).subscribe({
      next: (slots) => (this.selectedSlots = slots ?? []),
      error: () => (this.selectedSlots = []),
    });
  }

  addSlot(): void {
    if (!this.selectedPsicologo) return;
    this.slotError = '';
    const slot: DisponibilidadSlot = {
      psicologo: this.selectedPsicologo.id,
      dia_semana: Number(this.newDiaSemana),
      hora_inicio: `${this.newHoraInicio}:00`,
      hora_fin: `${this.newHoraFin}:00`,
      activo: true,
    };
    this.psicologoService.createDisponibilidad(slot).subscribe({
      next: (created) => this.selectedSlots.push(created),
      error: (err) => (this.slotError = this.parseError(err)),
    });
  }

  deleteSlot(slot: DisponibilidadSlot, index: number): void {
    if (!slot.id) {
      this.selectedSlots.splice(index, 1);
      return;
    }
    this.psicologoService.deleteDisponibilidad(slot.id).subscribe({
      next: () => this.selectedSlots.splice(index, 1),
      error: () => this.selectedSlots.splice(index, 1),
    });
  }

  getDiaLabel(dia: number): string {
    return this.diasSemanaLabels[dia] ?? `Día ${dia}`;
  }

  private parseError(err: any): string {
    const body = err?.error;
    if (body && typeof body === 'object') {
      const firstKey = Object.keys(body)[0];
      const val = body[firstKey];
      if (Array.isArray(val)) return `${firstKey}: ${val[0]}`;
      if (typeof val === 'string') return val;
    }
    return 'La operación no se pudo completar. Intenta de nuevo.';
  }
}
