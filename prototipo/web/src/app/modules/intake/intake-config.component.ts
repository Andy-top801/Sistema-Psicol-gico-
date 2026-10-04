// ==============================================================================
// MÓDULO: intake-config.component.ts
// CAPA BCE: BOUNDARY (Interfaz de Usuario) — IU_IntakeDigital
// CASOS DE USO: CU14: Configuración y Revisión de Cuestionarios Pre-Consulta (HU-23, HU-24)
//              HU-35: Asistente Piloto de Preconsulta con IA (Supervisión Humana)
// ==============================================================================
import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { AgendaService } from '../../core/services/agenda.service';
import { ClinicaService } from '../../core/services/clinica.service';
import { ClinicaSprint2Service } from '../../core/services/clinica-sprint2.service';
import { FormularioPreConsulta, RespuestaPreConsulta } from '../../core/models/clinica-sprint2.model';
import { Cita, Paciente } from '../../core/models';
import { IaAsistenteModalComponent } from './ia-asistente-modal.component';

@Component({
  selector: 'app-intake-config',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, IaAsistenteModalComponent],
  template: `
    <div class="intake-container">
      
      <!-- ==================================================================== -->
      <!-- VISTA 1: PORTAL DEL PACIENTE (Responder Cuestionario Pre-Consulta)    -->
      <!-- ==================================================================== -->
      <ng-container *ngIf="authService.isPaciente()">
        <div class="patient-portal-centered">

          <!-- Encabezado Clínico de Bienvenida (Estético, Formal y Calibrado) -->
          <div class="patient-hero-banner mb-4">
            <div class="patient-hero-badge">
              <i class="fa-solid fa-heart-pulse me-1"></i> ATENCIÓN CLÍNICA PERSONALIZADA
            </div>
            <h1 class="patient-hero-title">Cuestionario Clínico de Pre-Consulta</h1>
            <p class="patient-hero-subtitle">
              Bienvenido(a). Le agradecemos completar este instrumento clínico previo a su próxima sesión. Sus respuestas permitirán a su profesional de la salud estructurar la consulta con mayor profundidad y adaptada a su situación.
            </p>
            <div class="patient-hero-meta">
              <span class="meta-item"><i class="fa-solid fa-shield-halved text-emerald"></i> Confidencialidad y secreto profesional</span>
              <span class="meta-divider">•</span>
              <span class="meta-item"><i class="fa-regular fa-clock"></i> Tiempo estimado: 3 a 5 minutos</span>
            </div>
          </div>

          <!-- Estado de Carga -->
          <div *ngIf="cargando()" class="loading-state-card text-center p-5 mb-4">
            <i class="fa-solid fa-circle-notch fa-spin fa-2x text-primary mb-3"></i>
            <p class="text-muted fw-semibold mb-0">Cargando sus citas e instrumentos clínicos...</p>
          </div>

          <!-- Notificación de Éxito / Feedback -->
          <div *ngIf="mensajeExito()" class="alert-success-formal d-flex align-items-center mb-4">
            <i class="fa-solid fa-circle-check fa-lg text-emerald me-3"></i>
            <div>
              <strong class="d-block text-emerald-dark">Registro Exitoso</strong>
              <span>{{ mensajeExito() }}</span>
            </div>
          </div>

          <div *ngIf="!cargando()">
            <!-- Si no tiene citas programadas -->
            <div *ngIf="citasPaciente().length === 0" class="empty-state-card text-center p-5 mb-4">
              <div class="empty-icon-circle mb-3">
                <i class="fa-solid fa-calendar-xmark fa-2x text-muted"></i>
              </div>
              <h3 class="fw-bold text-slate-800">No cuenta con citas programadas actualmente</h3>
              <p class="text-muted max-w-500 mx-auto mb-4">
                Para responder un cuestionario de preconsulta clínica, es necesario que tenga una cita agendada con un profesional del centro.
              </p>
              <a routerLink="/agenda" class="btn btn-primary px-4 py-2">
                <i class="fa-solid fa-calendar-plus me-2"></i> Agendar una Cita Clínica
              </a>
            </div>

            <!-- Si tiene citas programadas -->
            <div *ngIf="citasPaciente().length > 0">
              
              <!-- SECCIÓN 1: Selección Calibrada de Cita -->
              <div class="patient-section-card mb-4">
                <div class="section-badge-step">
                  <span class="step-num">PASO 1</span>
                  <span class="step-label">CONFIRMAR CITA ASOCIADA</span>
                </div>
                <h3 class="section-title-formal">Seleccione la cita para la cual completará este cuestionario:</h3>
                
                <div class="cita-selector-grid">
                  <div 
                    *ngFor="let c of citasPaciente()" 
                    class="patient-cita-card" 
                    [class.selected]="citaSeleccionadaId === c.id"
                    (click)="seleccionarCitaParaIntake(c.id)"
                  >
                    <div class="cita-card-top">
                      <div class="cita-date-pill">
                        <i class="fa-regular fa-calendar-check me-1 text-primary"></i>
                        <strong>{{ c.fecha }}</strong>
                        <span class="text-muted ms-1">({{ c.hora_inicio.slice(0, 5) }} - {{ c.hora_fin.slice(0, 5) }})</span>
                      </div>
                      <div class="radio-indicator">
                        <i class="fa-solid fa-circle-check text-primary" *ngIf="citaSeleccionadaId === c.id"></i>
                        <i class="fa-regular fa-circle text-muted" *ngIf="citaSeleccionadaId !== c.id"></i>
                      </div>
                    </div>

                    <div class="cita-card-body">
                      <div class="cita-meta-row">
                        <i class="fa-solid fa-user-doctor text-muted me-2"></i>
                        <span>Terapeuta: <strong>{{ c.psicologo_nombre }}</strong></span>
                      </div>
                      <div class="cita-meta-row">
                        <i class="fa-solid" [class.fa-video]="c.modalidad === 'VIRTUAL'" [class.fa-building]="c.modalidad !== 'VIRTUAL'" text-muted me-2></i>
                        <span>Modalidad: <strong>{{ c.modalidad }}</strong></span>
                      </div>
                    </div>

                    <div class="cita-card-footer">
                      <span class="status-chip" [class.completed]="tieneIntakeRespondido(c.id)" [class.pending]="!tieneIntakeRespondido(c.id)">
                        <i class="fa-solid" [class.fa-circle-check]="tieneIntakeRespondido(c.id)" [class.fa-clock]="!tieneIntakeRespondido(c.id)"></i>
                        {{ tieneIntakeRespondido(c.id) ? 'Cuestionario Completado' : 'Pendiente de Responder' }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- CASO A: Ya respondió el cuestionario para la cita seleccionada -->
              <div *ngIf="tieneIntakeRespondido(citaSeleccionadaId)" class="patient-completed-card p-5 mb-4">
                <div class="completed-icon-circle mx-auto mb-3">
                  <i class="fa-solid fa-clipboard-check fa-3x text-emerald"></i>
                </div>
                <h2 class="completed-title text-slate-900">¡Cuestionario Clínico Registrado!</h2>
                <p class="completed-subtitle max-w-600 mx-auto text-muted">
                  Sus respuestas ya fueron selladas e integradas a su expediente clínico. Su terapeuta tratante tiene acceso a ellas para preparar su consulta programada.
                </p>

                <div class="completed-summary-box text-start mt-4 p-4" *ngIf="getRespuestaDeCita(citaSeleccionadaId) as resp">
                  <div class="d-flex justify-content-between align-items-center border-bottom pb-3 mb-3">
                    <div>
                      <small class="text-muted d-block">Fecha y hora de envío:</small>
                      <strong>{{ resp.fecha_envio | date:'dd/MM/yyyy HH:mm' }}</strong>
                    </div>
                    <div class="text-end">
                      <small class="text-muted d-block">Nivel de malestar reportado:</small>
                      <span class="badge-malestar">{{ resp.nivel_urgencia_percibido }} / 5</span>
                    </div>
                  </div>
                  
                  <div class="mb-3">
                    <small class="text-muted d-block fw-semibold text-uppercase">Motivo principal de consulta:</small>
                    <p class="summary-motivo p-3 rounded-lg">{{ resp.motivo_consulta }}</p>
                  </div>

                  <h5 class="fw-bold text-slate-800 fs-6 mb-3">
                    <i class="fa-solid fa-list-check text-primary me-2"></i> Respuestas a preguntas clínicas:
                  </h5>
                  <div class="summary-answers-list">
                    <div *ngFor="let item of parseRespuestas(resp.respuestas_json || resp.respuestas_detalle)" class="summary-answer-item p-3 mb-2">
                      <div class="text-muted small fw-medium mb-1">{{ item.pregunta }}</div>
                      <div class="text-slate-900 fw-bold">{{ item.respuesta }}</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- CASO B: Formulario interactivo clínico formal y calibrado -->
              <div *ngIf="!tieneIntakeRespondido(citaSeleccionadaId) && getFormularioActivo() as fActivo" class="patient-form-card mb-4">
                
                <!-- Encabezado del Formulario Clínico -->
                <div class="form-header-box mb-4">
                  <div class="section-badge-step mb-2">
                    <span class="step-num">PASO 2</span>
                    <span class="step-label">EVALUACIÓN CLÍNICA</span>
                  </div>
                  <h2 class="form-title-formal">{{ fActivo.titulo }}</h2>
                  <p class="form-desc-formal">
                    <i class="fa-solid fa-circle-info text-primary me-2"></i>
                    {{ fActivo.descripcion || 'Por favor responda las siguientes preguntas con honestidad y tranquilidad. Sus respuestas son estrictamente confidenciales.' }}
                  </p>
                </div>

                <form (ngSubmit)="enviarIntakePaciente()" class="patient-questions-form">

                  <!-- Pregunta 1: Motivo Principal de Consulta -->
                  <div class="question-formal-card mb-4">
                    <div class="question-header">
                      <span class="q-number-pill">01</span>
                      <div class="q-title-wrap">
                        <label class="q-label-text">¿Cuál es el motivo principal por el que buscas atención psicológica? <span class="text-danger">*</span></label>
                        <p class="q-hint-text">Describe con tus propias palabras qué dificultades, síntomas o situaciones estás experimentando (ansiedad, desánimo, estrés, conflictos personales o laborales).</p>
                      </div>
                    </div>
                    <div class="q-input-wrap">
                      <textarea 
                        class="form-control-formal" 
                        rows="3" 
                        [(ngModel)]="motivoConsultaPaciente" 
                        name="motivoConsulta" 
                        required 
                        placeholder="Ejemplo: Últimamente siento que la ansiedad me sobrepasa en el trabajo y me cuesta conciliar el sueño...">
                      </textarea>
                    </div>
                  </div>

                  <!-- Pregunta 2: Nivel de Malestar Emocional (1 al 5) Calibrado -->
                  <div class="question-formal-card mb-4">
                    <div class="question-header">
                      <span class="q-number-pill">02</span>
                      <div class="q-title-wrap">
                        <label class="q-label-text">¿Cuál es tu nivel actual de malestar o angustia emocional? <span class="text-danger">*</span></label>
                        <p class="q-hint-text">En una escala del 1 (leve o manejable) al 5 (severo, agudo o urgente), califica cómo te sientes hoy:</p>
                      </div>
                    </div>
                    
                    <div class="scale-calibrated-container">
                      <div 
                        *ngFor="let n of [1, 2, 3, 4, 5]" 
                        class="scale-calibrated-pill"
                        [class.active]="nivelUrgenciaPaciente === n"
                        (click)="nivelUrgenciaPaciente = n"
                      >
                        <span class="pill-number">{{ n }}</span>
                        <span class="pill-descriptor">{{ n === 1 ? 'Mínimo' : (n === 2 ? 'Leve' : (n === 3 ? 'Moderado' : (n === 4 ? 'Alto' : 'Severo'))) }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- Preguntas Dinámicas Clínicas del Instrumento -->
                  <div *ngFor="let q of fActivo.preguntas_json; let i = index" class="question-formal-card mb-4">
                    <div class="question-header">
                      <span class="q-number-pill">{{ (i + 3) < 10 ? '0' + (i + 3) : (i + 3) }}</span>
                      <div class="q-title-wrap">
                        <label class="q-label-text">
                          {{ q.texto }}
                          <span *ngIf="q.requerido" class="text-danger">*</span>
                        </label>
                      </div>
                    </div>

                    <!-- Tipo: Escala 1 al 5 -->
                    <div *ngIf="q.tipo === 'escala_1_5'" class="scale-calibrated-container">
                      <div 
                        *ngFor="let val of [1, 2, 3, 4, 5]" 
                        class="scale-calibrated-pill" 
                        [class.active]="respuestasPacienteForm[q.id] === val"
                        (click)="respuestasPacienteForm[q.id] = val"
                      >
                        <span class="pill-number">{{ val }}</span>
                        <span class="pill-descriptor">{{ val === 1 ? 'Nada' : (val === 3 ? 'A veces' : (val === 5 ? 'Siempre' : '')) }}</span>
                      </div>
                    </div>

                    <!-- Tipo: Likert -->
                    <div *ngIf="q.tipo === 'likert'" class="likert-calibrated-container">
                      <button 
                        type="button" 
                        *ngFor="let opt of ['Totalmente en desacuerdo', 'En desacuerdo', 'Neutral', 'De acuerdo', 'Totalmente de acuerdo']"
                        class="likert-pill"
                        [class.active]="respuestasPacienteForm[q.id] === opt"
                        (click)="respuestasPacienteForm[q.id] = opt"
                      >
                        {{ opt }}
                      </button>
                    </div>

                    <!-- Tipo: Opción Múltiple como Tarjetas Elegantes -->
                    <div *ngIf="q.tipo === 'opcion_multiple'" class="options-choice-grid">
                      <div 
                        *ngFor="let op of q.opciones" 
                        class="option-choice-card"
                        [class.selected]="respuestasPacienteForm[q.id] === op"
                        (click)="respuestasPacienteForm[q.id] = op"
                      >
                        <div class="choice-radio">
                          <i class="fa-solid fa-circle-check text-primary" *ngIf="respuestasPacienteForm[q.id] === op"></i>
                          <i class="fa-regular fa-circle text-muted" *ngIf="respuestasPacienteForm[q.id] !== op"></i>
                        </div>
                        <span class="choice-text">{{ op }}</span>
                      </div>
                    </div>

                    <!-- Tipo: Booleano (Segmented Toggle Estético) -->
                    <div *ngIf="q.tipo === 'booleano'" class="boolean-toggle-container">
                      <button 
                        type="button" 
                        class="boolean-pill yes" 
                        [class.active]="respuestasPacienteForm[q.id] === true"
                        (click)="respuestasPacienteForm[q.id] = true"
                      >
                        <i class="fa-solid fa-check me-2"></i> Sí
                      </button>
                      <button 
                        type="button" 
                        class="boolean-pill no" 
                        [class.active]="respuestasPacienteForm[q.id] === false"
                        (click)="respuestasPacienteForm[q.id] = false"
                      >
                        <i class="fa-solid fa-xmark me-2"></i> No
                      </button>
                    </div>

                    <!-- Tipo: Texto Libre -->
                    <div *ngIf="q.tipo === 'texto'" class="q-input-wrap">
                      <textarea 
                        class="form-control-formal" 
                        rows="2" 
                        [(ngModel)]="respuestasPacienteForm[q.id]" 
                        [name]="'q_' + q.id"
                        placeholder="Escribe tu respuesta aquí...">
                      </textarea>
                    </div>
                  </div>

                  <!-- Consentimiento Ético y Confidencialidad IA (HU-35) -->
                  <div class="consent-ethical-card mb-4">
                    <div class="form-check d-flex align-items-start gap-3 m-0">
                      <input 
                        class="form-check-input consent-checkbox mt-1" 
                        type="checkbox" 
                        [(ngModel)]="consentimientoIAPaciente" 
                        id="consentIA" 
                        name="consentIA" 
                      />
                      <label class="form-check-label" for="consentIA">
                        <span class="consent-title d-block">
                          <i class="fa-solid fa-shield-heart text-emerald me-1"></i>
                          Consentimiento Ético de Triaje Clínico Supervisado (HU-35)
                        </span>
                        <span class="consent-text d-block text-muted">
                          Autorizo el procesamiento confidencial de mis respuestas bajo supervisión profesional directa de mi terapeuta. Entiendo que los datos están resguardados bajo el secreto profesional médico y la legislación vigente de protección de datos de salud.
                        </span>
                      </label>
                    </div>
                  </div>

                  <!-- Alerta de Error si faltan datos -->
                  <div *ngIf="errorEnvioPaciente" class="alert alert-danger d-flex align-items-center mb-4">
                    <i class="fa-solid fa-circle-exclamation fa-lg me-3"></i>
                    <div>{{ errorEnvioPaciente }}</div>
                  </div>

                  <!-- Botón Principal de Envío Calibrado y Centrado -->
                  <div class="patient-submit-box text-center pt-2">
                    <button 
                      type="submit" 
                      class="btn-formal-submit" 
                      [disabled]="enviandoRespuesta() || !motivoConsultaPaciente"
                    >
                      <i class="fa-solid" [class.fa-paper-plane]="!enviandoRespuesta()" [class.fa-spinner]="enviandoRespuesta()" [class.fa-spin]="enviandoRespuesta()"></i>
                      <span class="ms-2">{{ enviandoRespuesta() ? 'Enviando Respuestas Confidenciales...' : 'Enviar Cuestionario Clínico' }}</span>
                    </button>
                    <p class="security-caption mt-3">
                      <i class="fa-solid fa-lock text-emerald me-1"></i> Sus respuestas se transmiten de forma cifrada y segura a su expediente.
                    </p>
                  </div>
                </form>
              </div>
            </div>
          </div>

        </div>
      </ng-container>

      <!-- ==================================================================== -->
      <!-- VISTA 2: GESTIÓN DE CUESTIONARIOS (Staff / Psicólogo / Admin)         -->
      <!-- ==================================================================== -->
      <ng-container *ngIf="!authService.isPaciente()">
        <!-- Encabezado Principal -->
        <div class="page-header glass-panel mb-4">
          <div class="header-content">
            <h1 class="page-title">
              <i class="fa-solid fa-clipboard-question text-primary"></i>
              Intake Digital & Cuestionarios Pre-Consulta
            </h1>
            <p class="page-subtitle">
              Instrumentos psicométricos y cuestionarios anamnésicos previos a la primera cita.
              Procesamiento clínico con motor de IA supervisada (Sprint 2 - HU-23, HU-24, HU-35).
            </p>
          </div>
          <div class="header-actions">
            <button class="btn btn-outline-primary" (click)="activeTab = 'respuestas'">
              <i class="fa-solid fa-inbox me-1"></i> Respuestas Pacientes ({{ respuestas().length }})
            </button>
            <button class="btn btn-primary" (click)="openCreateModal()">
              <i class="fa-solid fa-plus me-1"></i> Nuevo Cuestionario
            </button>
          </div>
        </div>

        <!-- Navegación por Pestañas -->
        <div class="tabs-bar glass-panel mb-4">
          <button class="tab-btn" [class.active]="activeTab === 'formularios'" (click)="activeTab = 'formularios'">
            <i class="fa-solid fa-file-lines me-1"></i>
            Plantillas de Cuestionarios ({{ formularios().length }})
          </button>
          <button class="tab-btn" [class.active]="activeTab === 'respuestas'" (click)="activeTab = 'respuestas'">
            <i class="fa-solid fa-clipboard-check me-1"></i>
            Respuestas Recibidas de Pacientes ({{ respuestas().length }})
          </button>
        </div>

        <!-- Notificación Flotante -->
        <div *ngIf="mensajeExito()" class="alert alert-success d-flex align-items-center mb-4">
          <i class="fa-solid fa-circle-check me-2"></i>
          <span>{{ mensajeExito() }}</span>
        </div>

        <!-- TAB 1: PLANTILLAS DE FORMULARIOS -->
        <div *ngIf="activeTab === 'formularios'">
          <div *ngIf="cargando()" class="loading-state glass-panel">
            <i class="fa-solid fa-spinner fa-spin fa-2x text-primary mb-3"></i>
            <span>Cargando plantillas de cuestionarios...</span>
          </div>

          <div *ngIf="!cargando() && formularios().length === 0" class="empty-state glass-panel text-center p-5">
            <i class="fa-solid fa-file-circle-plus fa-3x text-dim mb-3"></i>
            <h3>No hay cuestionarios pre-consulta configurados</h3>
            <p class="text-muted">Cree el primer formulario pre-consulta para que los pacientes respondan antes de su cita.</p>
            <button class="btn btn-primary mt-2" (click)="openCreateModal()">
              <i class="fa-solid fa-plus me-1"></i> Configurar Cuestionario
            </button>
          </div>

          <div class="cards-grid" *ngIf="!cargando() && formularios().length > 0">
            <div class="questionnaire-card" *ngFor="let form of formularios()">
              <div class="card-header-row">
                <div class="version-badge">{{ formatearVersion(form.version) }}</div>
                <span class="status-pill" [class.active]="form.activo">
                  <span class="status-dot"></span>
                  {{ form.activo ? 'ACTIVO' : 'INACTIVO' }}
                </span>
              </div>

              <h3 class="form-title" [title]="form.titulo">{{ form.titulo }}</h3>
              <p class="form-desc">{{ form.descripcion || 'Sin descripción clínica especificada.' }}</p>
              
              <div class="form-meta">
                <span class="meta-field">
                  <i class="fa-solid fa-list-check text-primary me-1"></i>
                  <strong>{{ form.preguntas_json.length }}</strong> preguntas
                </span>
                <span class="meta-field">
                  <i class="fa-regular fa-calendar text-muted me-1"></i>
                  {{ form.fecha_creacion | date:'dd/MM/yyyy' }}
                </span>
              </div>

              <div class="questions-preview">
                <span class="preview-label">
                  <i class="fa-solid fa-layer-group me-1"></i> Muestra de preguntas clínicas:
                </span>
                <ul class="preview-list">
                  <li *ngFor="let q of form.preguntas_json.slice(0, 3)" class="preview-item">
                    <span class="preview-text">
                      <i class="fa-solid fa-circle text-primary preview-bullet"></i>
                      {{ q.texto }}
                    </span>
                    <span class="badge-type">{{ q.tipo }}</span>
                  </li>
                </ul>
              </div>

              <div class="card-actions">
                <button class="btn btn-action-view" (click)="verDetalleFormulario(form)">
                  <i class="fa-regular fa-eye me-1"></i> Ver Preguntas
                </button>
                <button class="btn btn-action-edit" (click)="duplicarOEditar(form)">
                  <i class="fa-regular fa-pen-to-square me-1"></i> Editar
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- TAB 2: RESPUESTAS RECIBIDAS -->
        <div *ngIf="activeTab === 'respuestas'">
          <div *ngIf="cargando()" class="loading-state glass-panel">
            <i class="fa-solid fa-spinner fa-spin fa-2x text-primary mb-3"></i>
            <span>Cargando respuestas de pacientes...</span>
          </div>

          <div *ngIf="!cargando() && respuestas().length === 0" class="empty-state glass-panel text-center p-5">
            <i class="fa-solid fa-inbox fa-3x text-dim mb-3"></i>
            <h3>No se han recibido respuestas de pre-consulta</h3>
            <p class="text-muted">Cuando los pacientes completen el intake previo a su cita, aparecerán aquí para revisión.</p>
          </div>

          <div class="table-responsive glass-panel" *ngIf="!cargando() && respuestas().length > 0">
            <table class="custom-table">
              <thead>
                <tr>
                  <th>Paciente</th>
                  <th>Cuestionario</th>
                  <th>Fecha Respuesta</th>
                  <th>Consentimiento IA</th>
                  <th>Estado</th>
                  <th class="text-end">Acciones Clínicas</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let r of respuestas()">
                  <td>
                    <div class="patient-cell">
                      <div class="patient-avatar">{{ (r.paciente_nombre || 'P').charAt(0) }}</div>
                      <div>
                        <strong>{{ r.paciente_nombre || 'Paciente Registrado' }}</strong>
                        <small class="d-block text-muted">ID Cita: {{ (r.cita || '').toString().substring(0, 8) }}...</small>
                      </div>
                    </div>
                  </td>
                  <td>{{ r.formulario_titulo || 'Intake Psicológico Inicial' }}</td>
                  <td>{{ (r.fecha_envio || r.fecha_respuesta || '') | date:'dd/MM/yyyy HH:mm' }}</td>
                  <td>
                    <span class="badge" [class.bg-success]="r.consentimiento_ia_procesamiento" [class.bg-secondary]="!r.consentimiento_ia_procesamiento">
                      {{ r.consentimiento_ia_procesamiento ? 'Autorizado' : 'Pendiente' }}
                    </span>
                  </td>
                  <td>
                    <span class="badge" [class.bg-warning]="r.tiene_urgencia_alta" [class.bg-info]="!r.tiene_urgencia_alta">
                      {{ r.tiene_urgencia_alta ? 'Urgencia Elevada' : (r.estado || 'Enviado') }}
                    </span>
                  </td>
                  <td class="text-end">
                    <button class="btn btn-sm btn-outline-secondary me-2" (click)="verDetalleRespuesta(r)">
                      <i class="fa-solid fa-file-lines"></i> Ver Respuestas
                    </button>
                    <button 
                      class="btn btn-sm btn-ai-gradient"
                      (click)="abrirAsistenteIA(r)"
                      title="Ejecutar Asistente de IA (Reglas Romero)">
                      <i class="fa-solid fa-brain"></i> Asistente IA (HU-35)
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- MODAL: CREAR / EDITAR CUESTIONARIO -->
        <div *ngIf="mostrarModalForm" class="modal-backdrop-custom" (click)="mostrarModalForm = false">
          <div class="modal-dialog-custom glass-card-modal modal-lg" (click)="$event.stopPropagation()">
            <div class="modal-header-custom">
              <h2 class="modal-title">
                <i class="fa-solid fa-clipboard-question text-primary me-2"></i>
                Configurar Cuestionario Pre-Consulta (Intake)
              </h2>
              <button class="btn-close-custom" (click)="mostrarModalForm = false">
                <i class="fa-solid fa-xmark"></i>
              </button>
            </div>

            <div class="modal-body-custom">
              <div class="row g-3 mb-3">
                <div class="col-md-8">
                  <label class="form-label">Título del Instrumento / Cuestionario *</label>
                  <input type="text" class="form-control" [(ngModel)]="nuevoFormulario.titulo" 
                         placeholder="Ej. Cuestionario de Sintomatología Inicial y Motivo de Consulta" />
                </div>
                <div class="col-md-4">
                  <label class="form-label">Estado</label>
                  <div class="form-check form-switch mt-2">
                    <input class="form-check-input" type="checkbox" [(ngModel)]="nuevoFormulario.activo" id="activoCheck" />
                    <label class="form-check-label" for="activoCheck">Publicado y Activo</label>
                  </div>
                </div>
                <div class="col-12">
                  <label class="form-label">Instrucciones o Descripción</label>
                  <textarea class="form-control" [(ngModel)]="nuevoFormulario.descripcion" rows="2"
                            placeholder="Instrucciones para el paciente antes de responder..."></textarea>
                </div>
              </div>

              <!-- Editor de Preguntas Dinámicas -->
              <div class="questions-builder-panel glass-panel p-3 mb-3">
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <h4 class="m-0"><i class="fa-solid fa-list-ol text-primary me-2"></i>Banco de Preguntas</h4>
                  <button class="btn btn-sm btn-outline-primary" (click)="agregarPregunta()">
                    <i class="fa-solid fa-plus"></i> Añadir Pregunta
                  </button>
                </div>

                <div *ngFor="let p of nuevoFormulario.preguntas_json; let idx = index" class="question-row-card mb-2 p-2">
                  <div class="d-flex align-items-center gap-2 mb-2">
                    <span class="badge bg-secondary">#{{ idx + 1 }}</span>
                    <input type="text" class="form-control form-control-sm flex-grow-1" [(ngModel)]="p.texto" 
                           placeholder="Escriba la pregunta o ítem clínico..." />
                    
                    <select class="form-select form-select-sm" [(ngModel)]="p.tipo" style="width: 170px;">
                      <option value="texto">Texto Libre</option>
                      <option value="escala_1_5">Escala Likert (1 - 5)</option>
                      <option value="booleano">Sí / No</option>
                      <option value="opcion_multiple">Opción Múltiple</option>
                    </select>

                    <div class="form-check form-check-inline m-0">
                      <input class="form-check-input" type="checkbox" [(ngModel)]="p.requerido" [id]="'req_' + idx">
                      <label class="form-check-label small" [for]="'req_' + idx">Obligatoria</label>
                    </div>

                    <button class="btn btn-sm btn-outline-danger" (click)="eliminarPregunta(idx)">
                      <i class="fa-solid fa-trash"></i>
                    </button>
                  </div>

                  <div *ngIf="p.tipo === 'opcion_multiple'" class="ps-4">
                    <input type="text" class="form-control form-control-sm" 
                           [ngModel]="(p.opciones || []).join(', ')"
                           (ngModelChange)="actualizarOpcionesPregunta(p, $event)"
                           placeholder="Opciones separadas por coma (ej. Casi nunca, A veces, Siempre)" />
                  </div>
                </div>
              </div>
            </div>

            <div class="modal-footer-custom">
              <button class="btn btn-secondary" (click)="mostrarModalForm = false">Cancelar</button>
              <button class="btn btn-primary" [disabled]="!nuevoFormulario.titulo" (click)="guardarFormulario()">
                <i class="fa-solid fa-save me-1"></i> Guardar Cuestionario
              </button>
            </div>
          </div>
        </div>

        <!-- MODAL: VER DETALLES DE RESPUESTA DE PACIENTE -->
        <div *ngIf="respuestaSeleccionada" class="modal-backdrop-custom" (click)="respuestaSeleccionada = null">
          <div class="modal-dialog-custom glass-card-modal modal-lg" (click)="$event.stopPropagation()">
            <div class="modal-header-custom">
              <h2 class="modal-title">
                <i class="fa-solid fa-clipboard-user text-primary me-2"></i>
                Respuestas de {{ respuestaSeleccionada.paciente_nombre }}
              </h2>
              <button class="btn-close-custom" (click)="respuestaSeleccionada = null">
                <i class="fa-solid fa-xmark"></i>
              </button>
            </div>

            <div class="modal-body-custom">
              <div class="patient-info-strip glass-panel p-3 mb-3 d-flex justify-content-between align-items-center">
                <div>
                  <strong>Fecha de Envío:</strong> {{ (respuestaSeleccionada.fecha_envio || respuestaSeleccionada.fecha_respuesta) | date:'medium' }}
                </div>
                <div>
                  <strong>Consentimiento IA:</strong> 
                  <span class="badge ms-1" [class.bg-success]="respuestaSeleccionada.consentimiento_ia_procesamiento" [class.bg-secondary]="!respuestaSeleccionada.consentimiento_ia_procesamiento">
                    {{ respuestaSeleccionada.consentimiento_ia_procesamiento ? 'Autorizado' : 'Rechazado' }}
                  </span>
                </div>
              </div>

              <div class="answers-container">
                <div *ngFor="let item of parseRespuestas(respuestaSeleccionada.respuestas_json || respuestaSeleccionada.respuestas_detalle)" class="answer-item p-3 mb-2 glass-panel">
                  <div class="text-muted small mb-1"><i class="fa-solid fa-circle-question me-1"></i> {{ item.pregunta }}</div>
                  <div class="fw-bold text-dark fs-6">{{ item.respuesta }}</div>
                </div>
              </div>
            </div>

            <div class="modal-footer-custom">
              <button class="btn btn-secondary" (click)="respuestaSeleccionada = null">Cerrar</button>
              <button 
                *ngIf="respuestaSeleccionada.consentimiento_ia_procesamiento"
                class="btn btn-ai-gradient"
                (click)="abrirAsistenteIA(respuestaSeleccionada)">
                <i class="fa-solid fa-brain me-1"></i> Analizar con Asistente IA
              </button>
            </div>
          </div>
        </div>

        <!-- MODAL HU-35: ASISTENTE IA DE PRECONSULTA -->
        <app-ia-asistente-modal
          *ngIf="mostrarModalIA"
          [respuestaId]="respuestaIdParaIA"
          (cerrar)="mostrarModalIA = false"
          (decisionRegistrada)="onDecisionIARegistrada($event)">
        </app-ia-asistente-modal>
      </ng-container>

    </div>
  `,
  styles: [`
    .intake-container {
      max-width: 1300px;
      margin: 0 auto;
    }

    .page-header {
      padding: 1.75rem 2.25rem;
      border-radius: 18px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #ffffff;
      border: 1px solid #e2e8f0;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
    }

    .header-content {
      flex: 1;
    }

    .page-title {
      font-size: 1.55rem;
      font-weight: 700;
      color: #0f172a;
      margin: 0 0 0.35rem 0;
      letter-spacing: -0.01em;
    }

    .page-subtitle {
      font-size: 0.9rem;
      color: #64748b;
      margin: 0;
      max-width: 780px;
      line-height: 1.5;
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 0.85rem;
      flex-shrink: 0;
      white-space: nowrap;
    }

    .tabs-bar {
      display: flex;
      gap: 0.5rem;
      padding: 0.4rem;
      background: #f1f5f9;
      border-radius: 12px;
      border: 1px solid #e2e8f0;
    }

    .tab-btn {
      padding: 0.7rem 1.4rem;
      border: none;
      background: transparent;
      color: #64748b;
      font-weight: 600;
      font-size: 0.9rem;
      border-radius: 9px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .tab-btn.active {
      background: #ffffff;
      color: #0d9488;
      font-weight: 700;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }

    .cards-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(440px, 1fr));
      gap: 1.75rem;
      align-items: stretch;
    }

    .questionnaire-card {
      padding: 1.75rem 2rem;
      border-radius: 18px;
      background: #ffffff;
      border: 1.5px solid #e2e8f0;
      display: flex;
      flex-direction: column;
      height: 100%;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
      transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .questionnaire-card:hover {
      transform: translateY(-3px);
      box-shadow: 0 12px 28px -4px rgba(0, 0, 0, 0.08);
      border-color: #99f6e4;
    }

    .card-header-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }

    .version-badge {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      color: #334155;
      font-size: 0.75rem;
      font-weight: 800;
      padding: 0.25rem 0.65rem;
      border-radius: 8px;
      letter-spacing: 0.03em;
    }

    .status-pill {
      font-size: 0.72rem;
      font-weight: 700;
      padding: 0.25rem 0.75rem;
      border-radius: 20px;
      background: #f1f5f9;
      color: #64748b;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      letter-spacing: 0.04em;
    }

    .status-pill.active {
      background: #dcfce7;
      color: #15803d;
      border: 1px solid #bbf7d0;
    }

    .status-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: currentColor;
    }

    .form-title {
      font-size: 1.25rem;
      font-weight: 700;
      color: #0f172a;
      margin: 0 0 0.5rem 0;
      min-height: 3.2rem;
      display: flex;
      align-items: flex-start;
      line-height: 1.35;
      letter-spacing: -0.01em;
    }

    .form-desc {
      font-size: 0.88rem;
      color: #64748b;
      margin: 0 0 1.2rem 0;
      line-height: 1.5;
      min-height: 4rem;
      display: flex;
      align-items: flex-start;
    }

    .form-meta {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.82rem;
      color: #64748b;
      padding: 0.75rem 0;
      border-top: 1px solid #f1f5f9;
      border-bottom: 1px solid #f1f5f9;
      margin-bottom: 1.25rem;
    }

    .meta-field {
      display: flex;
      align-items: center;
    }

    .questions-preview {
      flex: 1;
      min-height: 175px;
      background: #f8fafc;
      border: 1px solid #eef2f6;
      border-radius: 12px;
      padding: 1rem 1.25rem;
      margin-bottom: 1.5rem;
      display: flex;
      flex-direction: column;
    }

    .preview-label {
      font-size: 0.74rem;
      font-weight: 700;
      color: #475569;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      margin-bottom: 0.65rem;
      display: flex;
      align-items: center;
    }

    .preview-list {
      list-style: none;
      padding: 0;
      margin: 0;
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
      flex: 1;
    }

    .preview-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.75rem;
      font-size: 0.82rem;
      color: #334155;
      line-height: 1.35;
    }

    .preview-text {
      display: flex;
      align-items: center;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .preview-bullet {
      font-size: 0.35rem;
      margin-right: 0.6rem;
      color: #0d9488;
      flex-shrink: 0;
    }

    .badge-type {
      font-size: 0.68rem;
      font-weight: 700;
      color: #0284c7;
      background: #e0f2fe;
      padding: 0.2rem 0.55rem;
      border-radius: 12px;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      white-space: nowrap;
      flex-shrink: 0;
    }

    .card-actions {
      margin-top: auto;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.85rem;
    }

    .btn-action-view {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      padding: 0.7rem 1rem;
      border-radius: 10px;
      font-weight: 600;
      font-size: 0.88rem;
      border: 1.5px solid #cbd5e1;
      background: #ffffff;
      color: #334155;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .btn-action-view:hover {
      border-color: #0d9488;
      background: #f0fdfa;
      color: #0d9488;
    }

    .btn-action-edit {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      padding: 0.7rem 1rem;
      border-radius: 10px;
      font-weight: 600;
      font-size: 0.88rem;
      border: 1.5px solid #0d9488;
      background: #0d9488;
      color: #ffffff;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .btn-action-edit:hover {
      background: #0f766e;
      border-color: #0f766e;
      box-shadow: 0 4px 12px rgba(13, 148, 136, 0.25);
    }

    .custom-table {
      width: 100%;
      border-collapse: collapse;
      background: #ffffff;
      border-radius: 12px;
      overflow: hidden;
    }

    .custom-table th {
      background: #f8fafc;
      padding: 1rem;
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      color: #64748b;
      border-bottom: 1px solid #e2e8f0;
    }

    .custom-table td {
      padding: 1rem;
      font-size: 0.85rem;
      color: #1e293b;
      border-bottom: 1px solid #f1f5f9;
      vertical-align: middle;
    }

    .patient-cell {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }

    .patient-avatar {
      width: 36px;
      height: 36px;
      background: #e0f2fe;
      color: #0369a1;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 0.9rem;
    }

    .btn-ai-gradient {
      background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
      color: #ffffff;
      border: none;
      font-weight: 600;
      box-shadow: 0 2px 6px rgba(99, 102, 241, 0.25);
    }

    .btn-ai-gradient:hover {
      opacity: 0.95;
      color: #ffffff;
      transform: translateY(-1px);
    }

    /* Modal Styles */
    .modal-backdrop-custom {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(15, 23, 42, 0.6);
      backdrop-filter: blur(4px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1050;
      padding: 1rem;
    }

    .glass-card-modal {
      background: #ffffff;
      border-radius: 16px;
      border: 1px solid #e2e8f0;
      box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
      width: 100%;
      max-height: 90vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    .modal-lg { max-width: 800px; }

    .modal-header-custom {
      padding: 1.25rem 1.5rem;
      border-bottom: 1px solid #e2e8f0;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .modal-title {
      font-size: 1.2rem;
      font-weight: 700;
      color: #0f172a;
      margin: 0;
      display: flex;
      align-items: center;
    }

    .btn-close-custom {
      background: transparent;
      border: none;
      color: #94a3b8;
      font-size: 1.25rem;
      cursor: pointer;
    }

    .btn-close-custom:hover { color: #0f172a; }

    .modal-body-custom {
      padding: 1.5rem;
      overflow-y: auto;
    }

    .modal-footer-custom {
      padding: 1rem 1.5rem;
      border-top: 1px solid #e2e8f0;
      display: flex;
      justify-content: flex-end;
      gap: 0.75rem;
      background: #f8fafc;
    }

    .question-row-card {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
    }

    /* ========================================================================== */
    /* ESTILOS: PORTAL DEL PACIENTE (CENTRADOS, FORMALES Y CALIBRADOS)            */
    /* ========================================================================== */
    .patient-portal-centered {
      max-width: 860px;
      margin: 0 auto;
      padding: 0.5rem 1rem 3rem 1rem;
    }

    /* Hero Banner */
    .patient-hero-banner {
      background: linear-gradient(135deg, #092e20 0%, #115e59 100%);
      color: #ffffff;
      border-radius: 20px;
      padding: 2.2rem 2.5rem;
      box-shadow: 0 10px 25px -5px rgba(9, 46, 32, 0.25);
      position: relative;
      overflow: hidden;
    }

    .patient-hero-banner::after {
      content: '';
      position: absolute;
      top: -40px;
      right: -40px;
      width: 180px;
      height: 180px;
      background: radial-gradient(circle, rgba(45, 212, 191, 0.15) 0%, rgba(255,255,255,0) 70%);
      border-radius: 50%;
      pointer-events: none;
    }

    .patient-hero-badge {
      display: inline-flex;
      align-items: center;
      background: rgba(255, 255, 255, 0.15);
      backdrop-filter: blur(8px);
      color: #99f6e4;
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      padding: 0.35rem 0.85rem;
      border-radius: 30px;
      margin-bottom: 0.85rem;
      border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .patient-hero-title {
      font-size: 1.75rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      color: #ffffff;
      margin: 0 0 0.65rem 0;
      line-height: 1.25;
    }

    .patient-hero-subtitle {
      font-size: 0.95rem;
      color: #ccfbf1;
      line-height: 1.55;
      margin: 0 0 1.2rem 0;
      max-width: 720px;
    }

    .patient-hero-meta {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      font-size: 0.82rem;
      color: #99f6e4;
      flex-wrap: wrap;
    }

    .meta-item {
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }

    .meta-divider {
      opacity: 0.5;
    }

    .text-emerald {
      color: #10b981;
    }

    .text-emerald-dark {
      color: #065f46;
    }

    /* Loading and Empty State Cards */
    .loading-state-card, .empty-state-card {
      background: #ffffff;
      border-radius: 18px;
      border: 1px solid #e2e8f0;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
    }

    .empty-icon-circle {
      width: 70px;
      height: 70px;
      background: #f1f5f9;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto;
    }

    .alert-success-formal {
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
      border-radius: 14px;
      padding: 1rem 1.25rem;
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.08);
    }

    /* Section Step Badges */
    .section-badge-step {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      background: #f0fdfa;
      border: 1px solid #ccfbf1;
      border-radius: 20px;
      padding: 0.25rem 0.75rem;
      margin-bottom: 0.75rem;
    }

    .step-num {
      font-size: 0.7rem;
      font-weight: 800;
      color: #0f766e;
      letter-spacing: 0.05em;
    }

    .step-label {
      font-size: 0.72rem;
      font-weight: 700;
      color: #115e59;
      letter-spacing: 0.04em;
    }

    /* Step 1: Appointment Selector */
    .patient-section-card {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 18px;
      padding: 1.75rem 2rem;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
    }

    .section-title-formal {
      font-size: 1.15rem;
      font-weight: 700;
      color: #1e293b;
      margin: 0 0 1.25rem 0;
    }

    .cita-selector-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 1.2rem;
    }

    .patient-cita-card {
      border: 2px solid #e2e8f0;
      background: #fafbfc;
      border-radius: 14px;
      padding: 1.2rem;
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    .patient-cita-card:hover {
      border-color: #99f6e4;
      background: #f0fdfa;
      transform: translateY(-2px);
    }

    .patient-cita-card.selected {
      border-color: #0d9488;
      background: #f0fdfa;
      box-shadow: 0 6px 18px rgba(13, 148, 136, 0.14);
    }

    .cita-card-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .cita-date-pill {
      font-size: 0.92rem;
      color: #0f172a;
    }

    .radio-indicator {
      font-size: 1.1rem;
    }

    .cita-card-body {
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
      font-size: 0.85rem;
      color: #475569;
    }

    .cita-meta-row {
      display: flex;
      align-items: center;
    }

    .cita-card-footer {
      margin-top: 0.25rem;
    }

    .status-chip {
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      font-size: 0.75rem;
      font-weight: 700;
      padding: 0.3rem 0.65rem;
      border-radius: 20px;
    }

    .status-chip.pending {
      background: #fef3c7;
      color: #92400e;
      border: 1px solid #fde68a;
    }

    .status-chip.completed {
      background: #d1fae5;
      color: #065f46;
      border: 1px solid #a7f3d0;
    }

    /* Step 2: Main Questionnaire Form Card */
    .patient-form-card {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 20px;
      padding: 2.5rem;
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.04);
    }

    .form-header-box {
      border-bottom: 1px solid #f1f5f9;
      padding-bottom: 1.5rem;
    }

    .form-title-formal {
      font-size: 1.45rem;
      font-weight: 700;
      color: #0f172a;
      margin: 0 0 0.5rem 0;
      letter-spacing: -0.01em;
    }

    .form-desc-formal {
      font-size: 0.92rem;
      color: #64748b;
      margin: 0;
      line-height: 1.5;
    }

    /* Individual Question Cards */
    .question-formal-card {
      background: #fafbfc;
      border: 1px solid #eef2f6;
      border-radius: 16px;
      padding: 1.5rem 1.75rem;
      transition: border-color 0.2s;
    }

    .question-formal-card:focus-within {
      border-color: #cbd5e1;
      background: #ffffff;
    }

    .question-header {
      display: flex;
      align-items: flex-start;
      gap: 0.85rem;
      margin-bottom: 1.15rem;
    }

    .q-number-pill {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 32px;
      height: 32px;
      border-radius: 10px;
      background: #e0f2fe;
      color: #0369a1;
      font-size: 0.82rem;
      font-weight: 800;
      flex-shrink: 0;
    }

    .q-title-wrap {
      flex: 1;
    }

    .q-label-text {
      font-size: 1rem;
      font-weight: 700;
      color: #1e293b;
      margin: 0 0 0.25rem 0;
      display: block;
      line-height: 1.4;
    }

    .q-hint-text {
      font-size: 0.84rem;
      color: #64748b;
      margin: 0;
      line-height: 1.4;
    }

    /* Inputs & Textareas */
    .form-control-formal {
      width: 100%;
      border: 1.5px solid #cbd5e1;
      border-radius: 12px;
      padding: 0.85rem 1.1rem;
      font-size: 0.95rem;
      color: #0f172a;
      background: #ffffff;
      outline: none;
      transition: all 0.2s ease;
      font-family: inherit;
    }

    .form-control-formal:focus {
      border-color: #0d9488;
      box-shadow: 0 0 0 4px rgba(13, 148, 136, 0.12);
    }

    /* Calibrated 1-5 Scale Rating Selector */
    .scale-calibrated-container {
      display: flex;
      justify-content: center;
      gap: 12px;
      margin-top: 0.5rem;
    }

    .scale-calibrated-pill {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      width: 82px;
      height: 72px;
      border-radius: 14px;
      border: 1.5px solid #cbd5e1;
      background: #ffffff;
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .scale-calibrated-pill:hover {
      border-color: #0d9488;
      background: #f0fdfa;
      transform: translateY(-2px);
    }

    .scale-calibrated-pill.active {
      border-color: #0d9488;
      background: #0d9488;
      color: #ffffff;
      box-shadow: 0 6px 16px rgba(13, 148, 136, 0.35);
      transform: translateY(-2px);
    }

    .pill-number {
      font-size: 1.35rem;
      font-weight: 800;
      line-height: 1;
    }

    .pill-descriptor {
      font-size: 0.68rem;
      font-weight: 600;
      margin-top: 4px;
      opacity: 0.9;
    }

    /* Likert Scale Pills */
    .likert-calibrated-container {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: center;
      margin-top: 0.5rem;
    }

    .likert-pill {
      padding: 0.6rem 1.1rem;
      border-radius: 20px;
      border: 1.5px solid #cbd5e1;
      background: #ffffff;
      color: #334155;
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .likert-pill:hover {
      border-color: #0d9488;
      background: #f0fdfa;
    }

    .likert-pill.active {
      background: #0d9488;
      color: #ffffff;
      border-color: #0d9488;
      box-shadow: 0 4px 12px rgba(13, 148, 136, 0.25);
    }

    /* Option Choice Grid */
    .options-choice-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 0.75rem;
      margin-top: 0.5rem;
    }

    .option-choice-card {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.85rem 1rem;
      border-radius: 12px;
      border: 1.5px solid #cbd5e1;
      background: #ffffff;
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .option-choice-card:hover {
      border-color: #0d9488;
      background: #f0fdfa;
    }

    .option-choice-card.selected {
      border-color: #0d9488;
      background: #f0fdfa;
      box-shadow: 0 4px 12px rgba(13, 148, 136, 0.12);
    }

    .choice-text {
      font-size: 0.9rem;
      font-weight: 600;
      color: #1e293b;
    }

    /* Boolean Segmented Toggle */
    .boolean-toggle-container {
      display: flex;
      gap: 12px;
      margin-top: 0.5rem;
    }

    .boolean-pill {
      flex: 1;
      max-width: 140px;
      padding: 0.75rem 1.25rem;
      border-radius: 12px;
      border: 1.5px solid #cbd5e1;
      background: #ffffff;
      font-weight: 700;
      font-size: 0.95rem;
      cursor: pointer;
      transition: all 0.2s ease;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      color: #475569;
    }

    .boolean-pill.yes:hover, .boolean-pill.yes.active {
      border-color: #0d9488;
      background: #0d9488;
      color: #ffffff;
      box-shadow: 0 4px 12px rgba(13, 148, 136, 0.25);
    }

    .boolean-pill.no:hover, .boolean-pill.no.active {
      border-color: #64748b;
      background: #64748b;
      color: #ffffff;
      box-shadow: 0 4px 12px rgba(100, 116, 139, 0.25);
    }

    /* Consent Ethical Card */
    .consent-ethical-card {
      background: #f0fdf4;
      border: 1.5px solid #bbf7d0;
      border-radius: 16px;
      padding: 1.25rem 1.5rem;
    }

    .consent-checkbox {
      width: 1.35rem;
      height: 1.35rem;
      cursor: pointer;
      accent-color: #0d9488;
    }

    .consent-title {
      font-size: 0.95rem;
      font-weight: 700;
      color: #065f46;
      margin-bottom: 0.25rem;
    }

    .consent-text {
      font-size: 0.84rem;
      line-height: 1.5;
    }

    /* Submit Button Area */
    .patient-submit-box {
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    .btn-formal-submit {
      background: linear-gradient(135deg, #0d9488 0%, #059669 100%);
      color: #ffffff;
      border: none;
      border-radius: 50px;
      padding: 1rem 2.8rem;
      font-size: 1.05rem;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 8px 20px rgba(13, 148, 136, 0.3);
      transition: all 0.25s ease;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }

    .btn-formal-submit:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 12px 24px rgba(13, 148, 136, 0.4);
    }

    .btn-formal-submit:disabled {
      opacity: 0.55;
      cursor: not-allowed;
      box-shadow: none;
    }

    .security-caption {
      font-size: 0.8rem;
      color: #64748b;
      margin: 0;
    }

    /* Completed View */
    .patient-completed-card {
      background: #ffffff;
      border: 1.5px solid #a7f3d0;
      border-radius: 20px;
      box-shadow: 0 8px 24px rgba(16, 185, 129, 0.08);
      text-align: center;
    }

    .completed-icon-circle {
      width: 80px;
      height: 80px;
      background: #ecfdf5;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .completed-title {
      font-size: 1.6rem;
      font-weight: 800;
      margin: 0 0 0.5rem 0;
      letter-spacing: -0.01em;
    }

    .completed-subtitle {
      font-size: 0.95rem;
      line-height: 1.55;
    }

    .completed-summary-box {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 14px;
    }

    .badge-malestar {
      background: #0284c7;
      color: #ffffff;
      font-size: 0.85rem;
      font-weight: 700;
      padding: 0.25rem 0.65rem;
      border-radius: 20px;
    }

    .summary-motivo {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      color: #1e293b;
      font-size: 0.92rem;
      line-height: 1.5;
    }

    .summary-answer-item {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
    }
  `]
})
export class IntakeConfigComponent implements OnInit {
  activeTab: 'formularios' | 'respuestas' = 'formularios';
  cargando = signal<boolean>(true);
  formularios = signal<FormularioPreConsulta[]>([]);
  respuestas = signal<RespuestaPreConsulta[]>([]);
  mensajeExito = signal<string | null>(null);

