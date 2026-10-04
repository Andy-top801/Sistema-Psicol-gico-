import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface ChatbotMessage {
  id?: string;
  remitente: 'USUARIO' | 'BOT' | 'OPERADOR';
  texto: string;
  es_alerta_crisis?: boolean;
  opciones_sugeridas?: string[];
  timestamp?: string;
}

export interface ChatbotResponse {
  session_id: string;
  conversacion_id: string;
  estado: 'BOT_ACTIVO' | 'ESCALADA_HUMANO' | 'EN_ATENCION' | 'FINALIZADA';
  nivel_riesgo: 'NORMAL' | 'MODERADO' | 'CRISIS';
  es_crisis: boolean;
  mensaje_usuario?: ChatbotMessage;
  mensaje_bot?: ChatbotMessage;
  esperando_operador?: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class ChatbotService {
  private apiUrl = `${environment.apiUrl}/clinica/chatbot`;
  private storageKey = 'sigepsi_chatbot_session';

  // Signals reactivos para el estado del chatbot
  isOpen = signal<boolean>(false);
  isLoading = signal<boolean>(false);
  isCrisis = signal<boolean>(false);
  isHumanHandover = signal<boolean>(false);
  messages = signal<ChatbotMessage[]>([]);
  unreadCount = signal<number>(0);

  constructor(private http: HttpClient) {
    this.initSession();
  }

  private initSession(): void {
    let session = localStorage.getItem(this.storageKey);
    if (!session) {
      session = 'sess_' + Math.random().toString(36).substring(2, 15) + Date.now().toString(36);
      localStorage.setItem(this.storageKey, session);
    }
  }

  getSessionId(): string {
    let session = localStorage.getItem(this.storageKey);
    if (!session) {
      session = 'sess_' + Math.random().toString(36).substring(2, 15) + Date.now().toString(36);
      localStorage.setItem(this.storageKey, session);
    }
    return session;
  }

  toggleChat(): void {
    const nextState = !this.isOpen();
    this.isOpen.set(nextState);
    if (nextState) {
      this.unreadCount.set(0);
      if (this.messages().length === 0) {
        this.cargarHistorial().subscribe();
      }
    }
  }

  enviarMensaje(texto: string): Observable<ChatbotResponse> {
    this.isLoading.set(true);
    const sessionId = this.getSessionId();

    // Mensaje optimista local en el stream
    const tempUserMsg: ChatbotMessage = {
      remitente: 'USUARIO',
      texto,
      timestamp: new Date().toISOString()
    };
    this.messages.update(msgs => [...msgs, tempUserMsg]);

    return this.http.post<ChatbotResponse>(`${this.apiUrl}/mensaje/`, {
      session_id: sessionId,
      mensaje: texto
    }).pipe(
      tap({
        next: (res) => {
          this.isLoading.set(false);
          if (res.es_crisis) {
            this.isCrisis.set(true);
          }
          if (res.estado === 'ESCALADA_HUMANO' || res.esperando_operador) {
            this.isHumanHandover.set(true);
          }
          if (res.mensaje_bot) {
            this.messages.update(msgs => [...msgs, res.mensaje_bot!]);
            if (!this.isOpen()) {
              this.unreadCount.update(c => c + 1);
            }
          }
        },
        error: () => {
          this.isLoading.set(false);
          const errorMsg: ChatbotMessage = {
            remitente: 'BOT',
            texto: 'Lo siento, ocurrió un error de comunicación temporal. Si se trata de una urgencia o crisis emocional, por favor comunícate de inmediato con la Línea de la Vida al 800-11-3040 o al 911.',
            es_alerta_crisis: true,
            timestamp: new Date().toISOString()
          };
          this.messages.update(msgs => [...msgs, errorMsg]);
        }
      })
    );
  }

  cargarHistorial(): Observable<any> {
    const sessionId = this.getSessionId();
    this.isLoading.set(true);
    return this.http.get<any>(`${this.apiUrl}/historial/`, {
      params: { session_id: sessionId }
    }).pipe(
      tap({
        next: (res) => {
          this.isLoading.set(false);
          if (res.mensajes && res.mensajes.length > 0) {
            this.messages.set(res.mensajes);
            if (res.nivel_riesgo === 'CRISIS') {
              this.isCrisis.set(true);
            }
            if (res.estado === 'ESCALADA_HUMANO') {
              this.isHumanHandover.set(true);
            }
          } else {
            // Mensaje de bienvenida inicial
            this.messages.set([
              {
                remitente: 'BOT',
                texto: '¡Hola! Te damos la bienvenida a SIGEPSI. Soy el asistente virtual del centro. ¿En qué podemos orientarte el día de hoy?',
                opciones_sugeridas: [
                  '¿Cómo agendar mi cita?',
                  'Aranceles y Modalidades',
                  'Cuestionario Previo (Intake)',
                  'Hablar con Recepción'
                ],
                timestamp: new Date().toISOString()
              }
            ]);
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
    return this.http.post<any>(`${this.apiUrl}/solicitar-humano/`, {
      session_id: sessionId
    }).pipe(
      tap({
        next: (res) => {
          this.isHumanHandover.set(true);
          if (res.mensaje_bot) {
            this.messages.update(msgs => [...msgs, res.mensaje_bot]);
          }
        }
      })
    );
  }

  reiniciarConversacion(): void {
    const newSession = 'sess_' + Math.random().toString(36).substring(2, 15) + Date.now().toString(36);
    localStorage.setItem(this.storageKey, newSession);
    this.isCrisis.set(false);
    this.isHumanHandover.set(false);
    this.messages.set([
      {
        remitente: 'BOT',
        texto: 'Conversación reiniciada. ¿En qué podemos ayudarte el día de hoy?',
        opciones_sugeridas: [
          '¿Cómo agendar mi cita?',
          'Aranceles y Modalidades',
          'Cuestionario Previo (Intake)',
          'Hablar con Recepción'
        ],
        timestamp: new Date().toISOString()
      }
    ]);
  }
}
