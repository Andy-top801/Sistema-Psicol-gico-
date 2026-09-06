import { Component, OnInit } from '@angular/core';
import { CitaService, Cita } from '../../../../services/cita.service';
import {
  TeleconsultaService,
  Teleconsulta,
} from '../../../../services/teleconsulta.service';
import { AuthService } from '../../../../services/auth.service';

@Component({
  selector: 'app-portal-home',
  standalone: false,
  templateUrl: './portal-home.component.html',
  styleUrls: ['./portal-home.component.css'],
})
export class PortalHomeComponent implements OnInit {
  nombre = '';
  isLoading = true;
  proximaCita: Cita | null = null;
  citasCount = 0;
  teleconsultasProximas: Teleconsulta[] = [];

  constructor(
    private citaService: CitaService,
    private teleconsultaService: TeleconsultaService,
    auth: AuthService
  ) {
    this.nombre = auth.displayName();
  }

  ngOnInit(): void {
    this.citaService.getCitas({ mine: 1 }).subscribe({
      next: (citas) => {
        const activas = (citas ?? [])
          .filter((c) => c.estado !== 'cancelada')
          .filter((c) => new Date(c.fecha_hora) >= new Date())
          .sort(
            (a, b) =>
              new Date(a.fecha_hora).getTime() - new Date(b.fecha_hora).getTime()
          );
        this.proximaCita = activas[0] ?? null;
        this.citasCount = activas.length;
        this.isLoading = false;
      },
      error: () => (this.isLoading = false),
    });

    this.teleconsultaService.getTeleconsultas().subscribe({
      next: (tcs) => {
        this.teleconsultasProximas = (tcs ?? []).filter(
          (t) => t.estado === 'programada' || t.estado === 'en_curso'
        );
      },
    });
  }
}