  // Patient Intake Portal State
  citasPaciente = signal<Cita[]>([]);
  citaSeleccionadaId = '';
  pacienteActual = signal<Paciente | null>(null);
  respuestasPacienteForm: Record<string, any> = {};
  motivoConsultaPaciente = '';
  nivelUrgenciaPaciente = 3;
  consentimientoIAPaciente = true;
  enviandoRespuesta = signal<boolean>(false);
  errorEnvioPaciente: string | null = null;

  mostrarModalForm = false;
  respuestaSeleccionada: RespuestaPreConsulta | null = null;

  // HU-35 AI Modal State
  mostrarModalIA = false;
  respuestaIdParaIA = '';

  nuevoFormulario: {
    id: string;
    titulo: string;
    descripcion: string;
    activo: boolean;
    preguntas_json: Array<{
      id: string;
      texto: string;
      tipo: 'texto' | 'opcion_multiple' | 'escala_1_5' | 'booleano';
      opciones?: string[];
      requerido: boolean;
    }>;
  } = {
    id: '',
    titulo: '',
    descripcion: '',
    activo: true,
    preguntas_json: [
      { id: 'motivo_1', texto: '¿Cuál es el motivo principal por el que solicita atención psicológica?', tipo: 'texto', requerido: true },
      { id: 'tiempo_1', texto: '¿Desde hace cuánto tiempo experimenta estos síntomas?', tipo: 'texto', requerido: true },
      { id: 'animo_1', texto: 'En las últimas 2 semanas, ¿con qué frecuencia se ha sentido decaído o sin esperanzas?', tipo: 'escala_1_5', requerido: true },
      { id: 'ansiedad_1', texto: '¿Ha experimentado ataques repentinos de pánico o palpitaciones?', tipo: 'booleano', requerido: true },
      { id: 'alerta_1', texto: '¿Ha tenido pensamientos de que preferiría estar muerto o autolesionarse?', tipo: 'booleano', requerido: true }
    ]
  };

