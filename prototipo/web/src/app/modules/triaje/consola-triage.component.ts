// ==============================================================================
// MÓDULO: consola-triage.component.ts
// CAPA BCE: BOUNDARY — UI_ConsolaTriajeIA (CU21) + UI_ConsolaMatchingWeb (CU22)
// HISTORIAS DE USUARIO: HU-47, HU-48
//
// CU21 (Secuencia_Corregido_CU21_Clasificacion_IA)
//   CU21-paso 1:  ingresar_motivo_y_respuestas()          → intake del paciente o reclasificar(c)
//   CU21-paso 18: activar_banner_alerta_roja_prioritaria() → banner "PROTOCOLO CRISIS"
//   CU21-paso 26: mostrar_tarjeta_triaje_ordinaria()       → tarjeta de triaje regular
// CU22 (Secuencia_Corregido_CU22_Matching_Asignacion_IA)
//   CU22-paso 1:  solicitar_emparejamiento_ia(paciente_id)  → seleccionarEmparejamiento(c)
//   CU22-paso 19: mostrar_ranking_matching_IA(candidatos)
//   CU22-paso 20: confirmar_asignacion_IA(sugerencia_id, psicologo_id)
//   CU22-paso 29: mostrar_confirmacion_asignacion('Asignación HITL confirmada')
//   CU22-paso 30: rechazar_y_reasignar_manual(sugerencia_id, psicologo_manual_id, motivo)
//   CU22-paso 39: mostrar_confirmacion_manual('Asignación manual completada')
// La IA solo sugiere: ningún paciente se asigna sin la confirmación explícita del coordinador.
// ==============================================================================
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import {
  TriajeIAService, ClasificacionIA, CandidatoMatching, SugerenciasResponse, CATEGORIA_LABEL,
  CategoriaTriaje, SeveridadTriaje, FactoresMatching, mensajeErrorApi
} from '../../core/services/triaje-ia.service';
import { ClinicaService } from '../../core/services/clinica.service';

type Filtro = 'PENDIENTES' | 'CRISIS' | 'ASIGNADOS' | 'TODOS';
interface Aviso { tipo: 'success' | 'danger' | 'warning' | 'info'; texto: string; }
interface PsicologoOpcion { id: string; nombre: string; modalidad: string; }

const MOTIVO_MIN = 10;

