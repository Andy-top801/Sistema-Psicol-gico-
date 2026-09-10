// ==============================================================================
// MÓDULO: dashboard.component.ts
// CAPA BCE: BOUNDARY (Interfaz de Usuario) — IU_DashboardClinico, IU_AlertasClinicas
// CASOS DE USO: CU9 (Consultar Dashboard e Indicadores), CU10 (Alertas Tempranas y Priorización)
// DESCRIPCIÓN: Componente Angular interactivo para visualización de KPIs de gestión clínica
//              (ausentismo, ocupación, citas por estado) y priorización de alertas de deserción.
//              Implementa los pasos 1, 2, 7 y 8 de los Diagramas de Comunicación BCE.
// ==============================================================================
import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { UserService } from '../../core/services/user.service';
import { TenantService } from '../../core/services/tenant.service';
import { RoleService } from '../../core/services/role.service';
import { AgendaService } from '../../core/services/agenda.service';
import { DashboardKPIs, AlertaClinica, Tenant } from '../../core/models';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  template: `
    <div class="dashboard-wrapper">
      <!-- ═══════════════════════════════════════════════════════════════════ -->
      <!-- ENCABEZADO Y CONTROLES PRINCIPALES (Filtros de Período y Centro)    -->
      <!-- ═══════════════════════════════════════════════════════════════════ -->
      <div class="dash-header-card mb-4">
        <div class="header-main-info">
          <div class="user-greeting-row">
            <div class="avatar-circle">
              {{ (authService.currentUser()?.nombre || 'U').charAt(0).toUpperCase() }}
            </div>
            <div>
              <div class="d-flex align-center gap-2 flex-wrap">
                <h1 class="dash-title">
                  ¡Hola, {{ authService.currentUser()?.nombre || 'Usuario' }}!
                </h1>
                <span class="role-pill" [ngClass]="getRoleClass(authService.currentUser()?.rol?.nombre)">
                  <i class="fa-solid fa-shield-halved"></i>
                  {{ authService.currentUser()?.rol?.nombre || (authService.isSuperAdmin() ? 'SuperAdministrador' : 'Usuario') }}
                </span>
              </div>
              <p class="dash-subtitle">
                <i class="fa-solid fa-building me-1"></i>
                <span *ngIf="authService.isInTenantContext()">
                  Sede: <strong>{{ authService.currentTenant()?.nombre }}</strong> ({{ authService.currentTenant()?.slug }})
                </span>
                <span *ngIf="!authService.isInTenantContext() && authService.isSuperAdmin()">
                  Plataforma SaaS Global Multi-Tenant &bull; Esquema Public
                </span>
                <span *ngIf="!authService.isInTenantContext() && !authService.isSuperAdmin()">
                  Sistema Integral SIGEPSI
                </span>
              </p>
            </div>
          </div>
        </div>

        <div class="header-actions">
          <!-- Selector de Centro para SuperAdmin (Permite auditar cualquier centro al instante) -->
          <div *ngIf="authService.isSuperAdmin()" class="control-item">
            <label class="control-label"><i class="fa-solid fa-building-user"></i> Centro / Tenant</label>
            <select 
              class="form-select select-compact" 
              [ngModel]="selectedTenantSlug()"
              (ngModelChange)="onSelectTenant($event)">
              <option value="">Vista Global SaaS (Todos los Centros)</option>
              <option *ngFor="let t of availableTenants()" [value]="t.slug">
                {{ t.nombre }} ({{ t.slug }})
              </option>
            </select>
          </div>

          <!-- Filtro de Período (Mes y Año - HU-20 / TP-52) -->
          <div class="control-item">
            <label class="control-label"><i class="fa-solid fa-calendar-days"></i> Mes</label>
            <select 
              class="form-select select-compact" 
              [(ngModel)]="mesSeleccionado" 
              (ngModelChange)="onFiltroPeriodoChange()">
              <option *ngFor="let m of meses" [value]="m.valor">{{ m.nombre }}</option>
            </select>
          </div>

          <div class="control-item">
            <label class="control-label"><i class="fa-solid fa-calendar"></i> Año</label>
            <select 
              class="form-select select-compact" 
              [(ngModel)]="anioSeleccionado" 
              (ngModelChange)="onFiltroPeriodoChange()">
              <option *ngFor="let a of aniosDisponibles" [value]="a">{{ a }}</option>
            </select>
          </div>

          <!-- Botón de Refresco -->
          <button 
            type="button" 
            class="btn-refresh-icon" 
            (click)="recargarTodo()" 
            [disabled]="cargando()"
            title="Sincronizar métricas en tiempo real">
            <i class="fa-solid fa-rotate" [class.fa-spin]="cargando()"></i>
          </button>
        </div>
      </div>

      <!-- ═══════════════════════════════════════════════════════════════════ -->
      <!-- BANNER DIRECTO: TELECONSULTA / VIDEOLLAMADA EN VIVO (CU13 / HU-19)   -->
      <!-- ═══════════════════════════════════════════════════════════════════ -->
      <div class="teleconsulta-banner mb-4">
        <div class="tele-icon-circle">
          <i class="fa-solid fa-video"></i>
        </div>
        <div class="tele-info">
          <div class="d-flex align-center gap-2">
            <h3 class="tele-title">Teleconsulta & Videollamadas Jitsi Meet (WebRTC)</h3>
            <span class="badge-live-pulse">EN VIVO</span>
          </div>
          <p class="tele-desc">
            Videoconferencias clínicas encriptadas con audio y video bidireccional, rol moderador para terapeutas y control de tiempo (CU13 / HU-18 / HU-19).
          </p>
        </div>
        <div class="tele-actions">
          <button class="btn btn-emerald" (click)="iniciarTeleconsultaDemo()">
            <i class="fa-solid fa-play"></i> Probar Teleconsulta
          </button>
          <a routerLink="/agenda" class="btn btn-outline-white">
            <i class="fa-solid fa-calendar-check"></i> Ver Agenda de Sesiones
          </a>
        </div>
      </div>

      <!-- ═══════════════════════════════════════════════════════════════════ -->
      <!-- SECCIÓN SPRINT 0: RESUMEN INSTITUCIONAL SAAS                        -->
      <!-- ═══════════════════════════════════════════════════════════════════ -->
      <div *ngIf="authService.isSuperAdmin() && !authService.isInTenantContext()" class="mb-4">
        <div class="section-title-row mb-3">
          <h2 class="section-heading">
            <i class="fa-solid fa-network-wired text-primary"></i> Infraestructura Global Multi-Tenant (Sprint 0)
          </h2>
          <span class="badge badge-info">Esquemas PostgreSQL Aislados</span>
        </div>

        <div class="stats-grid-4">
          <!-- Card 1: Centros Registrados -->
          <div class="stat-card">
            <div class="stat-icon-box box-mint">
              <i class="fa-solid fa-building"></i>
            </div>
            <div class="stat-data">
              <div class="stat-number">{{ totalCentros() }}</div>
              <div class="stat-label">Centros psicológicos</div>
            </div>
          </div>

          <!-- Card 2: Usuarios Activos -->
          <div class="stat-card">
            <div class="stat-icon-box box-blue">
              <i class="fa-solid fa-users"></i>
            </div>
            <div class="stat-data">
              <div class="stat-number">{{ totalUsuarios() }}</div>
              <div class="stat-label">Usuarios del sistema</div>
            </div>
          </div>

          <!-- Card 3: Roles Configurados -->
          <div class="stat-card">
            <div class="stat-icon-box box-peach">
              <i class="fa-solid fa-shield-halved"></i>
            </div>
            <div class="stat-data">
              <div class="stat-number">{{ totalRoles() }}</div>
              <div class="stat-label">Roles configurados</div>
            </div>
          </div>

          <!-- Card 4: Permisos Definidos -->
          <div class="stat-card card-highlight">
            <div class="stat-icon-box box-emerald">
              <i class="fa-solid fa-circle-check"></i>
            </div>
            <div class="stat-data">
              <div class="stat-number">{{ totalPermisos() }}</div>
              <div class="stat-label">Permisos de seguridad</div>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══════════════════════════════════════════════════════════════════ -->
      <!-- SECCIÓN SPRINT 1: MÉTRICAS CLÍNICAS Y OPERATIVAS (CU9 / CU10)        -->
      <!-- ═══════════════════════════════════════════════════════════════════ -->
      <div class="clinical-section">
        <div class="section-title-row mb-3">
          <div class="d-flex align-center gap-2">
            <h2 class="section-heading">
              <i class="fa-solid fa-chart-pie text-primary"></i>
              Tablero Clínico y Operativo (Sprint 1 - HU-20)
            </h2>
            <span class="badge badge-primary">
              {{ getNombreMes(mesSeleccionado) }} {{ anioSeleccionado }}
            </span>
          </div>
          <span *ngIf="cargando()" class="text-sm text-muted">
            <i class="fa-solid fa-spinner fa-spin me-1"></i> Actualizando métricas...
          </span>
        </div>

        <!-- Fila de KPIs Principales (5 Tarjetas) -->
        <div class="kpi-cards-grid mb-4">
          <!-- Citas de Hoy -->
          <div class="kpi-card">
            <div class="kpi-header">
              <div class="kpi-icon-box bg-blue-subtle">
                <i class="fa-solid fa-calendar-day text-blue"></i>
              </div>
              <span class="kpi-period-tag">Hoy</span>
            </div>
            <div class="kpi-value">{{ kpis()?.total_citas_hoy ?? (kpis()?.citas_hoy?.total ?? 0) }}</div>
            <div class="kpi-title">Citas de hoy</div>
            <div class="kpi-subtext">
              <span class="text-success font-semibold">{{ kpis()?.citas_hoy?.realizadas || 0 }}</span> atendidas &bull; 
              <span>{{ kpis()?.citas_hoy?.programadas || 0 }}</span> programadas
            </div>
          </div>

          <!-- Total Sesiones del Mes -->
          <div class="kpi-card">
            <div class="kpi-header">
              <div class="kpi-icon-box bg-emerald-subtle">
                <i class="fa-solid fa-calendar-check text-emerald"></i>
              </div>
              <span class="kpi-period-tag">Mensual</span>
            </div>
            <div class="kpi-value">{{ kpis()?.total_citas_mes ?? (kpis()?.citas_mes?.total ?? 0) }}</div>
            <div class="kpi-title">Sesiones en el período</div>
            <div class="kpi-subtext">
              <span class="text-primary font-semibold">{{ kpis()?.tasa_asistencia_pct || 0 }}%</span> asistencia lograda
            </div>
          </div>

          <!-- Tasa de Ausentismo -->
          <div class="kpi-card">
            <div class="kpi-header">
              <div class="kpi-icon-box bg-amber-subtle">
                <i class="fa-solid fa-user-xmark text-amber"></i>
              </div>
              <span class="badge" [ngClass]="getAusentismoBadgeClass(kpis()?.tasa_ausentismo_pct || 0)">
                {{ getAusentismoNivel(kpis()?.tasa_ausentismo_pct || 0) }}
              </span>
            </div>
            <div class="kpi-value">{{ (kpis()?.tasa_ausentismo_pct ?? 0) | number:'1.1-2' }}%</div>
            <div class="kpi-title">Tasa de ausentismo</div>
            <div class="kpi-subtext">
              <span>{{ kpis()?.citas_mes?.inasistencias || 0 }} inasistencias registradas</span>
            </div>
          </div>

          <!-- Ingresos Estimados del Mes -->
          <div class="kpi-card">
            <div class="kpi-header">
              <div class="kpi-icon-box bg-purple-subtle">
                <i class="fa-solid fa-sack-dollar text-purple"></i>
              </div>
              <span class="kpi-period-tag">Facturación</span>
            </div>
            <div class="kpi-value">Bs. {{ (kpis()?.ingresos_mes || 0) | number:'1.2-2' }}</div>
            <div class="kpi-title">Ingresos generados</div>
            <div class="kpi-subtext">
              Por sesiones finalizadas
            </div>
          </div>

          <!-- Alertas Clínicas Activas -->
          <div class="kpi-card" [class.border-alert]="(kpis()?.alertas_activas?.length || 0) > 0">
            <div class="kpi-header">
              <div class="kpi-icon-box bg-rose-subtle">
                <i class="fa-solid fa-triangle-exclamation text-rose"></i>
              </div>
              <span class="badge badge-danger">Prioridad</span>
            </div>
            <div class="kpi-value text-rose">{{ kpis()?.alertas_activas?.length || 0 }}</div>
            <div class="kpi-title">Alertas activas</div>
            <div class="kpi-subtext">
              Pacientes con riesgo de deserción
            </div>
          </div>
        </div>

        <!-- ═════════════════════════════════════════════════════════════════ -->
        <!-- PANEL DE ALERTAS CLÍNICAS TEMPRANAS (HU-21 / CU10 / TP-53 / 54)   -->
        <!-- ═════════════════════════════════════════════════════════════════ -->
        <div class="alerts-section clean-card mb-4" *ngIf="kpis()?.alertas_activas && (kpis()?.alertas_activas?.length || 0) > 0">
          <div class="alerts-header">
            <div class="d-flex align-center gap-2">
              <span class="alert-pulse-icon"><i class="fa-solid fa-bell"></i></span>
              <div>
                <h3 class="alerts-title">Alertas Clínicas Tempranas de Ausentismo y Abandono (HU-21)</h3>
                <p class="alerts-subtitle mb-0">Atención prioritaria para pacientes con inasistencias reiteradas o deserciones.</p>
              </div>
            </div>
            <span class="badge badge-warning font-semibold">
              {{ kpis()?.alertas_activas?.length }} caso(s) pendiente(s)
            </span>
          </div>

          <div class="alerts-list">
            <div *ngFor="let alerta of kpis()?.alertas_activas" class="alert-card-item">
              <div class="alert-card-left">
                <span class="badge" [ngClass]="getSeveridadBadgeClass(alerta.severidad)">
                  {{ alerta.severidad }}
                </span>
                <div class="alert-details">
                  <div class="alert-patient-name">
                    <strong>{{ alerta.paciente_nombre }}</strong>
                    <span class="expediente-chip">Exp: {{ alerta.codigo_expediente }}</span>
                    <span *ngIf="alerta.centro_nombre" class="tenant-chip-sm">
                      <i class="fa-solid fa-building"></i> {{ alerta.centro_nombre }}
                    </span>
                  </div>
                  <p class="alert-description">{{ alerta.descripcion }}</p>
                  <span class="alert-date">
                    <i class="fa-regular fa-clock me-1"></i> Detectada: {{ alerta.fecha_creacion | date:'dd/MM/yyyy HH:mm' }}
                  </span>
                </div>
              </div>

              <div class="alert-card-actions">
                <button 
                  type="button"
                  class="btn btn-success btn-sm d-flex align-center gap-1"
                  (click)="abrirModalResolver(alerta)">
                  <i class="fa-solid fa-check-double"></i> Atender y Resolver
                </button>
              </div>
            </div>
          </div>
        </div>

        <div *ngIf="!kpis()?.alertas_activas || kpis()?.alertas_activas?.length === 0" class="clean-card p-3 mb-4 alerts-empty-banner">
          <div class="d-flex align-center gap-2">
            <i class="fa-solid fa-circle-check text-emerald fa-lg"></i>
            <div>
              <strong class="text-emerald">Sin alertas clínicas pendientes en el período</strong>
              <p class="text-sm text-muted mb-0">No se detectaron inasistencias consecutivas ni pacientes en riesgo de deserción.</p>
            </div>
          </div>
        </div>

        <!-- ═════════════════════════════════════════════════════════════════ -->
        <!-- GRÁFICOS Y ANÁLISIS: DISTRIBUCIÓN POR ESTADOS Y OCUPACIÓN         -->
        <!-- ═════════════════════════════════════════════════════════════════ -->
        <div class="analytics-row mb-4">
          <!-- Distribución de Consultas por Estado -->
          <div class="clean-card p-4">
            <div class="card-header-clean mb-3">
              <h4 class="card-title-clean">
                <i class="fa-solid fa-chart-simple text-primary me-2"></i>Distribución de Consultas por Estado
              </h4>
              <span class="badge badge-info">Total: {{ kpis()?.total_citas_mes ?? 0 }}</span>
            </div>

            <div class="progress-stack" *ngIf="kpis()?.distribucion_estados">
              <!-- Programadas -->
              <div class="status-bar-item">
                <div class="bar-header">
                  <span class="status-dot dot-cyan"></span>
                  <span class="status-label">Programadas (Pendientes)</span>
                  <div class="status-values">
                    <strong>{{ kpis()?.distribucion_estados?.PROGRAMADA || 0 }}</strong>
                    <span class="text-muted text-xs">({{ calcularPorcentaje(kpis()?.distribucion_estados?.PROGRAMADA) }}%)</span>
                  </div>
                </div>
                <div class="progress-track">
                  <div class="progress-fill fill-cyan" [style.width.%]="calcularPorcentaje(kpis()?.distribucion_estados?.PROGRAMADA)"></div>
                </div>
              </div>

              <!-- Confirmadas -->
              <div class="status-bar-item">
                <div class="bar-header">
                  <span class="status-dot dot-emerald"></span>
                  <span class="status-label">Confirmadas por Paciente</span>
                  <div class="status-values">
                    <strong>{{ kpis()?.distribucion_estados?.CONFIRMADA || 0 }}</strong>
                    <span class="text-muted text-xs">({{ calcularPorcentaje(kpis()?.distribucion_estados?.CONFIRMADA) }}%)</span>
                  </div>
                </div>
                <div class="progress-track">
                  <div class="progress-fill fill-emerald" [style.width.%]="calcularPorcentaje(kpis()?.distribucion_estados?.CONFIRMADA)"></div>
                </div>
              </div>

              <!-- Realizadas -->
              <div class="status-bar-item">
                <div class="bar-header">
                  <span class="status-dot dot-blue"></span>
                  <span class="status-label">Realizadas / Atendidas</span>
                  <div class="status-values">
                    <strong>{{ kpis()?.distribucion_estados?.REALIZADA || 0 }}</strong>
                    <span class="text-muted text-xs">({{ calcularPorcentaje(kpis()?.distribucion_estados?.REALIZADA) }}%)</span>
                  </div>
                </div>
                <div class="progress-track">
                  <div class="progress-fill fill-blue" [style.width.%]="calcularPorcentaje(kpis()?.distribucion_estados?.REALIZADA)"></div>
                </div>
              </div>

              <!-- Inasistencias -->
              <div class="status-bar-item">
                <div class="bar-header">
                  <span class="status-dot dot-amber"></span>
                  <span class="status-label">Inasistencias (No Asistió)</span>
                  <div class="status-values">
                    <strong>{{ kpis()?.distribucion_estados?.INASISTENCIA || 0 }}</strong>
                    <span class="text-muted text-xs">({{ calcularPorcentaje(kpis()?.distribucion_estados?.INASISTENCIA) }}%)</span>
                  </div>
                </div>
                <div class="progress-track">
                  <div class="progress-fill fill-amber" [style.width.%]="calcularPorcentaje(kpis()?.distribucion_estados?.INASISTENCIA)"></div>
                </div>
              </div>

              <!-- Canceladas -->
              <div class="status-bar-item">
                <div class="bar-header">
                  <span class="status-dot dot-red"></span>
                  <span class="status-label">Canceladas</span>
                  <div class="status-values">
                    <strong>{{ kpis()?.distribucion_estados?.CANCELADA || 0 }}</strong>
                    <span class="text-muted text-xs">({{ calcularPorcentaje(kpis()?.distribucion_estados?.CANCELADA) }}%)</span>
                  </div>
                </div>
                <div class="progress-track">
                  <div class="progress-fill fill-red" [style.width.%]="calcularPorcentaje(kpis()?.distribucion_estados?.CANCELADA)"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Ocupación y Horas de Terapeutas -->
          <div class="clean-card p-4">
            <div class="card-header-clean mb-3">
              <h4 class="card-title-clean">
                <i class="fa-solid fa-user-doctor text-primary me-2"></i>Rendimiento y Ocupación de Terapeutas
              </h4>
              <span class="badge badge-primary">{{ kpis()?.ocupacion_por_psicologo?.length || 0 }} activos</span>
            </div>

            <div class="table-container">
              <table class="custom-table table-compact">
                <thead>
                  <tr>
                    <th>Terapeuta</th>
                    <th>Colegiatura</th>
                    <th>Citas</th>
                    <th>Atendidas</th>
                    <th>Ingresos</th>
                  </tr>
                </thead>
                <tbody>
                  <tr *ngFor="let psi of kpis()?.ocupacion_por_psicologo">
                    <td>
                      <div class="d-flex align-center gap-2">
                        <div class="therapist-mini-avatar">
                          {{ psi.nombre.charAt(0) }}
                        </div>
                        <div>
                          <strong>{{ psi.nombre }}</strong>
                        </div>
                      </div>
                    </td>
                    <td><span class="font-mono text-xs">{{ psi.colegiado || 'S/C' }}</span></td>
                    <td><span class="badge badge-info">{{ psi.total_citas }}</span></td>
                    <td>
                      <span class="badge badge-success">{{ psi.horas_atendidas || psi.realizadas || 0 }} ses.</span>
                    </td>
                    <td><strong>Bs. {{ (psi.ingresos_generados || 0) | number:'1.2-2' }}</strong></td>
                  </tr>
                  <tr *ngIf="!kpis()?.ocupacion_por_psicologo || kpis()?.ocupacion_por_psicologo?.length === 0">
                    <td colspan="5" class="text-center text-muted py-4">
                      <i class="fa-regular fa-folder-open mb-2 d-block fa-2x"></i>
                      Sin actividad clínica registrada en el período seleccionado.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- ═════════════════════════════════════════════════════════════════ -->
        <!-- ACCESOS RÁPIDOS A MÓDULOS DEL SISTEMA                             -->
        <!-- ═════════════════════════════════════════════════════════════════ -->
        <div class="section-block mb-4">
          <h2 class="section-heading mb-3">
            <i class="fa-solid fa-compass text-primary me-1"></i> Módulos y Operaciones Frecuentes
          </h2>
          <div class="quick-actions-grid">
            <a routerLink="/agenda" class="quick-action-card">
              <div class="quick-icon-circle bg-mint">
                <i class="fa-solid fa-calendar-days text-emerald"></i>
              </div>
              <div class="quick-text">
                <h4 class="quick-title">Agenda Central y Citas</h4>
                <p class="quick-desc">Calendario mensual, semanal y teleconsultas</p>
              </div>
            </a>

            <a routerLink="/psicologos" class="quick-action-card">
              <div class="quick-icon-circle bg-blue">
                <i class="fa-solid fa-user-doctor text-blue"></i>
              </div>
              <div class="quick-text">
                <h4 class="quick-title">Directorio de Psicólogos</h4>
                <p class="quick-desc">Especialidades, aranceles y disponibilidad semanal</p>
              </div>
            </a>

            <a routerLink="/pacientes" class="quick-action-card">
              <div class="quick-icon-circle bg-peach">
                <i class="fa-solid fa-folder-open text-amber"></i>
              </div>
              <div class="quick-text">
                <h4 class="quick-title">Expedientes de Pacientes</h4>
                <p class="quick-desc">Fichas clínicas, tutores legales e historial</p>
              </div>
            </a>

            <a *ngIf="authService.isSuperAdmin()" routerLink="/tenants" class="quick-action-card">
              <div class="quick-icon-circle bg-emerald">
                <i class="fa-solid fa-building-circle-check text-emerald"></i>
              </div>
              <div class="quick-text">
                <h4 class="quick-title">Centros Psicológicos (SaaS)</h4>
                <p class="quick-desc">Gestión y aprovisionamiento de clínicas multi-tenant</p>
              </div>
            </a>

            <a routerLink="/users" class="quick-action-card">
              <div class="quick-icon-circle bg-purple">
                <i class="fa-solid fa-users-gear text-purple"></i>
              </div>
              <div class="quick-text">
                <h4 class="quick-title">Personal y Usuarios</h4>
                <p class="quick-desc">Gestión de cuentas, staff y accesos</p>
              </div>
            </a>

            <a routerLink="/centro" class="quick-action-card">
              <div class="quick-icon-circle bg-rose">
                <i class="fa-solid fa-sliders text-rose"></i>
              </div>
              <div class="quick-text">
                <h4 class="quick-title">Configuración Institucional</h4>
                <p class="quick-desc">Identidad del centro, sedes y políticas clínicas</p>
              </div>
            </a>
          </div>
        </div>

        <!-- ═════════════════════════════════════════════════════════════════ -->
        <!-- INFORMACIÓN TÉCNICA DEL SISTEMA                                   -->
        <!-- ═════════════════════════════════════════════════════════════════ -->
        <div class="system-info-card clean-card mb-4">
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">Versión de la Plataforma</span>
              <span class="info-val">SIGEPSI v1.1 — Sprint 1 (Clínico & WebRTC)</span>
            </div>
            <div class="info-item">
              <span class="info-label">Arquitectura Multi-Tenant</span>
              <span class="info-val">PostgreSQL con Esquemas Aislados (django-tenants)</span>
            </div>
            <div class="info-item">
              <span class="info-label">Contexto Activo</span>
              <span class="info-val font-mono">
                {{ authService.currentTenant()?.schema_name || 'public' }} 
                ({{ authService.isInTenantContext() ? 'Esquema de Centro' : 'Global SaaS' }})
              </span>
            </div>
            <div class="info-item">
              <span class="info-label">Motor WebRTC</span>
              <span class="info-val">Jitsi Meet API + JWT Cryptographic Claims</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ═════════════════════════════════════════════════════════════════ -->
      <!-- MODAL PARA RESOLVER ALERTA CLÍNICA CON NOTAS (HU-21 / TP-54)        -->
      <!-- ═════════════════════════════════════════════════════════════════ -->
      <div *ngIf="alertaParaResolver()" class="modal-backdrop-custom" (click)="cerrarModalResolver()">
        <div class="modal-card-custom" (click)="$event.stopPropagation()">
          <div class="modal-header-custom">
            <div class="d-flex align-center gap-2">
              <div class="stat-icon-box box-mint">
                <i class="fa-solid fa-notes-medical"></i>
              </div>
              <div>
                <h3 class="modal-title-custom">Resolver Alerta Clínica (HU-21)</h3>
                <p class="modal-sub-custom mb-0">Registrar intervención del equipo terapéutico en el expediente.</p>
              </div>
            </div>
            <button type="button" class="btn-close-custom" (click)="cerrarModalResolver()">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>

          <div class="modal-body-custom">
            <div class="alert-summary-box mb-3">
              <p class="mb-1"><strong>Paciente:</strong> {{ alertaParaResolver()?.paciente_nombre }}</p>
              <p class="mb-1"><strong>Expediente:</strong> {{ alertaParaResolver()?.codigo_expediente }}</p>
              <p class="mb-1"><strong>Motivo:</strong> {{ alertaParaResolver()?.descripcion }}</p>
              <span class="badge" [ngClass]="getSeveridadBadgeClass(alertaParaResolver()?.severidad || '')">
                Severidad {{ alertaParaResolver()?.severidad }}
              </span>
            </div>

            <div class="form-group mb-3">
              <label class="form-label font-semibold">Nota Clínica de Seguimiento / Justificación *</label>
              <textarea 
                class="form-control" 
                rows="4" 
                [(ngModel)]="notaResolucion" 
                placeholder="Ej. Se contactó telefónicamente al paciente o apoderado. Manifestó problema de transporte y se reagendó la sesión para la próxima semana.">
              </textarea>
            </div>
          </div>

          <div class="modal-footer-custom">
            <button type="button" class="btn btn-secondary" (click)="cerrarModalResolver()">Cancelar</button>
            <button 
              type="button" 
              class="btn btn-success" 
              [disabled]="resolviendoAlerta() || !notaResolucion.trim()" 
              (click)="confirmarResolverAlerta()">
              <i class="fa-solid fa-check" *ngIf="!resolviendoAlerta()"></i>
              <i class="fa-solid fa-spinner fa-spin" *ngIf="resolviendoAlerta()"></i>
              {{ resolviendoAlerta() ? 'Guardando...' : 'Marcar como Resuelta' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .dashboard-wrapper {
      max-width: 1400px;
      margin: 0 auto;
    }

    /* Header Card */
    .dash-header-card {
      background: linear-gradient(135deg, #ffffff 0%, #f4f9f6 100%);
      border: 1px solid #d9e7df;
      border-radius: 20px;
      padding: 22px 28px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 20px;
      box-shadow: 0 4px 16px rgba(15, 41, 34, 0.04);
    }
    .header-main-info {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    .user-greeting-row {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    .avatar-circle {
      width: 52px;
      height: 52px;
      border-radius: 16px;
      background: linear-gradient(135deg, #19734e 0%, #0d462f 100%);
      color: #ffffff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.4rem;
      font-weight: 800;
      box-shadow: 0 4px 12px rgba(25, 115, 78, 0.25);
    }
    .dash-title {
      font-size: 1.7rem;
      font-weight: 800;
      color: #12271f;
      margin: 0;
      letter-spacing: -0.02em;
    }
    .dash-subtitle {
      font-size: 0.88rem;
      color: #557164;
      margin-top: 4px;
      margin-bottom: 0;
    }
    .role-pill {
      font-size: 0.76rem;
      font-weight: 800;
      padding: 3px 10px;
      border-radius: 20px;
      letter-spacing: 0.3px;
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }
    .role-admin { background: #e8f1fd; color: #1d4ed8; border: 1px solid #bfdbfe; }
    .role-super { background: #fef2e6; color: #b45309; border: 1px solid #fde68a; }
    .role-psico { background: #e6f5ed; color: #15803d; border: 1px solid #bbf7d0; }
    .role-paciente { background: #f3e8ff; color: #7e22ce; border: 1px solid #e9d5ff; }

    /* Controls row in header */
    .header-actions {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }
    .control-item {
      display: flex;
      flex-direction: column;
      gap: 3px;
    }
    .control-label {
      font-size: 0.72rem;
      font-weight: 700;
      color: #557164;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .select-compact {
      padding: 6px 12px;
      font-size: 0.86rem;
      border-radius: 10px;
      border: 1px solid #c7d9ce;
      background: #ffffff;
      color: #12271f;
      font-weight: 600;
      min-width: 130px;
    }
    .btn-refresh-icon {
      width: 38px;
      height: 38px;
      border-radius: 10px;
      background: #ffffff;
      border: 1px solid #c7d9ce;
      color: #19734e;
      font-size: 1rem;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      margin-top: 14px;
      transition: all 0.2s ease;
    }
    .btn-refresh-icon:hover {
      background: #e6f5ed;
      border-color: #19734e;
      transform: rotate(45deg);
    }

    /* Teleconsulta Banner */
    .teleconsulta-banner {
      background: linear-gradient(135deg, #0f2922 0%, #1a4337 100%);
      border-radius: 20px;
      padding: 22px 28px;
      color: #ffffff;
      display: flex;
      align-items: center;
      gap: 20px;
      box-shadow: 0 8px 24px rgba(15, 41, 34, 0.15);
      border: 1px solid rgba(255, 255, 255, 0.1);
      flex-wrap: wrap;
    }
    .tele-icon-circle {
      width: 54px;
      height: 54px;
      border-radius: 16px;
      background: rgba(52, 211, 153, 0.2);
      border: 1px solid rgba(52, 211, 153, 0.4);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.5rem;
      color: #34d399;
      flex-shrink: 0;
    }
    .tele-info {
      flex: 1;
      min-width: 260px;
    }
    .tele-title {
      font-size: 1.2rem;
      font-weight: 800;
      color: #ffffff;
      margin: 0;
    }
    .tele-desc {
      font-size: 0.88rem;
      color: #a7ccc0;
      margin: 4px 0 0;
    }
    .badge-live-pulse {
      background: #ef4444;
      color: #ffffff;
      font-size: 0.68rem;
      font-weight: 800;
      padding: 2px 8px;
      border-radius: 12px;
      letter-spacing: 0.5px;
      animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.6; }
    }
    .tele-actions {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
    .btn-emerald {
      background: #34d399;
      color: #064e3b;
      font-weight: 800;
      padding: 10px 18px;
      border-radius: 12px;
      border: none;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 0.88rem;
      transition: all 0.2s;
    }
    .btn-emerald:hover {
      background: #10b981;
      color: #ffffff;
      transform: translateY(-2px);
    }
    .btn-outline-white {
      background: transparent;
      color: #ffffff;
      font-weight: 700;
      padding: 10px 18px;
      border-radius: 12px;
      border: 1px solid rgba(255, 255, 255, 0.25);
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 0.88rem;
      transition: all 0.2s;
    }
    .btn-outline-white:hover {
      background: rgba(255, 255, 255, 0.1);
      border-color: #ffffff;
    }

    /* KPI Cards Grid (5 cols) */
    .kpi-cards-grid {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 16px;
    }
    @media (max-width: 1200px) {
      .kpi-cards-grid { grid-template-columns: repeat(3, 1fr); }
    }
    @media (max-width: 768px) {
      .kpi-cards-grid { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 480px) {
      .kpi-cards-grid { grid-template-columns: 1fr; }
    }

    .kpi-card {
      background: #ffffff;
      border: 1px solid #e3ebe6;
      border-radius: 18px;
      padding: 18px 20px;
      display: flex;
      flex-direction: column;
      box-shadow: 0 2px 10px rgba(15, 41, 34, 0.03);
      transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
    }
    .kpi-card:hover {
      transform: translateY(-3px);
      box-shadow: 0 8px 20px rgba(15, 41, 34, 0.08);
      border-color: #c4d7cd;
    }
    .kpi-card.border-alert {
      border: 1.5px solid #f87171;
      background: #fffafa;
    }
    .kpi-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }
    .kpi-icon-box {
      width: 42px;
      height: 42px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.2rem;
    }
    .bg-blue-subtle { background: #e8f1fd; }
    .bg-emerald-subtle { background: #e6f7ee; }
    .bg-amber-subtle { background: #fef3c7; }
    .bg-purple-subtle { background: #f3e8ff; }
    .bg-rose-subtle { background: #fee2e2; }

    .text-blue { color: #2563eb; }
    .text-emerald { color: #16a34a; }
    .text-amber { color: #d97706; }
    .text-purple { color: #9333ea; }
    .text-rose { color: #dc2626; }

    .kpi-period-tag {
      font-size: 0.72rem;
      font-weight: 700;
      color: #557164;
      background: #f4f7f5;
      padding: 3px 8px;
      border-radius: 6px;
    }
    .kpi-value {
      font-size: 1.85rem;
      font-weight: 800;
      color: #12271f;
      line-height: 1.1;
      font-family: 'Outfit', sans-serif;
    }
    .kpi-title {
      font-size: 0.88rem;
      font-weight: 700;
      color: #3b564a;
      margin-top: 4px;
    }
    .kpi-subtext {
      font-size: 0.76rem;
      color: #658b7c;
      margin-top: 6px;
    }

    /* Stats Grid 4 (Sprint 0) */
    .stats-grid-4 {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
    }
    @media (max-width: 900px) {
      .stats-grid-4 { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 500px) {
      .stats-grid-4 { grid-template-columns: 1fr; }
    }
    .stat-card {
      background: #ffffff;
      border: 1px solid #e3ebe6;
      border-radius: 18px;
      padding: 18px 20px;
      display: flex;
      align-items: center;
      gap: 16px;
      box-shadow: 0 2px 8px rgba(15, 41, 34, 0.03);
    }
    .stat-card.card-highlight {
      border: 1.5px solid #1fa158;
    }
    .stat-icon-box {
      width: 44px;
      height: 44px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.2rem;
      flex-shrink: 0;
    }
    .box-mint { background: #e6f5ed; color: #19734e; }
    .box-blue { background: #e8f1fd; color: #2563eb; }
    .box-peach { background: #fef2e6; color: #d97706; }
    .box-emerald { background: #e6f7ee; color: #16a34a; }
    .stat-number {
      font-size: 1.7rem;
      font-weight: 800;
      color: #12271f;
      font-family: 'Outfit', sans-serif;
      line-height: 1.1;
    }
    .stat-label {
      font-size: 0.82rem;
      color: #557164;
      font-weight: 600;
    }

    /* Alerts Section */
    .alerts-section {
      border: 1.5px solid #fde68a;
      background: #fffef7;
      border-radius: 20px;
      padding: 22px;
    }
    .alerts-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      flex-wrap: wrap;
      gap: 10px;
    }
    .alert-pulse-icon {
      width: 38px;
      height: 38px;
      border-radius: 10px;
      background: #fef3c7;
      color: #d97706;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.15rem;
    }
    .alerts-title {
      font-size: 1.05rem;
      font-weight: 800;
      color: #92400e;
      margin: 0;
    }
    .alerts-subtitle {
      font-size: 0.82rem;
      color: #78350f;
    }
    .alerts-list {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .alert-card-item {
      background: #ffffff;
      border: 1px solid #fde68a;
      border-radius: 14px;
      padding: 14px 18px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
      box-shadow: 0 2px 6px rgba(180, 83, 9, 0.04);
    }
    .alert-card-left {
      display: flex;
      align-items: flex-start;
      gap: 14px;
      flex: 1;
      min-width: 240px;
    }
    .alert-patient-name {
      font-size: 0.95rem;
      color: #12271f;
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }
    .expediente-chip {
      background: #f4f7f5;
      color: #3b564a;
      font-size: 0.74rem;
      padding: 2px 7px;
      border-radius: 6px;
      font-family: var(--font-mono);
      font-weight: 600;
    }
    .tenant-chip-sm {
      background: #e6f5ed;
      color: #19734e;
      font-size: 0.72rem;
      padding: 2px 7px;
      border-radius: 6px;
      font-weight: 700;
    }
    .alert-description {
      font-size: 0.85rem;
      color: #557164;
      margin: 4px 0 2px;
    }
    .alert-date {
      font-size: 0.74rem;
      color: #8da89d;
    }
    .alerts-empty-banner {
      border: 1px solid #bbf7d0;
      background: #f0fdf4;
      border-radius: 14px;
    }

    /* Analytics Row (2 columns) */
    .analytics-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }
    @media (max-width: 992px) {
      .analytics-row { grid-template-columns: 1fr; }
    }
    .card-header-clean {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .card-title-clean {
      font-size: 1.05rem;
      font-weight: 800;
      color: #12271f;
      margin: 0;
    }

    /* Status progress bars */
    .progress-stack {
      display: flex;
      flex-direction: column;
      gap: 14px;
    }
    .status-bar-item {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .bar-header {
      display: flex;
      align-items: center;
      font-size: 0.86rem;
      color: #3b564a;
    }
    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      margin-right: 8px;
    }
    .dot-cyan { background: #06b6d4; }
    .dot-emerald { background: #10b981; }
    .dot-blue { background: #3b82f6; }
    .dot-amber { background: #f59e0b; }
    .dot-red { background: #ef4444; }

    .status-label {
      flex: 1;
      font-weight: 600;
    }
    .status-values {
      display: flex;
      align-items: baseline;
      gap: 5px;
    }
    .progress-track {
      height: 10px;
      border-radius: 6px;
      background: #edf3ef;
      overflow: hidden;
    }
    .progress-fill {
      height: 100%;
      border-radius: 6px;
      transition: width 0.6s ease;
    }
    .fill-cyan { background: #06b6d4; }
    .fill-emerald { background: #10b981; }
    .fill-blue { background: #3b82f6; }
    .fill-amber { background: #f59e0b; }
    .fill-red { background: #ef4444; }

    /* Therapist Mini Avatar */
    .therapist-mini-avatar {
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: #e6f5ed;
      color: #19734e;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 0.78rem;
    }

    /* Quick Actions Grid */
    .quick-actions-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
    }
    @media (max-width: 992px) {
      .quick-actions-grid { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 600px) {
      .quick-actions-grid { grid-template-columns: 1fr; }
    }
    .quick-action-card {
      background: #ffffff;
      border: 1px solid #e3ebe6;
      border-radius: 16px;
      padding: 16px 18px;
      display: flex;
      align-items: center;
      gap: 14px;
      text-decoration: none;
      transition: all 0.2s;
      box-shadow: 0 2px 6px rgba(15, 41, 34, 0.02);
    }
    .quick-action-card:hover {
      border-color: #19734e;
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(15, 41, 34, 0.06);
    }
    .quick-icon-circle {
      width: 44px;
      height: 44px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.15rem;
      flex-shrink: 0;
    }
    .quick-title {
      font-size: 0.94rem;
      font-weight: 700;
      color: #12271f;
      margin: 0 0 2px;
    }
    .quick-desc {
      font-size: 0.78rem;
      color: #557164;
      margin: 0;
    }

    /* System Info */
    .system-info-card {
      padding: 18px 24px;
      border-radius: 18px;
    }
    .info-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
    }
    @media (max-width: 900px) {
      .info-grid { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 500px) {
      .info-grid { grid-template-columns: 1fr; }
    }
    .info-item {
      display: flex;
      flex-direction: column;
      gap: 3px;
    }
    .info-label {
      font-size: 0.75rem;
      font-weight: 600;
      color: #658b7c;
      text-transform: uppercase;
    }
    .info-val {
      font-size: 0.88rem;
      font-weight: 700;
      color: #12271f;
    }

    /* Modal Custom */
    .modal-backdrop-custom {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(15, 41, 34, 0.6);
      backdrop-filter: blur(4px);
      z-index: 999;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .modal-card-custom {
      background: #ffffff;
      border-radius: 20px;
      width: 100%;
      max-width: 540px;
      padding: 24px 28px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
      border: 1px solid #d9e7df;
      animation: fadeInModal 0.2s ease-out;
    }
    @keyframes fadeInModal {
      from { opacity: 0; transform: scale(0.95); }
      to { opacity: 1; transform: scale(1); }
    }
    .modal-header-custom {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 18px;
    }
    .modal-title-custom {
      font-size: 1.15rem;
      font-weight: 800;
      color: #12271f;
      margin: 0;
    }
    .modal-sub-custom {
      font-size: 0.82rem;
      color: #557164;
    }
    .btn-close-custom {
      background: #f4f7f5;
      border: none;
      width: 32px;
      height: 32px;
      border-radius: 8px;
      cursor: pointer;
      color: #557164;
    }
    .alert-summary-box {
      background: #f8faf9;
      border: 1px solid #e3ebe6;
      border-radius: 12px;
      padding: 14px 16px;
      font-size: 0.86rem;
    }
    .modal-footer-custom {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      margin-top: 18px;
    }

    .clean-card {
      background: #ffffff;
      border: 1px solid #e3ebe6;
      border-radius: 18px;
      box-shadow: 0 2px 10px rgba(15, 41, 34, 0.03);
    }
    .section-heading {
      font-size: 1.15rem;
      font-weight: 800;
      color: #12271f;
      margin: 0;
    }
    .section-title-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
    }
    .font-semibold { font-weight: 600; }
    .text-xs { font-size: 0.75rem; }
    .text-sm { font-size: 0.85rem; }
    .me-1 { margin-right: 4px; }
    .me-2 { margin-right: 8px; }
    .p-3 { padding: 16px; }
    .p-4 { padding: 22px; }
    .mb-0 { margin-bottom: 0; }
    .mb-1 { margin-bottom: 4px; }
    .mb-2 { margin-bottom: 8px; }
    .mb-3 { margin-bottom: 14px; }
    .mb-4 { margin-bottom: 24px; }
    .d-flex { display: flex; }
    .align-center { align-items: center; }
    .gap-1 { gap: 4px; }
    .gap-2 { gap: 8px; }
    .font-mono { font-family: var(--font-mono); }
    .text-center { text-align: center; }
  `]
})
export class DashboardComponent implements OnInit {
  // Estado general de conteos globales (Sprint 0)
  totalCentros = signal<number>(1);
  totalUsuarios = signal<number>(1);
  totalRoles = signal<number>(3);
  totalPermisos = signal<number>(6);

