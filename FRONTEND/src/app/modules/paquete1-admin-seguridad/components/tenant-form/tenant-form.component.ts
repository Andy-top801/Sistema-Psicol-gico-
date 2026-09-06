import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { TenantService } from '../../../../services/tenant.service';

@Component({
  selector: 'app-tenant-form',
  standalone: false,
  templateUrl: './tenant-form.component.html',
  styleUrls: ['./tenant-form.component.css'],
})
export class TenantFormComponent {
  tenantForm: FormGroup;
  isLoading = false;
  errorMessage = '';
  successMessage = '';

  constructor(
    private fb: FormBuilder,
    private tenantService: TenantService,
    private router: Router
  ) {
    this.tenantForm = this.fb.group({
      name: ['', Validators.required],
      schema_name: ['', [Validators.required, Validators.pattern(/^[a-z][a-z0-9_]{2,62}$/)]],
      domain_url: ['', Validators.required],
      admin_first_name: [''],
      admin_last_name: [''],
      admin_email: ['', [Validators.required, Validators.email]],
      admin_password: ['', [Validators.required, Validators.minLength(8)]],
    });

    // schema_name → saneado + autocompletar el subdominio.
    this.tenantForm.get('schema_name')!.valueChanges.subscribe((raw: string) => {
      const clean = (raw || '').toLowerCase().replace(/[^a-z0-9_]/g, '');
      if (clean !== raw) {
        this.tenantForm.get('schema_name')!.setValue(clean, { emitEvent: false });
      }
      const domainCtrl = this.tenantForm.get('domain_url')!;
      if (!domainCtrl.dirty || domainCtrl.value.endsWith('.localhost')) {
        domainCtrl.setValue(clean ? `${clean}.localhost` : '', { emitEvent: false });
      }
    });
  }

  onSubmit(): void {
    if (this.tenantForm.invalid) {
      this.tenantForm.markAllAsTouched();
      return;
    }
    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.tenantService.createTenant(this.tenantForm.value).subscribe({
      next: () => {
        this.isLoading = false;
        this.successMessage = 'Centro creado. Se aprovisionó su esquema y su administrador inicial.';
        setTimeout(() => this.router.navigate(['/tenants']), 1200);
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = this.parseError(err);
      },
    });
  }

  private parseError(err: any): string {
    const body = err?.error;
    if (body && typeof body === 'object') {
      const k = Object.keys(body)[0];
      const v = body[k];
      if (Array.isArray(v)) return `${k}: ${v[0]}`;
      if (typeof v === 'string') return v;
      if (body['detail']) return body['detail'];
    }
    return 'No se pudo crear el centro.';
  }
}
