import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap, catchError, of, timeout } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface ChatbotBotonAccion {
  etiqueta: string;
  accion: string;
}

export interface ChatbotHistorialItem {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatbotMessage {
  id?: string;
  remitente: 'USUARIO' | 'BOT' | 'OPERADOR';
  texto: string;
  intencion_detectada?: string;
  contiene_riesgo?: boolean;
  nivel_riesgo?: 'BAJO' | 'MEDIO' | 'ALTO' | 'CRITICO' | 'NORMAL' | 'CRISIS';
  es_alerta_crisis?: boolean;
  escalar_humano?: boolean;
  lineas_auxilio?: string[];
  botones_accion?: ChatbotBotonAccion[];
  opciones_sugeridas?: string[];
  timestamp?: string;
}

export interface ChatbotApiResponse {
  session_id: string;
  remitente: 'BOT' | string;
  respuesta: string;
  intencion_detectada: string;
  contiene_riesgo: boolean;
  nivel_riesgo: 'BAJO' | 'MEDIO' | 'ALTO' | 'CRITICO';
  alerta_crisis: boolean;
  escalar_humano: boolean;
  lineas_auxilio: string[];
  botones_accion: ChatbotBotonAccion[];
  timestamp: string;
}

@Injectable({
  providedIn: 'root'
})
export class ChatbotService {
  // Endpoint de Producción en Hugging Face Space (con CORS habilitado *)
  private hfApiUrl = 'https://antidino-iacupficct.hf.space/api/v1/chatbot/mensaje/';
  // Endpoint de Respaldo en Backend Django SIGEPSI
  private backendApiUrl = `${environment.apiUrl}/clinica/chatbot/mensaje/`;
  private storageKey = 'sigepsi_chatbot_session';
  private storageMsgsKey = 'sigepsi_chatbot_messages';

  // Signals reactivos para el estado del chatbot
  isOpen = signal<boolean>(false);
  isLoading = signal<boolean>(false);
  isCrisis = signal<boolean>(false);
  isHumanHandover = signal<boolean>(false);
  messages = signal<ChatbotMessage[]>([]);
  unreadCount = signal<number>(0);

  constructor(private http: HttpClient) {
    this.initSession();
    this.cargarMensajesLocales();
  }

  private initSession(): void {
    let session = localStorage.getItem(this.storageKey);
    if (!session) {
      session = 'sess_' + Math.random().toString(36).substring(2, 11) + Date.now().toString(36);
      localStorage.setItem(this.storageKey, session);
    }
  }

  getSessionId(): string {
    let session = localStorage.getItem(this.storageKey);
    if (!session) {
      session = 'sess_' + Math.random().toString(36).substring(2, 11) + Date.now().toString(36);
      localStorage.setItem(this.storageKey, session);
    }
    return session;
  }

  private cargarMensajesLocales(): void {
    try {
      const guardados = localStorage.getItem(this.storageMsgsKey);
      if (guardados) {
        const msgs = JSON.parse(guardados) as ChatbotMessage[];
        if (msgs && msgs.length > 0) {
          this.messages.set(msgs);
          const tieneCrisis = msgs.some(m => m.es_alerta_crisis);
          if (tieneCrisis) this.isCrisis.set(true);
          const tieneEscalamiento = msgs.some(m => m.escalar_humano);
          if (tieneEscalamiento) this.isHumanHandover.set(true);
          return;
        }
      }
    } catch {
      // Ignorar error de parsing
    }

    // Mensaje de bienvenida inicial si no hay historial
    this.establecerMensajeBienvenida();
  }

  private persistirMensajes(): void {
    try {
      localStorage.setItem(this.storageMsgsKey, JSON.stringify(this.messages()));
    } catch {
      // Storage lleno o privado
    }
  }

  private establecerMensajeBienvenida(): void {
    this.messages.set([
      {
        remitente: 'BOT',
        texto: '¡Hola! Te damos la bienvenida a SIGEPSI. Soy el asistente virtual con IA para orientación psicológica y consultas del centro. ¿En qué puedo acompañarte u orientarte hoy?',
        es_alerta_crisis: false,
        botones_accion: [
          { etiqueta: 'Agendar Cita', accion: 'AGENDAR_CITA' },
          { etiqueta: 'Aranceles y Modalidades', accion: 'CONSULTAR_ARANCELES' },
          { etiqueta: 'Formulario Previo (Intake)', accion: 'IR_INTAKE' },
          { etiqueta: 'Hablar con Recepcionista', accion: 'SOLICITAR_HUMANO' }
        ],
        timestamp: new Date().toISOString()
      }
    ]);
    this.persistirMensajes();
  }

  toggleChat(): void {
    const nextState = !this.isOpen();
    this.isOpen.set(nextState);
    if (nextState) {
      this.unreadCount.set(0);
    }
  }

  /**
   * Obtiene los últimos intercambios en el formato { role, content } para la memoria de la IA.
   */
  obtenerHistorialParaIA(): ChatbotHistorialItem[] {
    const msgs = this.messages();
    return msgs
      .filter(m => m.remitente === 'USUARIO' || m.remitente === 'BOT')
      .slice(-10) // Mantener últimos 10 turnos de conversación
      .map(m => ({
        role: (m.remitente === 'USUARIO' ? 'user' : 'assistant') as 'user' | 'assistant',
        content: m.texto
      }));
  }