  // KPIs clínicos en tiempo real (Sprint 1)
  kpis = signal<DashboardKPIs | null>(null);
  cargando = signal<boolean>(false);

  // Lista de clínicas para el selector de SuperAdmin
  availableTenants = signal<Tenant[]>([]);
  selectedTenantSlug = signal<string>('');

  // Filtros de período (HU-20 / TP-52)
  hoy = new Date();
  anioSeleccionado: number = this.hoy.getFullYear();
  mesSeleccionado: number = this.hoy.getMonth() + 1;

  aniosDisponibles: number[] = [2025, 2026, 2027];
  meses = [
    { valor: 1, nombre: 'Enero' },
    { valor: 2, nombre: 'Febrero' },
    { valor: 3, nombre: 'Marzo' },
    { valor: 4, nombre: 'Abril' },
    { valor: 5, nombre: 'Mayo' },
    { valor: 6, nombre: 'Junio' },
    { valor: 7, nombre: 'Julio' },
    { valor: 8, nombre: 'Agosto' },
    { valor: 9, nombre: 'Septiembre' },
    { valor: 10, nombre: 'Octubre' },
    { valor: 11, nombre: 'Noviembre' },
    { valor: 12, nombre: 'Diciembre' }
  ];

  // Estado para modal de resolución de alerta (HU-21 / TP-54)
  alertaParaResolver = signal<AlertaClinica | null>(null);
  notaResolucion: string = '';
  resolviendoAlerta = signal<boolean>(false);

