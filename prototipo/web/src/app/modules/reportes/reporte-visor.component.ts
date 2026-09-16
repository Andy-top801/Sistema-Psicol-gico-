import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ReportService, ColumnaDef, FiltroDef, ReporteResultado, FuenteMetadata } from '../../core/services/report.service';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-reporte-visor',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  template: `
    <div class="visor-container">
      <!-- Breadcrumb & Top Bar -->
      <div class="top-nav-bar">
        <a routerLink="/reportes" class="btn-back">
          <i class="fa-solid fa-arrow-left"></i> Volver al Centro de Reportes
        </a>
        <div class="top-actions">
          <button class="btn-action-outline" (click)="toggleFiltros()">
            <i class="fa-solid fa-filter"></i>
            <span>{{ mostrarFiltros ? 'Ocultar Filtros' : 'Mostrar Filtros' }}</span>
          </button>
          <button class="btn-action-outline" (click)="abrirModalColumnas()">
            <i class="fa-solid fa-table-columns"></i>
            <span>Columnas ({{ columnasVisibles.length }}/{{ todasLasColumnas.length }})</span>
          </button>
          <button class="btn-action-outline" (click)="abrirModalEmail()">
            <i class="fa-solid fa-envelope"></i>
            <span>Enviar por Email</span>
          </button>
          <div class="export-dropdown">
            <button class="btn-export-main" (click)="exportarPDF()">
              <i class="fa-solid fa-file-pdf"></i> Exportar PDF
            </button>
            <button class="btn-export-secondary" (click)="exportarExcel()" title="Exportar a Excel (.xlsx)">
              <i class="fa-solid fa-file-excel"></i>
            </button>
            <button class="btn-export-secondary" (click)="exportarHTML()" title="Exportar a HTML">
              <i class="fa-solid fa-code"></i>
            </button>
            <button class="btn-export-secondary" (click)="imprimirReporte()" title="Imprimir Reporte">
              <i class="fa-solid fa-print"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- Header Section -->
      <div class="report-header">
        <div class="report-title-group">
          <div class="report-icon-box">
            <i [class]="getFuenteIcono()"></i>
          </div>
          <div>
            <h1 class="report-title">{{ tituloReporte }}</h1>
            <p class="report-subtitle">
              {{ descripcionReporte }}
            </p>
          </div>
        </div>
        <div class="report-badges-meta">
          <span class="meta-pill">
            <i class="fa-solid fa-database"></i> Fuente: <strong>{{ fuente }}</strong>
          </span>
          <span class="meta-pill">
            <i class="fa-regular fa-clock"></i> Actualizado: {{ fechaActualizacion }}
          </span>
        </div>
      </div>

      <!-- KPI Summary Cards -->
      <div class="kpi-summary-grid" *ngIf="resultado && resultado.resumen">
        <div class="kpi-card">
          <div class="kpi-icon-wrap"><i class="fa-solid fa-list-ol"></i></div>
          <div class="kpi-info">
            <span class="kpi-label">Total Registros</span>
            <span class="kpi-value">{{ resultado.total }}</span>
          </div>
        </div>

        <div class="kpi-card" *ngIf="resultado.resumen['total_ingresos'] !== undefined">
          <div class="kpi-icon-wrap bg-emerald"><i class="fa-solid fa-money-bill-wave"></i></div>
          <div class="kpi-info">
            <span class="kpi-label">Monto Total</span>
            <span class="kpi-value">Bs. {{ resultado.resumen['total_ingresos'] | number:'1.2-2' }}</span>
          </div>
        </div>

        <div class="kpi-card" *ngIf="resultado.resumen['por_estado']">
          <div class="kpi-icon-wrap bg-amber"><i class="fa-solid fa-chart-pie"></i></div>
          <div class="kpi-info">
            <span class="kpi-label">Distribución por Estado</span>
            <div class="sub-badges">
              <span *ngFor="let item of getResumenEstadoEntries()" class="state-pill">
                {{ item[0] }}: {{ item[1] }}
              </span>
            </div>
          </div>
        </div>

        <div class="kpi-card" *ngIf="resultado.resumen['por_modalidad']">
          <div class="kpi-icon-wrap bg-blue"><i class="fa-solid fa-video"></i></div>
          <div class="kpi-info">
            <span class="kpi-label">Modalidades</span>
            <div class="sub-badges">
              <span *ngFor="let item of getResumenModalidadEntries()" class="state-pill">
                {{ item[0] }}: {{ item[1] }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Dynamic Filters Drawer -->
      <div class="filters-panel" *ngIf="mostrarFiltros">
        <div class="panel-header">
          <h3><i class="fa-solid fa-sliders"></i> Criterios de Selección y Filtros</h3>
          <div class="panel-actions">
            <button class="btn-clear" (click)="limpiarFiltros()">Limpiar Filtros</button>
            <button class="btn-apply" (click)="cargarReporte()">
              <i class="fa-solid fa-magnifying-glass"></i> Aplicar Criterios
            </button>
          </div>
        </div>

        <div class="filters-grid">
          <div *ngFor="let filtro of filtrosDisponibles" class="filter-group">
            <label class="filter-label">{{ filtro.label }}</label>

            <!-- Date -->
            <input 
              *ngIf="filtro.type === 'date'"
              type="date" 
              [(ngModel)]="valoresFiltros[filtro.key]"
              class="form-control"
            />

            <!-- Select -->
            <select 
              *ngIf="filtro.type === 'select'"
              [(ngModel)]="valoresFiltros[filtro.key]"
              class="form-control">
              <option value="">-- Todos --</option>
              <option *ngFor="let opc of filtro.opciones" [value]="opc">{{ opc }}</option>
            </select>

            <!-- Text -->
            <input 
              *ngIf="filtro.type === 'text'"
              type="text" 
              [(ngModel)]="valoresFiltros[filtro.key]"
              placeholder="Buscar..."
              class="form-control"
              (keyup.enter)="cargarReporte()"
            />
          </div>
        </div>
      </div>

      <!-- Main Data Table Container -->
      <div class="table-card">
        <!-- Table Control Toolbar -->
        <div class="table-toolbar">
          <div class="table-search">
            <i class="fa-solid fa-magnifying-glass"></i>
            <input 
              type="text" 
              [(ngModel)]="busquedaRapida" 
              placeholder="Filtrar resultados en pantalla..."
              class="toolbar-input"
            />
          </div>

          <div class="table-meta-right">
            <span class="showing-text">
              Mostrando <strong>{{ datosPaginados().length }}</strong> de <strong>{{ datosFiltrados().length }}</strong> registros
            </span>
            <div class="page-size-selector">
              <label>Filas:</label>
              <select [(ngModel)]="tamanoPagina" (change)="paginaActual = 1">
                <option [ngValue]="10">10</option>
                <option [ngValue]="25">25</option>
                <option [ngValue]="50">50</option>
                <option [ngValue]="100">100</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Loading Indicator -->
        <div *ngIf="cargando" class="loading-state">
          <i class="fa-solid fa-circle-notch fa-spin"></i>
          <span>Cargando y procesando reporte...</span>
        </div>

        <!-- Table View -->
        <div class="table-responsive" *ngIf="!cargando && datosFiltrados().length > 0">
          <table class="data-table">
            <thead>
              <tr>
                <th 
                  *ngFor="let col of columnasParaMostrar()"
                  (click)="cambiarOrden(col.key)"
                  [class.sorted]="ordenColumna === col.key"
                  class="sortable-th">
                  <div class="th-content">
                    <span>{{ col.label }}</span>
                    <i 
                      *ngIf="ordenColumna === col.key" 
                      class="fa-solid" 
                      [class.fa-arrow-up]="ordenDireccion === 'ASC'" 
                      [class.fa-arrow-down]="ordenDireccion === 'DESC'">
                    </i>
                    <i *ngIf="ordenColumna !== col.key" class="fa-solid fa-sort text-muted-icon"></i>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let fila of datosPaginados()">
                <td *ngFor="let col of columnasParaMostrar()">
                  <!-- Status Badges -->
                  <ng-container *ngIf="col.key === 'estado'">
                    <span class="badge-status" [ngClass]="'status-' + (fila[col.key] | lowercase)">
                      {{ fila[col.key] }}
                    </span>
                  </ng-container>

                  <!-- Boolean Badge -->
                  <ng-container *ngIf="col.key === 'activo' || col.key === 'resuelta'">
                    <span class="badge-status" [ngClass]="fila[col.key] === 'true' || fila[col.key] === true ? 'status-activo' : 'status-inactivo'">
                      {{ (fila[col.key] === 'true' || fila[col.key] === true) ? 'Sí' : 'No' }}
                    </span>
                  </ng-container>

                  <!-- Default Text Format -->
                  <ng-container *ngIf="col.key !== 'estado' && col.key !== 'activo' && col.key !== 'resuelta'">
                    <span [class.font-mono]="col.key === 'ci' || col.key === 'codigo_expediente' || col.key === 'ip'">
                      {{ fila[col.key] !== null && fila[col.key] !== undefined ? fila[col.key] : '—' }}
                    </span>
                  </ng-container>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Zero State -->
        <div *ngIf="!cargando && datosFiltrados().length === 0" class="empty-state">
          <i class="fa-solid fa-inbox empty-icon"></i>
          <h4>No se encontraron datos para este reporte</h4>
          <p>Prueba ajustando los criterios de filtrado o seleccionando un rango de fechas diferente.</p>
          <button class="btn-clear" (click)="limpiarFiltros()">Restablecer Filtros</button>
        </div>

        <!-- Table Pagination Footer -->
        <div class="table-pagination" *ngIf="!cargando && datosFiltrados().length > 0">
          <span class="pagination-info">
            Página {{ paginaActual }} de {{ totalPaginas() }}
          </span>
          <div class="pagination-buttons">
            <button 
              class="btn-page" 
              [disabled]="paginaActual === 1" 
              (click)="paginaActual = 1" 
              title="Primera página">
              <i class="fa-solid fa-angles-left"></i>
            </button>
            <button 
              class="btn-page" 
              [disabled]="paginaActual === 1" 
              (click)="paginaActual = paginaActual - 1" 
              title="Página anterior">
              <i class="fa-solid fa-angle-left"></i>
            </button>
            <span class="current-page-pill">{{ paginaActual }}</span>
            <button 
              class="btn-page" 
              [disabled]="paginaActual >= totalPaginas()" 
              (click)="paginaActual = paginaActual + 1" 
              title="Página siguiente">
              <i class="fa-solid fa-angle-right"></i>
            </button>
            <button 
              class="btn-page" 
              [disabled]="paginaActual >= totalPaginas()" 
              (click)="paginaActual = totalPaginas()" 
              title="Última página">
              <i class="fa-solid fa-angles-right"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- Modal Selector de Columnas -->
      <div class="modal-backdrop" *ngIf="modalColumnasAbierto" (click)="modalColumnasAbierto = false">
        <div class="modal-content" (click)="$event.stopPropagation()">
          <div class="modal-header">
            <h3><i class="fa-solid fa-table-columns"></i> Seleccionar Columnas Visibles</h3>
            <button class="btn-close-modal" (click)="modalColumnasAbierto = false">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>
          <div class="modal-body">
            <p class="modal-desc">Marca las columnas que deseas mostrar en la tabla y en las exportaciones:</p>
            <div class="col-quick-actions">
              <button class="btn-link-action" (click)="marcarTodasColumnas(true)">Seleccionar todas</button>
              <button class="btn-link-action" (click)="marcarTodasColumnas(false)">Deseleccionar todas</button>
            </div>
            <div class="columns-checkbox-grid">
              <label *ngFor="let col of todasLasColumnas" class="checkbox-label">
                <input 
                  type="checkbox" 
                  [checked]="columnasVisibles.includes(col.key)"
                  (change)="toggleColumna(col.key)"
                />
                <span>{{ col.label }}</span>
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-apply" (click)="modalColumnasAbierto = false; cargarReporte()">
              Aplicar y Actualizar
            </button>
          </div>
        </div>
      </div>

      <!-- Modal Enviar por Email -->
      <div class="modal-backdrop" *ngIf="modalEmailAbierto" (click)="modalEmailAbierto = false">
        <div class="modal-content" (click)="$event.stopPropagation()">
          <div class="modal-header">
            <h3><i class="fa-solid fa-envelope"></i> Enviar Reporte por Correo</h3>
            <button class="btn-close-modal" (click)="modalEmailAbierto = false">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>
          <div class="modal-body">
            <div class="form-group-modal">
              <label>Correo Electrónico Destinatario *</label>
              <input 
                type="email" 
                [(ngModel)]="emailDestino" 
                placeholder="ejemplo@clinica.com" 
                class="form-control"
              />
            </div>
            <div class="form-group-modal">
              <label>Asunto del Correo</label>
              <input 
                type="text" 
                [(ngModel)]="emailAsunto" 
                class="form-control"
              />
            </div>
            <div class="email-preview-alert">
              <i class="fa-solid fa-circle-info"></i>
              <span>Se enviará un resumen con los <strong>{{ resultado ? resultado.total : 0 }}</strong> registros filtrados en formato HTML estilizado y compatible con clientes de correo.</span>
            </div>
            <div *ngIf="emailMensaje" class="alert-success-modal">
              <i class="fa-solid fa-check"></i> {{ emailMensaje }}
            </div>
            <div *ngIf="emailError" class="alert-error-modal">
              <i class="fa-solid fa-triangle-exclamation"></i> {{ emailError }}
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-clear" (click)="modalEmailAbierto = false">Cerrar</button>
            <button class="btn-apply" [disabled]="enviandoEmail || !emailDestino" (click)="enviarPorCorreo()">
              <i class="fa-solid" [class.fa-paper-plane]="!enviandoEmail" [class.fa-spinner]="enviandoEmail" [class.fa-spin]="enviandoEmail"></i>
              {{ enviandoEmail ? 'Enviando...' : 'Enviar Reporte' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .visor-container {
      max-width: 1400px;
      margin: 0 auto;
    }

    .top-nav-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      margin-bottom: 20px;
      flex-wrap: wrap;
    }

    .btn-back {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 0.88rem;
      font-weight: 700;
      color: #19734e;
      text-decoration: none;
      padding: 8px 14px;
      background: #e8f5ed;
      border-radius: 10px;
      transition: all 0.2s ease;
    }

    .btn-back:hover {
      background: #d3ebe0;
      color: #0d462f;
    }

    .top-actions {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }

    .btn-action-outline {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 14px;
      background: #ffffff;
      border: 1px solid #cde0d7;
      border-radius: 10px;
      font-size: 0.84rem;
      font-weight: 600;
      color: #1f3c31;
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .btn-action-outline:hover {
      border-color: #19734e;
      background: #f4faf7;
      color: #19734e;
    }

    .export-dropdown {
      display: flex;
      align-items: center;
      background: #19734e;
      border-radius: 10px;
      overflow: hidden;
      box-shadow: 0 4px 12px rgba(25, 115, 78, 0.25);
    }

    .btn-export-main {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      background: transparent;
      border: none;
      color: #ffffff;
      font-weight: 700;
      font-size: 0.85rem;
      cursor: pointer;
      transition: background 0.15s;
    }

    .btn-export-main:hover {
      background: rgba(255, 255, 255, 0.12);
    }

    .btn-export-secondary {
      background: transparent;
      border: none;
      border-left: 1px solid rgba(255, 255, 255, 0.2);
      color: #ffffff;
      padding: 8px 12px;
      font-size: 0.9rem;
      cursor: pointer;
      transition: background 0.15s;
    }

    .btn-export-secondary:hover {
      background: rgba(255, 255, 255, 0.15);
    }

    /* Report Header */
    .report-header {
      background: #ffffff;
      border: 1px solid #dce8e2;
      border-radius: 16px;
      padding: 24px 28px;
      margin-bottom: 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 20px;
      flex-wrap: wrap;
    }

    .report-title-group {
      display: flex;
      align-items: center;
      gap: 18px;
    }

    .report-icon-box {
      width: 52px;
      height: 52px;
      border-radius: 14px;
      background: linear-gradient(135deg, #19734e 0%, #0f2922 100%);
      color: #ffffff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.4rem;
      box-shadow: 0 4px 12px rgba(25, 115, 78, 0.2);
    }

    .report-title {
      font-size: 1.55rem;
      font-weight: 800;
      color: #0f2922;
      margin: 0 0 4px 0;
    }

    .report-subtitle {
      font-size: 0.88rem;
      color: #5c7b6f;
      margin: 0;
    }

    .report-badges-meta {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }

    .meta-pill {
      font-size: 0.78rem;
      background: #f1f7f4;
      border: 1px solid #dce8e2;
      color: #3b5a4e;
      padding: 6px 12px;
      border-radius: 20px;
      font-weight: 600;
    }

    /* KPI Summary Cards */
    .kpi-summary-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }

    .kpi-card {
      background: #ffffff;
      border: 1px solid #dce8e2;
      border-radius: 14px;
      padding: 16px 20px;
      display: flex;
      align-items: center;
      gap: 16px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }

    .kpi-icon-wrap {
      width: 44px;
      height: 44px;
      border-radius: 10px;
      background: #e6f4ee;
      color: #19734e;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.2rem;
      flex-shrink: 0;
    }

    .kpi-icon-wrap.bg-emerald {
      background: #ecfdf5;
      color: #059669;
    }

    .kpi-icon-wrap.bg-amber {
      background: #fffbeb;
      color: #d97706;
    }

    .kpi-icon-wrap.bg-blue {
      background: #eff6ff;
      color: #2563eb;
    }

    .kpi-info {
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    .kpi-label {
      font-size: 0.74rem;
      font-weight: 700;
      color: #799a8d;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .kpi-value {
      font-size: 1.35rem;
      font-weight: 800;
      color: #12271f;
    }

    .sub-badges {
      display: flex;
      gap: 4px;
      flex-wrap: wrap;
      margin-top: 4px;
    }

    .state-pill {
      font-size: 0.70rem;
      background: #f1f5f3;
      padding: 2px 6px;
      border-radius: 4px;
      font-weight: 600;
      color: #3b5a4e;
    }

    /* Filters Drawer */
    .filters-panel {
      background: #ffffff;
      border: 1px solid #cde0d7;
      border-radius: 16px;
      padding: 22px 26px;
      margin-bottom: 24px;
      box-shadow: 0 4px 15px rgba(0,0,0,0.03);
      animation: slideDown 0.2s ease-out;
    }

    .panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 18px;
    }

    .panel-header h3 {
      font-size: 1.05rem;
      font-weight: 700;
      color: #12271f;
      margin: 0;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .panel-actions {
      display: flex;
      gap: 10px;
    }

    .filters-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
      gap: 16px;
    }

    .filter-group {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .filter-label {
      font-size: 0.78rem;
      font-weight: 700;
      color: #48665b;
      text-transform: uppercase;
      letter-spacing: 0.4px;
    }

    .form-control {
      padding: 9px 12px;
      border: 1px solid #cfded6;
      border-radius: 8px;
      font-size: 0.88rem;
      color: #12271f;
      outline: none;
      transition: border 0.15s;
      background: #fafcfb;
    }

    .form-control:focus {
      border-color: #19734e;
      background: #ffffff;
    }

    .btn-clear {
      padding: 7px 14px;
      background: #f1f5f3;
      border: 1px solid #d4e2db;
      border-radius: 8px;
      font-weight: 600;
      font-size: 0.82rem;
      color: #4d6d60;
      cursor: pointer;
    }

    .btn-apply {
      padding: 7px 16px;
      background: #19734e;
      border: none;
      border-radius: 8px;
      font-weight: 700;
      font-size: 0.82rem;
      color: #ffffff;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }

    .btn-apply:hover {
      background: #145e3f;
    }

    /* Main Table Card */
    .table-card {
      background: #ffffff;
      border: 1px solid #dce8e2;
      border-radius: 16px;
      box-shadow: 0 4px 15px rgba(0,0,0,0.02);
      overflow: hidden;
    }

    .table-toolbar {
      padding: 16px 20px;
      border-bottom: 1px solid #eef4f1;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
    }

    .table-search {
      display: flex;
      align-items: center;
      gap: 10px;
      background: #f7faf8;
      border: 1px solid #dce8e2;
      padding: 7px 14px;
      border-radius: 8px;
      width: 320px;
    }

    .table-search i {
      color: #8da89d;
    }

    .toolbar-input {
      border: none;
      background: transparent;
      outline: none;
      width: 100%;
      font-size: 0.85rem;
      color: #12271f;
    }

    .table-meta-right {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .showing-text {
      font-size: 0.82rem;
      color: #5c7b6f;
    }

    .page-size-selector {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.82rem;
      color: #5c7b6f;
    }

    .page-size-selector select {
      border: 1px solid #dce8e2;
      border-radius: 6px;
      padding: 4px 8px;
      font-size: 0.82rem;
      outline: none;
      background: #ffffff;
    }

    /* Table View */
    .table-responsive {
      overflow-x: auto;
    }

    .data-table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
    }

    .data-table th {
      background: #f7faf8;
      padding: 12px 16px;
      font-size: 0.78rem;
      font-weight: 700;
      color: #4b6b5f;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      border-bottom: 1px solid #dce8e2;
      white-space: nowrap;
    }

    .sortable-th {
      cursor: pointer;
      user-select: none;
    }

    .sortable-th:hover {
      background: #eef5f1;
      color: #19734e;
    }

    .th-content {
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .text-muted-icon {
      color: #b0c7bd;
      font-size: 0.75rem;
    }

    .data-table td {
      padding: 12px 16px;
      font-size: 0.86rem;
      color: #1c362c;
      border-bottom: 1px solid #edf4f0;
      white-space: nowrap;
    }

    .data-table tbody tr:hover {
      background: #f4faf7;
    }

    .font-mono {
      font-family: monospace;
      font-size: 0.85rem;
    }

    /* Badges */
    .badge-status {
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 0.74rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.4px;
    }

    .status-programada { background: #e0f2fe; color: #0369a1; }
    .status-confirmada { background: #fef3c7; color: #b45309; }
    .status-realizada { background: #dcfce7; color: #15803d; }
    .status-cancelada { background: #fee2e2; color: #b91c1c; }
    .status-inasistencia { background: #f3e8ff; color: #7e22ce; }
    .status-activo { background: #dcfce7; color: #15803d; }
    .status-inactivo { background: #fee2e2; color: #b91c1c; }

    /* Loading & Empty */
    .loading-state {
      padding: 60px 20px;
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
      color: #19734e;
      font-weight: 600;
    }

    .loading-state i {
      font-size: 2rem;
    }

    .empty-state {
      padding: 50px 20px;
      text-align: center;
    }

    .empty-icon {
      font-size: 2.8rem;
      color: #b3cdc2;
      margin-bottom: 12px;
    }

    .empty-state h4 {
      font-size: 1.1rem;
      color: #12271f;
      margin: 0 0 6px 0;
    }

    .empty-state p {
      font-size: 0.86rem;
      color: #638577;
      margin: 0 0 16px 0;
    }

    /* Pagination */
    .table-pagination {
      padding: 14px 20px;
      border-top: 1px solid #eef4f1;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .pagination-info {
      font-size: 0.82rem;
      color: #5c7b6f;
    }

    .pagination-buttons {
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .btn-page {
      width: 32px;
      height: 32px;
      border: 1px solid #dce8e2;
      background: #ffffff;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.78rem;
      color: #3b5a4e;
      cursor: pointer;
      transition: all 0.15s;
    }

    .btn-page:hover:not(:disabled) {
      background: #19734e;
      color: #ffffff;
      border-color: #19734e;
    }

    .btn-page:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }

    .current-page-pill {
      font-size: 0.85rem;
      font-weight: 700;
      color: #19734e;
      padding: 0 8px;
    }

    /* Modal Backdrop & Body */
    .modal-backdrop {
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(15, 41, 34, 0.6);
      backdrop-filter: blur(4px);
      z-index: 1000;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
      animation: fadeIn 0.18s ease-out;
    }

    .modal-content {
      background: #ffffff;
      border-radius: 18px;
      width: 100%;
      max-width: 520px;
      box-shadow: 0 20px 50px rgba(0,0,0,0.25);
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }

    .modal-header {
      padding: 18px 24px;
      background: #f7faf8;
      border-bottom: 1px solid #eef4f1;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .modal-header h3 {
      font-size: 1.1rem;
      font-weight: 800;
      color: #12271f;
      margin: 0;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .btn-close-modal {
      background: transparent;
      border: none;
      font-size: 1.1rem;
      color: #799a8d;
      cursor: pointer;
    }

    .modal-body {
      padding: 22px 24px;
      max-height: 60vh;
      overflow-y: auto;
    }

    .modal-desc {
      font-size: 0.86rem;
      color: #5c7b6f;
      margin: 0 0 12px 0;
    }

    .col-quick-actions {
      display: flex;
      gap: 12px;
      margin-bottom: 14px;
    }

    .btn-link-action {
      background: transparent;
      border: none;
      color: #19734e;
      font-weight: 700;
      font-size: 0.8rem;
      cursor: pointer;
      text-decoration: underline;
      padding: 0;
    }

    .columns-checkbox-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }

    .checkbox-label {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.85rem;
      color: #1f3c31;
      cursor: pointer;
    }

    .modal-footer {
      padding: 16px 24px;
      background: #f7faf8;
      border-top: 1px solid #eef4f1;
      display: flex;
      justify-content: flex-end;
      gap: 10px;
    }

    .form-group-modal {
      margin-bottom: 16px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .form-group-modal label {
      font-size: 0.80rem;
      font-weight: 700;
      color: #48665b;
      text-transform: uppercase;
    }

    .email-preview-alert {
      padding: 12px;
      background: #eaf4ee;
      border-radius: 8px;
      font-size: 0.82rem;
      color: #1e4b37;
      display: flex;
      gap: 8px;
      align-items: flex-start;
      margin-top: 8px;
    }

    .alert-success-modal {
      margin-top: 12px;
      padding: 10px;
      background: #dcfce7;
      color: #15803d;
      border-radius: 6px;
      font-size: 0.84rem;
      font-weight: 600;
    }

    .alert-error-modal {
      margin-top: 12px;
      padding: 10px;
      background: #fee2e2;
      color: #b91c1c;
      border-radius: 6px;
      font-size: 0.84rem;
      font-weight: 600;
    }

    @keyframes slideDown {
      from { opacity: 0; transform: translateY(-8px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
  `]
})
export class ReporteVisorComponent implements OnInit {
  fuente = 'citas';
  tituloReporte = 'Reporte Clínico';
  descripcionReporte = '';
  fechaActualizacion = '';

  todasLasColumnas: ColumnaDef[] = [];
  columnasVisibles: string[] = [];
  filtrosDisponibles: FiltroDef[] = [];
  valoresFiltros: Record<string, any> = {};

  resultado: ReporteResultado | null = null;
  cargando = false;
  mostrarFiltros = true;

  // Sorting & quick search
  busquedaRapida = '';
  ordenColumna = '';
  ordenDireccion: 'ASC' | 'DESC' = 'ASC';

  // Pagination
  paginaActual = 1;
  tamanoPagina = 25;

  // Modals
  modalColumnasAbierto = false;
  modalEmailAbierto = false;
  emailDestino = '';
  emailAsunto = '';
  enviandoEmail = false;
  emailMensaje = '';
  emailError = '';

  constructor(
    private route: ActivatedRoute,
    private reportService: ReportService,
    public authService: AuthService
  ) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      const f = params.get('fuente');
      if (f) {
        this.fuente = f;
        this.configurarFuente();
        this.cargarReporte();
      }
    });
  }

  configurarFuente(): void {
    const titulos: Record<string, { titulo: string; desc: string }> = {
      citas: {
        titulo: 'Reporte de Citas Clínicas & Atenciones',
        desc: 'Consultas programadas, realizadas, canceladas e inasistencias con costos y profesionales asignados.'
      },
      psicologos: {
        titulo: 'Directorio de Psicólogos & Rendimiento',
        desc: 'Cuerpo profesional con colegiatura, tarifas, especialidades y volumen de atención.'
      },
      pacientes: {
        titulo: 'Padrón de Pacientes & Expedientes',
        desc: 'Listado oficial de pacientes con códigos de expediente clínico, tutores y contactos de emergencia.'
      },
      alertas: {
        titulo: 'Historial de Alertas Clínicas',
        desc: 'Seguimiento de eventos centinela, riesgos de deserción y emergencias registradas.'
      },
      ingresos: {
        titulo: 'Reporte Financiero de Ingresos',
        desc: 'Métricas de recaudación por fecha, modalidad y psicólogo tratante.'
      },
      teleconsultas: {
        titulo: 'Reporte de Teleconsultas Virtuales',
        desc: 'Sesiones remotas por videollamada con duración real y sala Jitsi asignada.'
      },
      usuarios: {
        titulo: 'Catálogo de Usuarios del Sistema',
        desc: 'Cuentas activas, roles y permisos asignados en el centro.'
      },
      bitacora: {
        titulo: 'Bitácora de Auditoría (Trazabilidad Cifrada)',
        desc: 'Registro de seguridad inmutable de acciones realizadas en la plataforma.'
      }
    };

    const info = titulos[this.fuente] || { titulo: `Reporte de ${this.fuente}`, desc: 'Módulo de reportería SIGEPSI' };
    this.tituloReporte = info.titulo;
    this.descripcionReporte = info.desc;
    this.emailAsunto = `SIGEPSI — ${this.tituloReporte}`;

    // Cargar metadata de columnas y filtros disponibles
    this.reportService.getMetadata().subscribe({
      next: (meta) => {
        const fMeta = meta[this.fuente];
        if (fMeta) {
          this.todasLasColumnas = fMeta.columnas;
          this.filtrosDisponibles = fMeta.filtros;
          // Por defecto todas visibles
          if (this.columnasVisibles.length === 0) {
            this.columnasVisibles = fMeta.columnas.map(c => c.key);
          }
        }
      }
    });
  }

  cargarReporte(): void {
    this.cargando = true;
    const orden = this.ordenColumna ? { columna: this.ordenColumna, direccion: this.ordenDireccion } : undefined;
    const cols = this.columnasVisibles.length > 0 ? this.columnasVisibles : undefined;

    this.reportService.getReporte(this.fuente, this.valoresFiltros, cols, orden).subscribe({
      next: (res) => {
        this.resultado = res;
        this.todasLasColumnas = res.columnas;
        if (this.columnasVisibles.length === 0) {
          this.columnasVisibles = res.columnas.map(c => c.key);
        }
        this.fechaActualizacion = new Date().toLocaleTimeString('es-BO');
        this.cargando = false;
        this.paginaActual = 1;
      },
      error: (err) => {
        console.error('Error cargando reporte:', err);
        this.cargando = false;
      }
    });
  }

  toggleFiltros(): void {
    this.mostrarFiltros = !this.mostrarFiltros;
  }

  limpiarFiltros(): void {
    this.valoresFiltros = {};
    this.busquedaRapida = '';
    this.cargarReporte();
  }

  // Column Selector
  abrirModalColumnas(): void {
    this.modalColumnasAbierto = true;
  }

  toggleColumna(key: string): void {
    if (this.columnasVisibles.includes(key)) {
      if (this.columnasVisibles.length > 1) {
        this.columnasVisibles = this.columnasVisibles.filter(k => k !== key);
      }
    } else {
      this.columnasVisibles.push(key);
    }
  }

  marcarTodasColumnas(marcar: boolean): void {
    if (marcar) {
      this.columnasVisibles = this.todasLasColumnas.map(c => c.key);
    } else {
      // Dejar al menos la primera
      this.columnasVisibles = [this.todasLasColumnas[0].key];
    }
  }

  columnasParaMostrar = computed(() => {
    return this.todasLasColumnas.filter(c => this.columnasVisibles.includes(c.key));
  });

  // Sorting
  cambiarOrden(colKey: string): void {
    if (this.ordenColumna === colKey) {
      this.ordenDireccion = this.ordenDireccion === 'ASC' ? 'DESC' : 'ASC';
    } else {
      this.ordenColumna = colKey;
      this.ordenDireccion = 'ASC';
    }
    this.cargarReporte();
  }

  // Quick Search & Pagination
  datosFiltrados = computed(() => {
    if (!this.resultado || !this.resultado.datos) return [];
    const q = this.busquedaRapida.toLowerCase().trim();
    if (!q) return this.resultado.datos;

    return this.resultado.datos.filter(fila => {
      return Object.values(fila).some(v =>
        v !== null && v !== undefined && String(v).toLowerCase().includes(q)
      );
    });
  });

  totalPaginas = computed(() => {
    return Math.ceil(this.datosFiltrados().length / this.tamanoPagina) || 1;
  });

  datosPaginados = computed(() => {
    const todos = this.datosFiltrados();
    const inicio = (this.paginaActual - 1) * this.tamanoPagina;
    return todos.slice(inicio, inicio + this.tamanoPagina);
  });

  // Helpers de Resumen
  getResumenEstadoEntries(): [string, any][] {
    if (!this.resultado?.resumen?.['por_estado']) return [];
    return Object.entries(this.resultado.resumen['por_estado']);
  }

  getResumenModalidadEntries(): [string, any][] {
    if (!this.resultado?.resumen?.['por_modalidad']) return [];
    return Object.entries(this.resultado.resumen['por_modalidad']);
  }

  getFuenteIcono(): string {
    const icons: Record<string, string> = {
      citas: 'fa-solid fa-calendar-check',
      psicologos: 'fa-solid fa-user-doctor',
      pacientes: 'fa-solid fa-hospital-user',
      alertas: 'fa-solid fa-triangle-exclamation',
      ingresos: 'fa-solid fa-money-bill-wave',
      teleconsultas: 'fa-solid fa-video',
      usuarios: 'fa-solid fa-users-gear',
      bitacora: 'fa-solid fa-shield-halved'
    };
    return icons[this.fuente] || 'fa-solid fa-chart-bar';
  }

  // Exportaciones
  exportarPDF(): void {
    if (!this.resultado) return;
    const currentTenant = this.authService.currentTenant()?.nombre;
    const currentUser = this.authService.currentUser()?.nombre || 'Administrador Clínico';
    const resAExportar = {
      ...this.resultado,
      columnas: this.columnasParaMostrar(),
      datos: this.datosFiltrados(),
      total: this.datosFiltrados().length
    };
    this.reportService.exportToPDF(resAExportar, this.tituloReporte, currentTenant, currentUser);
  }

  exportarExcel(): void {
    if (!this.resultado) return;
    const currentTenant = this.authService.currentTenant()?.nombre;
    const currentUser = this.authService.currentUser()?.nombre || 'Administrador Clínico';
    const resAExportar = {
      ...this.resultado,
      columnas: this.columnasParaMostrar(),
      datos: this.datosFiltrados(),
      total: this.datosFiltrados().length
    };
    this.reportService.exportToExcel(resAExportar, `reporte_${this.fuente}`, currentTenant, currentUser);
  }

  exportarHTML(): void {
    if (!this.resultado) return;
    const currentTenant = this.authService.currentTenant()?.nombre;
    const resAExportar = {
      ...this.resultado,
      columnas: this.columnasParaMostrar(),
      datos: this.datosFiltrados(),
      total: this.datosFiltrados().length
    };
    this.reportService.exportToHTML(resAExportar, this.tituloReporte, currentTenant);
  }

  imprimirReporte(): void {
    if (!this.resultado) return;
    const resAExportar = {
      ...this.resultado,
      columnas: this.columnasParaMostrar(),
      datos: this.datosFiltrados(),
      total: this.datosFiltrados().length
    };
    this.reportService.printReport(resAExportar, this.tituloReporte);
  }

  // Email
  abrirModalEmail(): void {
    this.modalEmailAbierto = true;
    this.emailMensaje = '';
    this.emailError = '';
    this.emailDestino = this.authService.currentUser()?.email || '';
  }

  enviarPorCorreo(): void {
    if (!this.emailDestino) return;
    this.enviandoEmail = true;
    this.emailMensaje = '';
    this.emailError = '';

    this.reportService.enviarEmail({
      email: this.emailDestino,
      fuente: this.fuente,
      asunto: this.emailAsunto,
      filtros: this.valoresFiltros,
      columnas: this.columnasVisibles
    }).subscribe({
      next: (res) => {
        this.enviandoEmail = false;
        this.emailMensaje = res.mensaje || 'Reporte enviado con éxito.';
        setTimeout(() => {
          this.modalEmailAbierto = false;
        }, 2000);
      },
      error: (err) => {
        this.enviandoEmail = false;
        this.emailError = err.error?.error || 'Error al enviar el reporte.';
      }
    });
  }
}