  constructor(
    public authService: AuthService,
    private clinicaSprint2Service: ClinicaSprint2Service,
    private clinicaService: ClinicaService,
    private agendaService: AgendaService
  ) {}

  ngOnInit(): void {
    this.cargarDatos();
  }

  cargarDatos(): void {
    this.cargando.set(true);
    this.clinicaSprint2Service.getFormulariosPreconsulta().subscribe({
      next: (forms) => {
        this.formularios.set(forms);
        this.clinicaSprint2Service.getRespuestasPreconsulta().subscribe({
          next: (resps) => {
            this.respuestas.set(resps);
            if (this.authService.isPaciente()) {
              this.cargarDatosPaciente();
            } else {
              this.cargando.set(false);
            }
          },
          error: () => this.cargando.set(false)
        });
      },
      error: () => this.cargando.set(false)
    });
  }

  cargarDatosPaciente(): void {
    this.clinicaService.getPacientes().subscribe({
      next: (pacs) => {
        if (pacs.length > 0) {
          this.pacienteActual.set(pacs[0]);
        }
        this.agendaService.getCitas().subscribe({
          next: (citas) => {
            this.citasPaciente.set(citas);
            if (citas.length > 0 && !this.citaSeleccionadaId) {
              const pend = citas.find(c => !this.tieneIntakeRespondido(c.id));
              this.citaSeleccionadaId = pend ? pend.id : citas[0].id;
            }
            this.cargando.set(false);
          },
          error: () => this.cargando.set(false)
        });
      },
      error: () => this.cargando.set(false)
    });
  }

