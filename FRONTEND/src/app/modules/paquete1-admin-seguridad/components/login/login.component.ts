import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: false,
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  loginForm: FormGroup;
  errorMessage: string = '';
  isLoading: boolean = false;
  showPassword: boolean = false;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required],
      rememberMe: [false]
    });
  }

  ngOnInit(): void {
    const rememberMe = localStorage.getItem('sigepsi_remember_me') === 'true';
    if (rememberMe) {
      const savedEmail = localStorage.getItem('sigepsi_remember_email') || '';
      const savedPass = localStorage.getItem('sigepsi_remember_pass') || '';
      this.loginForm.patchValue({
        email: savedEmail,
        password: savedPass,
        rememberMe: true
      });
    }
  }

  onSubmit() {
    if (this.loginForm.valid) {
      this.isLoading = true;
      this.errorMessage = '';
      const { email, password, rememberMe } = this.loginForm.value;
      
      this.authService.login(email, password).subscribe({
        next: () => {
          if (rememberMe) {
            localStorage.setItem('sigepsi_remember_me', 'true');
            localStorage.setItem('sigepsi_remember_email', email);
            localStorage.setItem('sigepsi_remember_pass', password);
          } else {
            localStorage.removeItem('sigepsi_remember_me');
            localStorage.removeItem('sigepsi_remember_email');
            localStorage.removeItem('sigepsi_remember_pass');
          }
          this.router.navigate(['/dashboard']);
        },
        error: (err: any) => {
          this.isLoading = false;
          this.errorMessage = 'Credenciales incorrectas o cuenta inactiva';
        }
      });
    }
  }

  togglePasswordVisibility() {
    this.showPassword = !this.showPassword;
  }

  fillDemo(email: string, pass: string) {
    this.loginForm.patchValue({
      email: email,
      password: pass
    });
    this.errorMessage = '';
  }
}
