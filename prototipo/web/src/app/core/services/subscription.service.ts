// ==============================================================================
// MÓDULO: subscription.service.ts
// DESCRIPCIÓN: Servicio Angular para comunicación con la API de suscripciones.
//              Gestiona planes, checkout con Stripe y verificación de pagos.
// PUNTO 7+8: Modelo SaaS en la nube — Web/Móvil con pasarela de pagos Stripe
// ==============================================================================
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Plan, CheckoutResponse, VerifyResponse } from '../models';

@Injectable({
  providedIn: 'root'
})
export class SubscriptionService {
  private apiUrl = `${environment.apiUrl}/subscriptions`;

  constructor(private http: HttpClient) {}

  /**
   * Obtiene la lista de planes de suscripción disponibles.
   */
  getPlans(): Observable<Plan[]> {
    return this.http.get<Plan[]>(`${this.apiUrl}/plans/`);
  }

  /**
   * Crea una sesión de Stripe Checkout para el plan seleccionado.
   * Retorna la URL de checkout para redirigir al usuario.
   */
  createCheckout(data: {
    plan: string;
    email: string;
    nombre_centro: string;
    nombre_admin?: string;
  }): Observable<CheckoutResponse> {
    return this.http.post<CheckoutResponse>(`${this.apiUrl}/create-checkout/`, data);
  }

  /**
   * Verifica la sesión de pago de Stripe y dispara la creación del tenant.
   * Se llama desde la página de checkout-success con el session_id.
   */
  verifySession(sessionId: string): Observable<VerifyResponse> {
    return this.http.post<VerifyResponse>(`${this.apiUrl}/verify-session/`, {
      session_id: sessionId
    });
  }

  /**
   * Fuerza el cambio de contraseña del usuario autenticado.
   */
  forceChangePassword(data: {
    current_password: string;
    new_password: string;
    new_password_confirm: string;
  }): Observable<any> {
    return this.http.post(`${environment.apiUrl}/auth/force-change-password/`, data);
  }
}
