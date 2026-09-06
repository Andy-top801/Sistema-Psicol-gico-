import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { TenantService } from '../../../../services/tenant.service';

export interface CentroTenant {
  id: number;
  name: string;
  schema_name: string;
  domain_url?: string;
  admin_name?: string;
  admin_email?: string;
  plan?: string;
  created_at?: string;
  is_active: boolean;
}

@Component({
  selector: 'app-tenant-list',
  templateUrl: './tenant-list.component.html',
  styleUrls: ['./tenant-list.component.css']
})
export class TenantListComponent implements OnInit {
  tenants: CentroTenant[] = [];
  filteredTenants: CentroTenant[] = [];
  isLoading = false;
  searchTerm = '';
  statusFilter = 'all';
  planFilter = 'all';

  // Stats
  totalCentros = 0;
  centrosActivos = 0;
  centrosInactivos = 0;
  mrrEstimado = 14250;

  constructor(
    private tenantService: TenantService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadTenants();
  }

  loadTenants(): void {
    this.isLoading = true;
    this.tenantService.getTenants().subscribe({
      next: (data: any[]) => {
        // Enriquecer con datos del wireframe si vienen básicos del backend
        this.tenants = data.map((t, index) => ({
          id: t.id,
          name: t.name || `Centro ${t.schema_name}`,
          schema_name: t.schema_name,
          domain_url: t.domains && t.domains.length > 0 ? t.domains[0].domain : `${t.schema_name}.sigepsi.com`,
          admin_name: index === 0 ? 'Dr. Carlos San Martín' : (index === 1 ? 'Dra. Rosa M. Morales' : 'Dr. Mateo Fernández'),
          admin_email: index === 0 ? 'carlos@sanmartin.sigepsi.com' : (index === 1 ? 'rosamorales@mentesana.com' : 'mfernandez@clinicaserena.com'),
          plan: index === 0 ? 'Anual - Enterprise' : (index === 1 ? 'Mensual - Professional' : 'Mensual - Starter'),
          created_at: t.created_at ? new Date(t.created_at).toLocaleDateString() : '15/12/2026',
          is_active: t.is_active !== undefined ? t.is_active : true
        }));

        if (this.tenants.length === 0) {
          // Si la BD solo tiene public, añadir ejemplos demo consistentes con el wireframe
          this.tenants = [
            {
              id: 1,
              name: 'Centro Psicológico San Martín',
              schema_name: 'tenant_sanmartin',
              domain_url: 'sanmartin.sigepsi.com',
              admin_name: 'Dr. Carlos San Martín',
              admin_email: 'carlos@sanmartinsigepsi.com',
              plan: 'Anual - Enterprise',
              created_at: '15/12/2026',
              is_active: true
            },
            {
              id: 2,
              name: 'Gabinete Psicológico Mente Sana',
              schema_name: 'clinica_demo',
              domain_url: 'mentesana.sigepsi.com',
              admin_name: 'Dra. Rosa M. Morales',
              admin_email: 'rosamorales@mentesana.com',
              plan: 'Mensual - Professional',
              created_at: '02/09/2026',
              is_active: true
            },
            {
              id: 3,
              name: 'Clínica Psiquiátrica & Psicológica Serena',
              schema_name: 'tenant_serena',
              domain_url: 'serena.sigepsi.com',
              admin_name: 'Dr. Mateo Fernández',
              admin_email: 'mfernandez@clinicaserena.com',
              plan: 'Mensual - Starter',
              created_at: '10/08/2026',
              is_active: false
            }
          ];
        }

        this.calculateStats();
        this.applyFilter();
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  calculateStats(): void {
    this.totalCentros = this.tenants.length;
    this.centrosActivos = this.tenants.filter(t => t.is_active).length;
    this.centrosInactivos = this.totalCentros - this.centrosActivos;
  }

  applyFilter(): void {
    this.filteredTenants = this.tenants.filter(t => {
      const matchQuery = !this.searchTerm || 
        t.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        t.schema_name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        (t.domain_url && t.domain_url.toLowerCase().includes(this.searchTerm.toLowerCase()));
      
      const matchStatus = this.statusFilter === 'all' || 
        (this.statusFilter === 'active' && t.is_active) ||
        (this.statusFilter === 'inactive' && !t.is_active);

      return matchQuery && matchStatus;
    });
  }

  toggleTenantStatus(tenant: CentroTenant): void {
    tenant.is_active = !tenant.is_active;
    this.tenantService.patchTenant(tenant.id, { is_active: tenant.is_active }).subscribe({
      next: () => {
        this.calculateStats();
      },
      error: () => {
        // revert if error
        tenant.is_active = !tenant.is_active;
      }
    });
  }

  navigateNew(): void {
    this.router.navigate(['/tenants/new']);
  }
}
