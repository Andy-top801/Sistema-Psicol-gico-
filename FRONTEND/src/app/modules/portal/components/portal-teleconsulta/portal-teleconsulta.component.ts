import { Component, OnInit } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import {
  TeleconsultaService,
  Teleconsulta,
} from '../../../../services/teleconsulta.service';

@Component({
  selector: 'app-portal-teleconsulta',
  standalone: false,
  templateUrl: './portal-teleconsulta.component.html',
  styleUrls: ['./portal-teleconsulta.component.css'],
})
export class PortalTeleconsultaComponent implements OnInit {
  teleconsultas: Teleconsulta[] = [];
  isLoading = true;
  loadError = false;

  salaAbierta: Teleconsulta | null = null;
  safeUrl: SafeResourceUrl | null = null;

  constructor(
    private teleconsultaService: TeleconsultaService,
    private sanitizer: DomSanitizer
  ) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.isLoading = true;
    this.loadError = false;
    this.teleconsultaService.getTeleconsultas().subscribe({
      next: (tcs) => {
        this.teleconsultas = (tcs ?? []).sort(
          (a, b) =>
            new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
        this.isLoading = false;
      },
      error: () => {
        this.loadError = true;
        this.isLoading = false;
      },
    });
  }

  entrar(t: Teleconsulta): void {
    this.salaAbierta = t;
    this.safeUrl = this.sanitizer.bypassSecurityTrustResourceUrl(
      t.enlace_paciente || t.enlace_psicologo
    );
  }

  cerrarSala(): void {
    this.salaAbierta = null;
    this.safeUrl = null;
  }
}