  tieneIntakeRespondido(citaId: string): boolean {
    return this.respuestas().some(r => r.cita === citaId);
  }

  getRespuestaDeCita(citaId: string): RespuestaPreConsulta | undefined {
    return this.respuestas().find(r => r.cita === citaId);
  }

  getFormularioActivo(): FormularioPreConsulta | undefined {
    return this.formularios().find(f => f.activo) || this.formularios()[0];
  }

  formatearVersion(version: any): string {
    if (!version && version !== 0) return 'v1.0';
    const s = version.toString().trim();
    if (s.startsWith('v')) return s;
    return `v${s}.0`;
  }

  seleccionarCitaParaIntake(citaId: string): void {
    this.citaSeleccionadaId = citaId;
    this.errorEnvioPaciente = null;
  }

  enviarIntakePaciente(): void {
    this.errorEnvioPaciente = null;
    const f = this.getFormularioActivo();
    const pac = this.pacienteActual();
    if (!f || !this.citaSeleccionadaId || !pac) {
      this.errorEnvioPaciente = 'No se ha podido asociar la cita o el expediente del paciente.';
      return;
    }
    if (!this.motivoConsultaPaciente.trim()) {
      this.errorEnvioPaciente = 'Por favor ingresa el motivo principal de tu consulta.';
      return;
    }

    this.enviandoRespuesta.set(true);
    const payload = {
      formulario: f.id,
      cita: this.citaSeleccionadaId,
      paciente: pac.id,
      motivo_consulta: this.motivoConsultaPaciente,
      nivel_urgencia_percibido: this.nivelUrgenciaPaciente,
      respuestas_detalle: this.respuestasPacienteForm,
      respuestas_json: this.respuestasPacienteForm,
      consentimiento_ia_procesamiento: this.consentimientoIAPaciente
    };

    this.clinicaSprint2Service.enviarRespuestaPreconsulta(payload).subscribe({
      next: () => {
        this.enviandoRespuesta.set(false);
        this.mostrarFeedback('¡Cuestionario de Pre-Consulta enviado con éxito! Tu psicólogo ya dispone de tus respuestas.');
        this.cargarDatos();
      },
      error: (err) => {
        this.enviandoRespuesta.set(false);
        const detalle = err.error?.error || err.error?.detail || (typeof err.error === 'object' ? JSON.stringify(err.error) : 'Error al enviar el cuestionario.');
        this.errorEnvioPaciente = detalle;
      }
    });
  }

