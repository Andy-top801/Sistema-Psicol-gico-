import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';

import { apiUrl, API } from '../../../../core/api';

@Component({
  selector: 'app-register-admin',
  templateUrl: './register-admin.component.html',
  styleUrls: ['./register-admin.component.css']
})
export class RegisterAdminComponent {
  registerForm: FormGroup;
  isLoading = false;
  errorMessage = '';
  successMessage = '';
  showPassword = false;
  showConfirmPassword = false;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private http: HttpClient
  ) {
    this.registerForm = this.fb.group({
      fullName: ['', [Validators.required, Validators.minLength(3)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', [Validators.required]],
      terms: [false, [Validators.requiredTrue]]
    }, {
      validators: this.passwordMatchValidator
    });
  }

  passwordMatchValidator(g: FormGroup) {
    const p = g.get('password')?.value;
    const cp = g.get('confirmPassword')?.value;
    return p === cp ? null : { mismatch: true };
  }

  get hasMinLength(): boolean {
    const val = this.registerForm.get('password')?.value || '';
    return val.length >= 8;
  }

  get hasUppercase(): boolean {
    const val = this.registerForm.get('password')?.value || '';
    return /[A-Z]/.test(val);
  }

  get hasSpecialChar(): boolean {
    const val = this.registerForm.get('password')?.value || '';
    return /[^A-Za-z0-9]/.test(val);
  }

  togglePassword() {
    this.showPassword = !this.showPassword;
  }

  toggleConfirmPassword() {
    this.showConfirmPassword = !this.showConfirmPassword;
  }

  onSubmit() {
    if (this.registerForm.invalid) {
      this.registerForm.markAllAsTouched();
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

    const fullName = this.registerForm.value.fullName.trim();
    const parts = fullName.split(' ');
    const firstName = parts[0] || 'Admin';
    const lastName = parts.slice(1).join(' ') || 'General';

    const payload = {
      email: this.registerForm.value.email,
      password: this.registerForm.value.password,
      first_name: firstName,
      last_name: lastName
    };

    this.http.post(apiUrl(API.register), payload).subscribe({
      next: (res: any) => {
        this.isLoading = false;
        this.successMessage = '¡Cuenta de Administrador creada exitosamente! Redirigiendo al inicio de sesión...';
        setTimeout(() => {
          this.router.navigate(['/login']);
        }, 2000);
      },
      error: (err: any) => {
        this.isLoading = false;
        if (err.error && typeof err.error === 'object') {
          const firstKey = Object.keys(err.error)[0];
          const val = err.error[firstKey];
          this.errorMessage = Array.isArray(val) ? val[0] : (typeof val === 'string' ? val : 'Error al registrar administrador.');
        } else {
          this.errorMessage = 'No se pudo conectar con el servidor. Intente más tarde.';
        }
      }
    });
  }
}
