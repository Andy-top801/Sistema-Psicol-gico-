import { Injectable, NgZone } from '@angular/core';
import { Subject, Observable } from 'rxjs';

export interface ExtractedVoiceParams {
  transcript: string;
  fuente?: string;
  mes?: string;
  mesNumero?: number;
  psicologo?: string;
  paciente?: string;
  clinica?: string;
  estado?: string;
  modalidad?: string;
  fecha_desde?: string;
  fecha_hasta?: string;
  columnasSugeridas?: string[];
  confianza?: number;
}

/**
 * CTR_SpeechParserService (Web Speech API NLP)
 * Implementa el reconocimiento de voz interactivo y procesamiento de lenguaje natural
 * para extraer parámetros estructurados (fuente, psicólogo, rango temporal, estado)
 * según el Caso de Uso HU-38 (CU25) y Diagramas de Secuencia y Comunicación.
 */
@Injectable({
  providedIn: 'root'
})
export class SpeechParserService {
  private recognition: any = null;
  private isListening = false;
  private readonly paramsSubject = new Subject<ExtractedVoiceParams>();
  private readonly transcriptSubject = new Subject<string>();
  private readonly listeningSubject = new Subject<boolean>();
  private readonly errorSubject = new Subject<string>();

  public paramsExtracted$: Observable<ExtractedVoiceParams> = this.paramsSubject.asObservable();
  public liveTranscript$: Observable<string> = this.transcriptSubject.asObservable();
  public isListening$: Observable<boolean> = this.listeningSubject.asObservable();
  public error$: Observable<string> = this.errorSubject.asObservable();

  constructor(private zone: NgZone) {
    this.initRecognition();
  }

