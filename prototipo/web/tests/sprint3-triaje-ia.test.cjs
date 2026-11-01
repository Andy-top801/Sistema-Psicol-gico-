const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const ts = require('typescript');
const rxjs = require('rxjs');

function loadTriajeService() {
  const file = path.join(__dirname, '../src/app/core/services/triaje-ia.service.ts');
  const js = ts.transpile(fs.readFileSync(file, 'utf8'), {
    module: ts.ModuleKind.CommonJS,
    target: ts.ScriptTarget.ES2020,
    experimentalDecorators: true
  });
  const requests = [];
  class HttpClient {
    post(url, body) { requests.push({ method: 'POST', url, body }); return rxjs.of({ ok: true, data: body }); }
    get(url, options) { requests.push({ method: 'GET', url, options }); return rxjs.of([{ id: 'clasif-1', alerta_crisis: true, nivel_severidad: 'CRITICA' }]); }
  }
  const module = { exports: {} };
  const modules = {
    '@angular/core': { Injectable: () => target => target },
    '@angular/common/http': { HttpClient },
    'rxjs': rxjs,
    '../../../environments/environment': { environment: { apiUrl: 'http://localhost:8000/api' } }
  };
  require('vm').runInNewContext(js, {
    module,
    exports: module.exports,
    require: name => modules[name] || require(name),
    console
  });
  return { service: new module.exports.TriajeIAService(new HttpClient()), requests };
}

function loadConsolaComponent() {
  const file = path.join(__dirname, '../src/app/modules/triaje/consola-triage.component.ts');
  const js = ts.transpile(fs.readFileSync(file, 'utf8'), {
    module: ts.ModuleKind.CommonJS,
    target: ts.ScriptTarget.ES2020,
    experimentalDecorators: true
  });
  const module = { exports: {} };
  const modules = {
    '@angular/core': { Component: () => target => target, OnInit: class {} },
    '@angular/common': {},
    '@angular/forms': {},
    '../../core/services/triaje-ia.service': {}
  };
  require('vm').runInNewContext(js, {
    module,
    exports: module.exports,
    require: name => modules[name] || require(name),
    console
  });
  return module.exports.ConsolaTriageComponent;
}

test('TriajeIAService generates expected endpoints for Crisis and Matching', () => {
  const { service, requests } = loadTriajeService();

  service.getAlertasCrisis().subscribe();
  assert.equal(requests[requests.length - 1].url, 'http://localhost:8000/api/clinica/triaje/alertas/');

  service.generarMatching('pac-123', 'ANSIEDAD_FOBIAS', 'MIXTA').subscribe();
  assert.equal(requests[requests.length - 1].url, 'http://localhost:8000/api/clinica/triaje/pac-123/sugerir-matching/');

  service.asignarPsicologoHITL('sug-1', 'pac-123', 'psi-99', 'Justificación profesional obligatoria').subscribe();
  assert.equal(requests[requests.length - 1].url, 'http://localhost:8000/api/clinica/triaje/asignar/');
  assert.equal(requests[requests.length - 1].body.justificacion_clinica, 'Justificación profesional obligatoria');
});

test('ConsolaTriageComponent identifies critical crisis and manages HITL selection', () => {
  const Consola = loadConsolaComponent();
  const mockService = {
    getClasificaciones: () => rxjs.of([
      { id: '1', alerta_crisis: false, nivel_severidad: 'MODERADO', categoria_principal: 'ANSIEDAD_FOBIAS', confianza_score: 0.85, hash_trazabilidad_sha256: 'a1b2c3' },
      { id: '2', alerta_crisis: true, nivel_severidad: 'CRITICA', categoria_principal: 'DEPRESION_ANIMO', confianza_score: 0.95, hash_trazabilidad_sha256: 'd4e5f6' }
    ]),
    generarMatching: () => rxjs.of([
      {
        id: 'sug-1',
        paciente: 'pac-1',
        psicologo_sugerido: 'psi-1',
        score_afinidad: 92.5,
        factores_ponderacion: { afinidad_especialidad: 40, disponibilidad_horaria: 30, balance_carga: 15, preferencia_modalidad: 7.5 },
        estado_decision: 'PENDIENTE_VALIDACION'
      }
    ]),
    asignarPsicologoHITL: () => rxjs.of({ mensaje: 'OK' })
  };

  const comp = new Consola(mockService);
  comp.ngOnInit();

  assert.equal(comp.clasificaciones.length, 2);
  assert.equal(comp.alertasCrisis.length, 1, 'Debe detectar exactamente 1 caso con alerta de crisis vital');
  assert.equal(comp.alertasCrisis[0].nivel_severidad, 'CRITICA');

  // Seleccionar caso y generar Top 3
  comp.seleccionarCaso(comp.clasificaciones[0]);
  comp.generarSugerenciasTop3();
  assert.equal(comp.sugerencias.length, 1);
  assert.equal(comp.sugerencias[0].score_afinidad, 92.5);

  // Abrir y confirmar HITL
  comp.abrirModalHITL(comp.sugerencias[0]);
  assert.ok(comp.sugerenciaSeleccionada);
  comp.confirmarAsignacionHITL();
  assert.equal(comp.sugerencias[0].estado_decision, 'APROBADO');
});
