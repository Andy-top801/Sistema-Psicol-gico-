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
  // Filtros especiales SuperAdmin (Centro Psicológico / Tenant)
  centro?: string;
  centro_nombre?: string;
}

// Catálogo de Centros Psicológicos (Tenants) registrados para reconocimiento por voz
export const CENTROS_CATALOGO_VOZ = [
  { slug: 'centro_esperanza', nombre: 'Centro Psicológico Esperanza', aliases: ['esperanza', 'centro esperanza', 'psicologico esperanza', 'clinica esperanza', 'clínica esperanza'] },
  { slug: 'mentesana', nombre: 'Gabinete Integral MenteSana', aliases: ['mentesana', 'mente sana', 'gabinete mentesana', 'integral mentesana', 'clinica mentesana', 'clínica mentesana'] },
  { slug: 'equilibrio_mental', nombre: 'Centro de Salud Emocional Equilibrio', aliases: ['equilibrio', 'equilibrio mental', 'salud emocional equilibrio', 'clinica equilibrio', 'clínica equilibrio'] },
  { slug: 'renacer_psicologia', nombre: 'Clínica de Psicoterapia Renacer', aliases: ['renacer', 'psicoterapia renacer', 'clinica renacer', 'clínica renacer'] },
  { slug: 'serenidad_sucre', nombre: 'Instituto Psicológico Serenidad', aliases: ['serenidad', 'serenidad sucre', 'instituto serenidad', 'clinica serenidad', 'clínica serenidad'] },
  { slug: 'vinculos_familiares', nombre: 'Centro Terapéutico Vínculos', aliases: ['vinculos', 'vínculos', 'vinculos familiares', 'vínculos familiares', 'clinica vinculos', 'clinica vínculos', 'clínica vinculos', 'clínica vínculos'] },
  { slug: 'armonia_cochabamba', nombre: 'Consultorios Psicológicos Armonía', aliases: ['armonia', 'armonía', 'armonia cochabamba', 'armonía cochabamba', 'clinica armonia', 'clínica armonía'] },
  { slug: 'bienestar_pleno', nombre: 'Centro de Psicología Clínica Bienestar Pleno', aliases: ['bienestar', 'bienestar pleno', 'clinica bienestar', 'clínica bienestar'] },
  { slug: 'crecer_infantil', nombre: 'Gabinete Infanto-Juvenil Crecer', aliases: ['crecer', 'infanto juvenil crecer', 'gabinete crecer', 'clinica crecer', 'clínica crecer'] },
  { slug: 'oasis_emocional', nombre: 'Consultorios Terapéuticos Oasis', aliases: ['oasis', 'oasis emocional', 'terapeuticos oasis', 'clinica oasis', 'clínica oasis'] },
  { slug: 'resiliencia_oruro', nombre: 'Centro Integral de Salud Mental Resiliencia', aliases: ['resiliencia', 'resiliencia oruro', 'clinica resiliencia', 'clínica resiliencia'] },
  { slug: 'vida_salud', nombre: 'Centro Psicoterapéutico Vida & Salud', aliases: ['vida y salud', 'vida & salud', 'vida salud', 'clinica vida y salud', 'clínica vida y salud'] },
];

// Palabras reservadas, artículos, preposiciones y nombres de sistema que NO son psicólogos
const PALABRAS_NO_NOMBRES = new Set([
  'la', 'el', 'los', 'las', 'un', 'una', 'unos', 'unas', 'lo', 'le', 'les',
  'de', 'del', 'al', 'en', 'por', 'para', 'con', 'sin', 'sobre', 'y', 'o',
  'modalidad', 'tipo', 'forma', 'citas', 'cita', 'sesion', 'sesiones',
  'paciente', 'pacientes', 'psicologo', 'psicologa', 'psicologos', 'psicologas',
  'psicólogo', 'psicóloga', 'psicólogos', 'psicólogas',
  'encargado', 'encargada', 'encargados', 'encargadas', 'reporte', 'reportes',
  'mes', 'año', 'semana', 'dia', 'hoy', 'ayer', 'manana', 'mañana',
  'atencion', 'atención', 'atenciones', 'presencial', 'virtual', 'mixta',
  'centro', 'clinica', 'clínica', 'gabinete', 'instituto', 'consultorio', 'consultorios',
  'todos', 'todas', 'cada', 'este', 'esta', 'estos', 'estas', 'nombre', 'registrado', 'registrados',
  'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
  'septiembre', 'setiembre', 'octubre', 'noviembre', 'diciembre',
  'esperanza', 'mentesana', 'armonia', 'armonía', 'bienestar', 'crecer',
  'equilibrio', 'oasis', 'renacer', 'resiliencia', 'serenidad', 'vida', 'vinculos', 'vínculos'
]);

