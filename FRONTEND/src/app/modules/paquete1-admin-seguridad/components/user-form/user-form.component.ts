import { Component, OnInit } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  Validators,
  AbstractControl,
  ValidationErrors,
  ValidatorFn,
} from '@angular/forms';
import { Router } from '@angular/router';
import { UserService } from '../../../../services/user.service';
import { RoleService } from '../../../../services/role.service';

export function securePasswordValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const value = control.value;
    if (!value) return null;
    const errors: Record<string, boolean> = {};
    if (value.length < 8) errors['minLengthError'] = true;
    if (!/[A-Z]/.test(value)) errors['missingUppercase'] = true;
    if (!/[a-z]/.test(value)) errors['missingLowercase'] = true;
    if (!/\d/.test(value)) errors['missingNumber'] = true;
    if (!/[^a-zA-Z0-9]/.test(value)) errors['missingSpecialChar'] = true;
    return Object.keys(errors).length > 0 ? errors : null;
  };
}

@Component({
  selector: 'app-user-form',
  standalone: false,
  templateUrl: './user-form.component.html',
  styleUrls: ['./user-form.component.css'],
})
export class UserFormComponent implements OnInit {
  userForm: FormGroup;
  roles: any[] = [];
  isLoading = false;
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private userService: UserService,
    private roleService: RoleService,
    private router: Router
  ) {
    this.userForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      first_name: ['', Validators.required],
      last_name: ['', Validators.required],
      password: ['', [Validators.required, securePasswordValidator()]],
      role_id: ['', Validators.required],
      is_active: [true],
    });
  }

  ngOnInit(): void {
    this.roleService.getRoles().subscribe({
      next: (data) => (this.roles = data ?? []),
      error: () => {},
    });
  }

  onSubmit(): void {
    if (this.userForm.invalid) {
      this.userForm.markAllAsTouched();
      return;
    }
    this.isLoading = true;
    this.errorMessage = '';

    const v = this.userForm.value;
    const payload = {
      email: v.email,
      username: v.email.split('@')[0],
      first_name: v.first_name,
      last_name: v.last_name,
      password: v.password,
      is_active: v.is_active,
      // Rol.id es UUID (string) — sin parseInt.
      roles: v.role_id ? [v.role_id] : [],
    };

    this.userService.createUser(payload).subscribe({
      next: () => {
        this.isLoading = false;
        this.router.navigate(['/users']);
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
      const firstKey = Object.keys(body)[0];
      const val = body[firstKey];
      if (Array.isArray(val)) return `${firstKey}: ${val[0]}`;
      if (typeof val === 'string') return val;
    }
    return 'No se pudo crear el usuario. Revisa los datos.';
  }

  get pwd(): string {
    return this.userForm.get('password')?.value || '';
  }
  get hasMinLength(): boolean {
    return this.pwd.length >= 8;
  }
  get hasUppercase(): boolean {
    return /[A-Z]/.test(this.pwd);
  }
  get hasLowercase(): boolean {
    return /[a-z]/.test(this.pwd);
  }
  get hasNumber(): boolean {
    return /\d/.test(this.pwd);
  }
  get hasSpecialChar(): boolean {
    return /[^a-zA-Z0-9]/.test(this.pwd);
  }
}
