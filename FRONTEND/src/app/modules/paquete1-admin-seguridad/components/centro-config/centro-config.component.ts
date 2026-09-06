import { Component, OnInit } from '@angular/core';
import { CentroService, CentroConfig } from '../../../../services/centro.service';

type Tab = 'generales' | 'horarios' | 'especialidades' | 'branding';

@Component({
  selector: 'app-centro-config',
  standalone: false,
  templateUrl: './centro-config.component.html',
  styleUrls: ['./centro-config.component.css'],
})
export class CentroConfigComponent implements OnInit {
  activeTab: Tab = 'generales';

  centro: CentroConfig = {
    nombre: '',
    nif_rif: '',
    registro_sanitario: '',
    direccion: '',
    telefono: '',
    email: '',
    modalidad: 'Presencial',
    linea_crisis: '',
    horarios_atencion: {},
    especialidades: [],
  };

  isLoading = false;
  loadError = false;
  successMessage = '';
  errorMessage = '';
  newEspecialidad = '';

  constructor(private centroService: CentroService) {}

  ngOnInit(): void {
    this.loadConfig();
  }

  loadConfig(): void {
    this.isLoading = true;
    this.loadError = false;
    this.centroService.getConfig().subscribe({
      next: (config) => {
        this.centro = {
          ...this.centro,
          ...config,
          horarios_atencion: config.horarios_atencion ?? {},
          especialidades: config.especialidades ?? [],
        };
        this.isLoading = false;
      },
      error: () => {
        this.loadError = true;
        this.isLoading = false;
      },
    });
  }

  setTab(tab: Tab): void {
    this.activeTab = tab;
  }

  addEspecialidad(): void {
    const v = this.newEspecialidad.trim();
    if (v && !this.centro.especialidades.includes(v)) {
      this.centro.especialidades.push(v);
    }
    this.newEspecialidad = '';
  }

  removeEspecialidad(index: number): void {
    this.centro.especialidades.splice(index, 1);
  }

  onSave(): void {
    this.isLoading = true;
    this.successMessage = '';
    this.errorMessage = '';
    this.centroService.saveConfig(this.centro).subscribe({
      next: (saved) => {
        this.centro = {
          ...saved,
          horarios_atencion: saved.horarios_atencion ?? {},
          especialidades: saved.especialidades ?? [],
        };
        this.isLoading = false;
        this.successMessage = 'Configuración del centro guardada.';
        setTimeout(() => (this.successMessage = ''), 4000);
      },
      error: () => {
        this.isLoading = false;
        this.errorMessage = 'No se pudieron guardar los cambios.';
      },
    });
  }
}
