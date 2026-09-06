import { Injectable, signal } from '@angular/core';

export type ThemeMode = 'light' | 'dark';

/**
 * Tema de la aplicación: claro por defecto, con toggle a oscuro.
 * Persiste la elección en localStorage y respeta `prefers-color-scheme`
 * cuando el usuario no ha elegido nada. Aplica `data-theme` en <html>.
 */
@Injectable({ providedIn: 'root' })
export class ThemeService {
  private readonly KEY = 'sigepsi_theme';
  private readonly _theme = signal<ThemeMode>(this.initial());
  readonly theme = this._theme.asReadonly();

  private initial(): ThemeMode {
    try {
      const saved = localStorage.getItem(this.KEY) as ThemeMode | null;
      if (saved === 'light' || saved === 'dark') return saved;
    } catch {
      /* storage no disponible */
    }
    return window.matchMedia?.('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light';
  }

  /** Llamar una vez al arrancar la app. */
  init(): void {
    this.apply(this._theme());
  }

  toggle(): void {
    this.set(this._theme() === 'dark' ? 'light' : 'dark');
  }

  set(mode: ThemeMode): void {
    this._theme.set(mode);
    try {
      localStorage.setItem(this.KEY, mode);
    } catch {
      /* ignore */
    }
    this.apply(mode);
  }

  private apply(mode: ThemeMode): void {
    document.documentElement.dataset['theme'] = mode;
  }
}
