const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const ts = require('typescript');
const rxjs = require('rxjs');
const vm = require('node:vm');

function transpile(file) {
  return ts.transpile(fs.readFileSync(file, 'utf8'), {
    module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, experimentalDecorators: true
  });
}

function loadService() {
  const requests = [];
  class HttpClient {
    post(url, body) { requests.push({ method: 'POST', url, body }); return rxjs.of({ id: 'event-1' }); }
    get(url, options) { requests.push({ method: 'GET', url, options }); return rxjs.of([]); }
  }
  class HttpParams { set() { return this; } }
  const module = { exports: {} };
  const modules = {
    '@angular/core': { Injectable: () => target => target },
    '@angular/common/http': { HttpClient, HttpParams },
    'rxjs': rxjs,
    '../../../environments/environment': { environment: { apiUrl: '/api' } },
    '../models/clinica-sprint2.model': {}, '../../models': {}, 'jspdf': {}, 'jspdf-autotable': {}, 'xlsx': {}
  };
  vm.runInNewContext(transpile(path.join(__dirname, '../src/app/core/services/clinica-sprint2.service.ts')), {
    module, exports: module.exports, require: name => modules[name] || require(name), console, Blob
  });
  return { service: new module.exports.ClinicaSprint2Service(new HttpClient()), requests };
}

function loadDerivacionComponent(confirmResult = false) {
  const module = { exports: {} };
  const signal = initial => { let value = initial; const fn = () => value; fn.set = next => { value = next; }; return fn; };
  const modules = {
    '@angular/core': { Component: () => target => target, OnInit: class {}, signal },
    '@angular/common': {}, '@angular/forms': {}, '@angular/router': {},
    '../../core/services/clinica-sprint2.service': {}, '../../core/models/clinica-sprint2.model': {}
  };
  vm.runInNewContext(transpile(path.join(__dirname, '../src/app/modules/derivaciones/derivacion-form.component.ts')), {
    module, exports: module.exports, require: name => modules[name] || require(name), console, setTimeout,
    window: { confirm: () => confirmResult }
  });
  return module.exports.DerivacionFormComponent;
}

test('closure service sends distinct summary, achievements and maintenance fields', () => {
  const { service, requests } = loadService();
  service.crearDerivacion({
    historia_clinica: 'h1', tipo_cierre: 'MUTUO_ACUERDO', motivo_derivacion: 'Resumen de egreso',
    resumen_evolucion: 'legacy referral field', logros_alcanzados: 'Logros reales',
    recomendaciones_mantenimiento: 'Mantener seguimiento'
  }).subscribe();
  const body = requests[0].body;
  assert.equal(body.tipo_derivacion, 'MUTUO_ACUERDO');
  assert.equal(body.motivo_clinico, 'Resumen de egreso');
  assert.equal(body.logros_alcanzados, 'Logros reales');
  assert.equal(body.recomendaciones_mantenimiento, 'Mantener seguimiento');
});

test('empty closure and confirmation cancellation make no network request', () => {
  const Component = loadDerivacionComponent();
  const calls = [];
  const component = new Component({}, {}, { crearDerivacion: data => { calls.push(data); return rxjs.of({ id: 'x' }); } });
  component.nuevaDerivacion.tipo_cierre = 'MUTUO_ACUERDO';
  component.nuevaDerivacion.historia_clinica = 'h1';
  component.nuevaDerivacion.motivo_derivacion = 'summary';
  component.nuevaDerivacion.logros_alcanzados = '';
  component.nuevaDerivacion.recomendaciones_mantenimiento = 'maintenance';
  component.guardarDerivacion();
  assert.equal(calls.length, 0);
  component.nuevaDerivacion.logros_alcanzados = 'achievement';
  component.guardarDerivacion();
  assert.equal(calls.length, 0);
});

test('backend errors remain visible while closure input remains available for retry', () => {
  const Component = loadDerivacionComponent(true);
  const component = new Component({}, {}, {
    crearDerivacion: () => new rxjs.Observable(subscriber => subscriber.error({ error: { historia_clinica: 'Hay una cita pendiente' } }))
  });
  component.nuevaDerivacion.tipo_cierre = 'MUTUO_ACUERDO';
  Object.assign(component.nuevaDerivacion, {
    historia_clinica: 'h1', motivo_derivacion: 'summary', logros_alcanzados: 'achievement', recomendaciones_mantenimiento: 'maintenance'
  });
  component.guardarDerivacion();
  assert.match(component.mensajeError(), /cita pendiente/);
  assert.equal(component.nuevaDerivacion.logros_alcanzados, 'achievement');
});

test('reactivation service uses dedicated endpoint and reason', () => {
  const { service, requests } = loadService();
  service.reactivarHistoriaClinica('h1', 'Nuevo plan').subscribe();
  assert.equal(requests[0].url, '/api/clinica/historias-clinicas/h1/reactivar/');
  assert.equal(requests[0].body.motivo_clinico, 'Nuevo plan');
});