  openCreateModal(): void {
    this.nuevoFormulario = {
      id: '',
      titulo: 'Cuestionario de Preconsulta Psicológica General',
      descripcion: 'Complete este cuestionario antes de su primera sesión para orientar a su terapeuta.',
      activo: true,
      preguntas_json: [
        { id: 'motivo_1', texto: '¿Cuál es el motivo principal por el que solicita atención psicológica?', tipo: 'texto', requerido: true },
        { id: 'tiempo_1', texto: '¿Desde hace cuánto tiempo experimenta estos síntomas?', tipo: 'texto', requerido: true },
        { id: 'animo_1', texto: 'En las últimas 2 semanas, ¿con qué frecuencia se ha sentido decaído o sin esperanzas? (1=Nunca, 5=Todos los días)', tipo: 'escala_1_5', requerido: true },
        { id: 'ansiedad_1', texto: '¿Ha experimentado crisis de ansiedad aguda o palpitaciones?', tipo: 'booleano', requerido: true },
        { id: 'alerta_1', texto: '¿Ha tenido pensamientos de muerte o deseos de desaparecer?', tipo: 'booleano', requerido: true }
      ]
    };
    this.mostrarModalForm = true;
  }

  agregarPregunta(): void {
    const idx = this.nuevoFormulario.preguntas_json.length + 1;
    this.nuevoFormulario.preguntas_json.push({
      id: `pregunta_${idx}`,
      texto: '',
      tipo: 'texto',
      requerido: true
    });
  }

