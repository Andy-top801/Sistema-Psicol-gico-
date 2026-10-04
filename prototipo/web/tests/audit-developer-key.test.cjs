const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const ts = require('typescript');
const path = require('node:path');

function loadService(relativePath, exportedClass) {
  const filename = path.join(__dirname, '..', relativePath);
  const source = fs.readFileSync(filename, 'utf8');
  const js = ts.transpile(source, { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, experimentalDecorators: true });
  const requests = [];
  class HttpParams {
    values = {};
    set(key, value) { this.values[key] = value; return this; }
  }
  class HttpClient {
    get(url, options) { requests.push({ method: 'GET', url, options }); return { subscribe() {} }; }
    post(url, body, options) { requests.push({ method: 'POST', url, body, options }); return { subscribe() {} }; }
  }
  const rxjs = require('rxjs');
  const modules = {
    '@angular/core': { Injectable: () => target => target },
    '@angular/common/http': { HttpClient, HttpParams },
    'rxjs': rxjs,
    '../../../environments/environment': { environment: { apiUrl: '/api' } },
    '../../models': {},
    'jspdf': { default: class {} },
    'jspdf-autotable': { default: () => {} },
    'xlsx': { utils: {}, write: () => new Uint8Array() }
  };
  const module = { exports: {} };
  vm.runInNewContext(js, { exports: module.exports, module, require: name => modules[name] || require(name), console, window: {}, document: {}, Blob, setTimeout });
  return { service: new module.exports[exportedClass](new HttpClient()), requests };
}

function expectNoKeyError(observable) {
  let error;
  observable.subscribe({ error: value => error = value });
  assert.match(error?.message || '', /clave de desarrollador/i);
}

test('direct audit logs fail closed without a key and send explicit header when supplied', () => {
  const { service, requests } = loadService('src/app/core/services/audit.service.ts', 'AuditService');
  expectNoKeyError(service.getLogs('2025-01-02', 'tenant'));
  assert.equal(requests.length, 0);
  service.getLogs('2025-01-02', ' tenant ', '  secret-value ').subscribe();
  assert.equal(requests.length, 1);
  assert.equal(requests[0].url, '/api/audit/logs/');
  assert.deepEqual(requests[0].options.params.values, { date: '2025-01-02', tenant: 'tenant' });
  assert.equal(requests[0].options.headers['X-Developer-Key'], 'secret-value');
  assert.equal(JSON.stringify(requests[0].options.params.values).includes('secret-value'), false);
});

test('all six report data/export/email endpoints isolate the key to bitacora', () => {
  const { service, requests } = loadService('src/app/core/services/report.service.ts', 'ReportService');
  const payload = { fuente: 'bitacora', columnas: ['action'], filtros: { date: '2025-01-02' } };
  const calls = [
    ['reporte', () => service.getReporte('bitacora', {}, ['action'], undefined, 'key-1')],
    ['custom', () => service.generarPersonalizado(payload, 'key-2')],
    ['email', () => service.enviarEmail({ email: 'a@b.test', fuente: 'bitacora' }, 'key-3')],
    ['excel', () => service.descargarExcelServer('bitacora', {}, undefined, 'key-4')],
    ['csv', () => service.descargarCSVServer('bitacora', {}, 'key-5')],
    ['html', () => service.descargarHTMLServer('bitacora', {}, undefined, 'key-6')]
  ];
  for (const [, call] of calls) call().subscribe();
  assert.equal(requests.length, 6);
  assert.deepEqual(requests.map(r => r.options.headers['X-Developer-Key']), ['key-1', 'key-2', 'key-3', 'key-4', 'key-5', 'key-6']);
  assert.deepEqual(requests.map(r => r.url), [
    '/api/reportes/bitacora/', '/api/reportes/personalizado/', '/api/reportes/email/',
    '/api/reportes/bitacora/export/excel/', '/api/reportes/bitacora/export/csv/', '/api/reportes/bitacora/export/html/'
  ]);
  for (const [, call] of [
    ['reporte', () => service.getReporte('bitacora')],
    ['custom', () => service.generarPersonalizado(payload)],
    ['email', () => service.enviarEmail({ email: 'a@b.test', fuente: 'bitacora' })],
    ['excel', () => service.descargarExcelServer('bitacora')],
    ['csv', () => service.descargarCSVServer('bitacora')],
    ['html', () => service.descargarHTMLServer('bitacora')]
  ]) expectNoKeyError(call());
  assert.equal(requests.length, 6);
});

test('metadata and non-audit sources never receive the developer key', () => {
  const { service, requests } = loadService('src/app/core/services/report.service.ts', 'ReportService');
  service.getMetadata().subscribe();
  service.getReporte('citas', {}, undefined, undefined, 'ignored').subscribe();
  service.generarPersonalizado({ fuente: 'citas' }, 'ignored').subscribe();
  service.enviarEmail({ email: 'a@b.test', fuente: 'citas' }, 'ignored').subscribe();
  service.descargarExcelServer('citas', {}, undefined, 'ignored').subscribe();
  service.descargarCSVServer('citas', {}, 'ignored').subscribe();
  service.descargarHTMLServer('citas', {}, undefined, 'ignored').subscribe();
  assert.equal(requests.length, 7);
  assert.ok(requests.every(request => !request.options?.headers?.['X-Developer-Key']));
});

