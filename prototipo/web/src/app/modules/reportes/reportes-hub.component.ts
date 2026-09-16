import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../core/services/auth.service';

interface ReportCard {
  id: string;
  titulo: string;
  descripcion: string;
  icono: string;
  colorIcono: string;
  ruta: string;
  categoria: 'clinico' | 'gestion' | 'financiero' | 'sistema';
  requiereSuperAdmin?: boolean;
  tags: string[];
}

@Component({
  selector: 'app-reportes-hub',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  template: `
    <div class="reportes-container">
      <!-- Header Hero -->
      <header class="hub-header">
        <div class="header-titles">
          <div class="badge-pill">
            <i class="fa-solid fa-chart-pie"></i>
            <span>Módulo de Inteligencia & Reportería</span>
          </div>
          <h1 class="page-title">Centro de Reportes & Exportaciones</h1>
          <p class="page-subtitle">
            Genera, filtra y exporta reportes clínicos, financieros y administrativos en formatos PDF, Excel (CSV), HTML o envíalos directamente por correo.
          </p>
        </div>

        <div class="header-actions">
          <a routerLink="/reportes/personalizado" class="btn-custom-builder">
            <i class="fa-solid fa-wand-magic-sparkles"></i>
            <span>Constructor Personalizado</span>
          </a>
        </div>
      </header>

      <!-- Search & Category Filters -->
      <div class="filters-bar">
        <div class="search-box">
          <i class="fa-solid fa-magnifying-glass"></i>
          <input 
            type="text" 
            [(ngModel)]="searchQuery" 
            placeholder="Buscar reporte por nombre o palabras clave..."
            class="search-input"
          />
          <button *ngIf="searchQuery" (click)="searchQuery = ''" class="btn-clear-search">
            <i class="fa-solid fa-xmark"></i>
          </button>
        </div>

        <div class="category-tabs">
          <button 
            class="tab-btn" 
            [class.active]="selectedCategory() === 'todos'"
            (click)="selectedCategory.set('todos')">
            Todos ({{ reportesFiltrados().length }})
          </button>
          <button 
            class="tab-btn" 
            [class.active]="selectedCategory() === 'clinico'"
            (click)="selectedCategory.set('clinico')">
            <i class="fa-solid fa-stethoscope"></i> Clínicos
          </button>
          <button 
            class="tab-btn" 
            [class.active]="selectedCategory() === 'gestion'"
            (click)="selectedCategory.set('gestion')">
            <i class="fa-solid fa-users-gear"></i> Gestión
          </button>
          <button 
            class="tab-btn" 
            [class.active]="selectedCategory() === 'financiero'"
            (click)="selectedCategory.set('financiero')">
            <i class="fa-solid fa-coins"></i> Financieros
          </button>
          <button 
            *ngIf="authService.isSuperAdmin()"
            class="tab-btn" 
            [class.active]="selectedCategory() === 'sistema'"
            (click)="selectedCategory.set('sistema')">
            <i class="fa-solid fa-shield-halved"></i> Auditoría
          </button>
        </div>
      </div>

      <!-- Hero Card: Constructor Personalizado -->
      <div class="builder-hero-card">
        <div class="builder-content">
          <div class="builder-badge">
            <i class="fa-solid fa-sliders"></i> Reporte a la Medida
          </div>
          <h2>¿Necesitas un reporte con columnas y filtros específicos?</h2>
          <p>
            Utiliza el constructor interactivo: selecciona cualquier fuente de datos (citas, pacientes, alertas, teleconsultas, etc.), elige qué columnas deseas mostrar, aplica criterios de búsqueda dinámicos, define el orden y descárgalo en PDF o Excel al instante.
          </p>
          <a routerLink="/reportes/personalizado" class="btn-hero-action">
            <i class="fa-solid fa-wand-magic-sparkles"></i> Diseñar mi propio reporte
          </a>
        </div>
        <div class="builder-illustration">
          <div class="visual-stack">
            <div class="pill-badge-item"><i class="fa-solid fa-file-pdf"></i> PDF con membrete</div>
            <div class="pill-badge-item"><i class="fa-solid fa-file-excel"></i> Excel / CSV</div>
            <div class="pill-badge-item"><i class="fa-solid fa-code"></i> HTML Web</div>
            <div class="pill-badge-item"><i class="fa-solid fa-envelope"></i> Envío por Email</div>
          </div>
        </div>
      </div>

      <!-- Predefined Reports Grid -->
      <section class="reports-grid">
        <div 
          *ngFor="let rep of reportesFiltrados()" 
          class="report-card"
          [routerLink]="rep.ruta">
          <div class="card-header">
            <div class="icon-avatar" [style.background]="rep.colorIcono">
              <i [class]="rep.icono"></i>
            </div>
            <span class="category-tag">{{ rep.categoria | uppercase }}</span>
          </div>

          <div class="card-body">
            <h3 class="card-title">{{ rep.titulo }}</h3>
            <p class="card-description">{{ rep.descripcion }}</p>
          </div>

          <div class="card-footer">
            <div class="export-badges">
              <span title="Exportar a PDF"><i class="fa-regular fa-file-pdf text-danger"></i> PDF</span>
              <span title="Exportar a Excel"><i class="fa-regular fa-file-excel text-success"></i> Excel</span>
              <span title="Exportar a HTML"><i class="fa-brands fa-html5 text-warning"></i> HTML</span>
              <span title="Enviar por Email"><i class="fa-regular fa-envelope text-info"></i> Email</span>
            </div>
            <span class="link-arrow">
              Ver reporte <i class="fa-solid fa-arrow-right"></i>
            </span>
          </div>
        </div>
      </section>

      <!-- Empty State -->
      <div *ngIf="reportesFiltrados().length === 0" class="empty-state">
        <i class="fa-solid fa-filter-circle-xmark empty-icon"></i>
        <h3>No se encontraron reportes</h3>
        <p>No hay reportes que coincidan con "{{ searchQuery }}". Intenta con otro término o limpia los filtros.</p>
        <button (click)="searchQuery = ''; selectedCategory.set('todos')" class="btn-reset-filters">
          Ver todos los reportes
        </button>
      </div>
    </div>
  `,
  styles: [`
    .reportes-container {
      max-width: 1300px;
      margin: 0 auto;
    }

    .hub-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 28px;
      gap: 20px;
      flex-wrap: wrap;
    }

    .badge-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 5px 14px;
      background: #e6f4ee;
      color: #19734e;
      border-radius: 20px;
      font-size: 0.8rem;
      font-weight: 700;
      letter-spacing: 0.4px;
      margin-bottom: 10px;
    }

    .page-title {
      font-size: 1.85rem;
      font-weight: 800;
      color: #0f2922;
      margin: 0 0 8px 0;
      letter-spacing: -0.5px;
    }

    .page-subtitle {
      font-size: 0.95rem;
      color: #557568;
      max-width: 750px;
      margin: 0;
      line-height: 1.5;
    }

    .btn-custom-builder {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 12px 22px;
      background: linear-gradient(135deg, #19734e 0%, #0f2922 100%);
      color: #ffffff;
      border-radius: 12px;
      font-weight: 700;
      font-size: 0.92rem;
      text-decoration: none;
      box-shadow: 0 6px 20px rgba(25, 115, 78, 0.25);
      transition: all 0.2s ease;
    }

    .btn-custom-builder:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(25, 115, 78, 0.35);
      background: linear-gradient(135deg, #228b60 0%, #153c30 100%);
    }

    /* Filters Bar */
    .filters-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      margin-bottom: 24px;
      flex-wrap: wrap;
    }

    .search-box {
      display: flex;
      align-items: center;
      gap: 10px;
      background: #ffffff;
      border: 1px solid #d8e5df;
      padding: 10px 16px;
      border-radius: 12px;
      flex: 1;
      min-width: 280px;
      max-width: 480px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }

    .search-box i {
      color: #799a8d;
    }

    .search-input {
      border: none;
      outline: none;
      width: 100%;
      font-size: 0.9rem;
      color: #12271f;
      background: transparent;
    }

    .btn-clear-search {
      background: transparent;
      border: none;
      color: #999;
      cursor: pointer;
      padding: 4px;
    }

    .category-tabs {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }

    .tab-btn {
      padding: 8px 16px;
      background: #ffffff;
      border: 1px solid #dce8e2;
      border-radius: 10px;
      font-size: 0.84rem;
      font-weight: 600;
      color: #4b6b5f;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
    }

    .tab-btn:hover {
      background: #f1f7f4;
      color: #19734e;
    }

    .tab-btn.active {
      background: #19734e;
      color: #ffffff;
      border-color: #19734e;
      box-shadow: 0 3px 10px rgba(25, 115, 78, 0.2);
    }

    /* Hero Builder Card */
    .builder-hero-card {
      background: linear-gradient(135deg, #0d2820 0%, #164939 100%);
      color: #ffffff;
      border-radius: 18px;
      padding: 30px 36px;
      margin-bottom: 32px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 30px;
      box-shadow: 0 10px 30px rgba(13, 40, 32, 0.18);
      position: relative;
      overflow: hidden;
    }

    .builder-hero-card::after {
      content: '';
      position: absolute;
      top: -50%;
      right: -10%;
      width: 400px;
      height: 400px;
      background: radial-gradient(circle, rgba(46, 196, 134, 0.15) 0%, transparent 70%);
      pointer-events: none;
    }

    .builder-content {
      max-width: 680px;
    }

    .builder-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 12px;
      background: rgba(255, 255, 255, 0.12);
      border: 1px solid rgba(255, 255, 255, 0.2);
      border-radius: 20px;
      font-size: 0.76rem;
      font-weight: 700;
      color: #a1e8cb;
      margin-bottom: 12px;
    }

    .builder-content h2 {
      font-size: 1.45rem;
      font-weight: 800;
      color: #ffffff !important;
      margin: 0 0 10px 0;
      line-height: 1.3;
      letter-spacing: -0.3px;
    }

    .builder-content p {
      font-size: 0.92rem;
      color: #d1ecdf !important;
      line-height: 1.55;
      margin: 0 0 20px 0;
    }

    .btn-hero-action {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 10px 20px;
      background: #2ec486;
      color: #0b221a;
      border-radius: 10px;
      font-weight: 700;
      font-size: 0.88rem;
      text-decoration: none;
      transition: all 0.2s ease;
    }

    .btn-hero-action:hover {
      background: #39e39c;
      transform: translateY(-2px);
      box-shadow: 0 4px 15px rgba(46, 196, 134, 0.4);
    }

    .visual-stack {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .pill-badge-item {
      padding: 8px 16px;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.12);
      backdrop-filter: blur(8px);
      border-radius: 12px;
      font-size: 0.85rem;
      font-weight: 600;
      color: #e3f2eb;
      display: flex;
      align-items: center;
      gap: 10px;
      white-space: nowrap;
    }

    /* Reports Grid */
    .reports-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
      gap: 20px;
    }

    .report-card {
      background: #ffffff;
      border: 1px solid #dce8e2;
      border-radius: 16px;
      padding: 24px;
      cursor: pointer;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
      box-shadow: 0 2px 8px rgba(0,0,0,0.02);
      text-decoration: none;
    }

    .report-card:hover {
      transform: translateY(-4px);
      border-color: #19734e;
      box-shadow: 0 10px 25px rgba(25, 115, 78, 0.12);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }

    .icon-avatar {
      width: 46px;
      height: 46px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #ffffff;
      font-size: 1.25rem;
      box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    }

    .category-tag {
      font-size: 0.70rem;
      font-weight: 800;
      color: #799a8d;
      letter-spacing: 0.6px;
      background: #f1f7f4;
      padding: 3px 8px;
      border-radius: 6px;
    }

    .card-title {
      font-size: 1.15rem;
      font-weight: 700;
      color: #12271f;
      margin: 0 0 8px 0;
    }

    .card-description {
      font-size: 0.86rem;
      color: #637f74;
      line-height: 1.45;
      margin: 0 0 20px 0;
    }

    .card-footer {
      border-top: 1px solid #eef4f1;
      padding-top: 14px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .export-badges {
      display: flex;
      gap: 8px;
      font-size: 0.74rem;
      color: #6c887d;
      font-weight: 600;
    }

    .export-badges span {
      display: inline-flex;
      align-items: center;
      gap: 3px;
    }

    .link-arrow {
      font-size: 0.82rem;
      font-weight: 700;
      color: #19734e;
      display: flex;
      align-items: center;
      gap: 5px;
      transition: gap 0.2s;
    }

    .report-card:hover .link-arrow {
      gap: 8px;
    }

    /* Empty State */
    .empty-state {
      text-align: center;
      padding: 60px 20px;
      background: #ffffff;
      border-radius: 16px;
      border: 1px dashed #ceddd6;
      margin-top: 20px;
    }

    .empty-icon {
      font-size: 3rem;
      color: #a4c4b8;
      margin-bottom: 16px;
    }

    .empty-state h3 {
      font-size: 1.25rem;
      color: #12271f;
      margin: 0 0 8px 0;
    }

    .empty-state p {
      color: #66887a;
      max-width: 450px;
      margin: 0 auto 20px auto;
      font-size: 0.9rem;
    }

    .btn-reset-filters {
      padding: 9px 18px;
      background: #19734e;
      color: #ffffff;
      border: none;
      border-radius: 8px;
      font-weight: 700;
      cursor: pointer;
    }

    @media (max-width: 900px) {
      .builder-hero-card {
        flex-direction: column;
        align-items: flex-start;
      }
      .visual-stack {
        flex-direction: row;
        flex-wrap: wrap;
      }
      .reports-grid {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class ReportesHubComponent implements OnInit {
  searchQuery = '';
  selectedCategory = signal<string>('todos');

  reportes: ReportCard[] = [
    {
      id: 'citas',
      titulo: 'Citas Clínicas & Atenciones',
      descripcion: 'Listado completo de citas por estado (programada, realizada, cancelada), modalidad, psicólogo y paciente con ingresos generados.',
      icono: 'fa-solid fa-calendar-check',
      colorIcono: 'linear-gradient(135deg, #16a34a, #15803d)',
      ruta: '/reportes/citas',
      categoria: 'clinico',
      tags: ['citas', 'atenciones', 'calendario', 'modalidad', 'costo']
    },
    {
      id: 'psicologos',
      titulo: 'Directorio y Rendimiento de Psicólogos',
      descripcion: 'Reporte de profesionales con número de colegiado, especialidades, modalidad de atención, tarifa base y total de citas atendidas.',
      icono: 'fa-solid fa-user-doctor',
      colorIcono: 'linear-gradient(135deg, #0284c7, #0369a1)',
      ruta: '/reportes/psicologos',
      categoria: 'gestion',
      tags: ['psicologos', 'especialidad', 'colegiado', 'tarifa', 'rendimiento']
    },
    {
      id: 'pacientes',
      titulo: 'Padrón de Pacientes & Expedientes',
      descripcion: 'Directorio de pacientes con código de expediente único, edad, género, datos de contacto de emergencia y tutores legales para menores.',
      icono: 'fa-solid fa-hospital-user',
      colorIcono: 'linear-gradient(135deg, #8b5cf6, #6d28d9)',
      ruta: '/reportes/pacientes',
      categoria: 'clinico',
      tags: ['pacientes', 'expediente', 'edad', 'menores', 'tutores', 'genero']
    },
    {
      id: 'alertas',
      titulo: 'Historial de Alertas Clínicas',
      descripcion: 'Monitoreo de eventos centinela, riesgos de deserción, inasistencias reiteradas y urgencias clínicas con fecha y nota de resolución.',
      icono: 'fa-solid fa-triangle-exclamation',
      colorIcono: 'linear-gradient(135deg, #ea580c, #c2410c)',
      ruta: '/reportes/alertas',
      categoria: 'clinico',
      tags: ['alertas', 'riesgo', 'desercion', 'inasistencia', 'urgencias']
    },
    {
      id: 'ingresos',
      titulo: 'Ingresos Financieros & Recaudación',
      descripcion: 'Balance financiero por rango de fechas, discriminado por psicólogo tratante y modalidad (presencial vs virtual).',
      icono: 'fa-solid fa-money-bill-trend-up',
      colorIcono: 'linear-gradient(135deg, #059669, #047857)',
      ruta: '/reportes/ingresos',
      categoria: 'financiero',
      tags: ['ingresos', 'dinero', 'costo', 'finanzas', 'recaudacion', 'bob']
    },
    {
      id: 'teleconsultas',
      titulo: 'Sesiones de Teleconsulta Virtual',
      descripcion: 'Métricas de atenciones en línea: duración real de la llamada, sala segura asignada, profesional y estado de la sesión.',
      icono: 'fa-solid fa-video',
      colorIcono: 'linear-gradient(135deg, #0d9488, #0f766e)',
      ruta: '/reportes/teleconsultas',
      categoria: 'clinico',
      tags: ['teleconsulta', 'virtual', 'video', 'duracion', 'sala']
    },
    {
      id: 'usuarios',
      titulo: 'Usuarios y Accesos al Sistema',
      descripcion: 'Catálogo de usuarios registrados con sus roles asignados, correo institucional, teléfono de contacto y estado activo.',
      icono: 'fa-solid fa-users-gear',
      colorIcono: 'linear-gradient(135deg, #475569, #334155)',
      ruta: '/reportes/usuarios',
      categoria: 'gestion',
      tags: ['usuarios', 'roles', 'accesos', 'sistema', 'cuentas']
    },
    {
      id: 'bitacora',
      titulo: 'Bitácora de Auditoría (Logs Cifrados)',
      descripcion: 'Registro inmutable de trazabilidad y eventos del sistema (método HTTP, usuario, IP, ruta y estado). Acceso exclusivo SuperAdmin.',
      icono: 'fa-solid fa-shield-halved',
      colorIcono: 'linear-gradient(135deg, #4f46e5, #3730a3)',
      ruta: '/reportes/bitacora',
      categoria: 'sistema',
      requiereSuperAdmin: true,
      tags: ['bitacora', 'auditoria', 'logs', 'seguridad', 'ip', 'trazabilidad']
    }
  ];

  constructor(public authService: AuthService) {}

  ngOnInit(): void {}

  reportesFiltrados = computed(() => {
    const query = this.searchQuery.toLowerCase().trim();
    const cat = this.selectedCategory();
    const isSuper = this.authService.isSuperAdmin();

    return this.reportes.filter(r => {
      // Regla de permisos para bitácora
      if (r.requiereSuperAdmin && !isSuper) {
        return false;
      }
      // Filtro por categoría
      if (cat !== 'todos' && r.categoria !== cat) {
        return false;
      }
      // Filtro por búsqueda
      if (query) {
        const inTitle = r.titulo.toLowerCase().includes(query);
        const inDesc = r.descripcion.toLowerCase().includes(query);
        const inTags = r.tags.some(t => t.toLowerCase().includes(query));
        return inTitle || inDesc || inTags;
      }
      return true;
    });
  });
}
