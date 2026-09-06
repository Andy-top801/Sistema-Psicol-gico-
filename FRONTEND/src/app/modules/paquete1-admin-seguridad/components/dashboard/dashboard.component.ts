import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { AuthService } from '../../../../services/auth.service';

@Component({
  selector: 'app-dashboard',
  standalone: false,
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  userName: string = 'Administrador';
  userRole: string = 'SuperAdmin';
  isLoading = false;

  // Live Backend Metrics
  citasTotales: number = 24;
  pacientesTotales: number = 56;
  inasistencias: number = 2;
  cargaProfesional: number = 8;
  centrosActivos: number = 3;

  constructor(
    private authService: AuthService,
    private http: HttpClient,
    private router: Router
  ) {}

  ngOnInit(): void {
    const user = this.authService.getUser();
    if (user) {
      this.userName = user.first_name || user.email || 'Administrador';
      this.userRole = user.rol_nombre || (user.is_superuser ? 'SuperAdmin' : 'Personal');
    }
    this.loadMetrics();
  }

  loadMetrics(): void {
    this.isLoading = true;
    this.http.get<any>('http://localhost:8000/api/users/dashboard/', {
      headers: this.authService.getAuthHeaders()
    }).subscribe({
      next: (data) => {
        if (data) {
          this.citasTotales = data.citas_totales !== undefined ? data.citas_totales : 24;
          this.pacientesTotales = data.pacientes_totales !== undefined ? data.pacientes_totales : 56;
          this.inasistencias = data.inasistencias !== undefined ? data.inasistencias : 2;
          this.cargaProfesional = data.carga_profesional !== undefined ? data.carga_profesional : 8;
        }
        this.isLoading = false;
      },
      error: () => {
        // En caso de que no haya citas creadas aún, mantener valores demo del Sprint 0
        this.isLoading = false;
      }
    });
  }
}
