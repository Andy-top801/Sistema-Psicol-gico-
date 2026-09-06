import { Component, OnInit } from '@angular/core';
import { CentroService, CentroConfig } from '../../../../services/centro.service';

@Component({
  selector: 'app-centro-config',
  templateUrl: './centro-config.component.html',
  styleUrls: ['./centro-config.component.css']
})
export class CentroConfigComponent implements OnInit {
  activeTab: 'generales' | 'horarios' | 'especialidades' | 'branding' = 'generales';
  
  centro: CentroConfig = {
    nombre: '',
    nif_rif: '',
    registro_sanitario: '',
    direccion: '',
    telefono: '',
    email: '',
    modalidad: 'Híbrida (Presencial + Telepsicología)',
    linea_crisis: '',
    horarios_atencion: {
      lunes_viernes: '08:00 - 19:00',
      sabado: '08:00 - 13:00'
    },
    especialidades: []
  };

  isLoading = false;
  successMessage = '';
  errorMessage = '';

  newEspecialidad = '';

  constructor(private centroService: CentroService) {}

  ngOnInit(): void {
    this.loadConfig();
  }

  loadConfig(): void {
    this.isLoading = true;
    this.centroService.getConfig().subscribe({
      next: (config) => {
        this.centro = config;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  setTab(tab: 'generales' | 'horarios' | 'especialidades' | 'branding'): void {
    this.activeTab = tab;
  }

  addEspecialidad(): void {
    if (this.newEspecialidad.trim()) {
      if (!this.centro.especialidades) {
        this.centro.especialidades = [];
      }
      this.centro.especialidades.push(this.newEspecialidad.trim());
      this.newEspecialidad = '';
    }
  }

  removeEspecialidad(index: number): void {
    if (this.centro.especialidades) {
      this.centro.especialidades.splice(index, 1);
    }
  }

  onSave(): void {
    this.isLoading = true;
    this.successMessage = '';
    this.errorMessage = '';

    this.centroService.saveConfig(this.centro).subscribe({
      next: (saved) => {
        this.centro = saved;
        this.isLoading = false;
        this.successMessage = '¡Perfil institucional guardado exitosamente!';
        setTimeout(() => this.successMessage = '', 4000);
      },
      error: () => {
        this.isLoading = false;
        this.errorMessage = 'Ocurrió un error al guardar los cambios.';
      }
    });
  }
}
