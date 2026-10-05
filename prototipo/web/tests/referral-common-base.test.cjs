const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const ts = require('typescript');
const rxjs = require('rxjs');

function loadService() {
  const file = path.join(__dirname, '../src/app/core/services/clinica-sprint2.service.ts');
  const js = ts.transpile(fs.readFileSync(file, 'utf8'), { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, experimentalDecorators: true });
  const requests = [];
  class HttpClient { post(url, body) { requests.push({ url, body }); return rxjs.of({ id: 'ref-1' }); } get(url, options) { requests.push({ url, options }); return rxjs.of(new Blob()); } }
  class HttpParams { set() { return this; } }
  const module = { exports: {} };
  const modules = {
    '@angular/core': { Injectable: () => target => target }, '@angular/common/http': { HttpClient, HttpParams },
    'rxjs': rxjs, '../../../environments/environment': { environment: { apiUrl: '/api' } },
    '../models/clinica-sprint2.model': {}, '../../models': {}, 'jspdf': {}, 'jspdf-autotable': {}, 'xlsx': {}
  };
  require('vm').runInNewContext(js, { module, exports: module.exports, require: name => modules[name] || require(name), console, Blob });
  return { service: new module.exports.ClinicaSprint2Service(new HttpClient()), requests };
}

function loadComponent() {
  const file = path.join(__dirname, '../src/app/modules/derivaciones/derivacion-form.component.ts');
  const js = ts.transpile(fs.readFileSync(file, 'utf8'), { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, experimentalDecorators: true });
  const signal = value => { const fn = () => value; fn.set = next => value = next; return fn; };
  const module = { exports: {} };
  const modules = {
    '@angular/core': { Component: () => target => target, OnInit: class {}, signal },
    '@angular/common': {}, '@angular/forms': {}, '@angular/router': {},
    '../../core/services/clinica-sprint2.service': {}, '../../core/models/clinica-sprint2.model': {}
  };
  require('vm').runInNewContext(js, { module, exports: module.exports, require: name => modules[name] || require(name), console, setTimeout });
  return module.exports.DerivacionFormComponent;
}

test('component exposes create/list/PDF errors and retains input while saving ends', () => {
  const Component = loadComponent();
  const errorRequest = () => new rxjs.Observable(subscriber => subscriber.error(new Error('offline')));
  const service = {
    getDerivaciones: errorRequest,
    getHistoriasClinicas: () => rxjs.of([]),
    crearDerivacion: errorRequest,
    descargarOrdenDerivacionPdf: errorRequest
  };
  const component = new Component({ queryParams: rxjs.EMPTY }, {}, service);
  component.nuevaDerivacion.motivo_derivacion = 'preserve me';
  component.guardarDerivacion();
  assert.equal(component.guardando, false);
  assert.equal(component.nuevaDerivacion.motivo_derivacion, 'preserve me');
  assert.match(component.mensajeError(), /guardar/i);
  component.descargarPdf('ref-1');
  assert.match(component.mensajeError(), /PDF/i);
});

test('translates form fields once at the API boundary and uses the PDF action', () => {
  const { service, requests } = loadService();
  service.crearDerivacion({ historia_clinica: 'h1', tipo_cierre: 'DERIVACION_PSIQUIATRIA', especialidad_destino: 'Psiquiatría', profesional_o_institucion_destino: 'Hospital', motivo_derivacion: 'Motivo', resumen_evolucion: 'Evolución', recomendaciones_tratamiento: 'Recomendación' }).subscribe();
  assert.equal(requests[0].body.tipo_derivacion, 'EXTERNA_PSIQUIATRIA');
  assert.equal(requests[0].body.motivo_clinico, 'Motivo\n\nEvolución: Evolución\nRecomendaciones: Recomendación');
  assert.equal(requests[0].body.psicologo_emisor, undefined);
  service.descargarOrdenDerivacionPdf('r1').subscribe();
  assert.equal(requests[1].url, '/api/clinica/derivaciones/r1/descargar-pdf/');
  assert.equal(requests[1].options.responseType, 'blob');
});
