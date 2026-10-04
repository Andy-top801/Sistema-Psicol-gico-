import { Component, ElementRef, ViewChild, AfterViewChecked, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatbotService, ChatbotMessage } from '../core/services/chatbot.service';

@Component({
  selector: 'app-chatbot-widget',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <!-- Floating Launcher Trigger Button -->
    <div class="chatbot-launcher-container">
      <button 
        type="button" 
        class="chatbot-launcher-btn" 
        [class.active]="chatService.isOpen()"
        [class.has-crisis]="chatService.isCrisis()"
        (click)="chatService.toggleChat()"
        [attr.aria-label]="chatService.isOpen() ? 'Cerrar chat de orientación' : 'Abrir chat de orientación clínica SIGEPSI'">
        
        <div class="icon-wrapper">
          <i *ngIf="!chatService.isOpen() && !chatService.isCrisis()" class="fa-solid fa-comments"></i>
          <span *ngIf="!chatService.isOpen() && chatService.isCrisis()" class="crisis-icon">⚠️</span>
          <i *ngIf="chatService.isOpen()" class="fa-solid fa-chevron-down"></i>
        </div>

        <span class="launcher-tooltip" *ngIf="!chatService.isOpen()">
          Orientación Clínica & Crisis
        </span>

        <!-- Badge de no leídos -->
        <span class="unread-badge" *ngIf="!chatService.isOpen() && chatService.unreadCount() > 0">
          {{ chatService.unreadCount() }}
        </span>
      </button>

      <!-- Chat Modal Card -->
      <div class="chatbot-window" *ngIf="chatService.isOpen()">
        <!-- Header -->
        <div class="chat-header">
          <div class="header-info">
            <div class="avatar-ring">
              <span class="psi-char">Ψ</span>
            </div>
            <div class="title-group">
              <h3 class="header-title">Orientación SIGEPSI</h3>
              <div class="status-indicator">
                <span class="status-dot" [class.human]="chatService.isHumanHandover()"></span>
                <span class="status-text">
                  {{ chatService.isHumanHandover() ? 'Recepción Conectada' : 'Asistente 24/7' }}
                </span>
              </div>
            </div>
          </div>

          <div class="header-actions">
            <button 
              type="button" 
              class="icon-btn" 
              (click)="solicitarAsesor()" 
              title="Solicitar atención de recepcionista humano"
              *ngIf="!chatService.isHumanHandover()">
              <i class="fa-solid fa-headset"></i>
            </button>
            <button 
              type="button" 
              class="icon-btn" 
              (click)="chatService.reiniciarConversacion()" 
              title="Reiniciar conversación">
              <i class="fa-solid fa-rotate-right"></i>
            </button>
            <button 
              type="button" 
              class="icon-btn close-btn" 
              (click)="chatService.toggleChat()" 
              title="Cerrar ventana">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>
        </div>

        <!-- Banner de Emergencia / Contención de Crisis (CU20 / HU-36) -->
        <div class="crisis-alert-banner" *ngIf="chatService.isCrisis()">
          <div class="crisis-banner-header">
            <i class="fa-solid fa-triangle-exclamation"></i>
            <strong>Contención Emocional Inmediata</strong>
          </div>
          <p class="crisis-banner-text">
            Si sientes que estás en peligro o necesitas apoyo urgente, estamos aquí para ti. Comunícate de inmediato y sin costo:
          </p>
          <div class="crisis-phone-pills">
            <a href="tel:800113040" class="phone-pill primary">
              <i class="fa-solid fa-phone"></i>
              <span>Línea de la Vida: <strong>800-11-3040</strong></span>
            </a>
            <a href="tel:911" class="phone-pill secondary">
              <i class="fa-solid fa-shield-heart"></i>
              <span>Emergencias: <strong>911</strong></span>
            </a>
          </div>
        </div>

        <!-- Mensajes Body -->
        <div class="chat-body" #scrollContainer>
          <div class="messages-list">
            <div 
              *ngFor="let msg of chatService.messages()" 
              class="message-row"
              [class.msg-user]="msg.remitente === 'USUARIO'"
              [class.msg-bot]="msg.remitente === 'BOT'"
              [class.msg-operator]="msg.remitente === 'OPERADOR'">

              <!-- Avatar Bot / Operador -->
              <div class="msg-avatar" *ngIf="msg.remitente !== 'USUARIO'">
                <span *ngIf="msg.remitente === 'BOT'">Ψ</span>
                <i *ngIf="msg.remitente === 'OPERADOR'" class="fa-solid fa-headset"></i>
              </div>

              <div class="msg-content-wrapper">
                <div class="msg-sender-label" *ngIf="msg.remitente === 'OPERADOR'">
                  Recepción Clínica
                </div>

                <div class="msg-bubble" [class.bubble-crisis]="msg.es_alerta_crisis">
                  <div class="msg-text">{{ msg.texto }}</div>
                </div>

                <!-- Opciones / Quick reply chips -->
                <div class="quick-options" *ngIf="msg.opciones_sugeridas && msg.opciones_sugeridas.length > 0">
                  <button 
                    *ngFor="let opt of msg.opciones_sugeridas" 
                    type="button" 
                    class="quick-pill"
                    (click)="seleccionarOpcion(opt)">
                    {{ opt }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Typing indicator -->
            <div class="typing-indicator" *ngIf="chatService.isLoading()">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>

        <!-- Footer / Input Form -->
        <div class="chat-footer">
          <form (submit)="enviar($event)" class="input-form">
            <input 
              type="text" 
              class="chat-input" 
              placeholder="Escribe tu consulta o duda..." 
              [(ngModel)]="mensajeInput" 
              name="mensajeInput"
              [disabled]="chatService.isLoading()"
              autocomplete="off" />
            
            <button 
              type="submit" 
              class="send-btn" 
              [disabled]="!mensajeInput.trim() || chatService.isLoading()"
              aria-label="Enviar mensaje">
              <i class="fa-solid fa-paper-plane"></i>
            </button>
          </form>

          <div class="ethical-disclaimer">
            Orientación confidencial SIGEPSI. En situaciones de riesgo vital, acude al centro de salud más cercano.
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .chatbot-launcher-container {
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 1050;
      font-family: inherit;
    }

    /* Botón flotante */
    .chatbot-launcher-btn {
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      width: 58px;
      height: 58px;
      border-radius: 50%;
      border: none;
      background: linear-gradient(135deg, #0d9488 0%, #0f766e 100%);
      color: #ffffff;
      font-size: 1.45rem;
      cursor: pointer;
      box-shadow: 0 10px 25px -5px rgba(13, 148, 136, 0.4), 0 8px 10px -6px rgba(13, 148, 136, 0.2);
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .chatbot-launcher-btn:hover {
      transform: translateY(-2px) scale(1.04);
      box-shadow: 0 14px 28px -5px rgba(13, 148, 136, 0.5);
    }

    .chatbot-launcher-btn.active {
      background: #0f172a;
      box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.4);
    }

    .chatbot-launcher-btn.has-crisis {
      background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
      animation: pulse-danger 2s infinite;
    }

    @keyframes pulse-danger {
      0% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.7); }
      70% { box-shadow: 0 0 0 14px rgba(220, 38, 38, 0); }
      100% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); }
    }

    .launcher-tooltip {
      position: absolute;
      right: 70px;
      white-space: nowrap;
      background: #0f172a;
      color: #f8fafc;
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 0.8rem;
      font-weight: 500;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.2s ease, transform 0.2s ease;
      transform: translateX(6px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .chatbot-launcher-btn:hover .launcher-tooltip {
      opacity: 1;
      transform: translateX(0);
    }

    .unread-badge {
      position: absolute;
      top: -4px;
      right: -4px;
      background: #ef4444;
      color: white;
      font-size: 0.75rem;
      font-weight: 700;
      width: 22px;
      height: 22px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 2px solid #ffffff;
    }

    /* Ventana del Chatbot */
    .chatbot-window {
      position: absolute;
      bottom: 74px;
      right: 0;
      width: 380px;
      max-width: calc(100vw - 32px);
      height: 560px;
      max-height: calc(100vh - 120px);
      background: #ffffff;
      border-radius: 20px;
      box-shadow: 0 20px 45px -10px rgba(15, 23, 42, 0.22), 0 0 0 1px rgba(15, 23, 42, 0.08);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      animation: slideUp 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes slideUp {
      from { opacity: 0; transform: translateY(16px) scale(0.97); }
      to { opacity: 1; transform: translateY(0) scale(1); }
    }

    /* Header */
    .chat-header {
      background: linear-gradient(135deg, #0d9488 0%, #0f766e 100%);
      color: #ffffff;
      padding: 16px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .header-info {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .avatar-ring {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.2);
      backdrop-filter: blur(4px);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.25rem;
      font-weight: 700;
      border: 1.5px solid rgba(255, 255, 255, 0.4);
    }

    .header-title {
      margin: 0;
      font-size: 1rem;
      font-weight: 700;
      line-height: 1.2;
    }

    .status-indicator {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.75rem;
      opacity: 0.9;
      margin-top: 2px;
    }

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #4ade80;
    }

    .status-dot.human {
      background: #fbbf24;
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .icon-btn {
      background: transparent;
      border: none;
      color: rgba(255, 255, 255, 0.85);
      width: 32px;
      height: 32px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-size: 0.95rem;
      transition: background 0.15s ease, color 0.15s ease;
    }

    .icon-btn:hover {
      background: rgba(255, 255, 255, 0.15);
      color: #ffffff;
    }

    /* Banner Crisis */
    .crisis-alert-banner {
      background: #fef2f2;
      border-bottom: 1px solid #fee2e2;
      padding: 12px 16px;
      color: #991b1b;
    }

    .crisis-banner-header {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.85rem;
      font-weight: 700;
      color: #b91c1c;
      margin-bottom: 4px;
    }

    .crisis-banner-text {
      margin: 0 0 10px 0;
      font-size: 0.78rem;
      line-height: 1.35;
      color: #7f1d1d;
    }

    .crisis-phone-pills {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .phone-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 0.8rem;
      text-decoration: none;
      font-weight: 500;
      transition: all 0.15s ease;
    }

    .phone-pill.primary {
      background: #dc2626;
      color: #ffffff;
    }

    .phone-pill.primary:hover {
      background: #b91c1c;
    }

    .phone-pill.secondary {
      background: #fee2e2;
      color: #991b1b;
      border: 1px solid #fca5a5;
    }

    .phone-pill.secondary:hover {
      background: #fecaca;
    }

    /* Chat Body */
    .chat-body {
      flex: 1;
      padding: 16px;
      overflow-y: auto;
      background: #f8fafc;
      scroll-behavior: smooth;
    }

    .messages-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .message-row {
      display: flex;
      gap: 10px;
      align-items: flex-start;
    }

    .msg-user {
      justify-content: flex-end;
    }

    .msg-avatar {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: #e2e8f0;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.85rem;
      font-weight: 700;
      color: #0f766e;
      flex-shrink: 0;
      margin-top: 2px;
    }

    .msg-operator .msg-avatar {
      background: #fef3c7;
      color: #b45309;
    }

    .msg-content-wrapper {
      max-width: 82%;
      display: flex;
      flex-direction: column;
    }

    .msg-user .msg-content-wrapper {
      align-items: flex-end;
    }

    .msg-sender-label {
      font-size: 0.72rem;
      color: #64748b;
      font-weight: 600;
      margin-bottom: 2px;
      padding-left: 2px;
    }

    .msg-bubble {
      padding: 10px 14px;
      border-radius: 14px;
      font-size: 0.88rem;
      line-height: 1.45;
      word-break: break-word;
      white-space: pre-line;
    }

    .msg-user .msg-bubble {
      background: #0d9488;
      color: #ffffff;
      border-bottom-right-radius: 4px;
    }

    .msg-bot .msg-bubble {
      background: #ffffff;
      color: #1e293b;
      border: 1px solid #e2e8f0;
      border-bottom-left-radius: 4px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }

    .msg-operator .msg-bubble {
      background: #fffbeb;
      color: #92400e;
      border: 1px solid #fde68a;
      border-bottom-left-radius: 4px;
    }

    .bubble-crisis {
      background: #fef2f2 !important;
      border-color: #fca5a5 !important;
      color: #7f1d1d !important;
    }

    /* Opciones rápidas */
    .quick-options {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 8px;
    }

    .quick-pill {
      background: #ffffff;
      border: 1px solid #ccfbf1;
      color: #0f766e;
      padding: 5px 10px;
      border-radius: 12px;
      font-size: 0.78rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.15s ease;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    }

    .quick-pill:hover {
      background: #f0fdfa;
      border-color: #5eead4;
      color: #115e59;
      transform: translateY(-1px);
    }

    /* Typing indicator */
    .typing-indicator {
      display: flex;
      align-items: center;
      gap: 5px;
      padding: 8px 14px;
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      width: fit-content;
      margin-left: 42px;
    }

    .typing-indicator span {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #94a3b8;
      animation: bounce 1.4s infinite ease-in-out both;
    }

    .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
    .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

    @keyframes bounce {
      0%, 80%, 100% { transform: scale(0); }
      40% { transform: scale(1); }
    }

    /* Footer */
    .chat-footer {
      padding: 12px 16px;
      background: #ffffff;
      border-top: 1px solid #f1f5f9;
    }

    .input-form {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .chat-input {
      flex: 1;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 10px 14px;
      font-size: 0.88rem;
      outline: none;
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
      background: #f8fafc;
    }

    .chat-input:focus {
      border-color: #0d9488;
      background: #ffffff;
      box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.12);
    }

    .send-btn {
      width: 40px;
      height: 40px;
      border-radius: 10px;
      border: none;
      background: #0d9488;
      color: #ffffff;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.95rem;
      transition: all 0.15s ease;
      flex-shrink: 0;
    }

    .send-btn:hover:not(:disabled) {
      background: #0f766e;
    }

    .send-btn:disabled {
      opacity: 0.45;
      cursor: not-allowed;
    }

    .ethical-disclaimer {
      font-size: 0.68rem;
      color: #94a3b8;
      text-align: center;
      margin-top: 8px;
      line-height: 1.25;
    }
  `]
})
export class ChatbotWidgetComponent implements AfterViewChecked {
  chatService = inject(ChatbotService);
  mensajeInput: string = '';

  @ViewChild('scrollContainer') private scrollContainer?: ElementRef;

  ngAfterViewChecked(): void {
    this.scrollToBottom();
  }

  private scrollToBottom(): void {
    if (this.scrollContainer) {
      try {
        this.scrollContainer.nativeElement.scrollTop = this.scrollContainer.nativeElement.scrollHeight;
      } catch (err) {}
    }
  }

  enviar(event: Event): void {
    event.preventDefault();
    const texto = this.mensajeInput.trim();
    if (!texto || this.chatService.isLoading()) return;

    this.mensajeInput = '';
    this.chatService.enviarMensaje(texto).subscribe();
  }

  seleccionarOpcion(opcion: string): void {
    if (this.chatService.isLoading()) return;
    this.chatService.enviarMensaje(opcion).subscribe();
  }

  solicitarAsesor(): void {
    this.chatService.solicitarHumano().subscribe();
  }
}
