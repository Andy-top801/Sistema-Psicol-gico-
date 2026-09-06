import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

import { AuthService } from '../../../../services/auth.service';
import { TenantContextService } from '../../../../core/services/tenant-context.service';

@Component({
  selector: 'app-login',
  standalone: false,
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
})
export class LoginComponent implements OnInit {
  loginForm: FormGroup;
  errorMessage = '';
  isLoading = false;
  showPassword = false;

  isPublicDomain: boolean;
  centerName: string;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute,
    tenant: TenantContextService
  ) {
    this.isPublicDomain = tenant.isPublicDomain;
    this.centerName = tenant.prettyName;
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required],
      rememberMe: [false],
    });
  }

  ngOnInit(): void {
    if (localStorage.getItem('sigepsi_remember_me') === 'true') {
      this.loginForm.patchValue({
        email: localStorage.getItem('sigepsi_remember_email') || '',
        rememberMe: true,
      });
    }
  }

  onSubmit(): void {
    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return;
    }
    this.isLoading = true;
    this.errorMessage = '';
    const { email, password, rememberMe } = this.loginForm.value;

    this.authService.login(email, password).subscribe({
      next: () => {
        if (rememberMe) {
          localStorage.setItem('sigepsi_remember_me', 'true');
          localStorage.setItem('sigepsi_remember_email', email);
        } else {
          localStorage.removeItem('sigepsi_remember_me');
          localStorage.removeItem('sigepsi_remember_email');
        }

        // El dominio público solo admite superadmin de plataforma.
        if (this.isPublicDomain && this.authService.primaryRole() !== 'superadmin') {
          this.authService.logout();
          this.isLoading = false;
          this.errorMessage =
            'Esta cuenta pertenece a un centro. Ingresa desde el subdominio de tu centro.';
          return;
        }

        const returnUrl = this.route.snapshot.queryParamMap.get('returnUrl');
        this.router.navigateByUrl(returnUrl ?? this.authService.homePathForRole());
      },
      error: (err: any) => {
        this.isLoading = false;
        this.errorMessage = this.parseError(err);
      },
    });
  }

  togglePasswordVisibility(): void {
    this.showPassword = !this.showPassword;
  }

  fillDemo(email: string, pass: string): void {
    this.loginForm.patchValue({ email, password: pass });
    this.errorMessage = '';
  }

  private parseError(err: any): string {
    if (err?.status === 0) return 'No se pudo conectar con el servidor.';
    if (err?.status === 401 || err?.status === 400) {
      return 'Credenciales incorrectas o cuenta inactiva.';
    }
    return 'No se pudo iniciar sesión. Intenta de nuevo.';
  }
}
