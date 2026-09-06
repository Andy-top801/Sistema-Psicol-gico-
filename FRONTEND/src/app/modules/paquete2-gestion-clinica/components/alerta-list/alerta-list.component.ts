import { Component, OnInit } from '@angular/core';
import {
  AlertaService,
  AlertaPriorizacion,
} from '../../../../services/alerta.service';

@Component({
  selector: 'app-alerta-list',
  standalone: false,
  templateUrl: './alerta-list.component.html',
  styleUrls: ['./alerta-list.component.css'],
})
export class AlertaListComponent implements OnInit {
  alertas: AlertaPriorizacion[] = [];
  isLoading = true;
  loadError = false;
  filtroEstado = 'all';
  filtroTipo = 'all';

  pendientesCount = 0;
  enRevisionCount = 0;
  resueltasCount = 0;

  showResolveModal = false;
  selectedAlerta: AlertaPriorizacion | null = null;
  accionTomada = '';
  resolveError = '';
  saving = false;

  constructor(private alertaService: AlertaService) {}

  ngOnInit(): void {
    this.loadAlertas();
  }

  loadAlertas(): void {
    this.isLoading = true;
    this.loadError = false;
    this.alertaService.getAlertas().subscribe({
      next: (data) => {
        this.alertas = data ?? [];
        this.calculateStats();
        this.isLoading = false;
      },
      error: () => {
        this.loadError = true;
        this.isLoading = false;
      },
    });
  }

  calculateStats(): void {
    this.pendientesCount = this.alertas.filter((a) => a.estado === 'pendiente').length;
    this.enRevisionCount = this.alertas.filter((a) => a.estado === 'en_revision').length;
    this.resueltasCount = this.alertas.filter((a) => a.estado === 'resuelta').length;
  }

  get filteredAlertas(): AlertaPriorizacion[] {
    return this.alertas.filter((a) => {
      const matchEstado = this.filtroEstado === 'all' || a.estado === this.filtroEstado;
      const matchTipo = this.filtroTipo === 'all' || a.tipo === this.filtroTipo;
      return matchEstado && matchTipo;
    });
  }

  marcarEnRevision(alerta: AlertaPriorizacion): void {
    this.alertaService.revisarAlerta(alerta.id).subscribe({
      next: (updated) => {
        Object.assign(alerta, updated);
        this.calculateStats();
      },
    });
  }

  openResolve(alerta: AlertaPriorizacion): void {
    this.selectedAlerta = alerta;
    this.accionTomada = alerta.accion_tomada || '';
    this.resolveError = '';
    this.showResolveModal = true;
  }

  closeResolve(): void {
    this.showResolveModal = false;
    this.selectedAlerta = null;
    this.accionTomada = '';
  }

  saveResolution(): void {
    if (!this.selectedAlerta) return;
    if (!this.accionTomada.trim()) {
      this.resolveError = 'Debe detallar la acción clínica ejecutada.';
      return;
    }
    this.saving = true;
    this.resolveError = '';
    const alerta = this.selectedAlerta;
    this.alertaService
      .resolverAlerta(alerta.id, this.accionTomada.trim())
      .subscribe({
        next: (updated) => {
          Object.assign(alerta, updated);
          this.calculateStats();
          this.saving = false;
          this.closeResolve();
        },
        error: () => {
          this.saving = false;
          this.resolveError = 'No se pudo guardar la resolución. Intenta de nuevo.';
        },
      });
  }
}
