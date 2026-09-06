import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { TenantService } from '../../../../services/tenant.service';
import { AuthService } from '../../../../services/auth.service';

@Component({
  selector: 'app-tenant-form',
  standalone: false,
  templateUrl: './tenant-form.component.html',
  styleUrls: ['./tenant-form.component.css']
})
export class TenantFormComponent implements OnInit {
  tenantForm: FormGroup;
  isLoading: boolean = false;
  errorMessage: string = '';
  successMessage: string = '';

  constructor(
    private fb: FormBuilder,
    private tenantService: TenantService,
    private authService: AuthService,
    private router: Router
  ) {
    this.tenantForm = this.fb.group({
      name: ['', Validators.required],
      schema_name: ['', Validators.required],
      domain_url: ['', Validators.required]
    });
  }

  ngOnInit(): void {}

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  onSubmit() {
    if (this.tenantForm.invalid) return;

    this.isLoading = true;
    this.tenantService.createTenant(this.tenantForm.value).subscribe({
      next: (res: any) => {
        this.isLoading = false;
        this.successMessage = 'Centro creado exitosamente. Se ha configurado su esquema de base de datos.';
        this.tenantForm.reset();
      },
      error: (err: any) => {
        this.isLoading = false;
        this.errorMessage = err.error?.detail || 'Error al crear el centro psicológico';
      }
    });
  }
}