function loadAuditComponent() {
  const filename = path.join(__dirname, '../src/app/modules/audit/audit-log.component.ts');
  const js = ts.transpile(fs.readFileSync(filename, 'utf8'), { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, experimentalDecorators: true });
  let authEffect;
  let effectOptions;
  const angular = {
    Component: () => target => target,
    signal: initial => { let value = initial; const fn = () => value; fn.set = next => value = next; return fn; },
    effect: (callback, options) => { authEffect = callback; effectOptions = options; callback(); },
    inject: () => ({})
  };
  class HttpErrorResponse extends Error { constructor(status) { super(); this.status = status; } }
  const modules = {
    '@angular/core': angular,
    '@angular/common': {},
    '@angular/forms': {},
    '@angular/common/http': { HttpErrorResponse },
    '../../core/services/audit.service': {},
    '../../core/models': {},
    '../../core/services/auth.service': {}
  };
  const module = { exports: {} };
  vm.runInNewContext(js, { module, exports: module.exports, require: name => modules[name], console });
  return { Component: module.exports.AuditLogComponent, getEffect: () => authEffect, effectOptions: () => effectOptions };
}

test('audit component cancels and clears protected data on edit, lock, destroy, and logout without initial load', () => {
  const { Component, getEffect, effectOptions } = loadAuditComponent();
  let authenticated = true;
  let calls = 0;
  let cancelled = false;
  const auditService = { getLogs: () => { calls++; return { subscribe: () => ({ unsubscribe: () => cancelled = true }) }; } };
  const authService = { isAuthenticated: () => authenticated };
  const component = new Component(auditService, authService);
  assert.equal(effectOptions().allowSignalWrites, true);
  component.ngOnInit();
  assert.equal(calls, 0);
  component.developerKey = 'temporary';
  component.loadLogs();
  assert.equal(calls, 1);
  component.events.set([{ action: 'private' }]);
  component.developerKey = 'edited';
  component.onKeyEdited();
  assert.equal(cancelled, true);
  assert.equal(component.developerKey, 'edited');
  assert.equal(component.events().length, 0);
  component.events.set([{ action: 'private' }]);
  component.lock();
  assert.equal(component.developerKey, '');
  assert.equal(component.events().length, 0);
  component.developerKey = 'temporary';
  component.events.set([{ action: 'private' }]);
  authenticated = false;
  getEffect()();
  assert.equal(component.developerKey, '');
  assert.equal(component.events().length, 0);
  component.ngOnDestroy();
  assert.equal(component.events().length, 0);
});

function loadReportComponent(file, exportedClass) {
  const filename = path.join(__dirname, '../src/app/modules/reportes', file);
  const js = ts.transpile(fs.readFileSync(filename, 'utf8'), {
    module: ts.ModuleKind.CommonJS,
    target: ts.ScriptTarget.ES2020,
    experimentalDecorators: true
  });
  const effects = [];
  const angular = {
    Component: () => target => target,
    computed: callback => callback,
    effect: callback => { effects.push(callback); callback(); }
  };
  const rxjs = require('rxjs');
  const modules = {
    '@angular/core': angular,
    '@angular/common': {},
    '@angular/forms': {},
    '@angular/router': { RouterModule: {} },
    '../../core/services/report.service': {},
    '../../core/services/auth.service': {},
    'rxjs': rxjs
  };
  const module = { exports: {} };
  vm.runInNewContext(js, { module, exports: module.exports, require: name => modules[name], console, Date, setTimeout });
  return { Component: module.exports[exportedClass], effects };
}

function makeReportHarness() {
  const calls = [];
  const createRequest = (method, args) => {
    const subject = new (require('rxjs').Subject)();
    calls.push({ method, args, subject });
    return subject;
  };
  const service = {
    getMetadata: () => require('rxjs').EMPTY,
    getReporte: (...args) => createRequest('getReporte', args),
    generarPersonalizado: (...args) => createRequest('generarPersonalizado', args),
    enviarEmail: (...args) => createRequest('enviarEmail', args)
  };
  let authenticated = true;
  const authService = {
    isAuthenticated: () => authenticated,
    isSuperAdmin: () => true,
    currentTenant: () => null,
    currentUser: () => null
  };
  return { calls, service, authService, setAuthenticated: value => authenticated = value };
}

const result = { columnas: [], datos: [{ action: 'private' }], total: 1 };