  /**
   * Envía el mensaje del usuario a la API del Chatbot en Hugging Face
   * con soporte de timeout, memoria de conversación, y fallback de alta disponibilidad.
   */
  enviarMensaje(texto: string): Observable<any> {
    this.isLoading.set(true);
    const sessionId = this.getSessionId();

    // 1. Registrar mensaje optimista en pantalla
    const userMsg: ChatbotMessage = {
      remitente: 'USUARIO',
      texto: texto.trim(),
      timestamp: new Date().toISOString()
    };
    this.messages.update(msgs => [...msgs, userMsg]);
    this.persistirMensajes();

    // 2. Construir historial de memoria para el modelo de IA
    const historial = this.obtenerHistorialParaIA().slice(0, -1); // Excluir el recién insertado

    const requestPayload = {
      session_id: sessionId,
      mensaje: texto.trim(),
      historial: historial
    };

    // 3. Petición a la API Hugging Face con timeout y fallback al backend SIGEPSI
    return this.http.post<ChatbotApiResponse>(this.hfApiUrl, requestPayload).pipe(
      timeout(35000), // 35 segundos de timeout
      catchError((hfError) => {
        console.warn('Hugging Face space tardó o no respondió, recurriendo a proxy backend:', hfError);
        // Fallback a proxy backend
        return this.http.post<any>(this.backendApiUrl, requestPayload).pipe(
          timeout(15000),
          catchError(() => {
            // Fallback de emergencia local ante desconexión
            const fallbackResponse: ChatbotApiResponse = {
              session_id: sessionId,
              remitente: 'BOT',
              respuesta: 'He recibido tu mensaje. Si estás experimentando angustia intensa o una emergencia emocional, por favor comunícate de inmediato con las líneas oficiales de auxilio.',
              intencion_detectada: 'FALLBACK_EMERGENCIA',
              contiene_riesgo: true,
              nivel_riesgo: 'CRITICO',
              alerta_crisis: true,
              escalar_humano: true,
              lineas_auxilio: ['800-11-3040', '911'],
              botones_accion: [
                { etiqueta: 'Contactar Recepción', accion: 'SOLICITAR_HUMANO' },
                { etiqueta: 'Agendar Cita', accion: 'AGENDAR_CITA' }
              ],
              timestamp: new Date().toISOString()
            };
            return of(fallbackResponse);
          })
        );
      }),
      tap({
        next: (res: ChatbotApiResponse | any) => {
          this.isLoading.set(false);

          const contienePalabrasCrisis = /suicid|morir|matarme|quitarme la vida|no aguanto m[aá]s|hacerme da[ñn]o/i.test(texto) ||
                                         /suicid|morir|matarme|quitarme la vida/i.test(res.respuesta || '');
          const esAlertaCrisis = Boolean(res.alerta_crisis || res.es_crisis || res.nivel_riesgo === 'CRITICO' || res.nivel_riesgo === 'ALTO' || contienePalabrasCrisis);
          const esEscalamiento = Boolean(res.escalar_humano || res.estado === 'ESCALADA_HUMANO' || esAlertaCrisis);

          if (esAlertaCrisis) {
            this.isCrisis.set(true);
          }
          if (esEscalamiento) {
            this.isHumanHandover.set(true);
          }

          // Garantizar líneas de auxilio oficiales ante cualquier evento de crisis
          const lineasEmergencia = (res.lineas_auxilio && res.lineas_auxilio.length > 0)
            ? res.lineas_auxilio
            : (esAlertaCrisis ? ['800-11-3040', '911'] : []);

          // Crear mensaje del BOT con los campos de la API de Hugging Face
          const botMsg: ChatbotMessage = {
            remitente: 'BOT',
            texto: res.respuesta || res.mensaje_bot?.texto || res.texto || 'No se recibió respuesta.',
            intencion_detectada: res.intencion_detectada,
            contiene_riesgo: Boolean(res.contiene_riesgo || esAlertaCrisis),
            nivel_riesgo: esAlertaCrisis ? 'CRITICO' : (res.nivel_riesgo || 'BAJO'),
            es_alerta_crisis: esAlertaCrisis,
            escalar_humano: esEscalamiento,
            lineas_auxilio: lineasEmergencia,
            botones_accion: res.botones_accion || [],
            opciones_sugeridas: res.botones_accion?.map((b: ChatbotBotonAccion) => b.etiqueta) || res.opciones || [],
            timestamp: res.timestamp || new Date().toISOString()
          };

          this.messages.update(msgs => [...msgs, botMsg]);
          this.persistirMensajes();

          if (!this.isOpen()) {
            this.unreadCount.update(c => c + 1);
          }
        },
        error: () => {
          this.isLoading.set(false);
        }
      })
    );
  }

  solicitarHumano(): Observable<any> {
    const sessionId = this.getSessionId();
    this.isHumanHandover.set(true);
    
    // Enviar solicitud de operador a la IA / backend
    return this.enviarMensaje('Por favor, deseo hablar con un recepcionista o asesor humano del centro.');
  }

  reiniciarConversacion(): void {
    const newSession = 'sess_' + Math.random().toString(36).substring(2, 11) + Date.now().toString(36);
    localStorage.setItem(this.storageKey, newSession);
    localStorage.removeItem(this.storageMsgsKey);
    this.isCrisis.set(false);
    this.isHumanHandover.set(false);
    this.establecerMensajeBienvenida();
  }
}