  private initRecognition(): void {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      try {
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.lang = 'es-ES';

        this.recognition.onstart = () => {
          this.zone.run(() => {
            this.isListening = true;
            this.listeningSubject.next(true);
          });
        };

        this.recognition.onresult = (event: any) => {
          let interimTranscript = '';
          let finalTranscript = '';

          for (let i = event.resultIndex; i < event.results.length; ++i) {
            const piece = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalTranscript += piece;
            } else {
              interimTranscript += piece;
            }
          }

          const currentText = (finalTranscript || interimTranscript).trim();
          this.zone.run(() => {
            this.transcriptSubject.next(currentText);
            if (finalTranscript) {
              const parsed = this.parseInstruction(finalTranscript);
              this.paramsSubject.next(parsed);
            }
          });
        };

        this.recognition.onerror = (event: any) => {
          this.zone.run(() => {
            this.isListening = false;
            this.listeningSubject.next(false);
            const err = event.error || 'Error al capturar audio';
            this.errorSubject.next(err);
          });
        };

        this.recognition.onend = () => {
          this.zone.run(() => {
            this.isListening = false;
            this.listeningSubject.next(false);
          });
        };
      } catch (e) {
        console.warn('SpeechRecognition initialization error:', e);
      }
    }
  }

  public isSupported(): boolean {
    return !!((window as any).SpeechRecognition || (window as any).webkitSpeechRecognition);
  }

  /**
   * 1a: presionar_boton_microfono()
   * Inicia la captura mediante la Web Speech API
   */
  public startListening(): void {
    if (this.recognition && !this.isListening) {
      try {
        this.recognition.start();
      } catch (err) {
        // En caso de estar ya en ejecución
        try {
          this.recognition.stop();
          setTimeout(() => this.recognition.start(), 150);
        } catch (_) {}
      }
    } else if (!this.recognition) {
      this.errorSubject.next('Tu navegador no soporta Web Speech API. Puedes escribir la instrucción en el simulador de voz.');
    }
  }

  public stopListening(): void {
    if (this.recognition && this.isListening) {
      try {
        this.recognition.stop();
      } catch (_) {}
      this.isListening = false;
      this.listeningSubject.next(false);
    }
  }

  /**
   * 2a: dictar_instruccion(texto) y parsear audio
   * Mapeo semántico de entidad, filtros temporales, psicólogo y modalidad.
   */
  public parseInstruction(rawText: string): ExtractedVoiceParams {
    let text = rawText.toLowerCase().replace(/[,.;:¿?¡!]/g, ' ').replace(/\s+/g, ' ').trim();
    const result: ExtractedVoiceParams = {
      transcript: rawText,
    };

    // 0. Clínica / tenant (solo lo usa el SuperAdmin): "citas de la clínica Esperanza en octubre".
    // Se toma el nombre hasta la primera palabra que ya es otro filtro, y se quita del texto
    // para que "Esperanza" no termine leyéndose como psicólogo.
    const mc = text.match(/\b(?:cl[ií]nica|centro|tenant)\s+(.+)$/);
    if (mc) {
      const paradas = new Set([
        'de', 'del', 'en', 'con', 'para', 'por', 'y', 'que', 'desde', 'hasta', 'durante', 'sobre', 'este', 'esta',
        'mes', 'hoy', 'ayer', 'semana', 'año', 'ano', 'modalidad', 'estado', 'presencial', 'virtual', 'psicologo',
        'psicólogo', 'psicologa', 'psicóloga', 'doctor', 'doctora', 'licenciado', 'licenciada', 'paciente',
        'cita', 'citas', 'realizadas', 'confirmadas', 'canceladas', 'programadas', 'pendientes', 'reporte',
        'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'setiembre',
        'octubre', 'noviembre', 'diciembre',
      ]);
      const palabras = mc[1].split(' ');
      let i = 0;
      while (i < palabras.length && ['de', 'del', 'la', 'el', 'los', 'las'].includes(palabras[i])) i++; // "clínica de la Esperanza"
      const nombre: string[] = [];
      for (; i < palabras.length && !paradas.has(palabras[i]) && !/^\d/.test(palabras[i]); i++) nombre.push(palabras[i]);
      if (nombre.length) {
        result.clinica = nombre.map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
        const inicio = mc.index ?? 0;
        const consumido = mc[0].split(' ').slice(0, 1 + i).join(' ');
        text = (text.slice(0, inicio) + ' ' + text.slice(inicio + consumido.length)).replace(/\s+/g, ' ').trim();
      }
    }

    // 1. Detección de entidad/fuente
    if (text.includes('cita') || text.includes('atencion') || text.includes('atención') || text.includes('sesion') || text.includes('sesión') || text.includes('agenda')) {
      result.fuente = 'citas';
    } else if (text.includes('psicolog') || text.includes('terapeuta') || text.includes('profesional')) {
      result.fuente = 'psicologos';
    } else if (text.includes('paciente') || text.includes('expediente') || text.includes('historia')) {
      result.fuente = 'pacientes';
    } else if (text.includes('alerta') || text.includes('crisis') || text.includes('riesgo')) {
      result.fuente = 'alertas';
    } else if (text.includes('ingreso') || text.includes('pago') || text.includes('cobro') || text.includes('recaudacion') || text.includes('recaudación')) {
      result.fuente = 'ingresos';
    } else if (text.includes('teleconsulta') || text.includes('virtual') || text.includes('videollamada')) {
      result.fuente = 'teleconsultas';
    } else if (text.includes('usuario')) {
      result.fuente = 'usuarios';
    } else if (text.includes('bitacora') || text.includes('bitácora') || text.includes('auditoria') || text.includes('auditoría')) {
      result.fuente = 'bitacora';
    } else {
      // Default si se solicitan citas por contexto común clínico
      result.fuente = 'citas';
    }

    // 2. Detección de mes / filtro temporal
    const meses = [
      { nombre: 'enero', num: 1, dias: 31 },
      { nombre: 'febrero', num: 2, dias: 28 },
      { nombre: 'marzo', num: 3, dias: 31 },
      { nombre: 'abril', num: 4, dias: 30 },
      { nombre: 'mayo', num: 5, dias: 31 },
      { nombre: 'junio', num: 6, dias: 30 },
      { nombre: 'julio', num: 7, dias: 31 },
      { nombre: 'agosto', num: 8, dias: 31 },
      { nombre: 'septiembre', num: 9, dias: 30 },
      { nombre: 'setiembre', num: 9, dias: 30 },
      { nombre: 'octubre', num: 10, dias: 31 },
      { nombre: 'noviembre', num: 11, dias: 30 },
      { nombre: 'diciembre', num: 12, dias: 31 },
    ];

    const fmt = (d: Date) =>
      `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
    const hoy = new Date();
    const anioDicho = text.match(/\b(20\d{2})\b/);
    const anio = anioDicho ? Number(anioDicho[1]) : hoy.getFullYear();

    for (const m of meses) {
      if (new RegExp(`\\b${m.nombre}\\b`).test(text)) {
        result.mes = m.nombre === 'setiembre' ? 'septiembre' : m.nombre;
        result.mesNumero = m.num;
        result.fecha_desde = fmt(new Date(anio, m.num - 1, 1));
        result.fecha_hasta = fmt(new Date(anio, m.num, 0)); // último día real (bisiestos incluidos)
        break;
      }
    }

    // Rangos relativos: "hoy", "esta semana", "este mes", "mes pasado", "este año", o solo "2025"
    if (!result.fecha_desde) {
      if (/\bhoy\b/.test(text)) {
        result.fecha_desde = result.fecha_hasta = fmt(hoy);
      } else if (/\bayer\b/.test(text)) {
        const ayer = new Date(hoy.getFullYear(), hoy.getMonth(), hoy.getDate() - 1);
        result.fecha_desde = result.fecha_hasta = fmt(ayer);
      } else if (/(esta|la) semana/.test(text)) {
        const lunes = new Date(hoy.getFullYear(), hoy.getMonth(), hoy.getDate() - ((hoy.getDay() + 6) % 7));
        result.fecha_desde = fmt(lunes);
        result.fecha_hasta = fmt(new Date(lunes.getFullYear(), lunes.getMonth(), lunes.getDate() + 6));
      } else if (/mes pasado|[uú]ltimo mes|mes anterior/.test(text)) {
        result.fecha_desde = fmt(new Date(hoy.getFullYear(), hoy.getMonth() - 1, 1));
        result.fecha_hasta = fmt(new Date(hoy.getFullYear(), hoy.getMonth(), 0));
      } else if (/(este|del|el) mes/.test(text)) {
        result.fecha_desde = fmt(new Date(hoy.getFullYear(), hoy.getMonth(), 1));
        result.fecha_hasta = fmt(new Date(hoy.getFullYear(), hoy.getMonth() + 1, 0));
      } else if (anioDicho || /este a[nñ]o/.test(text)) {
        result.fecha_desde = `${anio}-01-01`;
        result.fecha_hasta = `${anio}-12-31`;
      }
    }

    // 3. Detección de psicólogo / paciente.
    // Palabras que nunca son nombres (antes "de modalidad" o "de la" se tomaban como psicólogo y vaciaban el reporte).
    const noNombres = new Set([
      ...meses.map(m => m.nombre), 'mes', 'año', 'ano', 'semana', 'hoy', 'ayer', 'modalidad', 'estado', 'tipo',
      'reporte', 'reportes', 'lista', 'listado', 'cita', 'citas', 'paciente', 'pacientes', 'psicologo', 'psicólogo',
      'psicologos', 'psicólogos', 'psicologa', 'psicóloga', 'sesion', 'sesión', 'sesiones', 'atencion', 'atención',
      'atenciones', 'agenda', 'alertas', 'ingresos', 'pagos', 'teleconsultas', 'usuarios', 'bitacora', 'bitácora',
      'clinica', 'clínica', 'centro', 'tenant', 'la', 'el', 'los', 'las', 'un', 'una', 'este', 'esta', 'ese', 'esa', 'todo', 'todos', 'todas', 'mi', 'mis',
      'presencial', 'virtual', 'realizadas', 'confirmadas', 'canceladas', 'programadas', 'pendientes',
    ]);
    const nombreValido = (w?: string) => !!w && !noNombres.has(w) && !/^\d+$/.test(w);
    const cap = (w: string) => w.charAt(0).toUpperCase() + w.slice(1);

    const pac = text.match(/paciente\s+([a-záéíóúñü]+)/);
    if (pac && nombreValido(pac[1])) result.paciente = cap(pac[1]);

    const psicExplicito = text.match(/(?:psic[oó]log[oa]|doctor[a]?|dr[a]?\.?|licenciad[oa]|lic\.?|terapeuta)\s+([a-záéíóúñü]+)/);
    if (psicExplicito && nombreValido(psicExplicito[1])) {
      result.psicologo = cap(psicExplicito[1]);
    } else {
      // "citas de Carlos", "con Carlos": revisar TODAS las apariciones, no solo la primera "de"
      for (const m of text.matchAll(/\b(?:de|del|con)\s+([a-záéíóúñü]+)/g)) {
        if (nombreValido(m[1]) && cap(m[1]) !== result.paciente) {
          result.psicologo = cap(m[1]);
          break;
        }
      }
    }

    // 4. Detección de estado clínico
    if (text.includes('realizada') || text.includes('completada') || text.includes('atendida')) {
      result.estado = 'REALIZADA';
    } else if (text.includes('confirmada')) {
      result.estado = 'CONFIRMADA';
    } else if (text.includes('cancelada')) {
      result.estado = 'CANCELADA';
    } else if (text.includes('inasistencia') || text.includes('falta')) {
      result.estado = 'INASISTENCIA';
    } else if (text.includes('programada') || text.includes('pendiente')) {
      result.estado = 'PROGRAMADA';
    }

    // 5. Detección de modalidad
    if (text.includes('presencial')) {
      result.modalidad = 'PRESENCIAL';
    } else if (text.includes('virtual') || text.includes('teleconsulta') || text.includes('en linea') || text.includes('en línea')) {
      result.modalidad = 'VIRTUAL';
    }

    // 6. Proyección predeterminada de 5 columnas para citas (Paso 2 BDD):
    // 'Fecha', 'Psicólogo', 'Paciente', 'Estado', 'Modalidad'
    if (result.fuente === 'citas') {
      result.columnasSugeridas = ['fecha', 'psicologo_nombre', 'paciente_nombre', 'estado', 'modalidad'];
    }

    return result;
  }

  /**
   * Permite inyectar manualmente un comando de voz simulado para entornos de prueba
   */
  public simularComandoVoz(comandoTexto: string): ExtractedVoiceParams {
    this.transcriptSubject.next(comandoTexto);
    const parsed = this.parseInstruction(comandoTexto);
    this.paramsSubject.next(parsed);
    return parsed;
  }
}

// Alias requerido por el Diagrama de Secuencia y Comunicación
export const CTR_SpeechParserService = SpeechParserService;
