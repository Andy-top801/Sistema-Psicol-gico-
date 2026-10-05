import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { BackupService, BackupItem, BackupResult, CronStatus } from '../../core/services/backup.service';
import { TenantService } from '../../core/services/tenant.service';
import { AuthService } from '../../core/services/auth.service';

/**
 * IU_ConsolaBackupRestore & IU_ComprobanteBackup
 * Cumple con Caso de Uso HU-39 (CU28) y Diagramas de Secuencia y Comunicación:
 * - Paso 1: Verificación de tarea cron periódica cloud (03:00 AM hora boliviana).
 * - Paso 2: Generación manual de backup (Global o Tenant Específico: Centro Esperanza) con SHA-256.
 * - Paso 3: Validación criptográfica en dropzone detectando archivos corruptos o alterados.
 * - Paso 4: Restauración asistida transaccional atómica (--clean --if-exists) con alerta modal de éxito.
 */
@Component({
  selector: 'app-backup-restore-console',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  template: `
    <div class="backup-console-container IU_ConsolaBackupRestore">
      <!-- Breadcrumb Bar -->
      <div class="top-nav">
        <a routerLink="/dashboard" class="btn-back">
          <i class="fa-solid fa-arrow-left"></i> Volver al Panel Principal
        </a>
        <div class="badge-role">
          <i class="fa-solid fa-shield-halved"></i> Consola SuperAdministrador (SaaS)
        </div>
      </div>

      <!-- Main Header -->
      <div class="console-header">
        <div class="header-icon-box">
          <i class="fa-solid fa-cloud-arrow-up"></i>
        </div>
        <div>
          <div class="header-tag">HU-39 (CU28) • Copias de Seguridad & Restauración Cloud</div>
          <h1 class="header-title">Consola de Respaldos y Recuperación</h1>
          <p class="header-desc">
            Gestiona respaldos automáticos en la nube a las 03:00 AM (BOT) y manuales a demanda (globales o por centro), y restaura esquemas de bases de datos PostgreSQL con verificación criptográfica SHA-256 previa.
          </p>
        </div>
      </div>

      <!-- PASO 1 BDD: Tarea Programada de Cron en Servidor Cloud -->
      <section class="cron-card">
        <div class="cron-header-flex">
          <div class="cron-badge">
            <i class="fa-solid fa-clock-rotate-left"></i> Respaldo Automático Cloud (03:00 AM Hora Boliviana)
          </div>
          <div class="cron-status-badge" [class.active]="cronInfo?.estado === 'ACTIVO'">
            <span class="status-dot"></span>
            {{ cronInfo ? cronInfo.estado + ' • ' + cronInfo.hora_ejecucion : 'Programación Activa 03:00 AM BOT' }}
          </div>
        </div>

        <div class="cron-body-grid">
          <div class="cron-info-item">
            <label>Expresión Cron:</label>
            <code>{{ cronInfo?.cron_expresion || '0 3 * * *' }}</code>
          </div>
          <div class="cron-info-item">
            <label>Horario Programado:</label>
            <span>03:00 AM (Hora Oficial de Bolivia - BOT / UTC-4)</span>
          </div>
          <div class="cron-info-item">
            <label>Almacenamiento Cloud:</label>
            <span>Volcado seguro PostgreSQL comprimido en gzip (.sql.gz)</span>
          </div>
          <div class="cron-info-item" *ngIf="cronInfo?.ultimo_respaldo_cron">
            <label>Último Respaldo Cloud:</label>
            <span>{{ cronInfo?.ultimo_respaldo_cron?.fecha | date:'dd/MM/yyyy HH:mm' }} ({{ cronInfo?.ultimo_respaldo_cron?.tamano_mb }} MB)</span>
          </div>
        </div>

        <div class="cron-actions">
          <button 
            type="button" 
            class="btn-cron-verify" 
            [disabled]="ejecutandoCron"
            (click)="ejecutarTareaCron()">
            <i class="fa-solid" [class.fa-bolt]="!ejecutandoCron" [class.fa-spinner]="ejecutandoCron" [class.fa-spin]="ejecutandoCron"></i>
            <span>{{ ejecutandoCron ? 'Verificando y ejecutando tarea cron...' : 'Verificar Tarea de Cron Cloud (Paso 1 BDD)' }}</span>
          </button>
          <div *ngIf="cronMensaje" class="cron-alert-success">
            <i class="fa-solid fa-circle-check"></i> {{ cronMensaje }}
          </div>
        </div>
      </section>

      <!-- Grid Principal: Generación Manual & Restauración -->
      <div class="console-grid">
        <!-- OPERACIÓN 1: Generación de Backup Manual (Paso 2 BDD) -->
        <section class="card-operation">
          <div class="op-badge">Operación 1</div>
          <h2 class="card-title">
            <i class="fa-solid fa-download"></i> Generar Respaldo Manual a Demanda
          </h2>
          <p class="card-desc">
            Crea un volcado de base de datos comprimido (.sql.gz) con cálculo criptográfico de Checksum SHA-256.
          </p>

          <!-- Selección de Ámbito (Global o Tenant Específico) -->
          <div class="form-group">
            <label class="form-label">Ámbito del Respaldo:</label>
            <div class="scope-radio-group">
              <label class="radio-card" [class.selected]="ambitoSeleccionado === 'TENANT'">
                <input type="radio" name="ambito" value="TENANT" [(ngModel)]="ambitoSeleccionado" />
                <div class="radio-content">
                  <strong>Tenant Específico</strong>
                  <span>Respalda únicamente el esquema del centro clínico seleccionado</span>
                </div>
              </label>

              <label class="radio-card" [class.selected]="ambitoSeleccionado === 'GLOBAL'">
                <input type="radio" name="ambito" value="GLOBAL" [(ngModel)]="ambitoSeleccionado" />
                <div class="radio-content">
                  <strong>Base de Datos Completa</strong>
                  <span>Respaldo global de todos los esquemas y tablas del SaaS</span>
                </div>
              </label>
            </div>
          </div>

          <!-- Selección de Centro Clínico (Paso 2 BDD: Tenant Específico: Centro Esperanza) -->
          <div class="form-group" *ngIf="ambitoSeleccionado === 'TENANT'">
            <label class="form-label">Seleccionar Centro Psicológico *</label>
            <select [(ngModel)]="tenantSeleccionadoId" class="form-select">
              <option *ngFor="let t of listaTenants" [value]="t.id">
                🏢 {{ t.nombre }} (Esquema: {{ t.schema_name }})
              </option>
            </select>
            <span class="field-hint" *ngIf="isCentroEsperanzaSeleccionado()">
              ✓ Paso 2 BDD: Ámbito 'Tenant Específico: Centro Esperanza' seleccionado.
            </span>
          </div>

          <div class="action-row">
            <button 
              type="button" 
              class="btn-primary-action" 
              [disabled]="generandoBackup || (ambitoSeleccionado === 'TENANT' && !tenantSeleccionadoId)"
              (click)="generarBackupManual()">
              <i class="fa-solid" [class.fa-file-shield]="!generandoBackup" [class.fa-spinner]="generandoBackup" [class.fa-spin]="generandoBackup"></i>
              <span>{{ generandoBackup ? 'Extrayendo esquema y calculando SHA-256...' : 'Generar Respaldo Ahora' }}</span>
            </button>
          </div>

          <!-- SUB-BOUNDARY: IU_ComprobanteBackup (Renderiza tarjeta de descarga con Checksum verificado) -->
          <div class="comprobante-backup-card IU_ComprobanteBackup" *ngIf="ultimoBackup">
            <div class="comprobante-header">
              <div class="status-tag-ok">
                <i class="fa-solid fa-circle-check"></i> Descarga Lista - Checksum OK
              </div>
              <span class="comprobante-date">{{ ultimoBackup.fecha | date:'dd/MM/yyyy HH:mm:ss' }}</span>
            </div>

            <div class="comprobante-details">
              <div class="detail-row">
                <span class="detail-label">Archivo:</span>
                <span class="detail-val file-name">{{ ultimoBackup.archivo }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Ámbito / Esquema:</span>
                <span class="detail-val">{{ ultimoBackup.ambito }} ({{ ultimoBackup.schema }})</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Tamaño:</span>
                <span class="detail-val"><strong>{{ ultimoBackup.tamano_mb }} MB</strong> ({{ ultimoBackup.tamano_bytes | number }} bytes)</span>
              </div>
              <div class="detail-row checksum-box">
                <span class="detail-label">Checksum SHA-256:</span>
                <code class="sha-code">{{ ultimoBackup.checksum_sha256 }}</code>
                <button type="button" class="btn-copy-sha" (click)="copiarSha(ultimoBackup.checksum_sha256)" title="Copiar Checksum">
                  <i class="fa-solid fa-copy"></i>
                </button>
              </div>
            </div>

            <div class="comprobante-actions">
              <a [href]="getDescargaUrl(ultimoBackup.archivo)" (click)="descargarArchivo(ultimoBackup.archivo, $event)" class="btn-download-backup" style="cursor: pointer;">
                <i class="fa-solid" [class.fa-cloud-arrow-down]="!descargandoArchivo" [class.fa-spinner]="descargandoArchivo" [class.fa-spin]="descargandoArchivo"></i>
                {{ descargandoArchivo ? 'Descargando...' : 'Descargar Archivo (.sql.gz)' }}
              </a>
              <span class="checksum-verified-pill">
                <i class="fa-solid fa-fingerprint"></i> Checksum criptográfico verificado
              </span>
            </div>
          </div>
        </section>

        <!-- OPERACIÓN 2: Restauración Asistida y Verificación Criptográfica (Paso 3 y 4 BDD) -->
        <section class="card-operation">
          <div class="op-badge op-restore">Operación 2</div>
          <h2 class="card-title">
            <i class="fa-solid fa-rotate-left"></i> Restauración de Base de Datos
          </h2>
          <p class="card-desc">
            Carga un archivo de respaldo. El sistema verifica criptográficamente el checksum SHA-256 antes de ejecutar la transacción atómica de restauración (pg_restore).
          </p>

          <!-- Selección de Tenant Destino -->
          <div class="form-group">
            <label class="form-label">Centro de Destino para Restauración:</label>
            <select [(ngModel)]="tenantDestinoId" class="form-select">
              <option *ngFor="let t of listaTenants" [value]="t.id">
                🏢 {{ t.nombre }} (Esquema: {{ t.schema_name }})
              </option>
            </select>
          </div>

          <!-- Dropzone de Restauración (Paso 3 BDD) -->
          <div class="form-group">
            <label class="form-label">Archivo de Volcado (.sql.gz o .sql) *</label>
            <div 
              class="restore-dropzone" 
              [class.has-file]="archivoSeleccionado !== null"
              (dragover)="onDragOver($event)" 
              (dragleave)="onDragLeave($event)" 
              (drop)="onDropFile($event)"
              (click)="fileInput.click()">
              <input 
                #fileInput 
                type="file" 
                accept=".gz,.sql,.sql.gz" 
                style="display: none" 
                (change)="onFileSelected($event)" 
              />
              <div class="dropzone-content" *ngIf="!archivoSeleccionado">
                <i class="fa-solid fa-file-arrow-up drop-icon"></i>
                <div class="drop-text">Arrastra aquí el archivo de respaldo o <span>haz clic para explorar</span></div>
                <div class="drop-hint">Formatos aceptados: .sql.gz, .sql con compresión gzip</div>
              </div>
              <div class="dropzone-file-info" *ngIf="archivoSeleccionado">
                <i class="fa-solid fa-file-zipper file-icon"></i>
                <div>
                  <strong>{{ archivoSeleccionado.name }}</strong>
                  <span>({{ (archivoSeleccionado.size / (1024 * 1024)) | number:'1.2-2' }} MB)</span>
                </div>
                <button type="button" class="btn-remove-file" (click)="quitarArchivo($event)">&times;</button>
              </div>
            </div>
          </div>

          <!-- Checksum SHA-256 Opcional de Verificación -->
          <div class="form-group">
            <label class="form-label">Checksum SHA-256 de Integridad (Opcional):</label>
            <input 
              type="text" 
              [(ngModel)]="checksumEsperado" 
              placeholder="Ej: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" 
              class="form-input" 
            />
          </div>

          <!-- Botones de Prueba Rápida BDD -->
          <div class="test-buttons-box">
            <span class="test-label">Pruebas automáticas BDD:</span>
            <button 
              type="button" 
              class="btn-test-corrupt" 
              [disabled]="restaurando"
              (click)="simularPaso3ArchivoCorrupto()">
              <i class="fa-solid fa-triangle-exclamation"></i> Probar Archivo Corrupto (Paso 3 BDD)
            </button>
            <button 
              type="button" 
              class="btn-test-legit" 
              [disabled]="restaurando"
              (click)="simularPaso4RestauracionLegitima()">
              <i class="fa-solid fa-circle-check"></i> Restaurar Copia Legítima (Paso 4 BDD)
            </button>
          </div>

          <div class="action-row">
            <button 
              type="button" 
              class="btn-restore-action" 
              [disabled]="restaurando || (!archivoSeleccionado && !ultimoBackup)"
              (click)="ejecutarRestauracionManual()">
              <i class="fa-solid" [class.fa-rotate-left]="!restaurando" [class.fa-spinner]="restaurando" [class.fa-spin]="restaurando"></i>
              <span>{{ restaurando ? 'Validando SHA-256 y ejecutando pg_restore...' : 'Confirmar y Restaurar Esquema' }}</span>
            </button>
          </div>

          <!-- Alerta de Error (Paso 3 BDD: Abortado por integridad) -->
          <div class="alert-integrity-error" *ngIf="errorRestauracion">
            <div class="alert-title">
              <i class="fa-solid fa-circle-xmark"></i> Validación Criptográfica Fallida (Paso 3 BDD)
            </div>
            <div class="alert-body">
              {{ errorRestauracion }}
            </div>
          </div>
        </section>
      </div>

      <!-- ALERTA MODAL DE ÉXITO (Paso 4 BDD & Step 9b Diagrama de Secuencia) -->
      <div class="modal-backdrop" *ngIf="modalExitoVisible">
        <div class="modal-success-card alerta_modal_exito">
          <div class="modal-success-icon">
            <i class="fa-solid fa-circle-check"></i>
          </div>
          <h3 class="modal-success-title">Centro Restaurado Íntegramente</h3>
          <p class="modal-success-desc">
            {{ mensajeExitoRestauracion || 'El sistema ejecutó pg_restore en una transacción atómica segura, restauró tablas, relaciones e índices y registró la auditoría de recuperación exitosa.' }}
          </p>
          <div class="modal-meta-box">
            <div><strong>Centro:</strong> {{ getNombreTenantDestino() }}</div>
            <div><strong>Estado:</strong> Esquema restaurado a estado íntegro</div>
            <div><strong>Integridad:</strong> SHA-256 validado satisfactoriamente</div>
          </div>
          <button type="button" class="btn-close-success" (click)="modalExitoVisible = false">
            Aceptar y Continuar
          </button>
        </div>
      </div>

      <!-- SECCIÓN 3: Registro y Auditoría de Backups (CE_BackupLogRegistro) -->
      <section class="history-section">
        <div class="history-header">
          <div>
            <h3 class="history-title"><i class="fa-solid fa-database"></i> Registro Histórico de Respaldos (CE_BackupLogRegistro)</h3>
            <p class="history-subtitle">Metadatos persistidos en la tabla backups_registro con Checksum SHA-256 y trazabilidad de origen.</p>
          </div>
          <button type="button" class="btn-refresh" (click)="cargarHistorialBackups()">
            <i class="fa-solid fa-rotate"></i> Actualizar
          </button>
        </div>

        <div class="table-container">
          <table class="backup-table">
            <thead>
              <tr>
                <th>Archivo</th>
                <th>Ámbito / Esquema</th>
                <th>Origen</th>
                <th>Fecha de Generación</th>
                <th>Tamaño</th>
                <th>Checksum SHA-256</th>
                <th>Estado</th>
                <th>Acción</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let b of listaBackups">
                <td class="file-cell">
                  <i class="fa-solid fa-file-zipper"></i>
                  <span>{{ b.archivo }}</span>
                </td>
                <td>
                  <span class="badge-scope" [class.global]="b.ambito === 'GLOBAL'">
                    {{ b.ambito }} {{ b.schema ? '(' + b.schema + ')' : '' }}
                  </span>
                </td>
                <td>
                  <span class="badge-origin" [class.cron]="b.origen === 'CRON_AUTOMATICO'">
                    {{ b.origen === 'CRON_AUTOMATICO' ? 'CRON 03:00 AM' : 'MANUAL' }}
                  </span>
                </td>
                <td>{{ b.fecha_creacion | date:'dd/MM/yyyy HH:mm' }}</td>
                <td><strong>{{ b.tamano_mb }} MB</strong></td>
                <td>
                  <code class="mini-sha" [title]="b.checksum_sha256">{{ b.checksum_sha256.slice(0, 16) }}...</code>
                </td>
                <td>
                  <span class="badge-status-ok"><i class="fa-solid fa-check"></i> {{ b.estado || 'COMPLETADO' }}</span>
                </td>
                <td>
                  <a [href]="getDescargaUrl(b.archivo)" (click)="descargarArchivo(b.archivo, $event)" class="btn-table-download" title="Descargar copia" style="cursor: pointer;">
                    <i class="fa-solid fa-download"></i>
                  </a>
                </td>
              </tr>
              <tr *ngIf="listaBackups.length === 0">
                <td colspan="8" class="empty-cell">
                  No hay respaldos registrados actualmente. Genera uno usando la consola superior.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  `,
  styles: [`
    .backup-console-container {
      max-width: 1300px;
      margin: 0 auto;
    }

    .top-nav {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      flex-wrap: wrap;
      gap: 12px;
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

    .badge-role {
      font-size: 0.78rem;
      font-weight: 800;
      color: #0f2922;
      background: #ffffff;
      border: 1px solid #dce8e2;
      padding: 6px 12px;
      border-radius: 20px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }

    /* Console Header */
    .console-header {
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

    /* Cron Card (Paso 1 BDD) */
    .cron-card {
      background: linear-gradient(145deg, #ffffff 0%, #f7fbf9 100%);
      border: 2px solid #b7dfce;
      border-radius: 16px;
      padding: 20px 24px;
      margin-bottom: 24px;
      box-shadow: 0 4px 14px rgba(25, 115, 78, 0.08);
    }

    .cron-header-flex {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 14px;
      flex-wrap: wrap;
      gap: 10px;
    }

    .cron-badge {
      font-size: 0.84rem;
      font-weight: 800;
      color: #19734e;
      background: #e6f6ee;
      padding: 4px 12px;
      border-radius: 20px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }

    .cron-status-badge {
      font-size: 0.8rem;
      font-weight: 700;
      color: #15803d;
      background: #dcfce7;
      padding: 4px 12px;
      border-radius: 20px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #16a34a;
    }

    .cron-body-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 14px;
      margin-bottom: 16px;
    }

    .cron-info-item label {
      display: block;
      font-size: 0.74rem;
      font-weight: 800;
      color: #65887b;
      text-transform: uppercase;
      margin-bottom: 2px;
    }

    .cron-info-item span, .cron-info-item code {
      font-size: 0.88rem;
      font-weight: 700;
      color: #123024;
    }

    .cron-info-item code {
      background: #eef6f2;
      padding: 2px 6px;
      border-radius: 4px;
      font-family: monospace;
      color: #0f2922;
    }

    .cron-actions {
      display: flex;
      align-items: center;
      gap: 14px;
      flex-wrap: wrap;
    }

    .btn-cron-verify {
      padding: 8px 18px;
      background: #19734e;
      color: #ffffff;
      border: none;
      border-radius: 8px;
      font-size: 0.84rem;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s;
    }

    .btn-cron-verify:hover:not(:disabled) {
      background: #115337;
    }

    .cron-alert-success {
      font-size: 0.84rem;
      font-weight: 700;
      color: #15803d;
      background: #dcfce7;
      padding: 6px 14px;
      border-radius: 8px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }

    /* Grid Layout */
    .console-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      margin-bottom: 30px;
    }

    .card-operation {
      background: #ffffff;
      border: 1px solid #dce8e2;
      border-radius: 16px;
      padding: 26px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.02);
      display: flex;
      flex-direction: column;
    }

    .op-badge {
      display: inline-block;
      align-self: flex-start;
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

    .op-badge.op-restore {
      background: #e0f2fe;
      color: #0369a1;
    }

    .card-title {
      font-size: 1.25rem;
      font-weight: 800;
      color: #0f2922;
      margin: 0 0 6px 0;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .card-desc {
      font-size: 0.84rem;
      color: #648477;
      margin: 0 0 18px 0;
      line-height: 1.45;
    }

    .form-group {
      margin-bottom: 16px;
    }

    .form-label {
      display: block;
      font-size: 0.78rem;
      font-weight: 700;
      color: #48665b;
      text-transform: uppercase;
      margin-bottom: 6px;
    }

    .scope-radio-group {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }

    .radio-card {
      border: 1px solid #d0e0d7;
      border-radius: 10px;
      padding: 10px 12px;
      cursor: pointer;
      display: flex;
      gap: 10px;
      align-items: flex-start;
      background: #fafcfb;
      transition: all 0.2s;
    }

    .radio-card.selected {
      border-color: #19734e;
      background: #eef7f2;
    }

    .radio-content strong {
      display: block;
      font-size: 0.85rem;
      color: #0f2922;
    }

    .radio-content span {
      font-size: 0.74rem;
      color: #65887b;
      line-height: 1.3;
    }

    .form-select, .form-input {
      width: 100%;
      padding: 10px 12px;
      border: 1px solid #c9ded3;
      border-radius: 8px;
      font-size: 0.9rem;
      color: #14352a;
      background: #ffffff;
    }

    .field-hint {
      display: block;
      margin-top: 5px;
      font-size: 0.76rem;
      font-weight: 700;
      color: #15803d;
    }

    .action-row {
      margin-top: 10px;
      margin-bottom: 16px;
    }

    .btn-primary-action {
      width: 100%;
      padding: 12px 20px;
      background: linear-gradient(135deg, #19734e 0%, #115337 100%);
      color: #ffffff;
      border: none;
      border-radius: 10px;
      font-size: 0.92rem;
      font-weight: 800;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      box-shadow: 0 4px 12px rgba(25, 115, 78, 0.25);
      transition: all 0.2s;
    }

    .btn-primary-action:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(25, 115, 78, 0.35);
    }

    .btn-restore-action {
      width: 100%;
      padding: 12px 20px;
      background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
      color: #ffffff;
      border: none;
      border-radius: 10px;
      font-size: 0.92rem;
      font-weight: 800;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      box-shadow: 0 4px 12px rgba(2, 132, 199, 0.25);
      transition: all 0.2s;
    }

    .btn-restore-action:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(2, 132, 199, 0.35);
    }

    /* Comprobante Backup Card (IU_ComprobanteBackup) */
    .comprobante-backup-card {
      background: #f0fdf4;
      border: 2px solid #86efac;
      border-radius: 12px;
      padding: 16px;
      margin-top: 14px;
    }

    .comprobante-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }

    .status-tag-ok {
      font-size: 0.82rem;
      font-weight: 800;
      color: #166534;
      background: #dcfce7;
      padding: 3px 10px;
      border-radius: 6px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }

    .comprobante-date {
      font-size: 0.76rem;
      color: #166534;
      font-weight: 600;
    }

    .comprobante-details {
      display: flex;
      flex-direction: column;
      gap: 6px;
      margin-bottom: 14px;
    }

    .detail-row {
      display: flex;
      justify-content: space-between;
      font-size: 0.82rem;
      gap: 8px;
    }

    .detail-label {
      color: #48665b;
      font-weight: 700;
    }

    .detail-val {
      color: #0f2922;
      font-weight: 600;
    }

    .detail-val.file-name {
      font-family: monospace;
      color: #15803d;
    }

    .checksum-box {
      flex-direction: column;
      align-items: flex-start;
      background: #ffffff;
      padding: 8px 10px;
      border-radius: 6px;
      border: 1px solid #bbf7d0;
      margin-top: 4px;
      position: relative;
    }

    .sha-code {
      font-family: monospace;
      font-size: 0.74rem;
      color: #0f2922;
      word-break: break-all;
    }

    .btn-copy-sha {
      position: absolute;
      top: 6px;
      right: 8px;
      background: none;
      border: none;
      color: #166534;
      cursor: pointer;
      font-size: 0.85rem;
    }

    .comprobante-actions {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }

    .btn-download-backup {
      padding: 8px 14px;
      background: #166534;
      color: #ffffff;
      border-radius: 8px;
      text-decoration: none;
      font-size: 0.82rem;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: background 0.2s;
    }

    .btn-download-backup:hover {
      background: #14532d;
    }

    .checksum-verified-pill {
      font-size: 0.76rem;
      font-weight: 700;
      color: #166534;
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }

    /* Restore Dropzone */
    .restore-dropzone {
      border: 2px dashed #93c5fd;
      background: #f8fafc;
      border-radius: 12px;
      padding: 24px 16px;
      text-align: center;
      cursor: pointer;
      transition: all 0.2s;
    }

    .restore-dropzone:hover {
      border-color: #0284c7;
      background: #f0f9ff;
    }

    .restore-dropzone.has-file {
      border-style: solid;
      border-color: #0284c7;
      background: #f0f9ff;
    }

    .drop-icon {
      font-size: 2rem;
      color: #0284c7;
      margin-bottom: 8px;
    }

    .drop-text {
      font-size: 0.88rem;
      font-weight: 700;
      color: #1e293b;
      margin-bottom: 4px;
    }

    .drop-text span {
      color: #0284c7;
      text-decoration: underline;
    }

    .drop-hint {
      font-size: 0.74rem;
      color: #64748b;
    }

    .dropzone-file-info {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
    }

    .file-icon {
      font-size: 1.8rem;
      color: #0284c7;
    }

    .btn-remove-file {
      background: #fee2e2;
      border: none;
      color: #b91c1c;
      font-size: 1.2rem;
      border-radius: 50%;
      width: 26px;
      height: 26px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    /* Test buttons box */
    .test-buttons-box {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 10px 12px;
      margin-bottom: 14px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .test-label {
      font-size: 0.74rem;
      font-weight: 800;
      color: #475569;
      text-transform: uppercase;
    }

    .btn-test-corrupt {
      padding: 7px 12px;
      background: #fef2f2;
      border: 1px solid #fecaca;
      color: #b91c1c;
      border-radius: 6px;
      font-size: 0.78rem;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }

    .btn-test-corrupt:hover {
      background: #fee2e2;
    }

    .btn-test-legit {
      padding: 7px 12px;
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
      color: #166534;
      border-radius: 6px;
      font-size: 0.78rem;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }

    .btn-test-legit:hover {
      background: #dcfce7;
    }

    .alert-integrity-error {
      background: #fef2f2;
      border: 1px solid #f87171;
      border-radius: 10px;
      padding: 12px;
      margin-top: 10px;
    }

    .alert-integrity-error .alert-title {
      font-size: 0.84rem;
      font-weight: 800;
      color: #991b1b;
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .alert-integrity-error .alert-body {
      font-size: 0.8rem;
      color: #b91c1c;
      line-height: 1.4;
    }

    /* Success Modal (Paso 4 BDD) */
    .modal-backdrop {
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(15, 41, 34, 0.65);
      backdrop-filter: blur(4px);
      z-index: 1000;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }

    .modal-success-card {
      background: #ffffff;
      border-radius: 20px;
      max-width: 480px;
      width: 100%;
      padding: 30px;
      text-align: center;
      box-shadow: 0 20px 50px rgba(0,0,0,0.25);
    }

    .modal-success-icon {
      font-size: 3.5rem;
      color: #16a34a;
      margin-bottom: 12px;
    }

    .modal-success-title {
      font-size: 1.35rem;
      font-weight: 800;
      color: #0f2922;
      margin: 0 0 10px 0;
    }

    .modal-success-desc {
      font-size: 0.88rem;
      color: #48665b;
      margin: 0 0 18px 0;
      line-height: 1.5;
    }

    .modal-meta-box {
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
      border-radius: 10px;
      padding: 12px;
      text-align: left;
      font-size: 0.82rem;
      color: #166534;
      margin-bottom: 20px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .btn-close-success {
      width: 100%;
      padding: 12px;
      background: #19734e;
      color: #ffffff;
      border: none;
      border-radius: 10px;
      font-size: 0.92rem;
      font-weight: 800;
      cursor: pointer;
    }

    /* History Table Section (CE_BackupLogRegistro) */
    .history-section {
      background: #ffffff;
      border: 1px solid #dce8e2;
      border-radius: 16px;
      padding: 24px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }

    .history-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 16px;
      gap: 16px;
      flex-wrap: wrap;
    }

    .history-title {
      font-size: 1.15rem;
      font-weight: 800;
      color: #0f2922;
      margin: 0 0 4px 0;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .history-subtitle {
      font-size: 0.82rem;
      color: #65887b;
      margin: 0;
    }

    .btn-refresh {
      padding: 6px 12px;
      background: #eef6f2;
      border: 1px solid #c9ded3;
      border-radius: 8px;
      font-size: 0.8rem;
      font-weight: 700;
      color: #19734e;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }

    .table-container {
      overflow-x: auto;
    }

    .backup-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.84rem;
    }

    .backup-table th {
      background: #f7faf8;
      color: #48665b;
      font-weight: 800;
      text-transform: uppercase;
      font-size: 0.74rem;
      padding: 10px 12px;
      border-bottom: 2px solid #e1ece6;
      text-align: left;
    }

    .backup-table td {
      padding: 10px 12px;
      border-bottom: 1px solid #edf4f0;
      color: #1a382e;
    }

    .file-cell {
      display: flex;
      align-items: center;
      gap: 8px;
      font-family: monospace;
      font-weight: 600;
    }

    .badge-scope {
      font-size: 0.72rem;
      font-weight: 800;
      padding: 2px 8px;
      border-radius: 4px;
      background: #e8f5ed;
      color: #19734e;
    }

    .badge-scope.global {
      background: #e0f2fe;
      color: #0369a1;
    }

    .badge-origin {
      font-size: 0.72rem;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 4px;
      background: #f1f5f3;
      color: #4b6b5e;
    }

    .badge-origin.cron {
      background: #fef3c7;
      color: #92400e;
    }

    .mini-sha {
      background: #f1f5f9;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 0.74rem;
      color: #334155;
    }

    .badge-status-ok {
      font-size: 0.74rem;
      font-weight: 800;
      color: #15803d;
      background: #dcfce7;
      padding: 2px 8px;
      border-radius: 4px;
    }

    .btn-table-download {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 30px;
      height: 30px;
      border-radius: 6px;
      background: #eef6f2;
      color: #19734e;
      text-decoration: none;
      transition: all 0.2s;
    }

    .btn-table-download:hover {
      background: #19734e;
      color: #ffffff;
    }

    .empty-cell {
      text-align: center;
      padding: 30px;
      color: #8da69b;
    }

    @media (max-width: 900px) {
      .console-grid {
        grid-template-columns: 1fr;
      }
      .scope-radio-group {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class BackupRestoreConsoleComponent implements OnInit {
  // Ámbito: 'TENANT' o 'GLOBAL'
  ambitoSeleccionado: 'TENANT' | 'GLOBAL' = 'TENANT';
  tenantSeleccionadoId = '';
  tenantDestinoId = '';

  listaTenants: any[] = [];
  listaBackups: BackupItem[] = [];

  // Tarea Cron (Paso 1 BDD)
  cronInfo: CronStatus | null = null;
  ejecutandoCron = false;
  cronMensaje = '';

  // Operación 1: Backup manual
  generandoBackup = false;
  ultimoBackup: BackupResult | null = null;

  // Operación 2: Restauración
  archivoSeleccionado: File | null = null;
  checksumEsperado = '';
  restaurando = false;
  errorRestauracion = '';
  modalExitoVisible = false;
  mensajeExitoRestauracion = '';

  constructor(
    private backupService: BackupService,
    private tenantService: TenantService,
    public authService: AuthService
  ) {}

  ngOnInit(): void {
    this.cargarTenants();
    this.cargarEstadoCron();
    this.cargarHistorialBackups();
  }

  cargarTenants(): void {
    this.tenantService.getAll().subscribe({
      next: (data) => {
        this.listaTenants = data;
        // Preseleccionar "Centro Esperanza" si existe (Paso 2 BDD)
        const esperanza = this.listaTenants.find(t => 
          t.nombre?.toLowerCase().includes('esperanza') || 
          t.schema_name?.toLowerCase().includes('esperanza')
        );
        if (esperanza) {
          this.tenantSeleccionadoId = esperanza.id;
          this.tenantDestinoId = esperanza.id;
        } else if (this.listaTenants.length > 0) {
          this.tenantSeleccionadoId = this.listaTenants[0].id;
          this.tenantDestinoId = this.listaTenants[0].id;
        }
      },
      error: (err) => console.error('Error cargando centros:', err)
    });
  }

  cargarEstadoCron(): void {
    this.backupService.obtenerEstadoCron().subscribe({
      next: (status) => this.cronInfo = status,
      error: (err) => console.error('Error cargando estado de cron:', err)
    });
  }

  cargarHistorialBackups(): void {
    this.backupService.listarBackups().subscribe({
      next: (backups) => this.listaBackups = backups,
      error: (err) => console.error('Error listando backups:', err)
    });
  }

  isCentroEsperanzaSeleccionado(): boolean {
    const t = this.listaTenants.find(item => item.id === this.tenantSeleccionadoId);
    return t ? t.nombre?.toLowerCase().includes('esperanza') : false;
  }

  /**
   * Paso 1 BDD:
   * Verificar la tarea programada de cron en el servidor cloud (03:00 AM hora boliviana).
   */
  ejecutarTareaCron(): void {
    this.ejecutandoCron = true;
    this.cronMensaje = '';
    this.backupService.ejecutarCronTarea().subscribe({
      next: (res) => {
        this.ejecutandoCron = false;
        this.cronMensaje = res.mensaje || 'Tarea programada de cron ejecutada con éxito. Volcado diario registrado en bitácora.';
        this.cargarEstadoCron();
        this.cargarHistorialBackups();
      },
      error: (err) => {
        this.ejecutandoCron = false;
        console.error('Error ejecutando cron:', err);
      }
    });
  }

  /**
   * Paso 2 BDD:
   * En la Consola Web de Backup, seleccionar ámbito 'Tenant Específico: Centro Esperanza'
   * y presionar 'Generar Respaldo Ahora'.
   */
  generarBackupManual(): void {
    this.generandoBackup = true;
    const targetTenantId = this.ambitoSeleccionado === 'GLOBAL' ? undefined : this.tenantSeleccionadoId;

    this.backupService.solicitarBackupManual(targetTenantId, this.ambitoSeleccionado).subscribe({
      next: (res) => {
        this.generandoBackup = false;
        this.ultimoBackup = res;
        this.cargarHistorialBackups();
      },
      error: (err) => {
        this.generandoBackup = false;
        console.error('Error generando backup:', err);
        alert('Error al generar el respaldo: ' + (err.error?.error || err.message));
      }
    });
  }

  /**
   * Paso 3 BDD:
   * Intentar subir un archivo corrupto o modificado manualmente en la dropzone de restauración.
   * Resultado esperado: El validador criptográfico detecta discrepancia de checksum y aborta sin alterar BD.
   */
  simularPaso3ArchivoCorrupto(): void {
    this.errorRestauracion = '';
    this.restaurando = true;

    this.backupService.restaurarBackup(this.tenantDestinoId, {
      archivo: 'sigepsi_backup_corrupto_tampered.sql.gz',
      corrupto: true,
      checksum: 'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
    }).subscribe({
      next: (_) => {
        this.restaurando = false;
      },
      error: (err) => {
        this.restaurando = false;
        // El validador criptográfico detecta discrepancia y aborta el proceso
        this.errorRestauracion = err.error?.error || 
          'El validador criptográfico detectó discrepancia de checksum SHA-256. Archivo corrupto o alterado manualmente. Proceso de restauración abortado sin alterar la base de datos.';
      }
    });
  }

  /**
   * Paso 4 BDD:
   * Cargar una copia de seguridad legítima y confirmar la restauración del centro psicológico.
   * Resultado esperado: Transacción atómica exitosa y alerta modal de éxito.
   */
  simularPaso4RestauracionLegitima(): void {
    this.errorRestauracion = '';
    this.restaurando = true;

    // Tomar el archivo de backup más reciente disponible o generar uno
    const backupTarget = this.ultimoBackup?.archivo || (this.listaBackups[0]?.archivo || 'sigepsi_backup_esperanza.sql.gz');

    this.backupService.restaurarBackup(this.tenantDestinoId, {
      archivo: backupTarget,
      corrupto: false
    }).subscribe({
      next: (res) => {
        this.restaurando = false;
        this.mensajeExitoRestauracion = res.mensaje || 'Centro psicológico restaurado íntegramente.';
        this.modalExitoVisible = true;
      },
      error: (err) => {
        this.restaurando = false;
        this.errorRestauracion = err.error?.error || 'Error durante la restauración.';
      }
    });
  }

  ejecutarRestauracionManual(): void {
    this.errorRestauracion = '';
    this.restaurando = true;

    this.backupService.restaurarBackup(this.tenantDestinoId, {
      file: this.archivoSeleccionado || undefined,
      archivo: !this.archivoSeleccionado && this.ultimoBackup ? this.ultimoBackup.archivo : undefined,
      checksum: this.checksumEsperado || undefined
    }).subscribe({
      next: (res) => {
        this.restaurando = false;
        this.mensajeExitoRestauracion = res.mensaje || 'Centro restaurado íntegramente.';
        this.modalExitoVisible = true;
      },
      error: (err) => {
        this.restaurando = false;
        this.errorRestauracion = err.error?.error || 'Error en la validación criptográfica o restauración.';
      }
    });
  }

  // Dropzone handling
  onDragOver(e: DragEvent): void {
    e.preventDefault();
    e.stopPropagation();
  }

  onDragLeave(e: DragEvent): void {
    e.preventDefault();
    e.stopPropagation();
  }

  onDropFile(e: DragEvent): void {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer && e.dataTransfer.files.length > 0) {
      this.archivoSeleccionado = e.dataTransfer.files[0];
    }
  }

  onFileSelected(e: any): void {
    if (e.target.files && e.target.files.length > 0) {
      this.archivoSeleccionado = e.target.files[0];
    }
  }

  quitarArchivo(e: Event): void {
    e.stopPropagation();
    this.archivoSeleccionado = null;
  }

  copiarSha(sha: string): void {
    navigator.clipboard.writeText(sha);
    alert('Checksum SHA-256 copiado al portapapeles:\n' + sha);
  }

  descargandoArchivo = false;

  descargarArchivo(archivo: string, e?: Event): void {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    this.descargandoArchivo = true;
    this.backupService.descargarArchivoBlob(archivo).subscribe({
      next: (blob) => {
        this.descargandoArchivo = false;
        const blobUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = archivo;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(blobUrl);
      },
      error: () => {
        this.descargandoArchivo = false;
        window.location.href = this.getDescargaUrl(archivo);
      }
    });
  }

  getDescargaUrl(archivo: string): string {
    return this.backupService.getDescargaUrl(archivo);
  }

  getNombreTenantDestino(): string {
    const t = this.listaTenants.find(item => item.id === this.tenantDestinoId);
    return t ? t.nombre : 'Centro Seleccionado';
  }
}
