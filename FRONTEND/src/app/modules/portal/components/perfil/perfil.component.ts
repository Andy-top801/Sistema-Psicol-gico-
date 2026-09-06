import { Component, OnInit } from '@angular/core';
import { AuthService } from '../../../../services/auth.service';
import { PacienteService } from '../../../../services/paciente.service';
import { AppUser, ROLE_LABEL } from '../../../../core/models/user.model';

@Component({
  selector: 'app-perfil',
  standalone: false,
  templateUrl: './perfil.component.html',
  styleUrls: ['./perfil.component.css'],
})
export class PerfilComponent implements OnInit {
  user: AppUser | null = null;
  roleLabel = '';

  phone = '';
  direccion = '';
  saving = false;
  savedOk = false;
  saveError = '';

  resetSent = false;

  constructor(
    private auth: AuthService,
    private pacienteService: PacienteService
  ) {}

  ngOnInit(): void {
    this.user = this.auth.currentUser();
    this.roleLabel = ROLE_LABEL[this.auth.primaryRole()];
    this.phone = this.user?.phone ?? '';
    if (this.user?.paciente_id) {
      this.pacienteService.getPaciente(this.user.paciente_id).subscribe({
        next: (p) => {
          this.phone = p.usuario?.phone ?? this.phone;
          this.direccion = p.direccion ?? '';
        },
      });
    }
  }

  guardar(): void {
    if (!this.user?.paciente_id) {
      this.saveError = 'Tu perfil de paciente aún no está disponible.';
      return;
    }
    this.saving = true;
    this.savedOk = false;
    this.saveError = '';
    this.pacienteService
      .patchPaciente(this.user.paciente_id, {
        phone: this.phone,
        direccion: this.direccion,
      })
      .subscribe({
        next: () => {
          this.saving = false;
          this.savedOk = true;
        },
        error: () => {
          this.saving = false;
          this.saveError = 'No se pudieron guardar los cambios.';
        },
      });
  }

  solicitarCambioPassword(): void {
    if (!this.user?.email) return;
    this.auth.requestPasswordReset(this.user.email).subscribe({
      next: () => (this.resetSent = true),
      error: () => (this.resetSent = true),
    });
  }
}