  constructor(
    public authService: AuthService,
    private userService: UserService,
    private tenantService: TenantService,
    private roleService: RoleService,
    private agendaService: AgendaService
  ) {}

  ngOnInit() {
    this.cargarMetricasGlobales();
    this.cargarListaTenants();

    // Si ya estamos en el contexto de un tenant, sincronizar el slug seleccionado
    const curTenant = this.authService.currentTenant();
    if (curTenant && curTenant.slug) {
      this.selectedTenantSlug.set(curTenant.slug);
    }

    // Cargar métricas del dashboard (Sprint 1)
    this.cargarDashboardKPIs();
  }

  cargarListaTenants() {
    this.tenantService.getAll().subscribe({
      next: (list) => {
        if (list && list.length > 0) {
          this.availableTenants.set(list);
          this.totalCentros.set(list.length);
        }
      },
      error: () => {
        // Fallback público si no es superadmin
        this.tenantService.getPublicList().subscribe({
          next: (list) => {
            if (list) this.availableTenants.set(list);
          },
          error: () => {}
        });
      }
    });
  }

  cargarMetricasGlobales() {
    this.userService.getAll().subscribe({
      next: (list) => {
        const activos = list?.filter(u => u.activo)?.length ?? list?.length;
        this.totalUsuarios.set(activos || 1);
      },
      error: () => {}
    });

    this.roleService.getRoles().subscribe({
      next: (list) => this.totalRoles.set(list?.length || 3),
      error: () => {}
    });

    this.roleService.getPermisos().subscribe({
      next: (list) => this.totalPermisos.set(list?.length || 6),
      error: () => {}
    });
  }