/**
 * CTR_SpeechParserService (Web Speech API NLP)
 * Implementa el reconocimiento de voz interactivo y procesamiento de lenguaje natural
 * para extraer parámetros estructurados (fuente, psicólogo, rango temporal, estado, centro/tenant)
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
   * Mapeo semántico de entidad, filtros temporales, psicólogo, modalidad y centro/tenant.
   */
  public parseInstruction(rawText: string): ExtractedVoiceParams {
    const text = rawText.toLowerCase().trim();
    const result: ExtractedVoiceParams = {
      transcript: rawText,
    };

    // 0. Detección de Centro Psicológico (Tenant) / Clínica
    // Patrón prioritario: 'psicólogos de la clínica <nombre>', 'citas de la clínica <nombre>', 'del centro <nombre>'
    const matchClinicaExpl = text.match(/(?:de\s+la\s+cl[ií]nica|del\s+centro|de\s+la\s+instituci[oó]n|del\s+consultorio|cl[ií]nica|centro)\s+([a-záéíóúñ0-9\s&]+)/i);
    let centroEncontrado: { slug: string; nombre: string } | null = null;

    if (matchClinicaExpl && matchClinicaExpl[1]) {
      const terminoClinica = matchClinicaExpl[1].trim();
      for (const c of CENTROS_CATALOGO_VOZ) {
        if (c.aliases.some(a => terminoClinica.includes(a) || a.includes(terminoClinica))) {
          centroEncontrado = c;
          break;
        }
      }
    }

    // Búsqueda en catálogo de centros por alias en el texto completo
    if (!centroEncontrado) {
      for (const c of CENTROS_CATALOGO_VOZ) {
        if (c.aliases.some(alias => text.includes(alias))) {
          centroEncontrado = c;
          break;
        }
      }
    }

    if (centroEncontrado) {
      result.centro = centroEncontrado.slug;
      result.centro_nombre = centroEncontrado.nombre;
    }

    // 1. Detección de entidad/fuente con soporte diacríticos
    if (/(?:psic[oó]log|terapeuta|profesional)/i.test(text)) {
      // Si la frase habla explícitamente de "psicólogos de la clínica" o "psicólogos encargados"
      if (/(?:psic[oó]log(?:os?|as?)|profesionales|terapeutas)\s+(?:de\s+la\s+cl[ií]nica|del\s+centro|encargados)/i.test(text) ||
          /(?:directorio|lista|cat[aá]logo)\s+de\s+psic[oó]log/i.test(text)) {
        result.fuente = 'psicologos';
      } else if (/(?:cita|atenci[oó]n|sesi[oó]n|agenda)/i.test(text)) {
        result.fuente = 'citas';
      } else {
        result.fuente = 'psicologos';
      }
    } else if (/(?:cita|atenci[oó]n|sesi[oó]n|agenda)/i.test(text)) {
      result.fuente = 'citas';
    } else if (/(?:paciente|expediente|historia)/i.test(text)) {
      result.fuente = 'pacientes';
    } else if (/(?:alerta|crisis|riesgo)/i.test(text)) {
      result.fuente = 'alertas';
    } else if (/(?:ingreso|pago|cobro|recaudaci[oó]n|factura|financier)/i.test(text)) {
      result.fuente = 'ingresos';
    } else if (/(?:teleconsulta|virtual|videollamada)/i.test(text)) {
      result.fuente = 'teleconsultas';
    } else if (/(?:usuario)/i.test(text)) {
      result.fuente = 'usuarios';
    } else if (/(?:bit[aá]cora|auditor[ií]a)/i.test(text)) {
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
        const currentYear = new Date().getFullYear();
        const mm = String(m.num).padStart(2, '0');
        const dd = String(m.dias).padStart(2, '0');
        result.fecha_desde = `${currentYear}-${mm}-01`;
        result.fecha_hasta = `${currentYear}-${mm}-${dd}`;
        break;
      }
    }

    // 3. Detección precisa de nombre de psicólogo individual:
    // Solo si NO es plural ni comando enfocado en la clínica o modalidad general
    const esPluralOClinica = /(?:psic[oó]log(?:os|as)|de\s+la\s+cl[ií]nica|del\s+centro|modalidad)/i.test(text);
    if (!esPluralOClinica) {
      let matchPsicologo = text.match(/(?:del psic[oó]logo|de la psic[oó]loga|con el psic[oó]logo|con la psic[oó]loga|dr\.|dra\.|doctor[a]?|lic\.|licenciad[oa]|psic[oó]log[oa])\s+([a-záéíóúñ]+)/i);

      if (!matchPsicologo) {
        matchPsicologo = text.match(/(?:citas de|consulta de|atendido por|con)\s+([a-záéíóúñ]+)/i);
      }

      if (matchPsicologo && matchPsicologo[1]) {
        const candidato = matchPsicologo[1].trim().toLowerCase();
        // Validar que no sea artículo ("la", "el"), modalidad, centro ni palabra común
        if (candidato.length >= 3 && !PALABRAS_NO_NOMBRES.has(candidato)) {
          result.psicologo = candidato.charAt(0).toUpperCase() + candidato.slice(1);
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

    // 6. Proyección predeterminada de columnas sugeridas
    if (result.fuente === 'psicologos') {
      result.columnasSugeridas = ['nombre_completo', 'numero_colegiado', 'especialidades', 'modalidad', 'tarifa_base', 'activo', 'total_citas'];
    } else if (result.fuente === 'citas') {
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
