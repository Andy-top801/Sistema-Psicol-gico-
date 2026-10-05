import { Injectable, NgZone } from '@angular/core';
import { Subject, Observable } from 'rxjs';

export interface ExtractedVoiceParams {
  transcript: string;
  fuente?: string;
  mes?: string;
  mesNumero?: number;
  psicologo?: string;
  paciente?: string;
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
    const text = rawText.toLowerCase().trim();
    const result: ExtractedVoiceParams = {
      transcript: rawText,
    };

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

    for (const m of meses) {
      if (text.includes(m.nombre)) {
        result.mes = m.nombre === 'setiembre' ? 'septiembre' : m.nombre;
        result.mesNumero = m.num;
        // Asignar rango temporal automático para el año actual
        const currentYear = new Date().getFullYear();
        const mm = String(m.num).padStart(2, '0');
        const dd = String(m.dias).padStart(2, '0');
        result.fecha_desde = `${currentYear}-${mm}-01`;
        result.fecha_hasta = `${currentYear}-${mm}-${dd}`;
        break;
      }
    }

    // 3. Detección de psicólogo (ej: "de Carlos", "con Carlos", "psicólogo Carlos")
    const matchPsicologo = text.match(/(?:de|del psic[oó]logo|con el psic[oó]logo|doctor|licenciado|psic[oó]logo|con)\s+([a-záéíóúñ]+)/i);
    if (matchPsicologo && matchPsicologo[1]) {
      const candidato = matchPsicologo[1].trim();
      // Descartar palabras que sean meses o fuentes
      const noNombres = ['septiembre', 'setiembre', 'octubre', 'noviembre', 'diciembre', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'citas', 'pacientes', 'mes', 'año', 'semana'];
      if (!noNombres.includes(candidato.toLowerCase())) {
        result.psicologo = candidato.charAt(0).toUpperCase() + candidato.slice(1);
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
