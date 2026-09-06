import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  loginForm!: FormGroup;
  isLoading = false;
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]]
    });
  }

  onSubmit(): void {
    if (this.loginForm.valid) {
      this.isLoading = true;
      this.errorMessage = '';
      
      this.authService.login(this.loginForm.value).subscribe({
        next: (res) => {
          this.isLoading = false;
          // Successful login, redirect to a dashboard route (we'll implement this later)
          console.log('Login exitoso!', res);
          alert('¡Inicio de sesión exitoso!');
        },
        error: (err) => {
          this.isLoading = false;
          console.error(err);
          this.errorMessage = 'Credenciales inválidas. Por favor, intenta de nuevo.';
        }
      });
    } else {
      this.loginForm.markAllAsTouched();
    }
  }
}
