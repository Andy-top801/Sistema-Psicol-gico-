import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { AuthService } from '../../../../services/auth.service';
import { ROLE_LABEL } from '../../../../core/models/user.model';
import { apiUrl, API } from '../../../../core/api';

@Component({
  selector: 'app-dashboard',
  standalone: false,
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css'],
})
export class DashboardComponent implements OnInit {
  userName = '';
  userRole = '';
  isLoading = false;
  loadError = false;

  citasTotales = 0;
  pacientesTotales = 0;
  inasistencias = 0;
  cargaProfesional = 0;
  centrosActivos = 0;

  constructor(
    private authService: AuthService,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    this.userName = this.authService.displayName() || 'Usuario';
    this.userRole = ROLE_LABEL[this.authService.primaryRole()];
    this.loadMetrics();
  }

  loadMetrics(): void {
    this.isLoading = true;
    this.loadError = false;
    this.http.get<any>(apiUrl(API.dashboard)).subscribe({
      next: (data) => {
        this.citasTotales = data?.citas_totales ?? 0;
        this.pacientesTotales = data?.pacientes_totales ?? 0;
        this.inasistencias = data?.inasistencias ?? 0;
        this.cargaProfesional = data?.carga_profesional ?? 0;
        this.isLoading = false;
      },
      error: () => {
        this.loadError = true;
        this.isLoading = false;
      },
    });
  }
}