  /**
   * ═══════════════════════════════════════════════════════════════════════════
   * CU9: Consultar Dashboard e Indicadores Clínicos (HU-20)
   * CU10: Gestión de Alertas Tempranas y Priorización (HU-21)
   * Diagrama de Comunicación – Pasos del Flujo:
   *   Actor  → Director Clínico / Terapeuta / Administrador
   *   IU     → IU_DashboardClinico, IU_AlertasClinicas (DashboardComponent)
   *   CTR    → CTR_Dashboard, CTR_AlertaService (Django REST)
   *   CE     → CE_Metricas_y_Citas, CE_Alerta_y_Historial (PostgreSQL)
   * ═══════════════════════════════════════════════════════════════════════════
   */
  cargarDashboardKPIs(): void {
    // --- CU9 Paso 1: Acceder al Dashboard y seleccionar período en IU_DashboardClinico > ---
    // --- CU10 Paso 1: Consultar bandeja de alertas prioritarias en IU_AlertasClinicas > ---
    this.cargando.set(true);

    // --- CU9 Paso 2: GET /api/agenda/dashboard/kpis/?periodo=mes > ---
    // --- CU10 Paso 2: (Incluye alertas activas en el payload consolidado) > ---
    this.agendaService.getDashboardKPIs(this.anioSeleccionado, this.mesSeleccionado).subscribe({
      // --- CU9 Paso 7: 200 OK {total_citas, ausentismo, ocupacion} < ---
      // --- CU10 Paso 7: 200 OK {alertas_activas, nivel_riesgo: ALTO} < ---
      next: (res) => {
        this.kpis.set(res);
        this.cargando.set(false);
        // --- CU9 Paso 8: Renderizar KPIs, gráficos de tasa y métricas en IU_DashboardClinico < ---
        // --- CU10 Paso 8: Desplegar lista de pacientes en riesgo de abandono en IU_AlertasClinicas < ---
      },
      error: (err) => {
        console.error('Error al cargar KPIs del dashboard:', err);
        this.cargando.set(false);
      }
    });
  }