test('report viewer runs real component logic: explicit audit consult, transitions, cancellation, logout and destroy', () => {
  const { Component, effects } = loadReportComponent('reporte-visor.component.ts', 'ReporteVisorComponent');
  const harness = makeReportHarness();
  const routeParams = new (require('rxjs').Subject)();
  const component = new Component({ paramMap: routeParams }, harness.service, harness.authService);
  component.ngOnInit();

  routeParams.next({ get: () => 'bitacora' });
  assert.equal(harness.calls.filter(call => call.method === 'getReporte').length, 0);

  routeParams.next({ get: () => 'citas' });
  const pendingCitas = harness.calls.at(-1).subject;
  routeParams.next({ get: () => 'bitacora' });
  assert.equal(pendingCitas.observed, false);
  assert.equal(component.resultado, null);

  component.developerKey = 'audit-key';
  component.cargarReporte();
  const pendingAudit = harness.calls.at(-1).subject;
  pendingAudit.next(result);
  assert.equal(component.resultado, result);

  component.emailDestino = 'recipient@example.test';
  component.enviarPorCorreo();
  const pendingEmail = harness.calls.at(-1).subject;
  assert.equal(component.enviandoEmail, true);
  component.keyChanged();
  pendingAudit.next({ ...result, datos: [{ action: 'late' }] });
  pendingEmail.next({ mensaje: 'late email' });
  assert.equal(pendingAudit.observed, false);
  assert.equal(pendingEmail.observed, false);
  assert.equal(component.resultado, null);
  assert.equal(component.cargando, false);
  assert.equal(component.enviandoEmail, false);
  assert.equal(component.modalEmailAbierto, false);

  component.developerKey = 'audit-key';
  component.cargarReporte();
  const pendingLock = harness.calls.at(-1).subject;
  component.resultado = result;
  component.lockAudit();
  pendingLock.next(result);
  assert.equal(pendingLock.observed, false);
  assert.equal(component.resultado, null);
  assert.equal(component.developerKey, '');

  component.developerKey = 'audit-key';
  component.cargarReporte();
  const pendingLogout = harness.calls.at(-1).subject;
  component.resultado = result;
  harness.setAuthenticated(false);
  effects.at(-1)();
  pendingLogout.next(result);
  assert.equal(pendingLogout.observed, false);
  assert.equal(component.developerKey, '');
  assert.equal(component.resultado, null);
  assert.equal(component.enviandoEmail, false);

  routeParams.next({ get: () => 'citas' });
  const callsBeforeDestroy = harness.calls.length;
  component.ngOnDestroy();
  routeParams.next({ get: () => 'pacientes' });
  assert.equal(harness.calls.length, callsBeforeDestroy);
});

test('custom report runs real component logic: no initial audit request, source changes, key edit, lock, logout and destroy cancel subscriptions', () => {
  const { Component, effects } = loadReportComponent('reporte-personalizado.component.ts', 'ReportePersonalizadoComponent');
  const harness = makeReportHarness();
  const component = new Component(harness.service, harness.authService);
  component.ngOnInit();
  assert.equal(harness.calls.length, 0);

  component.fuenteSeleccionada = 'bitacora';
  component.onFuenteCambiada();
  component.generarReportePersonalizado();
  assert.equal(harness.calls.length, 0);
  component.developerKey = 'audit-key';
  component.generarReportePersonalizado();
  const pendingAudit = harness.calls.at(-1).subject;
  pendingAudit.next(result);
  assert.equal(component.resultado, result);

  component.emailDestino = 'recipient@example.test';
  component.enviarPorCorreo();
  const pendingEmail = harness.calls.at(-1).subject;
  assert.equal(component.enviandoEmail, true);
  component.developerKey = 'edited-key';
  component.keyChanged();
  pendingAudit.next({ ...result, datos: [{ action: 'late' }] });
  pendingEmail.next({ mensaje: 'late email' });
  assert.equal(pendingAudit.observed, false);
  assert.equal(pendingEmail.observed, false);
  assert.equal(component.resultado, null);
  assert.equal(component.generando, false);
  assert.equal(component.enviandoEmail, false);
  assert.equal(component.modalEmailAbierto, false);

  component.developerKey = 'audit-key';
  component.generarReportePersonalizado();
  const pendingLock = harness.calls.at(-1).subject;
  component.lockAudit();
  pendingLock.next(result);
  assert.equal(pendingLock.observed, false);
  assert.equal(component.resultado, null);
  assert.equal(component.developerKey, '');

  component.developerKey = 'audit-key';
  component.generarReportePersonalizado();
  const pendingSource = harness.calls.at(-1).subject;
  component.fuenteSeleccionada = 'citas';
  component.onFuenteCambiada();
  pendingSource.next(result);
  assert.equal(pendingSource.observed, false);
  assert.equal(component.resultado, null);
  assert.equal(component.developerKey, '');

  component.fuenteSeleccionada = 'bitacora';
  component.onFuenteCambiada();
  component.developerKey = 'audit-key';
  component.generarReportePersonalizado();
  const pendingLogout = harness.calls.at(-1).subject;
  component.resultado = result;
  harness.setAuthenticated(false);
  effects.at(-1)();
  pendingLogout.next(result);
  assert.equal(pendingLogout.observed, false);
  assert.equal(component.resultado, null);
  assert.equal(component.developerKey, '');
  assert.equal(component.generando, false);

  component.developerKey = 'audit-key';
  component.generarReportePersonalizado();
  const pendingDestroy = harness.calls.at(-1).subject;
  component.ngOnDestroy();
  pendingDestroy.next(result);
  assert.equal(pendingDestroy.observed, false);
  assert.equal(component.resultado, null);
});
