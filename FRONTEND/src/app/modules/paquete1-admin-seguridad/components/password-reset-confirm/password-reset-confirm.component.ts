import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../../../services/auth.service';

export function securePasswordValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const value = control.value;
    if (!value) return null;
    const errors: any = {};
    if (value.length < 8) errors.minLengthError = true;
    if (!/[A-Z]/.test(value)) errors.missingUppercase = true;
    if (!/[a-z]/.test(value)) errors.missingLowercase = true;
    if (!/\d/.test(value)) errors.missingNumber = true;
    if (!/[^a-zA-Z0-9]/.test(value)) errors.missingSpecialChar = true;
    return Object.keys(errors).length > 0 ? errors : null;
  };
}

@Component({
  selector: 'app-password-reset-confirm',
  standalone: false,
  templateUrl: './password-reset-confirm.component.html',
  styleUrls: ['./password-reset-confirm.component.css']
})
export class PasswordResetConfirmComponent implements OnInit {
  confirmForm: FormGroup;
  token: string | null = null;
  errorMessage: string = '';
  successMessage: string = '';
  isLoading: boolean = false;
  showPassword1: boolean = false;
  showPassword2: boolean = false;

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService
  ) {
    this.confirmForm = this.fb.group({
      newPassword: ['', [Validators.required, securePasswordValidator()]],
      confirmPassword: ['', Validators.required]
    }, { validators: this.passwordMatchValidator });
  }

  ngOnInit() {
    this.token = this.route.snapshot.queryParamMap.get('token');
    if (!this.token) {
      this.errorMessage = 'Enlace de recuperación inválido o inexistente.';
    }
  }

  passwordMatchValidator(g: FormGroup) {
    return g.get('newPassword')?.value === g.get('confirmPassword')?.value
      ? null : { mismatch: true };
  }

  togglePassword1() {
    this.showPassword1 = !this.showPassword1;
  }

  togglePassword2() {
    this.showPassword2 = !this.showPassword2;
  }

  onSubmit() {
    if (this.confirmForm.valid && this.token) {
      this.isLoading = true;
      this.errorMessage = '';
      
      const newPassword = this.confirmForm.get('newPassword')?.value;

      this.authService.confirmPasswordReset(this.token, newPassword).subscribe({
        next: () => {
          this.isLoading = false;
          this.successMessage = '¡Tu contraseña ha sido actualizada con éxito!';
          setTimeout(() => {
            this.router.navigate(['/login']);
          }, 3000);
        },
        error: (err) => {
          this.isLoading = false;
          this.errorMessage = err.error?.error || 'El enlace ha expirado o es inválido.';
        }
      });
    }
  }

  get hasMinLength(): boolean {
    const val = this.confirmForm.get('newPassword')?.value || '';
    return val.length >= 8;
  }

  get hasUppercase(): boolean {
    const val = this.confirmForm.get('newPassword')?.value || '';
    return /[A-Z]/.test(val);
  }

  get hasLowercase(): boolean {
    const val = this.confirmForm.get('newPassword')?.value || '';
    return /[a-z]/.test(val);
  }

  get hasNumber(): boolean {
    const val = this.confirmForm.get('newPassword')?.value || '';
    return /\d/.test(val);
  }

  get hasSpecialChar(): boolean {
    const val = this.confirmForm.get('newPassword')?.value || '';
    return /[^a-zA-Z0-9]/.test(val);
  }
}