  recargarTodo() {
    this.cargarMetricasGlobales();
    this.cargarDashboardKPIs();
  }

  onFiltroPeriodoChange() {
    this.cargarDashboardKPIs();
  }

  /**
   * Conmutación ágil de Centro / Tenant para el SuperAdmin
   */
  onSelectTenant(slug: string) {
    this.selectedTenantSlug.set(slug);
    if (!slug) {
      this.authService.clearTenant();
    } else {
      const found = this.availableTenants().find(t => t.slug === slug);
      if (found) {
        this.authService.setTenant(found);
      }
    }
    // Recargar datos para el nuevo tenant
    this.recargarTodo();
  }

  /**
   * CU10 / HU-21: Modal para resolver alerta clínica con notas de seguimiento
   */
  abrirModalResolver(alerta: AlertaClinica) {
    this.alertaParaResolver.set(alerta);
    this.notaResolucion = 'Se contactó telefónicamente al paciente. Justificó motivo de inasistencia y se coordinó seguimiento.';
  }

  cerrarModalResolver() {
    this.alertaParaResolver.set(null);
    this.notaResolucion = '';
  }

  /**
   * CU10: Resolución de Alerta de Deserción
   *   Paso 1: Actor ingresa nota de intervención en IU_AlertasClinicas
   *   Paso 2: PATCH /api/agenda/alertas/{id}/ {resuelta: true, notas_resolucion}
   *   (Paso 3-6: CTR_AlertaService actualiza CE_Alerta persistiendo estado y fecha)
   *   Paso 7: 200 OK con alerta resuelta
   *   Paso 8: Actualizar bandeja y decrementar contador de riesgo
   */
  confirmarResolverAlerta() {
    const alerta = this.alertaParaResolver();
    if (!alerta) return;

    this.resolviendoAlerta.set(true);
    // --- CU10 Paso 2: PATCH /api/agenda/alertas/{id}/resolver/ > ---
    this.agendaService.resolverAlerta(alerta.id, this.notaResolucion).subscribe({
      // --- CU10 Paso 7: 200 OK < ---
      next: () => {
        this.resolviendoAlerta.set(false);
        this.cerrarModalResolver();
        // --- CU10 Paso 8: Desplegar lista actualizada de pacientes en riesgo < ---
        this.cargarDashboardKPIs();
      },
      error: (err) => {
        console.error('Error al resolver alerta clínica:', err);
        this.resolviendoAlerta.set(false);
      }
    });
  }

