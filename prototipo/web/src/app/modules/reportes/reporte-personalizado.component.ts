import { Component, OnInit, OnDestroy, signal, computed, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';
import { ReportService, ColumnaDef, FiltroDef, ReporteResultado, FuenteMetadata } from '../../core/services/report.service';
import { SpeechParserService, ExtractedVoiceParams } from '../../core/services/speech-parser.service';
import { AuthService } from '../../core/services/auth.service';

/**
 * IU_ConstructorReportesQBE & IU_VisorReporteExportador
 * Cumple con Caso de Uso HU-38 (CU25) y los Diagramas de Secuencia y Comunicación:
 * - Modalidad 1: Comandos de Voz con Web Speech API y NLP
 * - Modalidad 2: Constructor QBE (Query By Example) con selección dinámica de columnas
 * - Modalidad 3: Estándar
 * - Exportación multiformato directa a Excel (.xlsx con OpenPyXL) y SMTP Email
 */
@Component({
  selector: 'app-reporte-personalizado',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  template: `
    <div class="builder-container IU_ConstructorReportesQBE">
      <!-- Breadcrumb Bar -->
      <div class="top-nav">
        <a routerLink="/reportes" class="btn-back">
          <i class="fa-solid fa-arrow-left"></i> Volver al Centro de Reportes
        </a>
        <div class="modality-selector">
          <button 
            type="button" 
            class="modality-btn" 
            [class.active]="modalidadActiva === 'voz'"
            (click)="setModalidad('voz')">
            <i class="fa-solid fa-microphone-lines"></i> Comandos de Voz
          </button>
          <button 
            type="button" 
            class="modality-btn" 
            [class.active]="modalidadActiva === 'qbe'"
            (click)="setModalidad('qbe')">
            <i class="fa-solid fa-filter-circle-dollar"></i> Constructor QBE
          </button>
          <button 
            type="button" 
            class="modality-btn" 
            [class.active]="modalidadActiva === 'estandar'"
            (click)="setModalidad('estandar')">
            <i class="fa-solid fa-table-list"></i> Estándar
          </button>
        </div>
      </div>

      <!-- Main Header -->
      <div class="builder-header">
        <div class="header-icon-box">
          <i class="fa-solid fa-wand-magic-sparkles"></i>
        </div>
        <div>
          <div class="header-tag">HU-38 (CU25) • Generador de Reportes QBE Multiformato</div>
          <h1 class="header-title">Generador de Reportes Personalizados</h1>
          <p class="header-desc">
            Construye reportes a medida seleccionando columnas, aplicando filtros dinámicos (QBE) o mediante comandos de voz en tiempo real con Web Speech API, y exporta a Excel (.xlsx con OpenPyXL), CSV o eMail.
          </p>
        </div>
      </div>

      <!-- SECCIÓN RECONOCIMIENTO DE VOZ (Paso 1 BDD) -->
      <section class="voice-module-card" [class.highlighted]="modalidadActiva === 'voz'">
        <div class="voice-header-flex">
          <div class="voice-badge">
            <i class="fa-solid fa-microphone"></i> Reconocimiento de Voz (Web Speech API)
          </div>
          <div class="speech-status-indicator" [class.listening]="isListening">
            <span class="status-dot"></span>
            {{ isListening ? 'Escuchando audio en tiempo real...' : 'Micrófono en espera' }}
          </div>
        </div>

        <div class="voice-main-actions">
          <!-- Botón de micrófono 'Dictar por Voz' (Paso 1 de la prueba) -->
          <button 
            type="button" 
            class="btn-voice-dictate" 
            [class.is-recording]="isListening"
            (click)="presionar_boton_microfono()">
            <div class="mic-wave" *ngIf="isListening"></div>
            <i class="fa-solid" [class.fa-microphone]="!isListening" [class.fa-stop]="isListening"></i>
            <span>{{ isListening ? 'Detener Dictado' : 'Dictar por Voz' }}</span>
          </button>

          <div class="voice-transcription-box">
            <div class="transcript-label">Transcripción capturada:</div>
            <div class="transcript-content" [class.has-text]="liveTranscript">
              {{ liveTranscript || 'Presiona "Dictar por Voz" y di por ejemplo: "Reporte de citas del mes de septiembre" o "Citas de Carlos en septiembre"...' }}
            </div>
          </div>
        </div>

        <!-- Chips de prueba rápida para simulación de voz -->
        <div class="voice-test-prompts">
          <span class="test-prompts-label">Prueba rápida BDD:</span>
          <button 
            type="button" 
            class="chip-prompt" 
            (click)="simularComando('Reporte de citas del mes de septiembre')">
            <i class="fa-solid fa-play"></i> "Reporte de citas del mes de septiembre"
          </button>
          <button 
            type="button" 
            class="chip-prompt" 
            (click)="simularComando('Citas de Carlos en septiembre')">
            <i class="fa-solid fa-play"></i> "Citas de Carlos en septiembre"
          </button>
          <button 
            type="button" 
            class="chip-prompt" 
            (click)="simularComando('Reporte de citas realizadas de modalidad presencial')">
            <i class="fa-solid fa-play"></i> "Citas realizadas en modalidad presencial"
          </button>
        </div>

        <!-- Feedback de Parámetros extraídos por el Parser NLP -->
        <div class="voice-extracted-feedback" *ngIf="ultimoParametrosExtraidos">
          <div class="feedback-badge"><i class="fa-solid fa-check"></i> Parámetros Extraídos (CTR_SpeechParserService):</div>
          <div class="extracted-tags">
            <span class="tag-extracted" *ngIf="ultimoParametrosExtraidos.fuente">
              <strong>Entidad:</strong> {{ ultimoParametrosExtraidos.fuente }}
            </span>
            <span class="tag-extracted" *ngIf="ultimoParametrosExtraidos.mes">
              <strong>Mes:</strong> {{ ultimoParametrosExtraidos.mes }}
            </span>
            <span class="tag-extracted" *ngIf="ultimoParametrosExtraidos.psicologo">
              <strong>Psicólogo:</strong> {{ ultimoParametrosExtraidos.psicologo }}
            </span>
            <span class="tag-extracted" *ngIf="ultimoParametrosExtraidos.estado">
              <strong>Estado:</strong> {{ ultimoParametrosExtraidos.estado }}
            </span>
            <span class="tag-extracted" *ngIf="ultimoParametrosExtraidos.modalidad">
              <strong>Modalidad:</strong> {{ ultimoParametrosExtraidos.modalidad }}
            </span>
          </div>
          <p class="feedback-note">
            ✓ Filtros QBE actualizados y columnas configuradas automáticamente según el dictado de voz.
          </p>
        </div>

        <div *ngIf="voiceError" class="voice-error-msg">
          <i class="fa-solid fa-triangle-exclamation"></i> {{ voiceError }}
        </div>
      </section>

      <!-- Configuration Grid / Steps Form -->
      <div class="config-grid">
        <!-- Paso 1: Fuente de Datos -->
        <div class="config-card">
          <div class="step-badge">Paso 1</div>
          <h3 class="card-step-title"><i class="fa-solid fa-database"></i> Entidad / Fuente de Información</h3>
          <p class="card-step-desc">Selecciona la entidad base para el reporte:</p>
          
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
          <div *ngIf="fuenteSeleccionada === 'bitacora'" class="filter-field">
            <label for="custom-audit-key">Clave de desarrollador</label>
            <input id="custom-audit-key" type="password" autocomplete="off" [(ngModel)]="developerKey" (ngModelChange)="keyChanged()">
            <p *ngIf="accessError" role="alert">{{ accessError }}</p>
            <button type="button" class="btn-clear" (click)="lockAudit()">Bloquear</button>
          </div>
        </div>

        <!-- Paso 2: Selección de Columnas (Paso 2 BDD) -->
        <div class="config-card">
          <div class="step-badge">Paso 2</div>
          <div class="card-step-header-flex">
            <div>
              <h3 class="card-step-title"><i class="fa-solid fa-table-columns"></i> Columnas a Mostrar (Proyección)</h3>
              <p class="card-step-desc">Marca las columnas visibles para proyectar en el reporte:</p>
            </div>
            <div class="quick-links">
              <button type="button" class="btn-preset-5" (click)="seleccionar5ColumnasBDD()" title="Seleccionar las 5 columnas de la prueba BDD">
                <i class="fa-solid fa-star"></i> 5 Columnas BDD
              </button>
              <button type="button" class="btn-link" (click)="seleccionarTodasColumnas(true)">Todas</button>
              <button type="button" class="btn-link" (click)="seleccionarTodasColumnas(false)">Limpiar</button>
            </div>
          </div>

          <div class="column-checkboxes-box">
            <label *ngFor="let col of columnasDisponibles" class="checkbox-item" [class.selected]="columnasSeleccionadas.includes(col.key)">
              <input 
                type="checkbox" 
                [checked]="columnasSeleccionadas.includes(col.key)"
                (change)="toggleColumna(col.key)"
              />
              <span class="checkbox-text">{{ col.label }}</span>
            </label>
          </div>
          <div class="selection-footer-info">
            <span class="selection-count">
              <strong>{{ columnasSeleccionadas.length }}</strong> de {{ columnasDisponibles.length }} columnas seleccionadas
            </span>
            <span class="bdd-indicator" *ngIf="is5ColumnasSeleccionadas()">
              ✓ 5 columnas solicitadas en BDD ('Fecha', 'Psicólogo', 'Paciente', 'Estado', 'Modalidad')
            </span>
          </div>
        </div>

        <!-- Paso 3: Criterios de Selección y Filtros Dinámicos (QBE) -->
        <div class="config-card full-width">
          <div class="step-badge">Paso 3</div>
          <div class="card-step-header-flex">
            <div>
              <h3 class="card-step-title"><i class="fa-solid fa-filter"></i> Criterios de Selección (Filtros Dinámicos QBE)</h3>
              <p class="card-step-desc">Filtros aplicados automáticamente por voz o configurables manualmente:</p>
            </div>
            <button type="button" class="btn-link text-danger" (click)="limpiarFiltros()">
              <i class="fa-solid fa-rotate-left"></i> Limpiar Filtros
            </button>
          </div>

          <div class="dynamic-filters-grid" *ngIf="filtrosDisponibles.length > 0">
            <div *ngFor="let f of filtrosDisponibles" class="filter-field">
              <label class="filter-label">
                {{ f.label }}
                <span *ngIf="filtrosValores[f.key]" class="filter-applied-badge">✓ Activo</span>
              </label>
              
              <!-- Date -->
              <input 
                *ngIf="f.type === 'date'"
                type="date" 
                [(ngModel)]="filtrosValores[f.key]"
                (change)="onFiltroCambiado()"
                class="form-control"
              />

              <!-- Select -->
              <select 
                *ngIf="f.type === 'select'"
                [(ngModel)]="filtrosValores[f.key]"
                (change)="onFiltroCambiado()"
                class="form-control">
                <option value="">-- Todos los registros --</option>
                <option *ngFor="let opc of f.opciones" [value]="opc">{{ opc }}</option>
              </select>

              <!-- Text -->
              <input 
                *ngIf="f.type === 'text'"
                type="text" 
                [(ngModel)]="filtrosValores[f.key]"
                (input)="onFiltroCambiado()"
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
              type="button"
              class="btn-generate-report" 
              [disabled]="generando || columnasSeleccionadas.length === 0"
              (click)="generarReportePersonalizado()">
              <i class="fa-solid" [class.fa-bolt]="!generando" [class.fa-spinner]="generando" [class.fa-spin]="generando"></i>
              <span>{{ generando ? 'Procesando consulta...' : 'Generar Vista Previa QBE' }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- VISOR Y EXPORTADOR DEL REPORTE (IU_VisorReporteExportador - Paso 2 y 3 BDD) -->
      <section class="results-section IU_VisorReporteExportador" *ngIf="resultado">
        <!-- Results Header & Export Toolbar -->
        <div class="results-header">
          <div class="results-title-meta">
            <div class="result-badge">
              <i class="fa-solid fa-check-circle"></i> Vista Previa Interactiva Generada
            </div>
            <h2>Vista Previa del Reporte: {{ getFuenteLabel() }}</h2>
            <p>
              Desplegando únicamente las <strong>{{ getColumnasActivas().length }}</strong> columnas seleccionadas | Total de registros: <strong>{{ resultado.total }}</strong>.
            </p>
          </div>

          <!-- Multi-format Export Actions (Paso 3 de la prueba) -->
          <div class="export-actions-bar">
            <!-- Botón obligatorio según BDD Paso 3: 'Descargar Excel (.xlsx)' -->
            <button 
              type="button" 
              class="btn-exp btn-excel-download" 
              [disabled]="descargandoExcel"
              (click)="descargarExcelOpenPyXL()" 
              title="Descargar archivo binario .xlsx con estilos corporativos OpenPyXL y cabecera del centro">
              <i class="fa-solid" [class.fa-file-excel]="!descargandoExcel" [class.fa-spinner]="descargandoExcel" [class.fa-spin]="descargandoExcel"></i>
              <span>{{ descargandoExcel ? 'Generando .xlsx...' : 'Descargar Excel (.xlsx)' }}</span>
            </button>

            <!-- Exportar a CSV plano -->
            <button type="button" class="btn-exp btn-csv" (click)="exportarCSVServer()" title="Descargar archivo CSV plano">
              <i class="fa-solid fa-file-csv"></i> CSV Plano
            </button>

            <!-- Enviar por correo SMTP -->
            <button type="button" class="btn-exp btn-email" (click)="abrirModalEmail()" title="Enviar reporte formal por correo electrónico SMTP">
              <i class="fa-solid fa-envelope"></i> Correo SMTP
            </button>

            <!-- Exportar PDF -->
            <button type="button" class="btn-exp btn-pdf" (click)="exportarPDF()">
              <i class="fa-solid fa-file-pdf"></i> PDF
            </button>

            <!-- Imprimir -->
            <button type="button" class="btn-exp btn-print" (click)="imprimirReporte()">
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
              placeholder="Buscar dentro de los registros proyectados..."
              class="table-search-input"
            />
          </div>
          <span class="records-summary">
            Mostrando {{ datosPaginados().length }} de {{ datosFiltrados().length }} registros
          </span>
        </div>

        <!-- Results Table (Paso 2 BDD: Vista previa con proyección exclusiva) -->
        <div class="table-container">
          <table class="report-table">
            <thead>
              <tr>
                <th *ngFor="let col of getColumnasActivas()">
                  {{ col.label }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let fila of datosPaginados()">
                <td *ngFor="let col of getColumnasActivas()">
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
          <i class="fa-solid fa-box-open empty-icon"></i>
          <h4>No se encontraron registros para los criterios seleccionados</h4>
          <p>Intenta ajustar los filtros de fecha, psicólogo o estado en el constructor QBE.</p>
        </div>

        <!-- Pagination -->
        <div class="pagination-footer" *ngIf="datosFiltrados().length > 0">
          <span class="page-text">Página {{ paginaActual }} de {{ totalPaginas() }}</span>
          <div class="page-buttons">
            <button class="btn-p" [disabled]="paginaActual === 1" (click)="paginaActual = paginaActual - 1">
              <i class="fa-solid fa-chevron-left"></i>
            </button>
            <span class="current-p">{{ paginaActual }}</span>
            <button class="btn-p" [disabled]="paginaActual >= totalPaginas()" (click)="paginaActual = paginaActual + 1">
              <i class="fa-solid fa-chevron-right"></i>
            </button>
          </div>
        </div>
      </section>

      <!-- Modal de Envío por Correo Electrónico (SMTP) -->
      <div class="modal-backdrop" *ngIf="modalEmailAbierto">
        <div class="modal-content modal_confirmacion_envio_correo">
          <div class="modal-header">
            <h3><i class="fa-solid fa-envelope-circle-check"></i> Enviar Reporte por Correo (SMTP)</h3>
            <button type="button" class="btn-close-modal" (click)="modalEmailAbierto = false">&times;</button>
          </div>
          <div class="modal-body">
            <div class="form-group-modal">
              <label>Correo Electrónico Destino *</label>
              <input type="email" [(ngModel)]="emailDestino" placeholder="admin@centro.com" class="form-control" />
            </div>
            <div class="form-group-modal">
              <label>Asunto del Mensaje</label>
              <input type="text" [(ngModel)]="emailAsunto" class="form-control" />
            </div>
            <div class="info-alert">
              <i class="fa-solid fa-circle-info"></i>
              <span>Se enviará el reporte con <strong>{{ resultado?.total }}</strong> registros y las <strong>{{ getColumnasActivas().length }}</strong> columnas seleccionadas mediante el servidor SMTP del centro.</span>
            </div>
            <div *ngIf="emailMensaje" class="alert-success">{{ emailMensaje }}</div>
            <div *ngIf="emailError" class="alert-error">{{ emailError }}</div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-clear" (click)="modalEmailAbierto = false">Cancelar</button>
            <button type="button" class="btn-apply" [disabled]="enviandoEmail || !emailDestino" (click)="enviarPorCorreoSMTP()">
              <i class="fa-solid" [class.fa-paper-plane]="!enviandoEmail" [class.fa-spinner]="enviandoEmail" [class.fa-spin]="enviandoEmail"></i>
              {{ enviandoEmail ? 'Enviando...' : 'Confirmar y Enviar' }}
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

    .modality-selector {
      display: flex;
      background: #ffffff;
      padding: 4px;
      border: 1px solid #dce8e2;
      border-radius: 12px;
      gap: 4px;
    }

    .modality-btn {
      padding: 6px 14px;
      border: none;
      background: transparent;
      border-radius: 8px;
      font-size: 0.82rem;
      font-weight: 700;
      color: #527568;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }

    .modality-btn.active {
      background: #19734e;
      color: #ffffff;
      box-shadow: 0 2px 6px rgba(25, 115, 78, 0.25);
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

    .header-tag {
      font-size: 0.72rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: #19734e;
      background: #e8f5ed;
      display: inline-block;
      padding: 2px 8px;
      border-radius: 6px;
      margin-bottom: 6px;
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

    /* Voice Module Card */
    .voice-module-card {
      background: linear-gradient(145deg, #ffffff 0%, #f7fbf9 100%);
      border: 2px solid #b7dfce;
      border-radius: 16px;
      padding: 22px 26px;
      margin-bottom: 24px;
      box-shadow: 0 4px 14px rgba(25, 115, 78, 0.08);
      position: relative;
      transition: all 0.3s ease;
    }

    .voice-module-card.highlighted {
      border-color: #19734e;
      box-shadow: 0 6px 20px rgba(25, 115, 78, 0.15);
    }

    .voice-header-flex {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      flex-wrap: wrap;
      gap: 10px;
    }

    .voice-badge {
      font-size: 0.82rem;
      font-weight: 800;
      color: #19734e;
      background: #e6f6ee;
      padding: 4px 12px;
      border-radius: 20px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }

    .speech-status-indicator {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 0.8rem;
      font-weight: 700;
      color: #6a8c7f;
    }

    .speech-status-indicator.listening {
      color: #dc2626;
    }

    .status-dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: #a3c2b4;
    }

    .speech-status-indicator.listening .status-dot {
      background: #dc2626;
      animation: pulse 1.2s infinite;
    }

    @keyframes pulse {
      0% { transform: scale(0.9); opacity: 0.8; }
      50% { transform: scale(1.4); opacity: 1; }
      100% { transform: scale(0.9); opacity: 0.8; }
    }

    .voice-main-actions {
      display: flex;
      align-items: center;
      gap: 20px;
      margin-bottom: 16px;
      flex-wrap: wrap;
    }

    .btn-voice-dictate {
      position: relative;
      padding: 14px 24px;
      background: linear-gradient(135deg, #19734e 0%, #115337 100%);
      color: #ffffff;
      border: none;
      border-radius: 12px;
      font-size: 0.95rem;
      font-weight: 800;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 10px;
      box-shadow: 0 4px 12px rgba(25, 115, 78, 0.3);
      transition: all 0.25s ease;
      overflow: hidden;
      flex-shrink: 0;
    }

    .btn-voice-dictate:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 18px rgba(25, 115, 78, 0.4);
    }

    .btn-voice-dictate.is-recording {
      background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
      box-shadow: 0 4px 14px rgba(220, 38, 38, 0.4);
    }

    .voice-transcription-box {
      flex: 1;
      min-width: 280px;
      background: #ffffff;
      border: 1px solid #cce2d7;
      border-radius: 12px;
      padding: 10px 16px;
    }

    .transcript-label {
      font-size: 0.72rem;
      font-weight: 800;
      color: #6e9485;
      text-transform: uppercase;
      margin-bottom: 4px;
    }

    .transcript-content {
      font-size: 0.9rem;
      color: #8da69b;
      font-style: italic;
    }

    .transcript-content.has-text {
      color: #0f2922;
      font-weight: 700;
      font-style: normal;
    }

    .voice-test-prompts {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 12px;
    }

    .test-prompts-label {
      font-size: 0.76rem;
      font-weight: 700;
      color: #55796c;
    }

    .chip-prompt {
      background: #ffffff;
      border: 1px solid #d3e5dc;
      color: #19734e;
      padding: 5px 12px;
      border-radius: 20px;
      font-size: 0.78rem;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s;
    }

    .chip-prompt:hover {
      background: #e8f5ed;
      border-color: #19734e;
    }

    .voice-extracted-feedback {
      background: #f0fdf4;
      border: 1px solid #86efac;
      border-radius: 10px;
      padding: 12px 16px;
      margin-top: 10px;
    }

    .feedback-badge {
      font-size: 0.78rem;
      font-weight: 800;
      color: #166534;
      margin-bottom: 8px;
    }

    .extracted-tags {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 6px;
    }

    .tag-extracted {
      background: #ffffff;
      border: 1px solid #bbf7d0;
      padding: 3px 10px;
      border-radius: 8px;
      font-size: 0.78rem;
      color: #15803d;
    }

    .feedback-note {
      font-size: 0.78rem;
      color: #166534;
      margin: 0;
      font-weight: 600;
    }

    .voice-error-msg {
      background: #fee2e2;
      color: #b91c1c;
      padding: 8px 12px;
      border-radius: 8px;
      font-size: 0.82rem;
      margin-top: 10px;
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
      font-weight: 800;
      color: #0f2922;
      margin: 0 0 6px 0;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .card-step-desc {
      font-size: 0.84rem;
      color: #648477;
      margin: 0 0 16px 0;
    }

    .card-step-header-flex {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;
      flex-wrap: wrap;
      gap: 10px;
    }

    .form-control-large {
      width: 100%;
      padding: 12px 14px;
      border: 1px solid #c9ded3;
      border-radius: 10px;
      font-size: 0.95rem;
      font-weight: 600;
      color: #14352a;
      background: #fdfefe;
    }

    .quick-links {
      display: flex;
      gap: 8px;
      align-items: center;
    }

    .btn-link {
      background: none;
      border: none;
      color: #19734e;
      font-weight: 700;
      font-size: 0.8rem;
      cursor: pointer;
      text-decoration: underline;
      padding: 0;
    }

    .btn-preset-5 {
      background: #e8f5ed;
      border: 1px solid #19734e;
      color: #19734e;
      border-radius: 8px;
      padding: 4px 10px;
      font-weight: 800;
      font-size: 0.78rem;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }

    .btn-preset-5:hover {
      background: #19734e;
      color: #ffffff;
    }

    .column-checkboxes-box {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      max-height: 240px;
      overflow-y: auto;
      border: 1px solid #e1ece6;
      border-radius: 10px;
      padding: 12px;
      background: #fafcfb;
    }

    .checkbox-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 6px 8px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.84rem;
      color: #355347;
      transition: background 0.15s;
    }

    .checkbox-item:hover {
      background: #eef6f2;
    }

    .checkbox-item.selected {
      background: #e3f2ea;
      font-weight: 700;
      color: #0f2922;
    }

    .selection-footer-info {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 10px;
      flex-wrap: wrap;
      gap: 8px;
    }

    .selection-count {
      font-size: 0.8rem;
      color: #65887b;
    }

    .bdd-indicator {
      font-size: 0.76rem;
      font-weight: 800;
      color: #166534;
      background: #dcfce7;
      padding: 2px 8px;
      border-radius: 6px;
    }

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
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .filter-applied-badge {
      font-size: 0.68rem;
      color: #166534;
      background: #dcfce7;
      padding: 1px 6px;
      border-radius: 4px;
      text-transform: none;
    }

    .form-control {
      padding: 9px 12px;
      border: 1px solid #d0e0d7;
      border-radius: 8px;
      font-size: 0.88rem;
      color: #1a382e;
      background: #ffffff;
    }

    .form-control:focus {
      outline: none;
      border-color: #19734e;
    }

    .no-filters-msg {
      padding: 20px;
      text-align: center;
      color: #8da69b;
      font-size: 0.88rem;
    }

    /* Order & Submit */
    .order-submit-card {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 20px;
      background: linear-gradient(135deg, #ffffff 0%, #f4faf6 100%);
    }

    .order-inputs {
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
    }

    .form-group-inline {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .form-group-inline label {
      font-size: 0.82rem;
      font-weight: 700;
      color: #55796c;
      white-space: nowrap;
    }

    .btn-generate-report {
      padding: 14px 28px;
      background: linear-gradient(135deg, #19734e 0%, #0f2922 100%);
      color: #ffffff;
      border: none;
      border-radius: 12px;
      font-size: 0.95rem;
      font-weight: 800;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 10px;
      box-shadow: 0 4px 14px rgba(25, 115, 78, 0.3);
      transition: all 0.2s;
    }

    .btn-generate-report:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(25, 115, 78, 0.4);
    }

    .btn-generate-report:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    /* Results Section */
    .results-section {
      background: #ffffff;
      border: 1px solid #dce8e2;
      border-radius: 16px;
      padding: 26px;
      margin-top: 10px;
      box-shadow: 0 4px 16px rgba(0,0,0,0.03);
    }

    .results-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 20px;
      gap: 20px;
      flex-wrap: wrap;
    }

    .result-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      background: #e8f5ed;
      color: #19734e;
      border-radius: 6px;
      font-size: 0.76rem;
      font-weight: 800;
      margin-bottom: 6px;
    }

    .results-title-meta h2 {
      font-size: 1.35rem;
      font-weight: 800;
      color: #0f2922;
      margin: 0 0 6px 0;
    }

    .results-title-meta p {
      font-size: 0.86rem;
      color: #65887b;
      margin: 0;
    }

    .export-actions-bar {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }

    .btn-exp {
      padding: 9px 15px;
      border: none;
      border-radius: 8px;
      font-size: 0.84rem;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 7px;
      transition: all 0.2s;
    }

    /* Botón específico BDD: Descargar Excel (.xlsx) */
    .btn-excel-download {
      background: linear-gradient(135deg, #107c41 0%, #0d5f32 100%);
      color: #ffffff;
      box-shadow: 0 3px 10px rgba(16, 124, 65, 0.3);
      padding: 10px 18px;
      font-size: 0.88rem;
    }

    .btn-excel-download:hover:not(:disabled) {
      background: #0d5f32;
      transform: translateY(-1px);
      box-shadow: 0 5px 14px rgba(16, 124, 65, 0.4);
    }

    .btn-csv {
      background: #f1f8f5;
      color: #1e523e;
      border: 1px solid #c9ded3;
    }

    .btn-csv:hover {
      background: #e0f0e8;
    }

    .btn-email {
      background: #0284c7;
      color: #ffffff;
    }

    .btn-email:hover {
      background: #0369a1;
    }

    .btn-pdf {
      background: #dc2626;
      color: #ffffff;
    }

    .btn-pdf:hover {
      background: #b91c1c;
    }

    .btn-print {
      background: #475569;
      color: #ffffff;
    }

    .quick-filter-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      gap: 16px;
      flex-wrap: wrap;
    }

    .search-input-wrap {
      position: relative;
      flex: 1;
      max-width: 400px;
    }

    .search-input-wrap i {
      position: absolute;
      left: 12px;
      top: 50%;
      transform: translateY(-50%);
      color: #7b9e91;
    }

    .table-search-input {
      width: 100%;
      padding: 8px 12px 8px 36px;
      border: 1px solid #d2e2d9;
      border-radius: 8px;
      font-size: 0.85rem;
    }

    .records-summary {
      font-size: 0.82rem;
      font-weight: 700;
      color: #648477;
    }

    .table-container {
      overflow-x: auto;
      border: 1px solid #e1ece6;
      border-radius: 10px;
      margin-bottom: 16px;
    }

    .report-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.86rem;
      text-align: left;
    }

    .report-table th {
      background: #19734e;
      color: #ffffff;
      padding: 12px 14px;
      font-weight: 700;
      white-space: nowrap;
      border-bottom: 2px solid #105237;
    }

    .report-table td {
      padding: 11px 14px;
      border-bottom: 1px solid #edf4f0;
      color: #1e382d;
    }

    .report-table tbody tr:nth-child(even) {
      background: #fbfdfc;
    }

    .report-table tbody tr:hover {
      background: #f0f7f3;
    }

    .badge-status {
      display: inline-block;
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 0.74rem;
      font-weight: 800;
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
      display: flex;
      align-items: center;
      gap: 8px;
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
export class ReportePersonalizadoComponent implements OnInit, OnDestroy {
  // Modalidades: 'estandar', 'qbe', 'voz' (Criterio a)
  modalidadActiva: 'estandar' | 'qbe' | 'voz' = 'voz';
  fuenteSeleccionada = 'citas';
  metadataFuentes: Record<string, FuenteMetadata> = {};

  columnasDisponibles: ColumnaDef[] = [];
  columnasSeleccionadas: string[] = ['fecha', 'psicologo_nombre', 'paciente_nombre', 'estado', 'modalidad'];

  filtrosDisponibles: FiltroDef[] = [];
  filtrosValores: Record<string, any> = {};

  columnaOrden = '';
  direccionOrden = 'ASC';

  generando = false;
  descargandoExcel = false;
  resultado: ReporteResultado | null = null;
  busquedaResultados = '';

  // Reconocimiento de voz (Web Speech API)
  isListening = false;
  liveTranscript = '';
  voiceError = '';
  ultimoParametrosExtraidos: ExtractedVoiceParams | null = null;

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
  developerKey = '';
  accessError = '';
  private requests = new Subscription();
  private configuredSource = 'citas';

  private subs: Subscription[] = [];

  constructor(
    private reportService: ReportService,
    private speechParser: SpeechParserService,
    public authService: AuthService
  ) {
    effect(() => { if (!this.authService.isAuthenticated()) this.clearAuditState(); });
  }

  ngOnInit(): void {
    this.cargarMetadata();
    this.setupSpeechListeners();
  }

  ngOnDestroy(): void {
    this.speechParser.stopListening();
    this.subs.forEach(s => s.unsubscribe());
  }

  private setupSpeechListeners(): void {
    this.subs.push(
      this.speechParser.isListening$.subscribe(listening => {
        this.isListening = listening;
      }),
      this.speechParser.liveTranscript$.subscribe(transcript => {
        this.liveTranscript = transcript;
      }),
      this.speechParser.error$.subscribe(err => {
        this.voiceError = err;
      }),
      this.speechParser.paramsExtracted$.subscribe(params => {
        this.procesarParametrosVoz(params);
      })
    );
  }

  setModalidad(mod: 'estandar' | 'qbe' | 'voz'): void {
    this.modalidadActiva = mod;
    if (mod === 'voz') {
      this.presionar_boton_microfono();
    }
  }

  /**
   * 1a: presionar_boton_microfono()
   * Dispara captura Web Speech API
   */
  presionar_boton_microfono(): void {
    this.voiceError = '';
    if (this.isListening) {
      this.speechParser.stopListening();
    } else {
      this.speechParser.startListening();
    }
  }

  /**
   * Simulación o inyección de comando de voz (Paso 1 de la prueba)
   */
  simularComando(comandoTexto: string): void {
    this.liveTranscript = comandoTexto;
    this.speechParser.simularComandoVoz(comandoTexto);
  }

  /**
   * 3a: parametros_extraidos(fuente, psicologo, mes, ...)
   * Mapea semánticamente y tilda automáticamente los filtros QBE
   */
  procesarParametrosVoz(params: ExtractedVoiceParams): void {
    this.ultimoParametrosExtraidos = params;

    // 1. Entidad / Fuente
    if (params.fuente && params.fuente !== this.fuenteSeleccionada) {
      this.fuenteSeleccionada = params.fuente;
      this.actualizarConfiguracionFuente();
    }

    // 2. Filtro temporal (mes)
    if (params.mes) {
      // Capitalizar para opciones de dropdown: "Septiembre"
      const mesCap = params.mes.charAt(0).toUpperCase() + params.mes.slice(1);
      this.filtrosValores['mes'] = mesCap;
      if (params.fecha_desde) this.filtrosValores['fecha_desde'] = params.fecha_desde;
      if (params.fecha_hasta) this.filtrosValores['fecha_hasta'] = params.fecha_hasta;
    }

    // 3. Psicólogo
    if (params.psicologo) {
      this.filtrosValores['psicologo'] = params.psicologo;
      this.filtrosValores['psicologo_id'] = params.psicologo;
    }

    // 4. Estado y modalidad
    if (params.estado) {
      this.filtrosValores['estado'] = params.estado;
    }
    if (params.modalidad) {
      this.filtrosValores['modalidad'] = params.modalidad;
    }

    // 5. Proyección de columnas sugeridas (Paso 2 BDD)
    if (params.columnasSugeridas && params.columnasSugeridas.length > 0) {
      this.columnasSeleccionadas = [...params.columnasSugeridas];
    }

    // Ejecutar automáticamente la consulta para actualizar la vista previa interactiva
    this.generarReportePersonalizado();
  }

  cargarMetadata(): void {
    this.reportService.getMetadata().subscribe({
      next: (meta) => {
        this.metadataFuentes = meta;
        this.actualizarConfiguracionFuente();
        // Cargar vista previa inicial si hay datos
        this.generarReportePersonalizado();
      },
      error: (err) => console.error('Error cargando metadata:', err)
    });
  }

  onFuenteCambiada(): void {
    if (this.configuredSource !== this.fuenteSeleccionada) {
      this.clearAuditState();
      this.resultado = null;
      this.configuredSource = this.fuenteSeleccionada;
    }
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

      // Si es citas, inicializar con las 5 columnas de BDD
      if (this.fuenteSeleccionada === 'citas') {
        this.seleccionar5ColumnasBDD();
      } else {
        this.columnasSeleccionadas = fMeta.columnas.map(c => c.key);
      }
      this.emailAsunto = `SIGEPSI — Reporte Personalizado de ${fMeta.label}`;
    }
  }

  /**
   * Paso 2 BDD: Seleccionar manualmente columnas visibles:
   * 'Fecha', 'Psicólogo', 'Paciente', 'Estado', 'Modalidad'.
   */
  seleccionar5ColumnasBDD(): void {
    const keys = ['fecha', 'psicologo_nombre', 'paciente_nombre', 'estado', 'modalidad'];
    this.columnasSeleccionadas = this.columnasDisponibles
      .map(c => c.key)
      .filter(k => keys.includes(k));
    if (this.resultado) {
      // Re-generar o refrescar vista previa interactiva proyectando exclusivamente las 5
      this.generarReportePersonalizado();
    }
  }

  is5ColumnasSeleccionadas(): boolean {
    const keys = ['fecha', 'psicologo_nombre', 'paciente_nombre', 'estado', 'modalidad'];
    return this.columnasSeleccionadas.length === 5 &&
           keys.every(k => this.columnasSeleccionadas.includes(k));
  }

  toggleColumna(key: string): void {
    if (this.columnasSeleccionadas.includes(key)) {
      if (this.columnasSeleccionadas.length > 1) {
        this.columnasSeleccionadas = this.columnasSeleccionadas.filter(k => k !== key);
      }
    } else {
      this.columnasSeleccionadas.push(key);
    }
    // Paso 2 BDD: La vista previa interactiva se actualiza en pantalla desplegando únicamente las columnas seleccionadas
    if (this.resultado) {
      this.generarReportePersonalizado();
    }
  }

  seleccionarTodasColumnas(marcar: boolean): void {
    if (marcar) {
      this.columnasSeleccionadas = this.columnasDisponibles.map(c => c.key);
    } else {
      this.columnasSeleccionadas = [this.columnasDisponibles[0]?.key || 'fecha'];
    }
    if (this.resultado) {
      this.generarReportePersonalizado();
    }
  }

  limpiarFiltros(): void {
    this.filtrosValores = {};
    this.ultimoParametrosExtraidos = null;
    this.generarReportePersonalizado();
  }

  onFiltroCambiado(): void {
    // Si ya existe resultado, refrescar preview
    if (this.resultado) {
      this.generarReportePersonalizado();
    }
  }

  columnasParaOrden(): ColumnaDef[] {
    return this.columnasDisponibles.filter(c => this.columnasSeleccionadas.includes(c.key));
  }

  /**
   * Obtiene la proyección de columnas activa para la tabla
   */
  getColumnasActivas(): ColumnaDef[] {
    if (this.resultado && this.resultado.columnas) {
      return this.resultado.columnas.filter(c => this.columnasSeleccionadas.includes(c.key));
    }
    return this.columnasDisponibles.filter(c => this.columnasSeleccionadas.includes(c.key));
  }

  /**
   * Step 4 / 5 del Diagrama de Secuencia:
   * POST /api/v1/reportes/personalizado/ (payload_qbe)
   */
  generarReportePersonalizado(): void {
    if (this.fuenteSeleccionada === 'bitacora' && !this.developerKey.trim()) {
      this.clearAuditResult();
      this.accessError = 'Ingresá la clave de desarrollador para consultar la bitácora.';
      return;
    }
    this.accessError = '';
    if (this.fuenteSeleccionada === 'bitacora') this.clearAuditRequest();
    this.generando = true;
    const fuenteConsultada = this.fuenteSeleccionada;
    const keyConsultada = fuenteConsultada === 'bitacora' ? this.developerKey : undefined;
    const orden = this.columnaOrden ? { columna: this.columnaOrden, direccion: this.direccionOrden } : undefined;

    const request = this.reportService.generarPersonalizado({
      fuente: fuenteConsultada,
      columnas: this.columnasSeleccionadas,
      filtros: this.filtrosValores,
      orden: orden
    }, keyConsultada);
    this.requests.add(request.subscribe({
      next: (res) => {
        if (fuenteConsultada !== this.fuenteSeleccionada || (fuenteConsultada === 'bitacora' && (keyConsultada !== this.developerKey || !this.authService.isAuthenticated()))) return;
        this.resultado = res;
        this.generando = false;
        this.paginaActual = 1;
      },
      error: (err) => {
        if (fuenteConsultada !== this.fuenteSeleccionada || (fuenteConsultada === 'bitacora' && (keyConsultada !== this.developerKey || !this.authService.isAuthenticated()))) return;
        if (fuenteConsultada === 'bitacora') this.accessError = err.status === 401 || err.status === 403
          ? 'Acceso denegado. Verificá la clave de desarrollador y tu sesión de SuperAdmin.'
          : 'No se pudo generar la bitácora. Verificá la clave e intentá nuevamente.';
        this.generando = false;
      }
    }));
  }

  keyChanged(): void { this.clearAuditResult(); this.accessError = ''; }
  private clearAuditRequest(): void { this.requests.unsubscribe(); this.requests = new Subscription(); }
  private clearAuditResult(): void {
    this.clearAuditRequest();
    this.resultado = null;
    this.generando = false;
    this.modalEmailAbierto = false;
    this.enviandoEmail = false;
    this.emailMensaje = '';
    this.emailError = '';
  }
  private clearAuditState(): void {
    this.clearAuditResult();
    this.developerKey = '';
    this.accessError = '';
  }
  lockAudit(): void { this.clearAuditState(); }
  ngOnDestroy(): void { this.clearAuditState(); this.requests.unsubscribe(); }

  /**
   * Paso 3 BDD & Step 9a/11a/12a del Diagrama de Secuencia:
   * Presionar botón 'Descargar Excel (.xlsx)'
   * -> POST /api/v1/reportes/personalizado/ con formato='EXCEL'
   * -> Genera archivo binario .xlsx con OpenPyXL con membrete del centro
   * -> Disparar descarga automática en navegador
   */
  descargarExcelOpenPyXL(): void {
    this.descargandoExcel = true;
    const orden = this.columnaOrden ? { columna: this.columnaOrden, direccion: this.direccionOrden } : undefined;
    const keyConsultada = this.fuenteSeleccionada === 'bitacora' ? this.developerKey : undefined;

    this.reportService.exportarPersonalizadoExcel({
      fuente: this.fuenteSeleccionada,
      columnas: this.columnasSeleccionadas,
      filtros: this.filtrosValores,
      orden: orden
    }, keyConsultada).subscribe({
      next: (blob) => {
        this.descargandoExcel = false;
        // Step 12a: disparar_descarga_automatica_en_navegador
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `reporte_${this.fuenteSeleccionada}.xlsx`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      },
      error: (err) => {
        console.error('Error al descargar Excel desde servidor:', err);
        this.descargandoExcel = false;
        // Fallback a cliente si fuera necesario
        this.exportarExcel();
      }
    });
  }

  /**
   * Exportación CSV plano (Criterio d BDD)
   */
  exportarCSVServer(): void {
    this.reportService.descargarCSVServer(this.fuenteSeleccionada, this.filtrosValores).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `reporte_${this.fuenteSeleccionada}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      },
      error: (err) => console.error('Error al descargar CSV:', err)
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

  exportarPDF(): void {
    if (!this.resultado) return;
    const currentTenant = this.authService.currentTenant()?.nombre;
    const currentUser = this.authService.currentUser()?.nombre || 'Administrador Clínico';
    const res = {
      ...this.resultado,
      columnas: this.getColumnasActivas(),
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
      columnas: this.getColumnasActivas(),
      datos: this.datosFiltrados(),
      total: this.datosFiltrados().length
    };
    this.reportService.exportToExcel(res, `reporte_personalizado_${this.fuenteSeleccionada}`, currentTenant, currentUser);
  }

  imprimirReporte(): void {
    if (!this.resultado) return;
    const res = {
      ...this.resultado,
      columnas: this.getColumnasActivas(),
      datos: this.datosFiltrados(),
      total: this.datosFiltrados().length
    };
    this.reportService.printReport(res, `Reporte Personalizado - ${this.getFuenteLabel()}`);
  }

  // Modal Email (SMTP)
  abrirModalEmail(): void {
    this.modalEmailAbierto = true;
    this.emailMensaje = '';
    this.emailError = '';
    this.emailDestino = this.authService.currentUser()?.email || '';
  }

  /**
   * Step 9b / 10b del Diagrama de Secuencia:
   * enviar_reporte_smtp(email_destino, dataset)
   */
  enviarPorCorreoSMTP(): void {
    if (!this.emailDestino) return;
    this.enviandoEmail = true;
    this.emailMensaje = '';
    this.emailError = '';

    const fuenteEnviada = this.fuenteSeleccionada;
    const keyEnviada = fuenteEnviada === 'bitacora' ? this.developerKey : undefined;
    const orden = this.columnaOrden ? { columna: this.columnaOrden, direccion: this.direccionOrden } : undefined;

    this.requests.add(this.reportService.exportarPersonalizadoEmail({
      email: this.emailDestino,
      fuente: this.fuenteSeleccionada,
      asunto: this.emailAsunto,
      filtros: this.filtrosValores,
      columnas: this.columnasSeleccionadas,
      orden: orden
    }, keyEnviada).subscribe({
      next: (res) => {
        if (fuenteEnviada !== this.fuenteSeleccionada || (fuenteEnviada === 'bitacora' && (keyEnviada !== this.developerKey || !this.authService.isAuthenticated()))) return;
        this.enviandoEmail = false;
        this.emailMensaje = res.mensaje || `Reporte enviado exitosamente por correo a ${this.emailDestino}`;
        setTimeout(() => {
          this.modalEmailAbierto = false;
        }, 2200);
      },
      error: (err) => {
        if (fuenteEnviada !== this.fuenteSeleccionada || (fuenteEnviada === 'bitacora' && keyEnviada !== this.developerKey)) return;
        this.enviandoEmail = false;
        this.emailError = fuenteEnviada === 'bitacora' && (err.status === 401 || err.status === 403)
          ? 'Acceso denegado. Verificá la clave de desarrollador y tu sesión de SuperAdmin.'
          : err.error?.error || 'Error al procesar el envío de correo SMTP.';
      }
    }));
  }
}
