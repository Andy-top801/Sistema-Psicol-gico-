import { Component, OnInit } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { TeleconsultaService, Teleconsulta } from '../../../../services/teleconsulta.service';
import { CitaService, Cita } from '../../../../services/cita.service';

@Component({
  selector: 'app-teleconsulta-list',
  templateUrl: './teleconsulta-list.component.html',
  styleUrls: ['./teleconsulta-list.component.css']
})
export class TeleconsultaListComponent implements OnInit {
  teleconsultas: Teleconsulta[] = [];
  citasDisponibles: Cita[] = [];
  isLoading = false;
  errorMessage = '';
  successMessage = '';

  // Filtros
  filtroEstado: string = 'all';

  // Modal Nueva Sesión
  showCreateModal = false;
  selectedCitaId: string = '';
  isSubmitting = false;

  // Sala Virtual Activa
  activeRoomTeleconsulta: Teleconsulta | null = null;
  safeRoomUrl: SafeResourceUrl | null = null;
  showVirtualRoomModal = false;

  // Copiado feedback
  copiedId: string | null = null;

  constructor(
    private teleconsultaService: TeleconsultaService,
    private citaService: CitaService,
    private sanitizer: DomSanitizer
  ) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.isLoading = true;
    this.teleconsultaService.getTeleconsultas().subscribe({
      next: (data) => {
        this.teleconsultas = data;
        this.isLoading = false;
      },
      error: (err) => {
        this.errorMessage = 'Error al cargar las sesiones de teleconsulta.';
        this.isLoading = false;
      }
    });

    this.citaService.getCitas().subscribe({
      next: (citas) => {
        this.citasDisponibles = citas;
      },
      error: () => {}
    });
  }

  get filteredTeleconsultas(): Teleconsulta[] {
    if (this.filtroEstado === 'all') {
      return this.teleconsultas;
    }
    return this.teleconsultas.filter(t => t.estado === this.filtroEstado);
  }

  // KPIs
  get totalSesiones(): number {
    return this.teleconsultas.length;
  }

  get sesionesEnCurso(): number {
    return this.teleconsultas.filter(t => t.estado === 'en_curso').length;
  }

  get sesionesProgramadas(): number {
    return this.teleconsultas.filter(t => t.estado === 'programada').length;
  }

  get sesionesFinalizadas(): number {
    return this.teleconsultas.filter(t => t.estado === 'finalizada').length;
  }

  // Acciones
  openCreateModal(): void {
    this.selectedCitaId = '';
    this.errorMessage = '';
    this.showCreateModal = true;
  }

  closeCreateModal(): void {
    this.showCreateModal = false;
  }

  crearTeleconsulta(): void {
    if (!this.selectedCitaId) {
      this.errorMessage = 'Debe seleccionar una cita previa para generar la teleconsulta.';
      return;
    }

    this.isSubmitting = true;
    this.teleconsultaService.createTeleconsulta({ cita: this.selectedCitaId }).subscribe({
      next: (nueva) => {
        this.isSubmitting = false;
        this.closeCreateModal();
        this.loadData();
        this.showSuccess('Sala de teleconsulta creada exitosamente.');
      },
      error: (err) => {
        this.isSubmitting = false;
        this.errorMessage = err.error?.detail || 'Error al generar la sala de teleconsulta.';
      }
    });
  }

  iniciar(t: Teleconsulta): void {
    this.teleconsultaService.iniciarTeleconsulta(t.id).subscribe({
      next: (updated) => {
        this.showSuccess('Sesión de teleconsulta iniciada.');
        this.loadData();
        this.abrirSalaVirtual(updated);
      },
      error: () => {
        this.errorMessage = 'No se pudo iniciar la teleconsulta.';
      }
    });
  }

  finalizar(t: Teleconsulta): void {
    if (!confirm('¿Desea dar por concluida esta teleconsulta?')) return;
    this.teleconsultaService.finalizarTeleconsulta(t.id).subscribe({
      next: () => {
        this.showSuccess('Teleconsulta finalizada correctamente.');
        if (this.activeRoomTeleconsulta?.id === t.id) {
          this.cerrarSalaVirtual();
        }
        this.loadData();
      },
      error: () => {
        this.errorMessage = 'Error al finalizar la teleconsulta.';
      }
    });
  }

  abrirSalaVirtual(t: Teleconsulta): void {
    this.activeRoomTeleconsulta = t;
    const url = t.enlace_psicologo || `https://meet.jit.si/${t.room_name}`;
    this.safeRoomUrl = this.sanitizer.bypassSecurityTrustResourceUrl(url);
    this.showVirtualRoomModal = true;
  }

  abrirEnNuevaPestana(url: string): void {
    window.open(url, '_blank');
  }

  cerrarSalaVirtual(): void {
    this.showVirtualRoomModal = false;
    this.activeRoomTeleconsulta = null;
    this.safeRoomUrl = null;
    this.loadData();
  }

  copiarEnlace(t: Teleconsulta): void {
    const enlace = t.enlace_paciente || `https://meet.jit.si/${t.room_name}`;
    navigator.clipboard.writeText(enlace).then(() => {
      this.copiedId = t.id;
      setTimeout(() => {
        this.copiedId = null;
      }, 2500);
    });
  }

  getCitaInfo(citaId: string): string {
    const c = this.citasDisponibles.find(x => x.id === citaId);
    if (!c) return `Cita #${citaId.substring(0, 8)}`;
    const fecha = new Date(c.fecha_hora).toLocaleString();
    const paciente = c.paciente_details ? `${c.paciente_details.first_name} ${c.paciente_details.last_name}` : 'Paciente';
    return `${fecha} — ${paciente}`;
  }

  private showSuccess(msg: string): void {
    this.successMessage = msg;
    setTimeout(() => {
      this.successMessage = '';
    }, 4000);
  }
}