  iniciarTeleconsultaDemo() {
    // Redirigir a teleconsulta con sala demo para prueba instantánea
    window.location.href = '/teleconsulta/demo-teleconsulta';
  }

  calcularPorcentaje(cantidad: number | undefined): number {
    const total = this.kpis()?.total_citas_mes ?? this.kpis()?.citas_mes?.total ?? 0;
    if (!total || !cantidad) return 0;
    return Math.round((cantidad / total) * 100);
  }

  getNombreMes(num: number): string {
    const m = this.meses.find(item => item.valor === Number(num));
    return m ? m.nombre : 'Mes Actual';
  }

  getSeveridadBadgeClass(sev: string): string {
    switch (sev) {
      case 'CRITICA': return 'badge-danger';
      case 'ALTA': return 'badge-warning';
      case 'MEDIA': return 'badge-info';
      default: return 'badge-secondary';
    }
  }

  getAusentismoBadgeClass(tasa: number): string {
    if (tasa <= 10) return 'badge-success';
    if (tasa <= 25) return 'badge-warning';
    return 'badge-danger';
  }

  getAusentismoNivel(tasa: number): string {
    if (tasa <= 10) return 'Excelente (< 10%)';
    if (tasa <= 25) return 'Moderado (10-25%)';
    return 'Crítico (> 25%)';
  }

  getRoleClass(rolName?: string): string {
    const r = (rolName || '').toLowerCase();
    if (r.includes('super')) return 'role-super';
    if (r.includes('admin') || r.includes('coordinador')) return 'role-admin';
    if (r.includes('psico') || r.includes('terapeuta')) return 'role-psico';
    return 'role-paciente';
  }
}
