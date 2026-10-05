// ==============================================================================
// MÓDULO: consentimientos-hub.component.ts
// CAPA BCE: BOUNDARY (Interfaz de Usuario) — IU_ConsentimientosInformados
// CASOS DE USO: CU18: Consentimiento Informado Digital y Sellado Criptográfico (HU-31, HU-32)
// DESCRIPCIÓN: Gestión de plantillas con variables dinámicas, lienzo de firma manuscrita
//              digital (touch/mouse), sello SHA-256, descarga en PDF y revocación.
// ==============================================================================
import { Component, OnInit, ViewChild, ElementRef, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ClinicaSprint2Service } from '../../core/services/clinica-sprint2.service';
import { ClinicaService } from '../../core/services/clinica.service';
import { ConsentimientoInformado, FirmaConsentimiento } from '../../core/models/clinica-sprint2.model';
import { Paciente } from '../../core/models';

@Component({
  selector: 'app-consentimientos-hub',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="consent-container">
      
      <!-- Encabezado -->
      <div class="page-header glass-panel mb-4">
        <div>
          <h1 class="page-title">
            <i class="fa-solid fa-file-signature text-primary"></i> Consentimientos Informados Digitales
          </h1>
          <p class="page-subtitle">
            Plantillas dinámicas con variables, captura biométrica de firma en pantalla táctil y sellado criptográfico SHA-256 (Sprint 2 - HU-31, HU-32).
          </p>
        </div>
        <div class="header-actions">
          <button class="btn btn-outline-primary me-2" (click)="abrirModalPlantilla()">
            <i class="fa-solid fa-file-circle-plus"></i> Nueva Plantilla
          </button>
          <button class="btn btn-primary" (click)="abrirModalFirmaDigital()">
            <i class="fa-solid fa-signature"></i> Registrar Firma de Paciente
          </button>
        </div>
      </div>

      <!-- Navegación por pestañas -->
      <div class="tabs-bar glass-panel mb-4">
        <button class="tab-btn" [class.active]="activeTab === 'firmas'" (click)="activeTab = 'firmas'">
          <i class="fa-solid fa-stamp"></i> Firmas Registradas y Selladas ({{ firmas().length }})
        </button>
        <button class="tab-btn" [class.active]="activeTab === 'plantillas'" (click)="activeTab = 'plantillas'">
          <i class="fa-solid fa-file-lines"></i> Plantillas Disponibles ({{ plantillas().length }})
        </button>
      </div>

      <!-- Mensajes Feedback -->
      <div *ngIf="mensajeAviso()" class="alert alert-success d-flex align-items-center mb-4">
        <i class="fa-solid fa-circle-check me-2"></i>
        <span>{{ mensajeAviso() }}</span>
      </div>

      <!-- TAB 1: FIRMAS REGISTRADAS -->
      <div *ngIf="activeTab === 'firmas'">
        <div *ngIf="cargando()" class="loading-state glass-panel text-center p-5">
          <i class="fa-solid fa-spinner fa-spin fa-2x text-primary mb-3"></i>
          <p class="text-muted">Cargando consentimientos firmados...</p>
        </div>

        <div *ngIf="!cargando() && firmas().length === 0" class="empty-state glass-panel text-center p-5">
          <i class="fa-solid fa-signature fa-3x text-dim mb-3"></i>
          <h3>No hay consentimientos informados firmados</h3>
          <p class="text-muted">Presione "Registrar Firma de Paciente" para hacer firmar el documento de inicio de tratamiento.</p>
        </div>

        <div class="table-responsive glass-panel" *ngIf="!cargando() && firmas().length > 0">
          <table class="custom-table">
            <thead>
              <tr>
                <th>Paciente</th>
                <th>Plantilla Legal</th>
                <th>Fecha y Hora</th>
                <th>IP de Origen</th>
                <th>Sello Criptográfico (SHA-256)</th>
                <th>Estado</th>
                <th class="text-end">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let f of firmas()">
                <td>
                  <div class="patient-cell">
                    <div class="avatar-sm">{{ (f.paciente_nombre || 'P').charAt(0) }}</div>
                    <strong>{{ f.paciente_nombre }}</strong>
                  </div>
                </td>
                <td>{{ f.plantilla_titulo || 'Consentimiento de Tratamiento' }}</td>
                <td>{{ f.fecha_firma | date:'dd/MM/yyyy HH:mm' }}</td>
                <td><code class="small text-muted">{{ f.ip_origen || '127.0.0.1' }}</code></td>
                <td>
                  <div class="hash-box-small" [title]="f.hash_integridad">
                    <i class="fa-solid fa-fingerprint text-accent me-1"></i>
                    <code class="hash-txt">{{ f.hash_integridad.substring(0, 16) }}...</code>
                  </div>
                </td>
                <td>
                  <span class="status-pill" [class.active]="!f.revocado" [class.revoked]="f.revocado">
                    {{ f.revocado ? 'REVOCADO' : 'VIGENTE' }}
                  </span>
                </td>
                <td class="text-end">
                  <button class="btn btn-sm btn-outline-danger me-2" (click)="descargarPdf(f.id)" title="Descargar orden PDF firmada">
                    <i class="fa-solid fa-file-pdf"></i> PDF
                  </button>
                  <button class="btn btn-sm btn-outline-secondary" *ngIf="!f.revocado" (click)="abrirModalRevocar(f)" title="Revocar consentimiento">
                    <i class="fa-solid fa-ban"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- TAB 2: PLANTILLAS LEGALES -->
      <div *ngIf="activeTab === 'plantillas'">
        <div class="plantillas-grid">
          <div class="plantilla-card glass-panel" *ngFor="let p of plantillas()">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <span class="badge bg-light text-dark font-monospace">{{ p.codigo_plantilla }}</span>
              <span class="badge bg-info text-white">v{{ p.version }}.0</span>
            </div>
            <h3 class="plantilla-title">{{ p.titulo }}</h3>
            <div class="preview-text-box small text-muted p-2 rounded bg-light mb-3">
              {{ p.cuerpo_plantilla.substring(0, 180) }}...
            </div>
            <div class="d-flex justify-content-between align-items-center">
              <span class="small text-muted"><i class="fa-solid fa-calendar me-1"></i> {{ p.fecha_creacion | date:'dd/MM/yyyy' }}</span>
              <button class="btn btn-sm btn-outline-primary" (click)="verPlantilla(p)">
                <i class="fa-solid fa-eye me-1"></i> Ver Plantilla
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- MODAL NUEVA / EDITAR PLANTILLA -->
      <div *ngIf="mostrarModalPlantillaForm" class="modal-backdrop-custom" (click)="mostrarModalPlantillaForm = false">
        <div class="modal-dialog-custom glass-card-modal modal-lg" (click)="$event.stopPropagation()">
          <div class="modal-header-custom">
            <div class="d-flex align-items-center gap-3">
              <div class="modal-icon-badge">
                <i class="fa-solid fa-file-contract"></i>
              </div>
              <div>
                <h2 class="modal-title-clean">Plantilla de Consentimiento</h2>
                <p class="modal-subtitle-clean">Definición de cláusulas normativas y tags legales automatizados</p>
              </div>
            </div>
            <button class="btn-close-modern" (click)="mostrarModalPlantillaForm = false" title="Cerrar ventana">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>
          <div class="modal-body-custom p-4">
            <!-- Grid de 3 columnas para Metadatos -->
            <div class="plantilla-meta-grid mb-3">
              <div class="form-group-clean">
                <label class="clean-label">Código Único <span class="req">*</span></label>
                <input type="text" class="clean-input font-monospace" [(ngModel)]="plantillaForm.codigo_plantilla" placeholder="Ej. CI-PSIC-2026" />
              </div>
              <div class="form-group-clean">
                <label class="clean-label">Título Oficial <span class="req">*</span></label>
                <input type="text" class="clean-input" [(ngModel)]="plantillaForm.titulo" placeholder="Ej. Consentimiento Informado para Tratamiento Psicoterapéutico" />
              </div>
              <div class="form-group-clean">
                <label class="clean-label">Versión Legal <span class="req">*</span></label>
                <input type="text" class="clean-input font-monospace text-center" [(ngModel)]="plantillaForm.version" placeholder="v1.0" />
              </div>
            </div>

            <!-- Panel de Variables Dinámicas Interactivas (HU-31) -->
            <div class="variables-panel mb-3">
              <div class="variables-panel-header">
                <i class="fa-solid fa-wand-magic-sparkles text-success me-1"></i>
                <span class="variables-panel-title">Variables Dinámicas Soportadas (Haz clic para insertar en el texto):</span>
              </div>
              <div class="variables-chips-row">
                <button type="button" class="variable-chip" (click)="insertarVariable('{paciente_nombre}')" title="Insertar nombre del paciente">
                  <code>&#123;paciente_nombre&#125;</code>
                  <span class="chip-label">Nombre Paciente</span>
                </button>
                <button type="button" class="variable-chip" (click)="insertarVariable('{ci}')" title="Insertar cédula de identidad">
                  <code>&#123;ci&#125;</code>
                  <span class="chip-label">Cédula / DNI</span>
                </button>
                <button type="button" class="variable-chip" (click)="insertarVariable('{psicologo}')" title="Insertar terapeuta tratante">
                  <code>&#123;psicologo&#125;</code>
                  <span class="chip-label">Terapeuta</span>
                </button>
                <button type="button" class="variable-chip" (click)="insertarVariable('{centro}')" title="Insertar nombre de la clínica">
                  <code>&#123;centro&#125;</code>
                  <span class="chip-label">Clínica</span>
                </button>
                <button type="button" class="variable-chip" (click)="insertarVariable('{fecha}')" title="Insertar fecha de emisión">
                  <code>&#123;fecha&#125;</code>
                  <span class="chip-label">Fecha</span>
                </button>
                <button type="button" class="variable-chip" (click)="insertarVariable('{version}')" title="Insertar versión legal">
                  <code>&#123;version&#125;</code>
                  <span class="chip-label">Versión</span>
                </button>
              </div>
            </div>

            <!-- Cuerpo del Consentimiento -->
            <div class="form-group-clean mb-2">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="clean-label mb-0">Cuerpo del Consentimiento Legal <span class="req">*</span></label>
                <span class="small text-muted">Texto normativo estructurado con soporte de tags dinámicos</span>
              </div>
              <textarea class="clean-textarea font-monospace" rows="8" [(ngModel)]="plantillaForm.cuerpo_plantilla"
                        placeholder="Por medio del presente documento, yo, {paciente_nombre}, con Cédula {ci}..."></textarea>
            </div>
          </div>
          <div class="modal-footer-custom p-3">
            <button class="btn btn-secondary" (click)="mostrarModalPlantillaForm = false">
              <i class="fa-solid fa-xmark me-1"></i> Cerrar
            </button>
            <button class="btn btn-primary" [disabled]="!plantillaForm.codigo_plantilla || !plantillaForm.cuerpo_plantilla" (click)="guardarPlantilla()">
              <i class="fa-solid fa-floppy-disk me-1"></i> Guardar Plantilla
            </button>
          </div>
        </div>
      </div>

      <!-- MODAL FIRMAR CONSENTIMIENTO DIGITAL (CANVAS DE FIRMA TOUCH / MOUSE) -->
      <div *ngIf="mostrarModalFirma" class="modal-backdrop-custom" (click)="cerrarModalFirma()">
        <div class="modal-dialog-custom glass-card-modal modal-lg" (click)="$event.stopPropagation()">
          <div class="modal-header-custom">
            <div class="d-flex align-items-center gap-3">
              <div class="modal-icon-badge">
                <i class="fa-solid fa-pen-clip"></i>
              </div>
              <div>
                <h2 class="modal-title-clean">Captura de Firma Digital</h2>
                <p class="modal-subtitle-clean">Lienzo biométrico táctil y sellado criptográfico SHA-256</p>
              </div>
            </div>
            <button class="btn-close-modern" (click)="cerrarModalFirma()" title="Cerrar ventana">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>
          <div class="modal-body-custom p-4">

            <!-- Alerta automática para menores de edad (HU-31 Criterio b) -->
            <div *ngIf="avisoMenorEdad" class="alert alert-warning d-flex align-items-center mb-3">
              <i class="fa-solid fa-user-shield me-2 fa-lg text-warning"></i>
              <span>{{ avisoMenorEdad }}</span>
            </div>
            
            <div class="firma-selects-grid mb-3">
              <div class="form-group-clean">
                <label class="clean-label">Seleccionar Paciente <span class="req">*</span></label>
                <select class="clean-input clean-select" [(ngModel)]="firmaForm.paciente" (ngModelChange)="onPacienteChange()">
                  <option value="" disabled selected>-- Elija paciente --</option>
                  <option *ngFor="let pac of pacientes()" [value]="pac.id">
                    {{ pac.usuario.nombre }} {{ pac.usuario.apellido }} (CI: {{ pac.ci }})
                  </option>
                </select>
              </div>

              <div class="form-group-clean">
                <label class="clean-label">Plantilla a Firmar <span class="req">*</span></label>
                <select class="clean-input clean-select" [(ngModel)]="firmaForm.plantilla" (ngModelChange)="actualizarVistaPreviaTexto()">
                  <option value="" disabled selected>-- Elija plantilla --</option>
                  <option *ngFor="let pl of plantillas()" [value]="pl.id">
                    {{ pl.titulo }} ({{ pl.version || 'v1.0' }})
                  </option>
                </select>
              </div>
            </div>

            <!-- Vista Previa del Documento con Variables Reemplazadas -->
            <div class="document-preview-box glass-panel p-3 mb-3 small">
              <h5 class="small fw-bold text-muted text-uppercase mb-2">Lectura del Documento Legal</h5>
              <div class="document-text">{{ textoRenderizadoPreview }}</div>
            </div>

            <!-- Lienzo de Firma Digital (Canvas) -->
            <div class="signature-canvas-section mb-3">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <label class="clean-label m-0 fw-bold">
                  <i class="fa-solid fa-signature text-success me-1"></i> Firma del Paciente / Tutor en Pantalla
                </label>
                <button class="btn btn-sm btn-outline-danger" (click)="limpiarLienzo()">
                  <i class="fa-solid fa-rotate-left me-1"></i> Limpiar Firma
                </button>
              </div>

              <div class="canvas-wrapper">
                <canvas 
                  #signatureCanvas 
                  width="700" 
                  height="160" 
                  class="signature-canvas"
                  (mousedown)="iniciarTrazo($event)"
                  (mousemove)="dibujarTrazo($event)"
                  (mouseup)="finalizarTrazo()"
                  (touchstart)="iniciarTrazoTouch($event)"
                  (touchmove)="dibujarTrazoTouch($event)"
                  (touchend)="finalizarTrazo()">
                </canvas>
                <div class="signature-line-guide">Firme sobre la línea</div>
              </div>
            </div>

            <div class="form-check">
              <input class="form-check-input" type="checkbox" [(ngModel)]="firmaForm.confirmado" id="chkConsent" />
              <label class="form-check-label small" for="chkConsent">
                Declaro haber leído detenidamente las condiciones del servicio, alcances del secreto profesional y excepciones de ley.
              </label>
            </div>

          </div>

          <div class="modal-footer-custom p-3">
            <button class="btn btn-secondary" (click)="cerrarModalFirma()">Cancelar</button>
            <button 
              class="btn btn-primary" 
              [disabled]="!firmaForm.paciente || !firmaForm.plantilla || !firmaForm.confirmado || !hayTrazoFirma"
              (click)="guardarFirmaDigital()">
              <i class="fa-solid fa-lock me-1"></i> Sellar y Registrar Consentimiento (SHA-256)
            </button>
          </div>
        </div>
      </div>

      <!-- MODAL REVOCAR -->
      <div *ngIf="firmaParaRevocar" class="modal-backdrop-custom" (click)="firmaParaRevocar = null">
        <div class="modal-dialog-custom glass-card-modal modal-md" (click)="$event.stopPropagation()">
          <div class="modal-header-custom">
            <div class="d-flex align-items-center gap-3">
              <div class="modal-icon-badge" style="background: #fee2e2; color: #dc2626;">
                <i class="fa-solid fa-ban"></i>
              </div>
              <div>
                <h2 class="modal-title-clean text-danger">Revocar Consentimiento Informado</h2>
                <p class="modal-subtitle-clean">Registro formal de desistimiento o anulación legal</p>
              </div>
            </div>
            <button class="btn-close-modern" (click)="firmaParaRevocar = null" title="Cerrar ventana">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>
          <div class="modal-body-custom p-4">
            <p class="small text-muted mb-2">
              El paciente o su tutor legal ha solicitado la rescisión del consentimiento. Indique el motivo legal del desistimiento:
            </p>
            <textarea class="clean-textarea" rows="3" [(ngModel)]="motivoRevocacion" placeholder="Motivo de la revocación..."></textarea>
          </div>
          <div class="modal-footer-custom p-3">
            <button class="btn btn-secondary" (click)="firmaParaRevocar = null">Cancelar</button>
            <button class="btn btn-danger" [disabled]="!motivoRevocacion.trim()" (click)="confirmarRevocacion()">
              Confirmar Revocación
            </button>
          </div>
        </div>
      </div>

    </div>
  `,
  styles: [`
    .consent-container { max-width: 1300px; margin: 0 auto; }
    .page-header {
      padding: 1.5rem 2rem; border-radius: 16px; background: #ffffff;
      border: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center;
    }
    .page-title { font-size: 1.5rem; font-weight: 700; color: #0f172a; margin: 0 0 0.25rem 0; }
    .page-subtitle { font-size: 0.88rem; color: #64748b; margin: 0; }

    .tabs-bar { display: flex; gap: 0.5rem; padding: 0.5rem; background: #f1f5f9; border-radius: 12px; }
    .tab-btn {
      padding: 0.65rem 1.25rem; border: none; background: transparent; color: #64748b;
      font-weight: 600; font-size: 0.9rem; border-radius: 8px; cursor: pointer;
      display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s;
    }
    .tab-btn.active { background: #ffffff; color: #0284c7; box-shadow: 0 2px 4px rgba(0,0,0,0.06); }

    .custom-table { width: 100%; border-collapse: collapse; background: #ffffff; border-radius: 12px; }
    .custom-table th { background: #f8fafc; padding: 0.85rem 1rem; font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; }
    .custom-table td { padding: 0.85rem 1rem; font-size: 0.85rem; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }

    .patient-cell { display: flex; align-items: center; gap: 0.6rem; }
    .avatar-sm {
      width: 32px; height: 32px; border-radius: 50%; background: #e0e7ff; color: #4338ca;
      font-weight: 700; display: flex; align-items: center; justify-content: center;
    }

    .hash-box-small { display: flex; align-items: center; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 4px; padding: 0.2rem 0.5rem; }
    .hash-txt { font-family: monospace; font-size: 0.75rem; color: #0284c7; }

    .status-pill { font-size: 0.72rem; font-weight: 700; padding: 0.2rem 0.6rem; border-radius: 9999px; }
    .status-pill.active { background: #dcfce7; color: #166534; }
    .status-pill.revoked { background: #fee2e2; color: #991b1b; }

    .plantillas-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 1.25rem; }
    .plantilla-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 1.25rem; }
    .plantilla-title { font-size: 1.05rem; font-weight: 700; color: #0f172a; margin: 0 0 0.5rem 0; }
    .preview-text-box { background: #f8fafc; border: 1px dashed #cbd5e1; max-height: 90px; overflow: hidden; line-height: 1.4; }

    .document-preview-box { background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; max-height: 180px; overflow-y: auto; }
    .document-text { white-space: pre-line; line-height: 1.5; color: #1e293b; }

    .canvas-wrapper {
      position: relative; border: 2px dashed #cbd5e1; border-radius: 8px;
      background: #ffffff; text-align: center; overflow: hidden;
    }
    .signature-canvas { width: 100%; height: 160px; touch-action: none; cursor: crosshair; }
    .signature-line-guide {
      position: absolute; bottom: 30px; left: 10%; right: 10%; border-top: 1px solid #e2e8f0;
      color: #94a3b8; font-size: 0.75rem; pointer-events: none;
    }

    .modal-backdrop-custom {
      position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
      background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px); z-index: 1050;
      display: flex; align-items: center; justify-content: center; padding: 1rem;
      overflow-y: auto;
    }
    .modal-dialog-custom {
      width: 100%; background: #ffffff; border-radius: 16px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
      display: flex; flex-direction: column;
      max-height: calc(100vh - 2rem);
      margin: auto;
    }
    .modal-md { max-width: 600px; }
    .modal-lg { max-width: 800px; }
    .modal-header-custom { padding: 1rem 1.5rem; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; flex-shrink: 0; }
    .modal-body-custom { padding: 1.25rem 1.5rem; overflow-y: auto; flex: 1 1 auto; }
    .modal-footer-custom { padding: 0.85rem 1.5rem; border-top: 1px solid #e2e8f0; background: #f8fafc; display: flex; justify-content: flex-end; gap: 0.75rem; flex-shrink: 0; }

    .modal-title-clean {
      font-size: 1.25rem;
      font-weight: 700;
      color: #0f2922;
      margin: 0;
      line-height: 1.2;
    }
    .modal-subtitle-clean {
      font-size: 0.8rem;
      color: #557164;
      margin: 2px 0 0 0;
    }
    .modal-icon-badge {
      width: 40px;
      height: 40px;
      border-radius: 10px;
      background: #e6f5ed;
      color: #19734e;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.2rem;
      flex-shrink: 0;
    }
    .btn-close-modern {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      border: 1px solid #e2e8f0;
      background: #f8fafc;
      color: #64748b;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s ease;
    }
    .btn-close-modern:hover {
      background: #fee2e2;
      border-color: #fecaca;
      color: #dc2626;
    }
    .plantilla-meta-grid {
      display: grid;
      grid-template-columns: 160px 1fr 110px;
      gap: 12px;
    }
    @media (max-width: 680px) {
      .plantilla-meta-grid {
        grid-template-columns: 1fr;
      }
    }
    .firma-selects-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }
    @media (max-width: 680px) {
      .firma-selects-grid {
        grid-template-columns: 1fr;
      }
    }
    .clean-select {
      cursor: pointer;
    }
    .form-group-clean {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .clean-label {
      font-size: 0.82rem;
      font-weight: 600;
      color: #1e293b;
      letter-spacing: 0.2px;
      text-transform: none;
    }
    .clean-label .req {
      color: #dc2626;
      font-weight: 700;
    }
    .clean-input {
      width: 100%;
      padding: 9px 12px;
      border: 1.5px solid #d1ded6;
      border-radius: 8px;
      font-size: 0.9rem;
      color: #0f2922;
      background: #ffffff;
      transition: all 0.2s;
    }
    .clean-input:focus {
      border-color: #19734e;
      box-shadow: 0 0 0 3px rgba(25, 115, 78, 0.15);
      outline: none;
    }
    .clean-textarea {
      width: 100%;
      padding: 12px 14px;
      border: 1.5px solid #d1ded6;
      border-radius: 10px;
      font-size: 0.88rem;
      line-height: 1.6;
      color: #1e293b;
      background: #ffffff;
      resize: vertical;
      transition: all 0.2s;
    }
    .clean-textarea:focus {
      border-color: #19734e;
      box-shadow: 0 0 0 3px rgba(25, 115, 78, 0.15);
      outline: none;
    }
    .variables-panel {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 10px 14px;
    }
    .variables-panel-header {
      font-size: 0.8rem;
      font-weight: 600;
      color: #334155;
      margin-bottom: 8px;
      display: flex;
      align-items: center;
    }
    .variables-chips-row {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    .variable-chip {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      padding: 4px 10px;
      cursor: pointer;
      font-size: 0.8rem;
      transition: all 0.15s ease;
      color: #0f172a;
    }
    .variable-chip code {
      color: #0284c7;
      font-weight: 700;
      font-size: 0.82rem;
    }
    .variable-chip .chip-label {
      color: #64748b;
      font-size: 0.74rem;
    }
    .variable-chip:hover {
      background: #e0f2fe;
      border-color: #38bdf8;
      transform: translateY(-1px);
    }
  `]
})
export class ConsentimientosHubComponent implements OnInit {
  activeTab: 'firmas' | 'plantillas' = 'firmas';
  cargando = signal<boolean>(true);
  firmas = signal<FirmaConsentimiento[]>([]);
  plantillas = signal<ConsentimientoInformado[]>([]);
  pacientes = signal<Paciente[]>([]);
  mensajeAviso = signal<string | null>(null);
  avisoMenorEdad = '';
  esMenorDetectado = false;

  // Plantilla Modal
  mostrarModalPlantillaForm = false;
  plantillaForm = {
    id: '',
    codigo_plantilla: '',
    titulo: '',
    cuerpo_plantilla: '',
    version: 'v1.0'
  };

  // Firma Modal
  mostrarModalFirma = false;
  firmaForm = {
    paciente: '',
    plantilla: '',
    confirmado: false
  };
  textoRenderizadoPreview = '';
  hayTrazoFirma = false;

  // Revocation
  firmaParaRevocar: FirmaConsentimiento | null = null;
  motivoRevocacion = '';

  @ViewChild('signatureCanvas') canvasRef?: ElementRef<HTMLCanvasElement>;
  private isDrawing = false;
  private ctx: CanvasRenderingContext2D | null = null;

  constructor(
    private clinicaService: ClinicaSprint2Service,
    private clinicaSprint1: ClinicaService
  ) {}

  ngOnInit(): void {
    this.cargarDatos();
  }

  cargarDatos(): void {
    this.cargando.set(true);
    this.clinicaService.getFirmasConsentimiento().subscribe({
      next: (fs) => {
        this.firmas.set(fs);
        this.clinicaService.getPlantillasConsentimiento().subscribe({
          next: (pls) => {
            this.plantillas.set(pls);
            this.clinicaSprint1.getPacientes().subscribe({
              next: (pacs) => {
                this.pacientes.set(pacs);
                this.cargando.set(false);
              },
              error: () => this.cargando.set(false)
            });
          },
          error: () => this.cargando.set(false)
        });
      },
      error: () => this.cargando.set(false)
    });
  }

  abrirModalPlantilla(): void {
    this.plantillaForm = {
      id: '',
      codigo_plantilla: 'CI-PSIC-2026',
      titulo: 'Consentimiento Informado para Tratamiento Psicoterapéutico',
      cuerpo_plantilla: `Por medio del presente documento, yo, {paciente_nombre}, titular de la Cédula de Identidad N° {ci}, manifiesto de forma libre y voluntaria que he sido informado/a detalladamente sobre el proceso terapéutico a cargo de {psicologo} en el centro {centro}.\n\nSe me ha explicado la confidencialidad de la información y sus límites legales (riesgo inminente de daño hacia sí mismo o hacia terceros, o requerimiento judicial expreso).\n\nEn señal de conformidad y aceptación, se suscribe en la fecha {fecha} bajo la versión legal {version}.`,
      version: 'v1.0'
    };
    this.mostrarModalPlantillaForm = true;
  }

  verPlantilla(p: ConsentimientoInformado): void {
    this.plantillaForm = {
      id: p.id,
      codigo_plantilla: p.codigo_plantilla,
      titulo: p.titulo,
      cuerpo_plantilla: p.cuerpo_plantilla,
      version: (p as any).version || 'v1.0'
    };
    this.mostrarModalPlantillaForm = true;
  }

  insertarVariable(variable: string): void {
    if (!this.plantillaForm.cuerpo_plantilla) {
      this.plantillaForm.cuerpo_plantilla = variable;
    } else {
      this.plantillaForm.cuerpo_plantilla += ' ' + variable;
    }
  }

  guardarPlantilla(): void {
    this.clinicaService.crearPlantillaConsentimiento(this.plantillaForm as any).subscribe({
      next: () => {
        this.mostrarModalPlantillaForm = false;
        this.mostrarAvisoFeedback('Plantilla de consentimiento guardada');
        this.cargarDatos();
      }
    });
  }

  abrirModalFirmaDigital(): void {
    const primerPaciente = this.pacientes().length > 0 ? this.pacientes()[0].id : '';
    const primeraPlantilla = this.plantillas().length > 0 ? this.plantillas()[0].id : '';
    this.firmaForm = {
      paciente: primerPaciente,
      plantilla: primeraPlantilla,
      confirmado: false
    };
    this.hayTrazoFirma = false;
    this.mostrarModalFirma = true;
    this.onPacienteChange();

    setTimeout(() => {
      this.iniciarCanvasContext();
    }, 150);
  }

  onPacienteChange(): void {
    const pac = this.pacientes().find(p => p.id === this.firmaForm.paciente);
    if (!pac) {
      this.avisoMenorEdad = '';
      this.esMenorDetectado = false;
      this.actualizarVistaPreviaTexto();
      return;
    }

    let edad = pac.edad;
    if (edad === undefined && pac.fecha_nacimiento) {
      const hoy = new Date();
      const fn = new Date(pac.fecha_nacimiento);
      edad = hoy.getFullYear() - fn.getFullYear();
      const m = hoy.getMonth() - fn.getMonth();
      if (m < 0 || (m === 0 && hoy.getDate() < fn.getDate())) {
        edad--;
      }
    }

    if (edad !== undefined && edad < 18) {
      this.esMenorDetectado = true;
      const tutorTxt = pac.tutor_legal_nombre ? ` Tutor legal registrado: ${pac.tutor_legal_nombre} (CI: ${pac.tutor_legal_ci || 'N/A'}).` : '';
      this.avisoMenorEdad = `El paciente ${pac.usuario?.nombre || ''} ${pac.usuario?.apellido || ''} es MENOR DE EDAD (${edad} años). Se ha seleccionado automáticamente la plantilla legal de Autorización para Menores y Tutores Legales.${tutorTxt}`;

      // Selector automático de plantilla para menores de 18 años (HU-31 Criterio b)
      const plantMenor = this.plantillas().find(pl =>
        pl.codigo_plantilla === 'MENORES_EDAD' ||
        (pl as any).tipo === 'MENORES_EDAD' ||
        pl.titulo.toLowerCase().includes('menor') ||
        pl.titulo.toLowerCase().includes('tutor')
      );
      if (plantMenor) {
        this.firmaForm.plantilla = plantMenor.id;
      }
    } else {
      this.esMenorDetectado = false;
      this.avisoMenorEdad = '';
    }

    this.actualizarVistaPreviaTexto();
  }

  actualizarVistaPreviaTexto(): void {
    const pac = this.pacientes().find(p => p.id === this.firmaForm.paciente);
    const plant = this.plantillas().find(p => p.id === this.firmaForm.plantilla);

    if (!plant) {
      this.textoRenderizadoPreview = 'Seleccione una plantilla y un paciente para visualizar el documento personalizado.';
      return;
    }

    let t = plant.cuerpo_plantilla || (plant as any).contenido_legal || '';
    const nombre = pac ? `${pac.usuario?.nombre} ${pac.usuario?.apellido}` : '[NOMBRE_DEL_PACIENTE]';
    const ci = pac?.ci || '[CI_DEL_PACIENTE]';
    const tutorNombre = pac?.tutor_legal_nombre || (this.esMenorDetectado ? '[TUTOR_LEGAL_NOMBRE]' : '');
    const tutorCi = pac?.tutor_legal_ci || (this.esMenorDetectado ? '[TUTOR_LEGAL_CI]' : '');
    const hoy = new Date().toLocaleDateString('es-ES', { day: '2-digit', month: 'long', year: 'numeric' });
    const version = (plant as any).version || 'v1.0';

    // Sustitución interactiva de variables en tiempo real (HU-31 Criterio a):
    t = t.replace(/\{(?:paciente_nombre|PACIENTE_NOMBRE|nombre_paciente)\}/gi, nombre);
    t = t.replace(/\{(?:ci|PACIENTE_CI|ci_paciente)\}/gi, ci);
    t = t.replace(/\{(?:fecha|FECHA)\}/gi, hoy);
    t = t.replace(/\{(?:psicologo|PSICOLOGO_CABECERA|psicologo_cabecera)\}/gi, 'Equipo Psicológico SIGEPSI');
    t = t.replace(/\{(?:centro|CENTRO_NOMBRE|nombre_centro)\}/gi, 'Centro de Atención Psicológica SIGEPSI');
    t = t.replace(/\{(?:version|VERSION)\}/gi, version);
    t = t.replace(/\{(?:tutor_nombre|TUTOR_NOMBRE)\}/gi, tutorNombre);
    t = t.replace(/\{(?:tutor_ci|TUTOR_CI)\}/gi, tutorCi);

    this.textoRenderizadoPreview = t;
  }

  iniciarCanvasContext(): void {
    if (!this.canvasRef) return;
    const canvas = this.canvasRef.nativeElement;
    this.ctx = canvas.getContext('2d');
    if (this.ctx) {
      this.ctx.lineWidth = 2.5;
      this.ctx.lineCap = 'round';
      this.ctx.strokeStyle = '#0f172a';
    }
  }

  iniciarTrazo(e: MouseEvent): void {
    if (!this.ctx || !this.canvasRef) return;
    this.isDrawing = true;
    const rect = this.canvasRef.nativeElement.getBoundingClientRect();
    this.ctx.beginPath();
    this.ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top);
  }

  dibujarTrazo(e: MouseEvent): void {
    if (!this.isDrawing || !this.ctx || !this.canvasRef) return;
    const rect = this.canvasRef.nativeElement.getBoundingClientRect();
    this.ctx.lineTo(e.clientX - rect.left, e.clientY - rect.top);
    this.ctx.stroke();
    this.hayTrazoFirma = true;
  }

  iniciarTrazoTouch(e: TouchEvent): void {
    if (!this.ctx || !this.canvasRef || e.touches.length === 0) return;
    e.preventDefault();
    this.isDrawing = true;
    const rect = this.canvasRef.nativeElement.getBoundingClientRect();
    const touch = e.touches[0];
    this.ctx.beginPath();
    this.ctx.moveTo(touch.clientX - rect.left, touch.clientY - rect.top);
  }

  dibujarTrazoTouch(e: TouchEvent): void {
    if (!this.isDrawing || !this.ctx || !this.canvasRef || e.touches.length === 0) return;
    e.preventDefault();
    const rect = this.canvasRef.nativeElement.getBoundingClientRect();
    const touch = e.touches[0];
    this.ctx.lineTo(touch.clientX - rect.left, touch.clientY - rect.top);
    this.ctx.stroke();
    this.hayTrazoFirma = true;
  }

  finalizarTrazo(): void {
    this.isDrawing = false;
  }

  limpiarLienzo(): void {
    if (!this.ctx || !this.canvasRef) return;
    const canvas = this.canvasRef.nativeElement;
    this.ctx.clearRect(0, 0, canvas.width, canvas.height);
    this.hayTrazoFirma = false;
  }

  guardarFirmaDigital(): void {
    if (!this.canvasRef) return;
    const firmaBase64 = this.canvasRef.nativeElement.toDataURL('image/png');

    const payload = {
      plantilla: this.firmaForm.plantilla,
      paciente: this.firmaForm.paciente,
      contenido_final_renderizado: this.textoRenderizadoPreview,
      firma_imagen: firmaBase64
    };

    this.clinicaService.firmarConsentimiento(payload).subscribe({
      next: (f) => {
        this.cerrarModalFirma();
        const hashStr = (f.hash_sha256 || f.hash_integridad || '').substring(0, 8);
        this.mostrarAvisoFeedback(`Consentimiento sellado criptográficamente inmutable (Hash: ${hashStr}...). Estado verificado y citas habilitadas.`);
        this.cargarDatos();
      }
    });
  }

  cerrarModalFirma(): void {
    this.mostrarModalFirma = false;
    this.limpiarLienzo();
  }

  descargarPdf(firmaId: string): void {
    this.clinicaService.descargarConsentimientoPdf(firmaId).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Consentimiento_${firmaId.substring(0, 8)}.pdf`;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    });
  }

  abrirModalRevocar(f: FirmaConsentimiento): void {
    this.firmaParaRevocar = f;
    this.motivoRevocacion = '';
  }

  confirmarRevocacion(): void {
    if (!this.firmaParaRevocar) return;
    this.clinicaService.revocarConsentimiento(this.firmaParaRevocar.id, this.motivoRevocacion).subscribe({
      next: () => {
        this.firmaParaRevocar = null;
        this.mostrarAvisoFeedback('Consentimiento marcado como revocado');
        this.cargarDatos();
      }
    });
  }

  mostrarAvisoFeedback(msg: string): void {
    this.mensajeAviso.set(msg);
    setTimeout(() => this.mensajeAviso.set(null), 4000);
  }
}