@Component({
  selector: 'app-consola-triage',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="tr-page">

      <!-- Encabezado -->
      <header class="tr-head">
        <div>
          <h1 class="tr-title"><i aria-hidden="true" class="fa-solid fa-brain"></i> Consola de Triaje y Asignación Asistida por IA</h1>
          <p class="muted">
            CU21 · Clasificación del motivo de consulta y detección de crisis (HU-47) —
            CU22 · Emparejamiento con validación humana (HU-48)
          </p>
        </div>
        <button type="button" class="btn btn-secondary btn-sm" (click)="cargarDatos()" [disabled]="cargando">
          <i aria-hidden="true" class="fa-solid fa-arrows-rotate" [class.fa-spin]="cargando"></i> Actualizar
        </button>
      </header>

      <div *ngIf="errorCarga" class="alert-box alert-danger" role="alert">
        <i aria-hidden="true" class="fa-solid fa-circle-xmark"></i><span>{{ errorCarga }}</span>
      </div>

      <!-- CU21-paso 18: activar_banner_alerta_roja_prioritaria('PROTOCOLO CRISIS') -->
      <div *ngIf="crisisPendientes.length > 0" class="crisis-banner" role="alert">
        <i aria-hidden="true" class="fa-solid fa-triangle-exclamation crisis-icon"></i>
        <div class="crisis-text">
          <h2>PROTOCOLO CRISIS · {{ crisisPendientes.length }} caso(s) con riesgo vital sin psicólogo asignado</h2>
          <p>Activar protocolo de crisis: contactar al paciente de inmediato, evaluar riesgo y derivar a atención prioritaria.</p>
        </div>
        <button type="button" class="btn btn-danger btn-sm" (click)="filtro = 'CRISIS'; seleccionarCaso(crisisPendientes[0])">
          Atender primero
        </button>
      </div>

      <div class="tr-grid">
        <!-- ═══ Columna izquierda: entradas de casos (CU21) ═══ -->
        <section class="glass-card panel" aria-label="Entradas de casos de triaje">
          <div class="panel-head">
            <h2 class="panel-title"><i aria-hidden="true" class="fa-solid fa-inbox"></i> Entradas de casos</h2>
            <span class="badge badge-primary">{{ casosFiltrados.length }} / {{ clasificaciones.length }}</span>
          </div>
          <input type="search" class="form-control" [(ngModel)]="busqueda"
                 placeholder="Buscar por paciente o expediente…" aria-label="Buscar caso">
          <div class="filtros" role="group" aria-label="Filtrar casos">
            <button type="button" *ngFor="let f of filtros" class="filtro-btn" [class.activo]="filtro === f.id"
                    [attr.aria-pressed]="filtro === f.id" (click)="filtro = f.id">
              {{ f.label }}
            </button>
          </div>

          <div class="case-list">
            <div *ngIf="cargando" class="empty"><i aria-hidden="true" class="fa-solid fa-spinner fa-spin"></i> Cargando casos…</div>
            <div *ngIf="!cargando && casosFiltrados.length === 0" class="empty">
              <i aria-hidden="true" class="fa-regular fa-folder-open"></i> No hay casos para este filtro.
            </div>
            <ng-container *ngIf="!cargando">
              <button type="button" *ngFor="let c of casosFiltrados" class="case-item"
                      [class.crisis]="c.alerta_crisis" [class.activo]="casoSeleccionado?.id === c.id"
                      [attr.aria-current]="casoSeleccionado?.id === c.id" (click)="seleccionarCaso(c)">
                <div class="case-top">
                  <div class="min-w-0">
                    <div class="case-name">{{ c.paciente_nombre }}</div>
                    <div class="case-meta">{{ c.paciente_expediente }} · {{ c.fecha_analisis | date:'dd/MM/yyyy HH:mm' }}</div>
                  </div>
                  <span class="badge" [ngClass]="claseSeveridad(c.nivel_severidad)">{{ c.nivel_severidad }} {{ c.puntaje_severidad }}/5</span>
                </div>
                <div class="chips">
                  <span class="badge badge-primary">{{ etiquetaCategoria(c.categoria_principal) }}</span>
                  <span *ngIf="c.alerta_crisis" class="badge badge-danger"><i aria-hidden="true" class="fa-solid fa-bell"></i> ALERTA_CRISIS</span>
                  <span *ngIf="c.psicologo_asignado_nombre" class="badge badge-success">
                    <i aria-hidden="true" class="fa-solid fa-user-check"></i> {{ c.psicologo_asignado_nombre }}
                  </span>
                </div>
              </button>
            </ng-container>
          </div>
        </section>

        <!-- ═══ Columna derecha: evaluación completa y asignación ═══ -->
        <section class="glass-card panel" aria-label="Evaluación y asignación">
          <div *ngIf="!casoSeleccionado" class="empty">
            <i aria-hidden="true" class="fa-solid fa-hand-pointer"></i> Seleccione un caso para ver su evaluación.
          </div>

          <ng-container *ngIf="casoSeleccionado as c">
            <div class="panel-head">
              <div class="min-w-0">
                <h2 class="paciente-name">{{ c.paciente_nombre }}</h2>
                <div class="muted">Expediente {{ c.paciente_expediente }}</div>
              </div>
              <button type="button" class="btn btn-outline-primary btn-sm" (click)="reclasificar(c)" [disabled]="reclasificando">
                <i aria-hidden="true" class="fa-solid" [ngClass]="reclasificando ? 'fa-spinner fa-spin' : 'fa-wand-magic-sparkles'"></i>
                {{ reclasificando ? 'Analizando con IA…' : 'Volver a analizar con IA' }}
              </button>
            </div>

            <div *ngIf="aviso" class="alert-box aviso" [ngClass]="'alert-' + aviso.tipo" role="status">{{ aviso.texto }}</div>

            <!-- CU21-paso 18 (crisis) / CU21-paso 26: mostrar_tarjeta_triaje_ordinaria('Triaje clasificado') -->
            <article class="triaje-card" [class.crisis]="c.alerta_crisis" aria-label="Análisis de triaje IA">
              <div class="triaje-head">
                <h3>
                  <i aria-hidden="true" class="fa-solid" [ngClass]="c.alerta_crisis ? 'fa-triangle-exclamation' : 'fa-clipboard-check'"></i>
                  {{ c.alerta_crisis ? 'PROTOCOLO CRISIS — atención prioritaria' : 'Triaje ordinario' }}
                </h3>
                <span class="badge" [ngClass]="claseSeveridad(c.nivel_severidad)">Severidad {{ c.nivel_severidad }} · {{ c.puntaje_severidad }}/5</span>
              </div>
              <dl class="datos">
                <div><dt>Área temática</dt><dd>{{ etiquetaCategoria(c.categoria_principal) }}</dd></div>
                <div><dt>Confianza del modelo</dt><dd>{{ c.confianza_score * 100 | number:'1.0-1' }}%</dd></div>
                <div><dt>Score de severidad</dt><dd>{{ c.score_severidad | number:'1.2-2' }} <span class="muted">(crisis ≥ 0.70)</span></dd></div>
                <div><dt>Motor</dt><dd class="mono">{{ c.modelo_ia || '—' }}</dd></div>
              </dl>
              <p class="explicacion">{{ c.explicacion_heuristica }}</p>
              <div *ngIf="c.palabras_clave_detectadas?.length" class="chips">
                <span *ngFor="let kw of c.palabras_clave_detectadas" class="badge badge-danger">{{ kw }}</span>
              </div>
              <div class="hash mono">SHA-256 {{ c.hash_trazabilidad_sha256 }}</div>
            </article>

            <!-- CU22: emparejamiento -->
            <div class="panel-head section-gap">
              <h3 class="panel-title"><i aria-hidden="true" class="fa-solid fa-user-doctor"></i> Asignación sugerida (Top 3)</h3>
              <button *ngIf="!c.psicologo_asignado_nombre" type="button" class="btn btn-primary btn-sm"
                      (click)="seleccionarEmparejamiento(c)" [disabled]="calculando || decidiendo">
                <i aria-hidden="true" class="fa-solid" [ngClass]="calculando ? 'fa-spinner fa-spin' : 'fa-ranking-star'"></i>
                {{ calculando ? 'Calculando…' : (ranking ? 'Recalcular' : 'Generar Top 3') }}
              </button>
            </div>

            <div *ngIf="c.psicologo_asignado_nombre" class="alert-box alert-success">
              <i aria-hidden="true" class="fa-solid fa-circle-check"></i>
              <span>Paciente asignado a <strong>{{ c.psicologo_asignado_nombre }}</strong>.
                La decisión quedó registrada en la bitácora del sistema.</span>
            </div>

            <div *ngIf="!c.psicologo_asignado_nombre && !ranking && !calculando" class="formula">
              Presione <strong>Generar Top 3</strong>. Fórmula transparente:
              <code>Score = 0.4×Afinidad + 0.3×Disponibilidad + 0.2×BalanceCarga + 0.1×Modalidad</code>
            </div>

            <!-- CU22-paso 19: mostrar_ranking_matching_IA(candidatos) -->
            <ng-container *ngIf="ranking && !c.psicologo_asignado_nombre">
              <p class="muted">
                Preferencia del paciente: <strong>{{ ranking.paciente.modalidad_preferencia }}</strong> ·
                Área: <strong>{{ etiquetaCategoria(ranking.triaje.categoria) }}</strong>
              </p>
              <div *ngIf="ranking.top3_candidatos.length === 0" class="alert-box alert-warning">No hay psicólogos activos para sugerir.</div>

              <article *ngFor="let cand of ranking.top3_candidatos" class="cand"
                       [class.top]="cand.ranking === 1 && !cand.cupo_completo" [attr.aria-label]="'Candidato ' + cand.ranking">
                <div class="cand-head">
                  <div class="min-w-0">
                    <span class="rank">#{{ cand.ranking }}</span>
                    <strong>{{ cand.nombre_psicologo }}</strong>
                    <div class="muted">Col. {{ cand.numero_colegiado }} · {{ cand.modalidad }}</div>
                    <div class="muted esp">{{ cand.especialidades.join(' · ') || 'Sin especialidades registradas' }}</div>
                  </div>
                  <div class="score">
                    <span class="score-num">{{ cand.score | number:'1.1-1' }}</span>
                    <span class="muted">compatibilidad</span>
                  </div>
                </div>

                <!-- Desglose: valor × peso = puntos -->
                <div class="factores">
                  <div *ngFor="let f of factores" class="factor">
                    <div class="factor-label">
                      <span>{{ f.label }} <span class="muted">({{ cand.pesos[f.key] * 100 | number:'1.0-0' }}%)</span></span>
                      <span class="mono">{{ cand.factores[f.key] | number:'1.2-2' }} → {{ puntos(cand, f.key) | number:'1.1-1' }} pts</span>
                    </div>
                    <div class="bar" role="progressbar" [attr.aria-label]="f.label"
                         [attr.aria-valuenow]="cand.factores[f.key] * 100" aria-valuemin="0" aria-valuemax="100">
                      <div class="bar-fill" [ngClass]="f.color" [style.width.%]="cand.factores[f.key] * 100"></div>
                    </div>
                  </div>
                </div>

                <div class="cand-foot">
                  <span class="carga" [class.llena]="cand.cupo_completo">
                    <i aria-hidden="true" class="fa-solid fa-users"></i> Carga {{ cand.carga_actual }}/{{ cand.cupo_maximo }}
                    <span *ngIf="cand.cupo_completo" class="badge badge-danger">Cupo completo</span>
                  </span>
                  <div class="acciones">
                    <button type="button" class="btn btn-danger btn-sm" (click)="abrirReasignacion(cand)" [disabled]="decidiendo">
                      <i aria-hidden="true" class="fa-solid fa-shuffle"></i> Rechazar y asignar otro
                    </button>
                    <button type="button" class="btn btn-primary btn-sm" (click)="abrirAprobacion(cand)" [disabled]="decidiendo">
                      <i aria-hidden="true" class="fa-solid fa-user-check"></i> Aprobar
                    </button>
                  </div>
                </div>
              </article>
              <p class="muted hitl-note">
                <i aria-hidden="true" class="fa-solid fa-shield-halved"></i> Sugerencia generada por IA. Requiere su confirmación; ningún paciente se asigna automáticamente.
              </p>
            </ng-container>
          </ng-container>
        </section>
      </div>

      <!-- CU22-paso 20: confirmar_asignacion_IA(sugerencia_id, psicologo_id) -->
      <div *ngIf="candidatoAprobar as cand" class="modal-overlay" (click)="cerrarModales()">
        <div class="modal-content" role="dialog" aria-modal="true" aria-labelledby="tituloAprobar" (click)="$event.stopPropagation()">
          <h2 id="tituloAprobar" class="modal-title"><i aria-hidden="true" class="fa-solid fa-user-shield"></i> Confirmar asignación (HITL)</h2>
          <p><strong>Paciente:</strong> {{ casoSeleccionado?.paciente_nombre }}</p>
          <p><strong>Psicólogo sugerido:</strong> {{ cand.nombre_psicologo }} (#{{ cand.ranking }}, {{ cand.score | number:'1.1-1' }} pts)</p>
          <div *ngIf="cand.cupo_completo" class="alert-box alert-warning">
            <i aria-hidden="true" class="fa-solid fa-triangle-exclamation"></i><span>Este profesional tiene el cupo completo.</span>
          </div>
          <div class="alert-box alert-info">La asignación definitiva es su decisión y queda registrada en la bitácora del sistema.</div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary btn-sm" (click)="cerrarModales()" [disabled]="decidiendo">Cancelar</button>
            <button type="button" class="btn btn-primary btn-sm" (click)="confirmarAsignacionIA()" [disabled]="decidiendo">
              <i aria-hidden="true" class="fa-solid" [ngClass]="decidiendo ? 'fa-spinner fa-spin' : 'fa-check'"></i>
              {{ decidiendo ? 'Asignando…' : 'Confirmar asignación' }}
            </button>
          </div>
        </div>
      </div>

      <!-- CU22-paso 30: rechazar_y_reasignar_manual(sugerencia_id, psicologo_manual_id, motivo) -->
      <div *ngIf="candidatoRechazar as cand" class="modal-overlay" (click)="cerrarModales()">
        <div class="modal-content" role="dialog" aria-modal="true" aria-labelledby="tituloReasignar" (click)="$event.stopPropagation()">
          <h2 id="tituloReasignar" class="modal-title danger"><i aria-hidden="true" class="fa-solid fa-shuffle"></i> Rechazar sugerencia y asignar manualmente</h2>
          <p><strong>Sugerencia rechazada:</strong> {{ cand.nombre_psicologo }} (#{{ cand.ranking }})</p>
          <label class="form-label" for="psicoManual">Psicólogo a asignar *</label>
          <select id="psicoManual" class="form-select" [(ngModel)]="psicologoManualId">
            <option value="" disabled>Seleccione un profesional activo…</option>
            <option *ngFor="let p of psicologosActivos" [value]="p.id">{{ p.nombre }} · {{ p.modalidad }}</option>
          </select>
          <div *ngIf="psicologosActivos.length === 0" class="hint error">No se pudo cargar la lista de psicólogos.</div>
          <label class="form-label campo" for="motivo">Motivo clínico *</label>
          <textarea id="motivo" class="form-control" rows="3" [(ngModel)]="motivo"
                    placeholder="Ej.: el paciente pidió continuidad con este profesional…"></textarea>
          <div class="hint" [class.error]="motivo.trim().length < motivoMin">
            Mínimo {{ motivoMin }} caracteres ({{ motivo.trim().length }}).
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary btn-sm" (click)="cerrarModales()" [disabled]="decidiendo">Cancelar</button>
            <button type="button" class="btn btn-danger btn-sm" (click)="rechazarYReasignarManual()"
                    [disabled]="decidiendo || !psicologoManualId || motivo.trim().length < motivoMin">
              <i aria-hidden="true" class="fa-solid" [ngClass]="decidiendo ? 'fa-spinner fa-spin' : 'fa-check'"></i>
              {{ decidiendo ? 'Registrando…' : 'Registrar asignación manual' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .tr-page { padding: 24px; display: grid; gap: 16px; color: var(--text-main); }
    .tr-head { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 12px; }
    .tr-title { font-size: 1.5rem; font-weight: 800; margin: 0 0 4px; }
    .tr-title i { color: var(--primary); margin-right: 6px; }
    .muted { color: var(--text-muted); font-size: 0.84rem; margin: 0; }
    .mono { font-family: var(--font-mono); font-size: 0.78rem; }
    .min-w-0 { min-width: 0; }

    .crisis-banner {
      display: flex; flex-wrap: wrap; align-items: center; gap: 16px; padding: 16px 20px;
      background: var(--danger-bg); border: 2px solid var(--danger); border-radius: 14px;
    }
    .crisis-icon { font-size: 2rem; color: var(--danger); animation: pulso 1.5s infinite; }
    .crisis-text { flex: 1; min-width: 240px; }
    .crisis-text h2 { font-size: 1rem; font-weight: 800; color: #991b1b; margin: 0 0 2px; }
    .crisis-text p { margin: 0; color: #991b1b; font-size: 0.86rem; }
    @keyframes pulso { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.12); } }
    @media (prefers-reduced-motion: reduce) { .crisis-icon { animation: none; } }

    .tr-grid { display: grid; grid-template-columns: minmax(300px, 5fr) 7fr; gap: 16px; align-items: start; }
    @media (max-width: 1024px) { .tr-grid { grid-template-columns: 1fr; } .tr-page { padding: 16px; } }
    .panel { padding: 18px; border-radius: 16px; display: grid; gap: 12px; min-width: 0; }
    .panel-head { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 10px; }
    .panel-title { font-size: 1rem; font-weight: 800; margin: 0; }
    .panel-title i { color: var(--primary); margin-right: 6px; }
    .section-gap { margin-top: 8px; }
    .empty { text-align: center; color: var(--text-muted); padding: 40px 12px; }
    .empty i { display: block; font-size: 1.6rem; margin-bottom: 8px; }

    .filtros { display: flex; gap: 6px; flex-wrap: wrap; }
    .filtro-btn {
      flex: 1; min-width: 80px; padding: 7px 10px; border-radius: 10px; font: inherit; font-size: 0.82rem; font-weight: 700;
      border: 1.5px solid var(--border-medium); background: var(--bg-surface); color: var(--text-body); cursor: pointer;
    }
    .filtro-btn.activo { background: var(--primary); border-color: var(--primary); color: #fff; }
    .filtro-btn:focus-visible, .case-item:focus-visible { outline: 3px solid var(--primary-glow); outline-offset: 2px; }

    .case-list { display: grid; gap: 8px; max-height: 64vh; overflow-y: auto; padding-right: 2px; }
    .case-item {
      display: grid; grid-template-columns: minmax(0, 1fr); gap: 8px; width: 100%; text-align: left; font: inherit; color: inherit; cursor: pointer;
      padding: 12px 14px; border-radius: 12px; background: var(--bg-surface); border: 1px solid var(--border-light);
      border-left: 4px solid var(--border-medium); transition: var(--transition);
    }
    .case-item:hover { background: var(--bg-card-hover); }
    .case-item.crisis { border-left-color: var(--danger); background: #fff7f7; }
    .case-item.activo { border-color: var(--primary); box-shadow: 0 0 0 2px var(--primary-glow); }
    .case-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }
    .case-top > .min-w-0 { flex: 1; }
    .case-top > .badge { flex-shrink: 0; white-space: nowrap; }
    .alert-box { gap: 8px; align-items: flex-start; }
    .case-name { font-weight: 700; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .case-meta { font-size: 0.76rem; color: var(--text-dim); }
    .chips { display: flex; flex-wrap: wrap; gap: 6px; }

    .paciente-name { font-size: 1.2rem; font-weight: 800; margin: 0; }
    .aviso { margin: 0; }
    .triaje-card { border-radius: 14px; padding: 16px; background: var(--bg-main); border: 1px solid var(--border-light); display: grid; gap: 10px; }
    .triaje-card.crisis { background: var(--danger-bg); border: 2px solid var(--danger); }
    .triaje-head { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 8px; }
    .triaje-head h3 { font-size: 0.98rem; font-weight: 800; margin: 0; }
    .triaje-card.crisis .triaje-head h3 { color: #991b1b; }
    .datos { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 8px 16px; margin: 0; }
    .datos dt { font-size: 0.74rem; color: var(--text-muted); font-weight: 600; }
    .datos dd { margin: 0; font-weight: 700; overflow-wrap: anywhere; }
    .explicacion { margin: 0; font-size: 0.86rem; color: var(--text-body); }
    .hash { color: var(--text-dim); font-size: 0.68rem; overflow-wrap: anywhere; }
    .formula { border: 1px dashed var(--border-medium); border-radius: 12px; padding: 14px; font-size: 0.86rem; color: var(--text-muted); }
    .formula code { display: block; margin-top: 6px; font-family: var(--font-mono); color: var(--primary); overflow-wrap: anywhere; }

    .cand { border: 1px solid var(--border-light); border-radius: 14px; padding: 14px; display: grid; gap: 12px; background: var(--bg-surface); }
    .cand.top { border: 2px solid var(--primary); }
    .cand-head { display: flex; justify-content: space-between; gap: 12px; }
    .rank { display: inline-block; background: var(--primary-light); color: var(--primary); font-weight: 800; border-radius: 8px; padding: 1px 8px; margin-right: 6px; }
    .cand.top .rank { background: var(--primary); color: #fff; }
    .esp { font-size: 0.78rem; }
    .score { text-align: right; display: grid; }
    .score-num { font-size: 1.5rem; font-weight: 800; color: var(--primary); line-height: 1.1; }
    .factores { display: grid; gap: 8px; }
    .factor-label { display: flex; justify-content: space-between; gap: 8px; font-size: 0.8rem; flex-wrap: wrap; }
    .bar { height: 7px; border-radius: 99px; background: var(--border-light); overflow: hidden; }
    .bar-fill { height: 100%; border-radius: 99px; }
    .f-afinidad { background: var(--primary); }
    .f-disponibilidad { background: var(--info); }
    .f-carga { background: var(--warning); }
    .f-modalidad { background: var(--accent); }
    .cand-foot { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 10px; padding-top: 10px; border-top: 1px solid var(--border-light); }
    .carga { font-size: 0.84rem; display: inline-flex; align-items: center; gap: 6px; }
    .carga.llena { color: var(--danger); font-weight: 700; }
    .acciones { display: flex; gap: 8px; flex-wrap: wrap; }
    .hitl-note i { color: var(--primary); }

    .modal-title { font-size: 1.15rem; font-weight: 800; color: var(--primary); margin: 0 0 14px; }
    .modal-title.danger { color: var(--danger); }
    .modal-content p { margin: 0 0 8px; }
    .modal-content .alert-box { margin: 10px 0; }
    .campo { margin-top: 14px; }
    .hint { font-size: 0.78rem; color: var(--text-muted); margin-top: 4px; }
    .hint.error { color: var(--danger); }
    .modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 18px; flex-wrap: wrap; }
  `]
})
export class ConsolaTriageComponent implements OnInit {
  readonly motivoMin = MOTIVO_MIN;
  readonly filtros: { id: Filtro; label: string }[] = [
    { id: 'PENDIENTES', label: 'Sin asignar' }, { id: 'CRISIS', label: 'Crisis' },
    { id: 'ASIGNADOS', label: 'Asignados' }, { id: 'TODOS', label: 'Todos' },
  ];
  readonly factores: { key: keyof FactoresMatching; label: string; color: string }[] = [
    { key: 'afinidad', label: 'Afinidad', color: 'f-afinidad' },
    { key: 'disponibilidad', label: 'Disponibilidad', color: 'f-disponibilidad' },
    { key: 'balance_carga', label: 'Balance de carga', color: 'f-carga' },
    { key: 'modalidad', label: 'Modalidad', color: 'f-modalidad' },
  ];

  clasificaciones: ClasificacionIA[] = [];
  casoSeleccionado: ClasificacionIA | null = null;
  ranking: SugerenciasResponse | null = null;
  psicologosActivos: PsicologoOpcion[] = [];

  filtro: Filtro = 'PENDIENTES';
  busqueda = '';
  aviso: Aviso | null = null;
  errorCarga = '';

  candidatoAprobar: CandidatoMatching | null = null;
  candidatoRechazar: CandidatoMatching | null = null;
  psicologoManualId = '';
  motivo = '';

  cargando = true;
  reclasificando = false;
  calculando = false;
  decidiendo = false;

  constructor(private triajeService: TriajeIAService, private clinicaService: ClinicaService) {}

  ngOnInit(): void {
    this.cargarDatos();
  }

  get crisisPendientes(): ClasificacionIA[] {
    return this.clasificaciones.filter(c => c.alerta_crisis && !c.psicologo_asignado_nombre);
  }

  get casosFiltrados(): ClasificacionIA[] {
    const q = this.busqueda.trim().toLowerCase();
    return this.clasificaciones.filter(c => {
      if (this.filtro === 'PENDIENTES' && c.psicologo_asignado_nombre) return false;
      if (this.filtro === 'ASIGNADOS' && !c.psicologo_asignado_nombre) return false;
      if (this.filtro === 'CRISIS' && !c.alerta_crisis) return false;
      return !q || `${c.paciente_nombre} ${c.paciente_expediente}`.toLowerCase().includes(q);
    });
  }

  cargarDatos(): void {
    this.cargando = true;
    this.errorCarga = '';
    this.triajeService.getClasificaciones().subscribe({
      next: data => {
        this.clasificaciones = data;
        const actual = this.casoSeleccionado && data.find(c => c.id === this.casoSeleccionado!.id);
        if (actual) {
          this.casoSeleccionado = actual;
        } else if (data.length) {
          this.seleccionarCaso(this.crisisPendientes[0] || this.casosFiltrados[0] || data[0]);
        }
        this.cargando = false;
      },
      error: (err: HttpErrorResponse) => {
        this.errorCarga = mensajeErrorApi(err, 'No se pudieron cargar los casos de triaje.');
        this.cargando = false;
      }
    });
  }

  seleccionarCaso(c: ClasificacionIA): void {
    if (this.casoSeleccionado?.id !== c.id) {
      this.ranking = null;
      this.aviso = null;
    }
    this.casoSeleccionado = c;
  }

  /** CU21-paso 1: ingresar_motivo_y_respuestas — vuelve a ejecutar la inferencia sobre el intake del caso. */
  reclasificar(c: ClasificacionIA): void {
    this.reclasificando = true;
    this.aviso = null;
    // CU21-paso 2: POST /api/v1/ia/clasificar-triaje/ (payload) → responde CU21-paso 17 o CU21-paso 25
    this.triajeService.clasificarTriaje(c.respuestapreconsulta).subscribe({
      next: res => {
        this.reemplazarCaso(res.clasificacion);
        this.ranking = null;
        this.aviso = res.alerta_crisis
          ? { tipo: 'danger', texto: `PROTOCOLO CRISIS (nivel ${res.nivel}). ${res.sugerencia_inmediata ?? ''}` }  // CU21-paso 18
          : { tipo: 'info', texto: 'Triaje ordinario actualizado (nivel REGULAR).' };                            // CU21-paso 26
        this.reclasificando = false;
      },
      error: (err: HttpErrorResponse) => {
        this.aviso = { tipo: 'danger', texto: mensajeErrorApi(err, 'No se pudo analizar el caso.') };
        this.reclasificando = false;
      }
    });
  }

  /** CU22-paso 1: solicitar_emparejamiento_ia(paciente_id) → termina en CU22-paso 19: mostrar_ranking_matching_IA */
  seleccionarEmparejamiento(c: ClasificacionIA): void {
    this.calculando = true;
    this.aviso = null;
    // CU22-paso 2: GET /api/v1/matching/sugerencias/?paciente_id= → CTR_MatchingController
    this.triajeService.obtenerSugerencias(c.paciente_id).subscribe({
      next: res => {
        // CU22-paso 18: HTTP 200 OK {top3_candidatos, scores} → CU22-paso 19: mostrar_ranking_matching_IA(candidatos)
        this.ranking = res;
        this.calculando = false;
      },
      error: (err: HttpErrorResponse) => {
        this.ranking = null;
        this.aviso = { tipo: err.status === 409 ? 'warning' : 'danger', texto: mensajeErrorApi(err, 'No se pudo calcular el emparejamiento.') };
        this.calculando = false;
        if (err.status === 409) this.cargarDatos();
      }
    });
  }

  abrirAprobacion(cand: CandidatoMatching): void {
    this.candidatoAprobar = cand;
  }

  abrirReasignacion(cand: CandidatoMatching): void {
    this.candidatoRechazar = cand;
    this.psicologoManualId = '';
    this.motivo = '';
    if (!this.psicologosActivos.length) this.cargarPsicologos();
  }

  cerrarModales(): void {
    if (this.decidiendo) return;
    this.candidatoAprobar = null;
    this.candidatoRechazar = null;
  }

  /** CU22-paso 20: confirmar_asignacion_IA(sugerencia_id, psicologo_id) → termina en CU22-paso 29 */
  confirmarAsignacionIA(): void {
    const cand = this.candidatoAprobar;
    if (!cand || this.decidiendo) return;
    this.decidiendo = true;
    // CU22-paso 21: POST /api/v1/matching/{id}/aprobar/ (psicologo_id)
    this.triajeService.aprobar(cand.sugerencia_id, cand.psicologo_id).subscribe({
      // CU22-paso 28: HTTP 200 OK → CU22-paso 29: mostrar_confirmacion_asignacion('Asignación HITL confirmada')
      next: res => this.finalizarDecision({ tipo: 'success', texto: `${res.mensaje}: ${res.psicologo_asignado}.` }, res.psicologo_asignado),
      error: (err: HttpErrorResponse) => this.falloDecision(err),
    });
  }

  /** CU22-paso 30: rechazar_y_reasignar_manual(sugerencia_id, psicologo_manual_id, motivo) → termina en CU22-paso 39 */
  rechazarYReasignarManual(): void {
    const cand = this.candidatoRechazar;
    const motivo = this.motivo.trim();
    if (!cand || this.decidiendo || !this.psicologoManualId || motivo.length < MOTIVO_MIN) return;
    this.decidiendo = true;
    // CU22-paso 31: POST /api/v1/matching/{id}/rechazar_y_reasignar/ (motivo)
    this.triajeService.rechazarYReasignar(cand.sugerencia_id, this.psicologoManualId, motivo).subscribe({
      // CU22-paso 38: HTTP 200 OK → CU22-paso 39: mostrar_confirmacion_manual('Asignación manual completada')
      next: res => this.finalizarDecision({ tipo: 'success', texto: `${res.mensaje}: ${res.psicologo_asignado}.` }, res.psicologo_asignado),
      error: (err: HttpErrorResponse) => this.falloDecision(err),
    });
  }

  etiquetaCategoria(code: CategoriaTriaje | string): string {
    return CATEGORIA_LABEL[code as CategoriaTriaje] || code;
  }

  claseSeveridad(sev: SeveridadTriaje): string {
    return ({ CRITICA: 'badge-danger', ALTA: 'badge-warning', MODERADA: 'badge-info', BAJA: 'badge-success' } as Record<string, string>)[sev] || 'badge-primary';
  }

  puntos(cand: CandidatoMatching, key: keyof FactoresMatching): number {
    return cand.factores[key] * cand.pesos[key] * 100;
  }

  private finalizarDecision(aviso: Aviso, psicologo: string): void {
    this.decidiendo = false;
    this.candidatoAprobar = null;
    this.candidatoRechazar = null;
    this.ranking = null;
    if (this.casoSeleccionado) {
      // Todas las clasificaciones del mismo paciente quedan asignadas
      this.clasificaciones = this.clasificaciones.map(c =>
        c.paciente_id === this.casoSeleccionado!.paciente_id ? { ...c, psicologo_asignado_nombre: psicologo } : c);
      this.casoSeleccionado = this.clasificaciones.find(c => c.id === this.casoSeleccionado!.id) || null;
    }
    this.aviso = aviso;
  }

  private falloDecision(err: HttpErrorResponse): void {
    this.decidiendo = false;
    this.candidatoAprobar = null;
    this.candidatoRechazar = null;
    this.aviso = { tipo: err.status === 409 ? 'warning' : 'danger', texto: mensajeErrorApi(err, 'No se pudo registrar la asignación.') };
    if (err.status === 409) {   // ya decidida o paciente ya asignado: refrescar estado real
      this.ranking = null;
      this.cargarDatos();
    }
  }

  private reemplazarCaso(nueva: ClasificacionIA): void {
    this.clasificaciones = this.clasificaciones.map(c => c.id === nueva.id ? nueva : c);
    if (!this.clasificaciones.some(c => c.id === nueva.id)) this.clasificaciones = [nueva, ...this.clasificaciones];
    this.casoSeleccionado = nueva;
  }

  private cargarPsicologos(): void {
    this.clinicaService.getPsicologos().subscribe({
      next: lista => {
        this.psicologosActivos = (lista || [])
          .filter(p => p.activo !== false)
          .map(p => ({
            id: p.id,
            nombre: `${p.usuario?.nombre ?? ''} ${p.usuario?.apellido ?? ''}`.trim() || p.numero_colegiado,
            modalidad: p.modalidad,
          }));
      },
      error: () => { this.psicologosActivos = []; }
    });
  }
}
