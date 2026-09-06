import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '../../../../services/auth.service';

@Component({
  selector: 'app-password-reset',
  standalone: false,
  templateUrl: './password-reset.component.html',
  styleUrls: ['./password-reset.component.css']
})
export class PasswordResetComponent implements OnInit {
  resetForm: FormGroup;
  isLoading: boolean = false;
  successMessage: string = '';
  errorMessage: string = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService
  ) {
    this.resetForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]]
    });
  }

  ngOnInit(): void {}

  onSubmit() {
    if (this.resetForm.invalid) return;

    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

    const { email } = this.resetForm.value;
    this.authService.requestPasswordReset(email).subscribe({
      next: (res: any) => {
        this.isLoading = false;
        this.successMessage = res.message || 'Si el correo existe, se ha enviado un enlace de recuperación.';
      },
      error: (err: any) => {
        this.isLoading = false;
        this.errorMessage = err.error?.error || 'Ocurrió un error al procesar la solicitud';
      }
    });
  }

  onResend() {
    this.successMessage = '';
    this.onSubmit();
  }
}
