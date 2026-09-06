import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, FormArray, FormControl } from '@angular/forms';
import { Router } from '@angular/router';
import { RoleService } from '../../../../services/role.service';

@Component({
  selector: 'app-role-form',
  standalone: false,
  templateUrl: './role-form.component.html',
  styleUrls: ['./role-form.component.css']
})
export class RoleFormComponent implements OnInit {
  roleForm: FormGroup;
  permisosDisponibles: any[] = [];
  isLoading = false;
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private roleService: RoleService,
    private router: Router
  ) {
    this.roleForm = this.fb.group({
      name: ['', Validators.required],
      description: [''],
      permisos: this.fb.array([])
    });
  }

  ngOnInit(): void {
    this.loadPermisos();
  }

  loadPermisos() {
    this.roleService.getPermisos().subscribe({
      next: (data) => {
        this.permisosDisponibles = data;
        const formArray = this.roleForm.get('permisos') as FormArray;
        this.permisosDisponibles.forEach(() => formArray.push(new FormControl(false)));
      },
      error: (err) => console.error('Error cargando permisos', err)
    });
  }

  get permisosFormArray() {
    return this.roleForm.get('permisos') as FormArray;
  }

  onSubmit() {
    if (this.roleForm.valid) {
      this.isLoading = true;
      const formData = { ...this.roleForm.value };
      
      // Mapear los checkboxes (booleanos) a los IDs reales de los permisos
      const selectedPermisosIds = this.roleForm.value.permisos
        .map((checked: boolean, i: number) => checked ? this.permisosDisponibles[i].id : null)
        .filter((v: any) => v !== null);
      
      formData.permisos = selectedPermisosIds;

      this.roleService.createRole(formData).subscribe({
        next: () => {
          this.isLoading = false;
          this.router.navigate(['/roles']);
        },
        error: (err) => {
          this.isLoading = false;
          this.errorMessage = err.error?.name?.[0] || 'Error al crear el rol.';
        }
      });
    }
  }
}
