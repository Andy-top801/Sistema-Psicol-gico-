import { Component, OnInit } from '@angular/core';
import { CitaService, Cita } from '../../../../services/cita.service';

@Component({
  selector: 'app-mis-citas',
  standalone: false,
  templateUrl: './mis-citas.component.html',
  styleUrls: ['./mis-citas.component.css'],
})
export class MisCitasComponent implements OnInit {
  citas: Cita[] = [];
  isLoading = true;
  loadError = false;

  // Reprogramar
  showReprogramar = false;
  selected: Cita | null = null;
  nuevaFecha = '';
  nuevaHora = '10:00';
  actionError = '';
  working = false;

  constructor(private citaService: CitaService) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.isLoading = true;
    this.loadError = false;
    this.citaService.getCitas({ mine: 1 }).subscribe({
      next: (citas) => {
        this.citas = (citas ?? []).sort(
          (a, b) =>
            new Date(b.fecha_hora).getTime() - new Date(a.fecha_hora).getTime()
        );
        this.isLoading = false;
      },
      error: () => {
        this.loadError = true;
        this.isLoading = false;
      },
    });
  }

  get proximas(): Cita[] {
    const now = new Date();
    return this.citas.filter(
      (c) => new Date(c.fecha_hora) >= now && c.estado !== 'cancelada'
    );
  }

  get historial(): Cita[] {
    const now = new Date();
    return this.citas.filter(
      (c) => new Date(c.fecha_hora) < now || c.estado === 'cancelada'
    );
  }

  cancelar(cita: Cita): void {
    this.working = true;
    this.citaService.cancelarCita(cita.id).subscribe({
      next: (updated) => {
        Object.assign(cita, updated);
        this.working = false;
      },
      error: () => (this.working = false),
    });
  }

  openReprogramar(cita: Cita): void {
    this.selected = cita;
    this.nuevaFecha = (cita.fecha_hora ?? '').split('T')[0];
    this.nuevaHora = '10:00';
    this.actionError = '';
    this.showReprogramar = true;
  }

  closeReprogramar(): void {
    this.showReprogramar = false;
    this.selected = null;
  }

  confirmarReprogramar(): void {
    if (!this.selected || !this.nuevaFecha || !this.nuevaHora) {
      this.actionError = 'Selecciona fecha y hora.';
      return;
    }
    this.working = true;
    this.actionError = '';
    const cita = this.selected;
    this.citaService
      .reprogramarCita(cita.id, `${this.nuevaFecha}T${this.nuevaHora}:00`)
      .subscribe({
        next: (updated) => {
          Object.assign(cita, updated);
          this.working = false;
          this.closeReprogramar();
        },
        error: (err) => {
          this.working = false;
          this.actionError = this.parseError(err);
        },
      });
  }

  private parseError(err: any): string {
    const body = err?.error;
    if (body && typeof body === 'object') {
      const k = Object.keys(body)[0];
      const v = body[k];
      if (Array.isArray(v)) return v[0];
      if (typeof v === 'string') return v;
    }
    return 'No se pudo completar la operación.';
  }
}
