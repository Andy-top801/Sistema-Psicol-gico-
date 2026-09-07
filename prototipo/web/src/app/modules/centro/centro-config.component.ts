import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CentroService } from '../../core/services/centro.service';
import { CentroConfig } from '../../core/models';

@Component({
  selector: 'app-centro-config',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="config-wrapper">
      <div class="page-header mb-4">
        <h1 class="page-title">Configuración Institucional del Centro</h1>
        <p class="page-subtitle">Personaliza datos de contacto, horarios de atención y políticas clínicas</p>
      </div>

      <!-- Success Notification -->
      <div *ngIf="successMessage()" class="alert-box alert-success mb-4">
        <i class="fa-solid fa-circle-check"></i>
        <span>{{ successMessage() }}</span>
      </div>

      <!-- Error Notification -->
      <div *ngIf="errorMessage()" class="alert-box alert-danger mb-4">
        <i class="fa-solid fa-triangle-exclamation"></i>
        <span>{{ errorMessage() }}</span>
        <button class="alert-close" (click)="errorMessage.set(null)">&times;</button>
      </div>

      <div class="glass-panel p-4 config-card">
        <form (ngSubmit)="onSaveConfig()">
          <h3 class="section-heading mb-3"><i class="fa-solid fa-building"></i> Datos Institucionales</h3>

          <div class="row">
            <div class="col-md-6 form-group">
              <label class="form-label">Nombre del Centro</label>
              <input type="text" class="form-control" [(ngModel)]="centro.nombre" name="nombre" required>
            </div>
            <div class="col-md-6 form-group">
              <label class="form-label">Correo Electrónico Oficial</label>
              <input type="email" class="form-control" [(ngModel)]="centro.email" name="email" required>
            </div>
          </div>

          <div class="row">
            <div class="col-md-6 form-group">
              <label class="form-label">Teléfono de Contacto</label>
              <input type="text" class="form-control" [(ngModel)]="centro.telefono" name="telefono">
            </div>
            <div class="col-md-6 form-group">
              <label class="form-label">Dirección Física</label>
              <input type="text" class="form-control" [(ngModel)]="centro.direccion" name="direccion">
            </div>
          </div>

          <hr class="divider my-4">

          <h3 class="section-heading mb-3"><i class="fa-solid fa-clock"></i> Horarios de Atención Semanal</h3>
          <div class="row">
            <div class="col-md-6 form-group">
              <label class="form-label">Lunes a Viernes</label>
              <input type="text" class="form-control" [(ngModel)]="centro.horarios_atencion['lunes_viernes']" name="lunes_viernes" placeholder="08:00 - 19:00">
            </div>
            <div class="col-md-6 form-group">
              <label class="form-label">Sábados</label>
              <input type="text" class="form-control" [(ngModel)]="centro.horarios_atencion['sabado']" name="sabado" placeholder="08:00 - 13:00">
            </div>
          </div>

          <hr class="divider my-4">

          <h3 class="section-heading mb-3"><i class="fa-solid fa-gear"></i> Políticas Clínicas y de Agenda</h3>
          <div class="row">
            <div class="col-md-6 form-group">
              <label class="form-label">Duración Predeterminada de Sesión (Minutos)</label>
              <input type="number" class="form-control" [(ngModel)]="centro.configuracion['duracion_sesion_minutos']" name="duracion" placeholder="50">
            </div>
            <div class="col-md-6 form-group">
              <label class="form-label">Anticipación Mínima para Cancelación (Horas)</label>
              <input type="number" class="form-control" [(ngModel)]="centro.configuracion['cancelacion_horas_anticipacion']" name="anticipacion" placeholder="24">
            </div>
          </div>

          <div class="d-flex justify-content-end gap-2 mt-4">
            <button type="submit" class="btn btn-primary" [disabled]="saving()">
              <i *ngIf="saving()" class="fa-solid fa-circle-notch fa-spin"></i>
              <span *ngIf="!saving()">Guardar Configuración Institucional</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  `,
  styles: [`
    .page-title { font-size: 1.5rem; font-weight: 800; }
    .page-subtitle { font-size: 0.88rem; color: var(--text-muted); }
    .config-card { max-width: 850px; }
    .section-heading { font-size: 1.05rem; font-weight: 700; color: var(--primary); display: flex; align-items: center; gap: 8px; }
    .divider { border: 0; border-top: 1px solid var(--border-glass); }
    .row { display: flex; flex-wrap: wrap; margin: 0 -10px; }
    .col-md-6 { flex: 0 0 50%; max-width: 50%; padding: 0 10px; }
    @media (max-width: 768px) { .col-md-6 { flex: 0 0 100%; max-width: 100%; } }
    .p-4 { padding: 24px; }
    .mb-3 { margin-bottom: 12px; }
    .mb-4 { margin-bottom: 20px; }
    .my-4 { margin-top: 20px; margin-bottom: 20px; }
    .mt-4 { margin-top: 20px; }
    .alert-box { padding: 12px 16px; border-radius: 10px; font-size: 0.88rem; display: flex; align-items: center; gap: 10px; }
    .alert-success { background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); color: #6ee7b7; }
    .alert-danger { background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); color: #fca5a5; }
    .alert-close { background: none; border: none; color: inherit; font-size: 1.2rem; cursor: pointer; margin-left: auto; }
    .d-flex { display: flex; }
    .justify-content-end { justify-content: flex-end; }
    @media (max-width: 640px) {
      .page-title { font-size: 1.3rem; }
      .p-4 { padding: 16px; }
      .btn-primary { width: 100%; justify-content: center; }
    }
  `]
})
export class CentroConfigComponent implements OnInit {
  centro: any = {
    nombre: '',
    email: '',
    telefono: '',
    direccion: '',
    horarios_atencion: { lunes_viernes: '08:00 - 19:00', sabado: '08:00 - 13:00' },
    configuracion: { duracion_sesion_minutos: 50, cancelacion_horas_anticipacion: 24 }
  };

  saving = signal<boolean>(false);
  successMessage = signal<string | null>(null);
  errorMessage = signal<string | null>(null);

  constructor(private centroService: CentroService) {}

  ngOnInit() {
    this.centroService.getConfig().subscribe({
      next: (data: CentroConfig) => {
        this.centro = {
          ...data,
          horarios_atencion: data.horarios_atencion || {},
          configuracion: data.configuracion || {}
        };
      },
      error: () => {
        this.errorMessage.set('Error al cargar la configuración del centro.');
      }
    });
  }

  onSaveConfig() {
    this.saving.set(true);
    this.successMessage.set(null);

    this.centroService.updateConfig(this.centro).subscribe({
      next: () => {
        this.saving.set(false);
        this.successMessage.set('¡Configuración institucional actualizada correctamente!');
        setTimeout(() => this.successMessage.set(null), 4000);
      },
      error: (err: any) => {
        this.saving.set(false);
        let msg = 'Error al guardar la configuración.';
        if (err.error) {
          if (typeof err.error === 'string') msg = err.error;
          else {
            const parts: string[] = [];
            for (const key of Object.keys(err.error)) {
              const val = err.error[key];
              if (Array.isArray(val)) parts.push(`${key}: ${val.join(', ')}`);
              else if (typeof val === 'string') parts.push(`${key}: ${val}`);
            }
            if (parts.length > 0) msg = parts.join(' | ');
          }
        }
        this.errorMessage.set(msg);
        setTimeout(() => this.errorMessage.set(null), 6000);
      }
    });
  }
}
