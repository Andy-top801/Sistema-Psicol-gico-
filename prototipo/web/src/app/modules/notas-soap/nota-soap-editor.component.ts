// ==============================================================================
// MÓDULO: nota-soap-editor.component.ts
// CAPA BCE: BOUNDARY (Interfaz de Usuario) — IU_RegistroNotaSesionSOAP
// CASOS DE USO: CU16: Modelado y Registro de Sesiones Clínicas SOAP (HU-27)
// DESCRIPCIÓN: Editor estructurado en 4 cuadrantes (S, O, A, P) con guardado automático
//              de borrador debounced (30s) y firma digital inmutable sellada con SHA-256.
// ==============================================================================
import { Component, OnInit, OnDestroy, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ClinicaSprint2Service } from '../../core/services/clinica-sprint2.service';
import { NotaSesion, HistoriaClinica } from '../../core/models/clinica-sprint2.model';

@Component({
  selector: 'app-nota-soap-editor',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <div class="soap-editor-container">
      
      <!-- Header Superior -->
      <div class="editor-header glass-panel mb-4">
        <div class="header-left">
          <div class="soap-icon-box">
            <i class="fa-solid fa-file-waveform"></i>
          </div>
          <div>
            <div class="d-flex align-items-center gap-2">
              <h1 class="editor-title">Nota de Evolución Clínica (Modelo SOAP)</h1>
              <span *ngIf="notaSesion()?.firmado" class="badge-firmado">
                <i class="fa-solid fa-lock"></i> SELLADA & INMUTABLE
              </span>
              <span *ngIf="!notaSesion()?.firmado" class="badge-borrador">
                <i class="fa-solid fa-pen-ruler"></i> MODO BORRADOR
              </span>
            </div>
            <p class="editor-subtitle">
              Expediente: <strong>{{ historia()?.numero_historia }}</strong> · Paciente: <strong>{{ historia()?.paciente_nombre }}</strong>
            </p>
          </div>
        </div>

        <!-- Acciones del Encabezado -->
        <div class="header-actions">
          <!-- Indicador de Autosave -->
          <div class="autosave-status" [class.dirty]="cambiosPendientes">
            <i class="fa-solid" [ngClass]="guardandoBorrador() ? 'fa-spinner fa-spin' : (cambiosPendientes ? 'fa-circle-dot text-warning' : 'fa-circle-check text-success')"></i>
            <span *ngIf="guardandoBorrador()">Guardando borrador...</span>
            <span *ngIf="!guardandoBorrador() && !cambiosPendientes && ultimoAutoguardado">
              Autoguardado: {{ ultimoAutoguardado | date:'HH:mm:ss' }}
            </span>
            <span *ngIf="!guardandoBorrador() && cambiosPendientes">Cambios sin guardar</span>
          </div>

          <button 
            class="btn btn-outline-primary" 
            *ngIf="!notaSesion()?.firmado"
            [disabled]="guardandoBorrador()" 
            (click)="guardarBorradorManual()">
            <i class="fa-solid fa-floppy-disk"></i> Guardar Borrador
          </button>

          <button 
            class="btn btn-primary" 
            *ngIf="!notaSesion()?.firmado"
            [disabled]="!formularioValidoParaFirmar()"
            (click)="abrirModalConfirmacionFirma()">
            <i class="fa-solid fa-signature"></i> Firmar y Sellar Nota
          </button>

          <a [routerLink]="['/historias-clinicas', historiaId]" class="btn btn-light" title="Volver al expediente">
            <i class="fa-solid fa-arrow-left"></i>
          </a>
        </div>
      </div>

      <!-- Banner de Nota Firmada -->
      <div *ngIf="notaSesion()?.firmado" class="signed-banner glass-panel mb-4">
        <div class="d-flex align-items-center gap-3">
          <i class="fa-solid fa-shield-halved fa-2x text-success"></i>
          <div class="flex-grow-1">
            <h4 class="m-0 text-success fw-bold">Nota Clínica Firmada e Inmutable</h4>
            <p class="m-0 small text-muted">
              Firmado por: <strong>{{ notaSesion()?.psicologo_nombre }}</strong> · Fecha de sellado: <strong>{{ notaSesion()?.fecha_firma | date:'medium' }}</strong>
            </p>
            <div class="hash-row mt-1">
              <span class="small text-muted">Hash SHA-256 de Integridad:</span>
              <code class="hash-val">{{ notaSesion()?.firma_hash_integridad }}</code>
            </div>
          </div>
        </div>
      </div>

      <!-- Metadatos de la Sesión: Riesgo y Duración -->
      <div class="meta-strip glass-panel mb-4">
        <div class="row g-3 align-items-center">
          <div class="col-md-3">
            <label class="form-label small fw-bold">Nivel de Riesgo Evaluado</label>
            <select class="form-select form-select-sm" [(ngModel)]="notaForm.nivel_riesgo" (ngModelChange)="marcarDirty()" [disabled]="!!notaSesion()?.firmado">
              <option value="BAJO">Bajo (Sin indicadores agudos)</option>
              <option value="MODERADO">Moderado (Sintomatología con afectación)</option>
              <option value="ALTO">Alto (Banderas rojas identificadas)</option>
              <option value="CRITICO">Crítico (Riesgo vital / Urgencia inmediata)</option>
            </select>
          </div>

          <div class="col-md-3">
            <label class="form-label small fw-bold">Duración de la Sesión (min)</label>
            <input type="number" class="form-control form-control-sm" [(ngModel)]="notaForm.duracion_minutos" (ngModelChange)="marcarDirty()" [disabled]="!!notaSesion()?.firmado" />
          </div>

          <div class="col-md-6">
            <label class="form-label small fw-bold">Técnicas e Intervenciones Aplicadas</label>
            <input type="text" class="form-control form-control-sm" [(ngModel)]="notaForm.intervenciones_aplicadas" 
                   (ngModelChange)="marcarDirty()" [disabled]="!!notaSesion()?.firmado"
                   placeholder="Ej. Reestructuración cognitiva, role-playing, técnica de respiración diafragmática..." />
          </div>
        </div>
      </div>

      <!-- LOS 4 CUADRANTES DEL MODELO SOAP -->
      <div class="soap-grid">
        
        <!-- CUADRANTE S: SUBJETIVO -->
        <div class="soap-quadrant glass-panel quadrant-s">
          <div class="quadrant-header">
            <div class="quadrant-letter">S</div>
            <div>
              <h3 class="quadrant-title">SUBJETIVO</h3>
              <p class="quadrant-subtitle">Relato espontáneo, sintomatología percibida y verbalizaciones del consultante</p>
            </div>
          </div>
          <div class="quadrant-body">
            <textarea 
              class="form-control soap-textarea" 
              rows="8"
              [(ngModel)]="notaForm.subjetivo" 
              (ngModelChange)="marcarDirty()"
              [disabled]="!!notaSesion()?.firmado"
              placeholder="Describa lo manifestado directamente por el paciente sobre su estado anímico, acontecimientos semanales, quejas somáticas o dificultades experimentadas..."></textarea>
          </div>
        </div>

        <!-- CUADRANTE O: OBJETIVO -->
        <div class="soap-quadrant glass-panel quadrant-o">
          <div class="quadrant-header">
            <div class="quadrant-letter">O</div>
            <div>
              <h3 class="quadrant-title">OBJETIVO</h3>
              <p class="quadrant-subtitle">Observación clínica, lenguaje no verbal, conducta y examen mental de sesión</p>
            </div>
          </div>
          <div class="quadrant-body">
            <textarea 
              class="form-control soap-textarea" 
              rows="8"
              [(ngModel)]="notaForm.objetivo" 
              (ngModelChange)="marcarDirty()"
              [disabled]="!!notaSesion()?.firmado"
              placeholder="Registre el porte y aspecto, modulación afectiva, latencia de respuesta, contacto ocular, congruencia ideo-afectiva y signos observables durante la sesión..."></textarea>
          </div>
        </div>

        <!-- CUADRANTE A: ANÁLISIS / EVALUACIÓN -->
        <div class="soap-quadrant glass-panel quadrant-a">
          <div class="quadrant-header">
            <div class="quadrant-letter">A</div>
            <div>
              <h3 class="quadrant-title">ANÁLISIS / EVALUACIÓN</h3>
              <p class="quadrant-subtitle">Hipótesis clínicas de trabajo, conceptualización del caso y valoración del progreso</p>
            </div>
          </div>
          <div class="quadrant-body">
            <textarea 
              class="form-control soap-textarea" 
              rows="8"
              [(ngModel)]="notaForm.analisis" 
              (ngModelChange)="marcarDirty()"
              [disabled]="!!notaSesion()?.firmado"
              placeholder="Articule la comprensión clínica de la sesión, respuesta al tratamiento, mecanismos de defensa o distorsiones cognitivas dominantes detectadas..."></textarea>
          </div>
        </div>

        <!-- CUADRANTE P: PLAN TERAPÉUTICO -->
        <div class="soap-quadrant glass-panel quadrant-p">
          <div class="quadrant-header">
            <div class="quadrant-letter">P</div>
            <div>
              <h3 class="quadrant-title">PLAN TERAPÉUTICO</h3>
              <p class="quadrant-subtitle">Acuerdos, prescripción de tareas inter-sesión y directrices para la próxima consulta</p>
            </div>
          </div>
          <div class="quadrant-body">
            <textarea 
              class="form-control soap-textarea" 
              rows="8"
              [(ngModel)]="notaForm.plan" 
              (ngModelChange)="marcarDirty()"
              [disabled]="!!notaSesion()?.firmado"
              placeholder="Indique las tareas o auto-registros acordados con el paciente, objetivos a trabajar en la siguiente cita y pautas de contingencia si aplica..."></textarea>
          </div>
        </div>

      </div>

      <!-- MODAL: CONFIRMACIÓN DE FIRMA INMUTABLE (HU-27) -->
      <div *ngIf="mostrarModalFirma" class="modal-backdrop-custom" (click)="mostrarModalFirma = false">
        <div class="modal-dialog-custom glass-card-modal modal-md" (click)="$event.stopPropagation()">
          <div class="modal-header-custom bg-light">
            <h2 class="modal-title text-danger">
              <i class="fa-solid fa-triangle-exclamation me-2"></i>
              Firmar y Sellar Nota de Sesión
            </h2>
            <button class="btn-close-custom" (click)="mostrarModalFirma = false"><i class="fa-solid fa-xmark"></i></button>
          </div>

          <div class="modal-body-custom p-4">
            <div class="alert alert-warning">
              <strong>ADVERTENCIA LEGAL Y DEONTOLÓGICA:</strong>
              <p class="small mb-0 mt-1">
                Conforme a la normativa de expedientes clínicos electrónicos, la firma de esta nota calculará un 
                <strong>sello criptográfico inmutable SHA-256</strong>. Una vez firmada, 
                <strong>la nota no podrá ser editada ni eliminada</strong> bajo ninguna circunstancia.
              </p>
            </div>

            <div class="summary-check p-3 glass-panel mb-3">
              <div class="d-flex justify-content-between mb-1">
                <span>Nivel de Riesgo:</span>
                <span class="badge bg-secondary">{{ notaForm.nivel_riesgo }}</span>
              </div>
              <div class="d-flex justify-content-between mb-1">
                <span>Duración:</span>
                <span>{{ notaForm.duracion_minutos }} minutos</span>
              </div>
              <div class="d-flex justify-content-between">
                <span>Cuadrantes SOAP:</span>
                <span class="text-success"><i class="fa-solid fa-check-double"></i> 4 Cuadrantes completos</span>
              </div>
            </div>

            <div class="form-check">
              <input class="form-check-input" type="checkbox" [(ngModel)]="aceptaCompromisoFirma" id="chkFirma" />
              <label class="form-check-label small" for="chkFirma">
                Certifico que la información registrada es veraz, confidencial y corresponde a la atención brindada.
              </label>
            </div>
          </div>

          <div class="modal-footer-custom p-3">
            <button class="btn btn-secondary" (click)="mostrarModalFirma = false">Cancelar</button>
            <button class="btn btn-danger" [disabled]="!aceptaCompromisoFirma || firmando()" (click)="confirmarFirma()">
              <i class="fa-solid fa-lock me-1"></i>
              {{ firmando() ? 'Sellando criptográficamente...' : 'Confirmar Firma Inmutable' }}
            </button>
          </div>
        </div>
      </div>

    </div>
  `,
  styles: [`
    .soap-editor-container { max-width: 1400px; margin: 0 auto; }
    
    .editor-header {
      padding: 1.25rem 1.75rem; border-radius: 16px; background: #ffffff;
      border: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center;
    }
    .header-left { display: flex; align-items: center; gap: 1rem; }
    .soap-icon-box {
      width: 48px; height: 48px; border-radius: 12px; background: #e0f2fe; color: #0284c7;
      font-size: 1.4rem; display: flex; align-items: center; justify-content: center;
    }
    .editor-title { font-size: 1.35rem; font-weight: 700; color: #0f172a; margin: 0; }
    .editor-subtitle { font-size: 0.85rem; color: #64748b; margin: 0.2rem 0 0 0; }
    .header-actions { display: flex; align-items: center; gap: 0.75rem; }

    .badge-firmado {
      font-size: 0.72rem; font-weight: 700; padding: 0.25rem 0.6rem; border-radius: 9999px;
      background: #dcfce7; color: #166534; border: 1px solid #bbf7d0;
    }
    .badge-borrador {
      font-size: 0.72rem; font-weight: 700; padding: 0.25rem 0.6rem; border-radius: 9999px;
      background: #fef9c3; color: #854d0e; border: 1px solid #fef08a;
    }

    .autosave-status {
      font-size: 0.8rem; color: #64748b; display: flex; align-items: center; gap: 0.4rem;
      background: #f8fafc; padding: 0.35rem 0.75rem; border-radius: 6px; border: 1px solid #e2e8f0;
    }
    .autosave-status.dirty { color: #d97706; }

    .signed-banner {
      background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px; padding: 1rem 1.5rem;
    }
    .hash-val {
      font-family: monospace; font-size: 0.78rem; background: #ffffff; padding: 0.2rem 0.5rem;
      border-radius: 4px; border: 1px solid #cbd5e1; color: #0284c7;
    }

    .meta-strip {
      background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1rem 1.5rem;
    }

    .soap-grid {
      display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.25rem;
    }

    .soap-quadrant {
      background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px;
      display: flex; flex-direction: column; overflow: hidden;
    }

    .quadrant-header {
      padding: 1rem 1.25rem; border-bottom: 1px solid #e2e8f0;
      display: flex; align-items: center; gap: 0.85rem; background: #f8fafc;
    }

    .quadrant-letter {
      width: 38px; height: 38px; border-radius: 8px; font-size: 1.2rem; font-weight: 800;
      display: flex; align-items: center; justify-content: center;
    }

    .quadrant-s .quadrant-letter { background: #e0f2fe; color: #0284c7; }
    .quadrant-o .quadrant-letter { background: #dcfce7; color: #166534; }
    .quadrant-a .quadrant-letter { background: #fef9c3; color: #854d0e; }
    .quadrant-p .quadrant-letter { background: #f3e8ff; color: #7e22ce; }

    .quadrant-title { font-size: 0.95rem; font-weight: 700; color: #0f172a; margin: 0; }
    .quadrant-subtitle { font-size: 0.75rem; color: #64748b; margin: 0.15rem 0 0 0; }
    .quadrant-body { padding: 1.25rem; flex: 1; }

    .soap-textarea {
      border: 1px solid #cbd5e1; border-radius: 8px; padding: 0.75rem;
      font-size: 0.9rem; line-height: 1.5; resize: vertical; min-height: 180px;
    }
    .soap-textarea:focus { border-color: #0284c7; box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15); }
    .soap-textarea:disabled { background: #f8fafc; color: #334155; }

    .modal-backdrop-custom {
      position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
      background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px); z-index: 1050;
      display: flex; align-items: center; justify-content: center; padding: 1.5rem;
    }
    .modal-dialog-custom {
      width: 100%; max-width: 550px; background: #ffffff; border-radius: 16px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); overflow: hidden;
    }
    .modal-header-custom { padding: 1.25rem 1.5rem; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
    .modal-footer-custom { border-top: 1px solid #e2e8f0; background: #f8fafc; display: flex; justify-content: flex-end; gap: 0.75rem; }
  `]
})
export class NotaSoapEditorComponent implements OnInit, OnDestroy {
  historiaId = '';
  notaId?: string;
  historia = signal<HistoriaClinica | null>(null);
  notaSesion = signal<NotaSesion | null>(null);

  notaForm = {
    subjetivo: '',
    objetivo: '',
    analisis: '',
    plan: '',
    intervenciones_aplicadas: '',
    nivel_riesgo: 'BAJO',
    duracion_minutos: 50
  };

  // Autosave State
  cambiosPendientes = false;
  guardandoBorrador = signal<boolean>(false);
  ultimoAutoguardado: Date | null = null;
  private autosaveInterval: any = null;

  // Signature Modal State
  mostrarModalFirma = false;
  aceptaCompromisoFirma = false;
  firmando = signal<boolean>(false);

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private clinicaService: ClinicaSprint2Service
  ) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe(q => {
      this.historiaId = q['historia'];
      this.notaId = q['id'];

      if (this.historiaId) {
        this.cargarHistoria();
      }

      if (this.notaId) {
        this.cargarNotaExistente();
      }
    });

    // Iniciar timer de autosave cada 30 segundos
    this.autosaveInterval = setInterval(() => {
      if (this.cambiosPendientes && !this.notaSesion()?.firmado && !this.guardandoBorrador()) {
        this.guardarBorrador();
      }
    }, 30000);
  }

  ngOnDestroy(): void {
    if (this.autosaveInterval) {
      clearInterval(this.autosaveInterval);
    }
  }

  cargarHistoria(): void {
    this.clinicaService.getHistoriaClinicaById(this.historiaId).subscribe({
      next: (hc) => this.historia.set(hc)
    });
  }

  cargarNotaExistente(): void {
    if (!this.notaId) return;
    this.clinicaService.getNotaSesionById(this.notaId).subscribe({
      next: (n) => {
        this.notaSesion.set(n);
        this.notaForm = {
          subjetivo: n.subjetivo,
          objetivo: n.objetivo,
          analisis: n.analisis,
          plan: n.plan,
          intervenciones_aplicadas: n.intervenciones_aplicadas || '',
          nivel_riesgo: n.nivel_riesgo,
          duracion_minutos: n.duracion_minutos || 50
        };
        this.cambiosPendientes = false;
      }
    });
  }

  marcarDirty(): void {
    this.cambiosPendientes = true;
  }

  guardarBorrador(): void {
    this.guardandoBorrador.set(true);
    const payload = {
      id: this.notaSesion()?.id,
      historia_clinica: this.historiaId,
      ...this.notaForm
    };

    this.clinicaService.guardarBorrador(payload).subscribe({
      next: (nota) => {
        this.notaSesion.set(nota);
        this.notaId = nota.id;
        this.cambiosPendientes = false;
        this.ultimoAutoguardado = new Date();
        this.guardandoBorrador.set(false);
      },
      error: () => this.guardandoBorrador.set(false)
    });
  }

  guardarBorradorManual(): void {
    this.guardarBorrador();
  }

  formularioValidoParaFirmar(): boolean {
    return (
      this.notaForm.subjetivo.trim().length > 0 &&
      this.notaForm.objetivo.trim().length > 0 &&
      this.notaForm.analisis.trim().length > 0 &&
      this.notaForm.plan.trim().length > 0
    );
  }

  abrirModalConfirmacionFirma(): void {
    this.aceptaCompromisoFirma = false;
    this.mostrarModalFirma = true;
  }

  confirmarFirma(): void {
    if (!this.notaId) {
      // First save draft to get an ID
      const payload = {
        historia_clinica: this.historiaId,
        ...this.notaForm
      };
      this.clinicaService.guardarBorrador(payload).subscribe({
        next: (nota) => {
          this.notaId = nota.id;
          this.ejecutarFirma(nota.id);
        }
      });
    } else {
      this.ejecutarFirma(this.notaId);
    }
  }

  private ejecutarFirma(id: string): void {
    this.firmando.set(true);
    this.clinicaService.firmarNotaSesion(id, this.notaForm).subscribe({
      next: (res) => {
        this.notaSesion.set(res.nota);
        this.firmando.set(false);
        this.mostrarModalFirma = false;
        this.cambiosPendientes = false;
      },
      error: () => this.firmando.set(false)
    });
  }
}