  eliminarPregunta(index: number): void {
    this.nuevoFormulario.preguntas_json.splice(index, 1);
  }

  actualizarOpcionesPregunta(p: any, valor: string): void {
    p.opciones = valor.split(',').map(s => s.trim()).filter(s => !!s);
  }

  guardarFormulario(): void {
    if (this.nuevoFormulario.id) {
      this.clinicaSprint2Service.actualizarFormularioPreconsulta(this.nuevoFormulario.id, this.nuevoFormulario).subscribe({
        next: () => {
          this.mostrarModalForm = false;
          this.mostrarFeedback('Cuestionario actualizado correctamente');
          this.cargarDatos();
        }
      });
    } else {
      this.clinicaSprint2Service.crearFormularioPreconsulta(this.nuevoFormulario).subscribe({
        next: () => {
          this.mostrarModalForm = false;
          this.mostrarFeedback('Cuestionario creado y publicado con éxito');
          this.cargarDatos();
        }
      });
    }
  }

  verDetalleFormulario(form: FormularioPreConsulta): void {
    this.nuevoFormulario = {
      id: form.id,
      titulo: form.titulo,
      descripcion: form.descripcion || '',
      activo: form.activo,
      preguntas_json: JSON.parse(JSON.stringify(form.preguntas_json))
    };
    this.mostrarModalForm = true;
  }

  duplicarOEditar(form: FormularioPreConsulta): void {
    this.verDetalleFormulario(form);
  }

  verDetalleRespuesta(r: RespuestaPreConsulta): void {
    this.respuestaSeleccionada = r;
  }

  parseRespuestas(respuestasJson: any): Array<{ pregunta: string; respuesta: any }> {
    if (!respuestasJson) return [];
    return Object.keys(respuestasJson).map(k => ({
      pregunta: k,
      respuesta: typeof respuestasJson[k] === 'boolean' ? (respuestasJson[k] ? 'Sí' : 'No') : respuestasJson[k]
    }));
  }

  abrirAsistenteIA(r: RespuestaPreConsulta): void {
    this.respuestaIdParaIA = r.id;
    this.mostrarModalIA = true;
  }

  onDecisionIARegistrada(evento: { decision: string; resumen: string }): void {
    this.mostrarFeedback(`Decisión humana registrada en auditoría: ${evento.decision}`);
    this.cargarDatos();
  }

  mostrarFeedback(msg: string): void {
    this.mensajeExito.set(msg);
    setTimeout(() => this.mensajeExito.set(null), 4000);
  }
}
