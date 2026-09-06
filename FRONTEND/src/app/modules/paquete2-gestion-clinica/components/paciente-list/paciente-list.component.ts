import { Component, OnInit } from '@angular/core';
import { PacienteService, Paciente } from '../../../../services/paciente.service';

@Component({
  selector: 'app-paciente-list',
  standalone: false,
  templateUrl: './paciente-list.component.html',
  styleUrls: ['./paciente-list.component.css'],
})
export class PacienteListComponent implements OnInit {
  pacientes: Paciente[] = [];
  isLoading = true;
  loadError = false;
  searchTerm = '';

  totalPacientes = 0;
  atendidosEsteMes = 0;
  nuevosIngresos = 0;

  showCreateModal = false;
  newEmail = '';
  newFirstName = '';
  newLastName = '';
  newPhone = '';
  newDocumento = '';
  newFechaNac = '';
  newGenero = 'Femenino';
  newDireccion = '';
  newPassword = '';

  createError = '';
  createSuccess = '';
  saving = false;

  constructor(private pacienteService: PacienteService) {}

  ngOnInit(): void {
    this.loadPacientes();
  }

  loadPacientes(): void {
    this.isLoading = true;
    this.loadError = false;
    this.pacienteService.getPacientes().subscribe({
      next: (data) => {
        this.pacientes = data ?? [];
        this.recalcStats();
        this.isLoading = false;
      },
      error: () => {
        this.loadError = true;
        this.isLoading = false;
      },
    });
  }

  private recalcStats(): void {
    this.totalPacientes = this.pacientes.length;
    const now = new Date();
    const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
    this.nuevosIngresos = this.pacientes.filter(
      (p) => p.created_at && new Date(p.created_at) >= monthStart
    ).length;
    this.atendidosEsteMes = this.pacientes.filter(
      (p) => (p.citas_count ?? 0) > 0
    ).length;
  }

  get filteredPacientes(): Paciente[] {
    if (!this.searchTerm.trim()) return this.pacientes;
    const q = this.searchTerm.toLowerCase();
    return this.pacientes.filter(
      (p) =>
        p.usuario.first_name.toLowerCase().includes(q) ||
        p.usuario.last_name.toLowerCase().includes(q) ||
        p.usuario.email.toLowerCase().includes(q) ||
        (p.documento_identidad ?? '').toLowerCase().includes(q)
    );
  }

  openModal(): void {
    this.resetForm();
    this.showCreateModal = true;
  }

  closeModal(): void {
    this.showCreateModal = false;
    this.resetForm();
  }

  private resetForm(): void {
    this.newEmail = '';
    this.newFirstName = '';
    this.newLastName = '';
    this.newPhone = '';
    this.newDocumento = '';
    this.newFechaNac = '';
    this.newGenero = 'Femenino';
    this.newDireccion = '';
    this.newPassword = '';
    this.createError = '';
    this.createSuccess = '';
  }

  saveNewPaciente(): void {
    if (!this.newEmail || !this.newFirstName || !this.newLastName) {
      this.createError = 'Complete los campos obligatorios (*).';
      return;
    }
    this.saving = true;
    this.createError = '';

    const payload: Record<string, unknown> = {
      email: this.newEmail,
      first_name: this.newFirstName,
      last_name: this.newLastName,
      phone: this.newPhone,
      documento_identidad: this.newDocumento,
      fecha_nacimiento: this.newFechaNac || null,
      genero: this.newGenero,
      direccion: this.newDireccion,
    };
    if (this.newPassword) payload['password'] = this.newPassword;

    this.pacienteService.createPaciente(payload).subscribe({
      next: (created) => {
        this.pacientes.unshift(created);
        this.recalcStats();
        this.createSuccess = 'Paciente registrado con éxito.';
        this.saving = false;
        setTimeout(() => this.closeModal(), 1200);
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
      if (Array.isArray(val)) return `${firstKey}: ${val[0]}`;
      if (typeof val === 'string') return val;
    }
    return 'No se pudo registrar el paciente. Revisa los datos e intenta de nuevo.';
  }
}
