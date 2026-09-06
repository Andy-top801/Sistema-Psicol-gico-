import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { TenantService } from '../../../../services/tenant.service';

export interface CentroTenant {
  id: number | string;
  name: string;
  schema_name: string;
  domain_url?: string;
  created_at?: string;
  is_active: boolean;
}

@Component({
  selector: 'app-tenant-list',
  standalone: false,
  templateUrl: './tenant-list.component.html',
  styleUrls: ['./tenant-list.component.css'],
})
export class TenantListComponent implements OnInit {
  tenants: CentroTenant[] = [];
  filteredTenants: CentroTenant[] = [];
  isLoading = false;
  loadError = false;
  searchTerm = '';
  statusFilter = 'all';

  totalCentros = 0;
  centrosActivos = 0;
  centrosInactivos = 0;

  constructor(
    private tenantService: TenantService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadTenants();
  }

  loadTenants(): void {
    this.isLoading = true;
    this.loadError = false;
    this.tenantService.getTenants().subscribe({
      next: (data: any[]) => {
        this.tenants = (data ?? []).map((t) => ({
          id: t.id,
          name: t.name || `Centro ${t.schema_name}`,
          schema_name: t.schema_name,
          domain_url:
            t.domains && t.domains.length ? t.domains[0].domain : t.domain,
          created_at: t.created_at,
          is_active: t.is_active ?? true,
        }));
        this.calculateStats();
        this.applyFilter();
        this.isLoading = false;
      },
      error: () => {
        this.loadError = true;
        this.isLoading = false;
      },
    });
  }

  calculateStats(): void {
    this.totalCentros = this.tenants.length;
    this.centrosActivos = this.tenants.filter((t) => t.is_active).length;
    this.centrosInactivos = this.totalCentros - this.centrosActivos;
  }

  applyFilter(): void {
    const q = this.searchTerm.toLowerCase();
    this.filteredTenants = this.tenants.filter((t) => {
      const matchQuery =
        !q ||
        t.name.toLowerCase().includes(q) ||
        t.schema_name.toLowerCase().includes(q) ||
        (t.domain_url ?? '').toLowerCase().includes(q);
      const matchStatus =
        this.statusFilter === 'all' ||
        (this.statusFilter === 'active' && t.is_active) ||
        (this.statusFilter === 'inactive' && !t.is_active);
      return matchQuery && matchStatus;
    });
  }

  toggleTenantStatus(tenant: CentroTenant): void {
    tenant.is_active = !tenant.is_active;
    this.tenantService.patchTenant(tenant.id, { is_active: tenant.is_active }).subscribe({
      next: () => this.calculateStats(),
      error: () => (tenant.is_active = !tenant.is_active),
    });
  }

  navigateNew(): void {
    this.router.navigate(['/tenants/new']);
  }
}
