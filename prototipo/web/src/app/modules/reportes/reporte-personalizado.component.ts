import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ReportService, ColumnaDef, FiltroDef, ReporteResultado, FuenteMetadata } from '../../core/services/report.service';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-reporte-personalizado',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  template: `
    <div class="builder-container">
      <!-- Breadcrumb Bar -->
      <div class="top-nav">
        <a routerLink="/reportes" class="btn-back">
          <i class="fa-solid fa-arrow-left"></i> Volver al Centro de Reportes
        </a>
        <div class="step-indicator">
          <span class="step-pill active">1. Fuente</span>
          <i class="fa-solid fa-chevron-right step-arrow"></i>
          <span class="step-pill active">2. Columnas</span>
          <i class="fa-solid fa-chevron-right step-arrow"></i>
          <span class="step-pill active">3. Filtros</span>
          <i class="fa-solid fa-chevron-right step-arrow"></i>
          <span class="step-pill active">4. Orden</span>
          <i class="fa-solid fa-chevron-right step-arrow"></i>
          <span class="step-pill" [class.active]="resultado !== null">5. Generación</span>
        </div>
      </div>

      <!-- Main Header -->
      <div class="builder-header">
        <div class="header-icon-box">
          <i class="fa-solid fa-wand-magic-sparkles"></i>
        </div>
        <div>
          <h1 class="header-title">Constructor Visual de Reportes Personalizados</h1>
          <p class="header-desc">
            Diseña tu propio reporte seleccionando la fuente de información, marcando las columnas deseadas, aplicando filtros de selección y definiendo el criterio de ordenamiento.
          </p>
        </div>
      </div>

      <!-- Configuration Grid / Steps Form -->
      <div class="config-grid">
        <!-- Paso 1: Fuente de Datos -->
        <div class="config-card">
          <div class="step-badge">Paso 1</div>
          <h3 class="card-step-title"><i class="fa-solid fa-database"></i> Fuente de Información</h3>
          <p class="card-step-desc">Selecciona la entidad base sobre la cual deseas construir el reporte:</p>
          
          <select 
            [(ngModel)]="fuenteSeleccionada" 
            (change)="onFuenteCambiada()" 
            class="form-control-large">
            <option value="citas">📅 Citas Clínicas & Atenciones</option>
            <option value="psicologos">👨‍⚕️ Directorio de Psicólogos</option>
            <option value="pacientes">🧑‍🤝‍🧑 Padrón de Pacientes & Expedientes</option>
            <option value="alertas">⚠️ Historial de Alertas Clínicas</option>
            <option value="ingresos">💰 Ingresos Financieros & Recaudación</option>
            <option value="teleconsultas">📹 Sesiones de Teleconsulta Virtual</option>
            <option value="usuarios">👥 Catálogo de Usuarios del Sistema</option>
            <option *ngIf="authService.isSuperAdmin()" value="bitacora">📜 Bitácora de Auditoría (Cifrada)</option>
          </select>
        </div>

        <!-- Paso 2: Selección de Columnas -->
        <div class="config-card">
          <div class="step-badge">Paso 2</div>
          <div class="card-step-header-flex">
            <div>
              <h3 class="card-step-title"><i class="fa-solid fa-table-columns"></i> Columnas a Mostrar</h3>
              <p class="card-step-desc">Marca únicamente las columnas que deben figurar en el reporte:</p>
            </div>
            <div class="quick-links">
              <button class="btn-link" (click)="seleccionarTodasColumnas(true)">Todas</button>
              <button class="btn-link" (click)="seleccionarTodasColumnas(false)">Ninguna</button>
            </div>
          </div>

          <div class="column-checkboxes-box">
            <label *ngFor="let col of columnasDisponibles" class="checkbox-item">
              <input 
                type="checkbox" 
                [checked]="columnasSeleccionadas.includes(col.key)"
                (change)="toggleColumna(col.key)"
              />
              <span class="checkbox-text">{{ col.label }}</span>
            </label>
          </div>
          <span class="selection-count">
            {{ columnasSeleccionadas.length }} de {{ columnasDisponibles.length }} columnas seleccionadas
          </span>
        </div>

        <!-- Paso 3: Criterios de Selección y Filtros -->
        <div class="config-card full-width">
          <div class="step-badge">Paso 3</div>
          <h3 class="card-step-title"><i class="fa-solid fa-filter"></i> Criterios de Selección (Filtros Previos)</h3>
          <p class="card-step-desc">Todo reporte antes de generar permite delimitar la información a obtener:</p>

          <div class="dynamic-filters-grid" *ngIf="filtrosDisponibles.length > 0">
            <div *ngFor="let f of filtrosDisponibles" class="filter-field">
              <label class="filter-label">{{ f.label }}</label>
              
              <!-- Date -->
              <input 
                *ngIf="f.type === 'date'"
                type="date" 
                [(ngModel)]="filtrosValores[f.key]"
                class="form-control"
              />

              <!-- Select -->
              <select 
                *ngIf="f.type === 'select'"
                [(ngModel)]="filtrosValores[f.key]"
                class="form-control">
                <option value="">-- Todos los registros --</option>
                <option *ngFor="let opc of f.opciones" [value]="opc">{{ opc }}</option>
              </select>

              <!-- Text -->
              <input 
                *ngIf="f.type === 'text'"
                type="text" 
                [(ngModel)]="filtrosValores[f.key]"
                placeholder="Criterio de búsqueda..."
                class="form-control"
              />
            </div>
          </div>

          <div *ngIf="filtrosDisponibles.length === 0" class="no-filters-msg">
            No se requieren filtros adicionales para esta fuente.
          </div>
        </div>

        <!-- Paso 4: Ordenamiento y Botón de Generación -->
        <div class="config-card full-width order-submit-card">
          <div class="order-controls">
            <div class="step-badge">Paso 4</div>
            <h3 class="card-step-title"><i class="fa-solid fa-arrow-down-a-z"></i> Criterio de Orden</h3>
            <div class="order-inputs">
              <div class="form-group-inline">
                <label>Ordenar por:</label>
                <select [(ngModel)]="columnaOrden" class="form-control">
                  <option value="">-- Por defecto --</option>
                  <option *ngFor="let col of columnasParaOrden()" [value]="col.key">{{ col.label }}</option>
                </select>
              </div>

              <div class="form-group-inline">
                <label>Dirección:</label>
                <select [(ngModel)]="direccionOrden" class="form-control">
                  <option value="ASC">Ascendente (A-Z / Menor a Mayor)</option>
                  <option value="DESC">Descendente (Z-A / Mayor a Menor)</option>
                </select>
              </div>
            </div>
          </div>

          <div class="submit-action">
            <button 
              class="btn-generate-report" 
              [disabled]="generando || columnasSeleccionadas.length === 0"
              (click)="generarReportePersonalizado()">
              <i class="fa-solid" [class.fa-bolt]="!generando" [class.fa-spinner]="generando" [class.fa-spin]="generando"></i>
              <span>{{ generando ? 'Procesando consulta...' : 'Generar Reporte Personalizado' }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Preview & Results Section -->
      <section class="results-section" *ngIf="resultado">
        <!-- Results Header & Export Toolbar -->
        <div class="results-header">
          <div class="results-title-meta">
            <div class="result-badge">
              <i class="fa-solid fa-check-circle"></i> Reporte Generado con Éxito
            </div>
            <h2>Vista Previa del Reporte: {{ getFuenteLabel() }}</h2>
            <p>
              Total de registros recuperados: <strong>{{ resultado.total }}</strong> con <strong>{{ resultado.columnas.length }}</strong> columnas seleccionadas.
            </p>
          </div>

          <!-- Multi-format Export Actions -->
          <div class="export-actions-bar">
            <button class="btn-exp btn-pdf" (click)="exportarPDF()">
              <i class="fa-solid fa-file-pdf"></i> Exportar PDF
            </button>
            <button class="btn-exp btn-excel" (click)="exportarExcel()" title="Descargar libro de Microsoft Excel (.xlsx)">
              <i class="fa-solid fa-file-excel"></i> Exportar Excel (.xlsx)
            </button>
            <button class="btn-exp btn-html" (click)="exportarHTML()">
              <i class="fa-solid fa-code"></i> Exportar HTML
            </button>
            <button class="btn-exp btn-email" (click)="abrirModalEmail()">
              <i class="fa-solid fa-envelope"></i> Enviar por Email
            </button>
            <button class="btn-exp btn-print" (click)="imprimirReporte()">
              <i class="fa-solid fa-print"></i> Imprimir
            </button>
          </div>
        </div>

        <!-- Quick Filter inside results -->
        <div class="quick-filter-row">
          <div class="search-input-wrap">
            <i class="fa-solid fa-magnifying-glass"></i>
            <input 
              type="text" 
              [(ngModel)]="busquedaResultados" 
              placeholder="Buscar dentro de los resultados generados..."
              class="table-search-input"
            />
          </div>
          <span class="records-summary">
            Mostrando {{ datosPaginados().length }} de {{ datosFiltrados().length }} registros
          </span>
        </div>

        <!-- Results Table -->
        <div class="table-container">
          <table class="report-table">
            <thead>
              <tr>
                <th *ngFor="let col of resultado.columnas">
                  {{ col.label }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let fila of datosPaginados()">
                <td *ngFor="let col of resultado.columnas">
                  <ng-container *ngIf="col.key === 'estado'">
                    <span class="badge-status" [ngClass]="'status-' + (fila[col.key] | lowercase)">
                      {{ fila[col.key] }}
                    </span>
                  </ng-container>

                  <ng-container *ngIf="col.key === 'activo' || col.key === 'resuelta'">
                    <span class="badge-status" [ngClass]="fila[col.key] === 'true' || fila[col.key] === true ? 'status-activo' : 'status-inactivo'">
                      {{ (fila[col.key] === 'true' || fila[col.key] === true) ? 'Sí' : 'No' }}
                    </span>
                  </ng-container>

                  <ng-container *ngIf="col.key !== 'estado' && col.key !== 'activo' && col.key !== 'resuelta'">
                    {{ fila[col.key] !== null && fila[col.key] !== undefined ? fila[col.key] : '—' }}
                  </ng-container>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Zero State within results -->
        <div *ngIf="datosFiltrados().length === 0" class="empty-table-state">
          <i class="fa-solid fa-folder-open empty-icon"></i>
          <h4>No se encontraron coincidencias para los criterios seleccionados</h4>
          <p>Prueba ampliando los filtros en el Paso 3 o seleccionando otra fuente de datos.</p>
        </div>

        <!-- Pagination Bar -->
        <div class="pagination-footer" *ngIf="datosFiltrados().length > 0">
          <span class="page-text">Página {{ paginaActual }} de {{ totalPaginas() }}</span>
          <div class="page-buttons">
            <button class="btn-p" [disabled]="paginaActual === 1" (click)="paginaActual = 1"><i class="fa-solid fa-angles-left"></i></button>
            <button class="btn-p" [disabled]="paginaActual === 1" (click)="paginaActual = paginaActual - 1"><i class="fa-solid fa-angle-left"></i></button>
            <span class="current-p">{{ paginaActual }}</span>
            <button class="btn-p" [disabled]="paginaActual >= totalPaginas()" (click)="paginaActual = paginaActual + 1"><i class="fa-solid fa-angle-right"></i></button>
            <button class="btn-p" [disabled]="paginaActual >= totalPaginas()" (click)="paginaActual = totalPaginas()"><i class="fa-solid fa-angles-right"></i></button>
          </div>
        </div>
      </section>

      <!-- Modal Enviar Email -->
      <div class="modal-backdrop" *ngIf="modalEmailAbierto" (click)="modalEmailAbierto = false">
        <div class="modal-content" (click)="$event.stopPropagation()">
          <div class="modal-header">
            <h3><i class="fa-solid fa-envelope"></i> Enviar Reporte Personalizado por Email</h3>
            <button class="btn-close-modal" (click)="modalEmailAbierto = false"><i class="fa-solid fa-xmark"></i></button>
          </div>
          <div class="modal-body">
            <div class="form-group-modal">
              <label>Correo Electrónico Destinatario *</label>
              <input type="email" [(ngModel)]="emailDestino" placeholder="destinatario@correo.com" class="form-control" />
            </div>
            <div class="form-group-modal">
              <label>Asunto</label>
              <input type="text" [(ngModel)]="emailAsunto" class="form-control" />
            </div>
            <div class="info-alert">
              <i class="fa-solid fa-circle-info"></i>
              <span>Se enviará el reporte con <strong>{{ resultado?.total }}</strong> registros y las <strong>{{ columnasSeleccionadas.length }}</strong> columnas seleccionadas.</span>
            </div>
            <div *ngIf="emailMensaje" class="alert-success">{{ emailMensaje }}</div>
            <div *ngIf="emailError" class="alert-error">{{ emailError }}</div>
          </div>
          <div class="modal-footer">
            <button class="btn-clear" (click)="modalEmailAbierto = false">Cerrar</button>
            <button class="btn-apply" [disabled]="enviandoEmail || !emailDestino" (click)="enviarPorCorreo()">
              <i class="fa-solid" [class.fa-paper-plane]="!enviandoEmail" [class.fa-spinner]="enviandoEmail" [class.fa-spin]="enviandoEmail"></i>
              {{ enviandoEmail ? 'Enviando...' : 'Enviar Ahora' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .builder-container {
      max-width: 1300px;
      margin: 0 auto;
    }

    .top-nav {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      gap: 16px;
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
    }

    .step-indicator {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.76rem;
      font-weight: 700;
      color: #65887b;
      flex-wrap: wrap;
    }

    .step-pill {
      padding: 4px 10px;
      background: #ffffff;
      border: 1px solid #dce8e2;
      border-radius: 12px;
    }

    .step-pill.active {
      background: #19734e;
      color: #ffffff;
      border-color: #19734e;
    }

    .step-arrow {
      font-size: 0.65rem;
      color: #b0c7bd;
    }

    /* Builder Header */
    .builder-header {
      background: #ffffff;
      border: 1px solid #dce8e2;
      border-radius: 16px;
      padding: 24px 28px;
      display: flex;
      align-items: center;
      gap: 20px;
      margin-bottom: 24px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }

    .header-icon-box {
      width: 56px;
      height: 56px;
      border-radius: 14px;
      background: linear-gradient(135deg, #19734e 0%, #0f2922 100%);
      color: #2ec486;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.6rem;
      flex-shrink: 0;
      box-shadow: 0 4px 15px rgba(25, 115, 78, 0.2);
    }

    .header-title {
      font-size: 1.55rem;
      font-weight: 800;
      color: #0f2922;
      margin: 0 0 6px 0;
    }

    .header-desc {
      font-size: 0.88rem;
      color: #5c7b6f;
      margin: 0;
      line-height: 1.45;
    }

    /* Config Grid */
    .config-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 30px;
    }

    .config-card {
      background: #ffffff;
      border: 1px solid #dce8e2;
      border-radius: 16px;
      padding: 24px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.02);
      position: relative;
    }

    .config-card.full-width {
      grid-column: 1 / -1;
    }

    .step-badge {
      display: inline-block;
      padding: 3px 10px;
      background: #e8f5ed;
      color: #19734e;
      border-radius: 6px;
      font-size: 0.72rem;
      font-weight: 800;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      margin-bottom: 8px;
    }

    .card-step-title {
      font-size: 1.15rem;
      font-weight: 700;
      color: #12271f;
      margin: 0 0 4px 0;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .card-step-desc {
      font-size: 0.84rem;
      color: #638577;
      margin: 0 0 16px 0;
    }

    .card-step-header-flex {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 8px;
    }

    .quick-links {
      display: flex;
      gap: 10px;
    }

    .btn-link {
      background: transparent;
      border: none;
      color: #19734e;
      font-weight: 700;
      font-size: 0.78rem;
      cursor: pointer;
      text-decoration: underline;
      padding: 0;
    }

    .form-control-large {
      width: 100%;
      padding: 12px 16px;
      border: 1px solid #cde0d7;
      border-radius: 10px;
      font-size: 0.95rem;
      font-weight: 600;
      color: #12271f;
      background: #fdfefe;
      outline: none;
      transition: border 0.2s;
    }

    .form-control-large:focus {
      border-color: #19734e;
    }

    .column-checkboxes-box {
      max-height: 200px;
      overflow-y: auto;
      border: 1px solid #e2ede7;
      border-radius: 10px;
      padding: 12px;
      background: #fbfdfc;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      margin-bottom: 8px;
    }

    .checkbox-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.84rem;
      color: #244136;
      cursor: pointer;
      user-select: none;
    }

    .selection-count {
      font-size: 0.76rem;
      color: #799a8d;
      font-weight: 600;
    }

    /* Dynamic Filters Grid */
    .dynamic-filters-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
      gap: 16px;
    }

    .filter-field {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .filter-label {
      font-size: 0.78rem;
      font-weight: 700;
      color: #48665b;
      text-transform: uppercase;
    }

    .form-control {
      padding: 9px 12px;
      border: 1px solid #cfded6;
      border-radius: 8px;
      font-size: 0.88rem;
      color: #12271f;
      outline: none;
      background: #fcfdfc;
    }

    .form-control:focus {
      border-color: #19734e;
      background: #ffffff;
    }

    .no-filters-msg {
      font-size: 0.86rem;
      color: #799a8d;
      font-style: italic;
    }

    /* Order & Submit Card */
    .order-submit-card {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 24px;
      flex-wrap: wrap;
    }

    .order-controls {
      flex: 1;
      min-width: 320px;
    }

    .order-inputs {
      display: flex;
      gap: 16px;
      margin-top: 10px;
      flex-wrap: wrap;
    }

    .form-group-inline {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.84rem;
      color: #3b5a4e;
      font-weight: 600;
    }

    .btn-generate-report {
      padding: 14px 28px;
      background: linear-gradient(135deg, #19734e 0%, #0f2922 100%);
      color: #ffffff;
      border: none;
      border-radius: 12px;
      font-weight: 800;
      font-size: 0.95rem;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 10px;
      box-shadow: 0 6px 20px rgba(25, 115, 78, 0.28);
      transition: all 0.2s ease;
    }

    .btn-generate-report:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(25, 115, 78, 0.4);
      background: linear-gradient(135deg, #228b60 0%, #153c30 100%);
    }

    .btn-generate-report:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    /* Results Section */
    .results-section {
      background: #ffffff;
      border: 1px solid #dce8e2;
      border-radius: 18px;
      padding: 26px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.03);
      margin-bottom: 40px;
    }

    .results-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 20px;
      margin-bottom: 20px;
      flex-wrap: wrap;
    }

    .result-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      background: #dcfce7;
      color: #15803d;
      border-radius: 6px;
      font-size: 0.74rem;
      font-weight: 800;
      margin-bottom: 6px;
    }

    .results-title-meta h2 {
      font-size: 1.4rem;
      font-weight: 800;
      color: #0f2922;
      margin: 0 0 4px 0;
    }

    .results-title-meta p {
      font-size: 0.88rem;
      color: #5c7b6f;
      margin: 0;
    }

    .export-actions-bar {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }

    .btn-exp {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 9px 14px;
      border: none;
      border-radius: 8px;
      font-size: 0.82rem;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .btn-pdf { background: #fee2e2; color: #991b1b; }
    .btn-pdf:hover { background: #fecaca; }

    .btn-excel { background: #dcfce7; color: #166534; }
    .btn-excel:hover { background: #bbf7d0; }

    .btn-html { background: #fef3c7; color: #92400e; }
    .btn-html:hover { background: #fde68a; }

    .btn-email { background: #e0f2fe; color: #075985; }
    .btn-email:hover { background: #bae6fd; }

    .btn-print { background: #f1f5f9; color: #334155; }
    .btn-print:hover { background: #e2e8f0; }

    .quick-filter-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      gap: 16px;
      flex-wrap: wrap;
    }

    .search-input-wrap {
      display: flex;
      align-items: center;
      gap: 8px;
      background: #f7faf8;
      border: 1px solid #dce8e2;
      padding: 7px 14px;
      border-radius: 8px;
      width: 320px;
    }

    .search-input-wrap i {
      color: #8da89d;
    }

    .table-search-input {
      border: none;
      background: transparent;
      outline: none;
      width: 100%;
      font-size: 0.85rem;
    }

    .records-summary {
      font-size: 0.82rem;
      color: #648477;
    }

    /* Table */
    .table-container {
      overflow-x: auto;
      border: 1px solid #e5eee8;
      border-radius: 12px;
      margin-bottom: 16px;
    }

    .report-table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
    }

    .report-table th {
      background: #19734e;
      color: #ffffff;
      padding: 12px 16px;
      font-size: 0.82rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      white-space: nowrap;
    }

    .report-table td {
      padding: 11px 16px;
      font-size: 0.86rem;
      color: #1f3b30;
      border-bottom: 1px solid #edf4f0;
      white-space: nowrap;
    }

    .report-table tbody tr:hover {
      background: #f4faf7;
    }

    .badge-status {
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 0.74rem;
      font-weight: 700;
      text-transform: uppercase;
    }

    .status-programada { background: #e0f2fe; color: #0369a1; }
    .status-confirmada { background: #fef3c7; color: #b45309; }
    .status-realizada { background: #dcfce7; color: #15803d; }
    .status-cancelada { background: #fee2e2; color: #b91c1c; }
    .status-inasistencia { background: #f3e8ff; color: #7e22ce; }
    .status-activo { background: #dcfce7; color: #15803d; }
    .status-inactivo { background: #fee2e2; color: #b91c1c; }

    .empty-table-state {
      padding: 50px 20px;
      text-align: center;
    }

    .empty-icon {
      font-size: 2.8rem;
      color: #a8c7ba;
      margin-bottom: 10px;
    }

    .pagination-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 8px;
    }

    .page-text {
      font-size: 0.82rem;
      color: #648477;
    }

    .page-buttons {
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .btn-p {
      width: 32px;
      height: 32px;
      border: 1px solid #dce8e2;
      background: #ffffff;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.78rem;
      cursor: pointer;
    }

    .btn-p:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }

    .current-p {
      font-weight: 700;
      font-size: 0.85rem;
      color: #19734e;
      padding: 0 8px;
    }

    /* Modal */
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
    }

    .modal-content {
      background: #ffffff;
      border-radius: 18px;
      width: 100%;
      max-width: 500px;
      box-shadow: 0 20px 50px rgba(0,0,0,0.25);
      overflow: hidden;
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
      margin: 0;
      font-size: 1.05rem;
      font-weight: 800;
      color: #12271f;
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
    }

    .form-group-modal {
      margin-bottom: 16px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .form-group-modal label {
      font-size: 0.78rem;
      font-weight: 700;
      color: #48665b;
      text-transform: uppercase;
    }

    .info-alert {
      padding: 12px;
      background: #eaf4ee;
      border-radius: 8px;
      font-size: 0.82rem;
      color: #1e4b37;
      display: flex;
      gap: 8px;
      align-items: flex-start;
    }

    .modal-footer {
      padding: 16px 24px;
      background: #f7faf8;
      border-top: 1px solid #eef4f1;
      display: flex;
      justify-content: flex-end;
      gap: 10px;
    }

    .btn-clear {
      padding: 7px 14px;
      background: #f1f5f3;
      border: 1px solid #d4e2db;
      border-radius: 8px;
      font-weight: 600;
      font-size: 0.82rem;
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

    .alert-success {
      margin-top: 10px;
      padding: 8px;
      background: #dcfce7;
      color: #15803d;
      border-radius: 6px;
      font-size: 0.82rem;
      font-weight: 600;
    }

    .alert-error {
      margin-top: 10px;
      padding: 8px;
      background: #fee2e2;
      color: #b91c1c;
      border-radius: 6px;
      font-size: 0.82rem;
      font-weight: 600;
    }

    @media (max-width: 800px) {
      .config-grid {
        grid-template-columns: 1fr;
      }
      .column-checkboxes-box {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class ReportePersonalizadoComponent implements OnInit {
  fuenteSeleccionada = 'citas';
  metadataFuentes: Record<string, FuenteMetadata> = {};

  columnasDisponibles: ColumnaDef[] = [];
  columnasSeleccionadas: string[] = [];

  filtrosDisponibles: FiltroDef[] = [];
  filtrosValores: Record<string, any> = {};

  columnaOrden = '';
  direccionOrden = 'ASC';

  generando = false;
  resultado: ReporteResultado | null = null;
  busquedaResultados = '';

  // Pagination
  paginaActual = 1;
  tamanoPagina = 25;

  // Modal Email
  modalEmailAbierto = false;
  emailDestino = '';
  emailAsunto = '';
  enviandoEmail = false;
  emailMensaje = '';
  emailError = '';

  constructor(
    private reportService: ReportService,
    public authService: AuthService
  ) {}

  ngOnInit(): void {
    this.cargarMetadata();
  }

  cargarMetadata(): void {
    this.reportService.getMetadata().subscribe({
      next: (meta) => {
        this.metadataFuentes = meta;
        this.actualizarConfiguracionFuente();
      },
      error: (err) => console.error('Error cargando metadata:', err)
    });
  }

  onFuenteCambiada(): void {
    this.filtrosValores = {};
    this.columnaOrden = '';
    this.resultado = null;
    this.actualizarConfiguracionFuente();
  }

  actualizarConfiguracionFuente(): void {
    const fMeta = this.metadataFuentes[this.fuenteSeleccionada];
    if (fMeta) {
      this.columnasDisponibles = fMeta.columnas;
      this.filtrosDisponibles = fMeta.filtros;
      // Por defecto seleccionar todas
      this.columnasSeleccionadas = fMeta.columnas.map(c => c.key);
      this.emailAsunto = `SIGEPSI — Reporte Personalizado de ${fMeta.label}`;
    }
  }

  toggleColumna(key: string): void {
    if (this.columnasSeleccionadas.includes(key)) {
      if (this.columnasSeleccionadas.length > 1) {
        this.columnasSeleccionadas = this.columnasSeleccionadas.filter(k => k !== key);
      }
    } else {
      this.columnasSeleccionadas.push(key);
    }
  }

  seleccionarTodasColumnas(marcar: boolean): void {
    if (marcar) {
      this.columnasSeleccionadas = this.columnasDisponibles.map(c => c.key);
    } else {
      // Dejar la primera seleccionada
      this.columnasSeleccionadas = [this.columnasDisponibles[0].key];
    }
  }

  columnasParaOrden(): ColumnaDef[] {
    return this.columnasDisponibles.filter(c => this.columnasSeleccionadas.includes(c.key));
  }

  generarReportePersonalizado(): void {
    this.generando = true;
    const orden = this.columnaOrden ? { columna: this.columnaOrden, direccion: this.direccionOrden } : undefined;

    this.reportService.generarPersonalizado({
      fuente: this.fuenteSeleccionada,
      columnas: this.columnasSeleccionadas,
      filtros: this.filtrosValores,
      orden: orden
    }).subscribe({
      next: (res) => {
        this.resultado = res;
        this.generando = false;
        this.paginaActual = 1;
      },
      error: (err) => {
        console.error('Error generando reporte personalizado:', err);
        this.generando = false;
      }
    });
  }

  getFuenteLabel(): string {
    return this.metadataFuentes[this.fuenteSeleccionada]?.label || this.fuenteSeleccionada;
  }

  // Table filtering & pagination
  datosFiltrados = computed(() => {
    if (!this.resultado || !this.resultado.datos) return [];
    const q = this.busquedaResultados.toLowerCase().trim();
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
    const start = (this.paginaActual - 1) * this.tamanoPagina;
    return todos.slice(start, start + this.tamanoPagina);
  });

  // Exportaciones
  exportarPDF(): void {
    if (!this.resultado) return;
    const currentTenant = this.authService.currentTenant()?.nombre;
    const currentUser = this.authService.currentUser()?.nombre || 'Administrador Clínico';
    const res = {
      ...this.resultado,
      datos: this.datosFiltrados(),
      total: this.datosFiltrados().length
    };
    this.reportService.exportToPDF(res, `Reporte Personalizado - ${this.getFuenteLabel()}`, currentTenant, currentUser);
  }

  exportarExcel(): void {
    if (!this.resultado) return;
    const currentTenant = this.authService.currentTenant()?.nombre;
    const currentUser = this.authService.currentUser()?.nombre || 'Administrador Clínico';
    const res = {
      ...this.resultado,
      datos: this.datosFiltrados(),
      total: this.datosFiltrados().length
    };
    this.reportService.exportToExcel(res, `reporte_personalizado_${this.fuenteSeleccionada}`, currentTenant, currentUser);
  }

  exportarHTML(): void {
    if (!this.resultado) return;
    const currentTenant = this.authService.currentTenant()?.nombre;
    const res = {
      ...this.resultado,
      datos: this.datosFiltrados(),
      total: this.datosFiltrados().length
    };
    this.reportService.exportToHTML(res, `Reporte Personalizado - ${this.getFuenteLabel()}`, currentTenant);
  }

  imprimirReporte(): void {
    if (!this.resultado) return;
    const res = {
      ...this.resultado,
      datos: this.datosFiltrados(),
      total: this.datosFiltrados().length
    };
    this.reportService.printReport(res, `Reporte Personalizado - ${this.getFuenteLabel()}`);
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
      fuente: this.fuenteSeleccionada,
      asunto: this.emailAsunto,
      filtros: this.filtrosValores,
      columnas: this.columnasSeleccionadas
    }).subscribe({
      next: (res) => {
        this.enviandoEmail = false;
        this.emailMensaje = res.mensaje || 'Reporte enviado exitosamente.';
        setTimeout(() => {
          this.modalEmailAbierto = false;
        }, 2000);
      },
      error: (err) => {
        this.enviandoEmail = false;
        this.emailError = err.error?.error || 'Error enviando el reporte.';
      }
    });
  }
}
