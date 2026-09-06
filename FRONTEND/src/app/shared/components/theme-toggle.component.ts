import { Component } from '@angular/core';
import { ThemeService } from '../../core/services/theme.service';

@Component({
  selector: 'app-theme-toggle',
  standalone: false,
  template: `
    <button
      type="button"
      class="theme-toggle"
      (click)="theme.toggle()"
      [attr.aria-label]="theme.theme() === 'dark' ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'"
      [title]="theme.theme() === 'dark' ? 'Tema claro' : 'Tema oscuro'">
      <svg *ngIf="theme.theme() === 'light'" viewBox="0 0 24 24" fill="none" width="18" height="18">
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <svg *ngIf="theme.theme() === 'dark'" viewBox="0 0 24 24" fill="none" width="18" height="18">
        <circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="2"/>
        <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
    </button>
  `,
  styles: [
    `
      .theme-toggle {
        display: grid;
        place-items: center;
        width: 36px;
        height: 36px;
        border-radius: var(--radius-md);
        border: 1px solid var(--color-border);
        background: var(--color-surface);
        color: var(--color-text-secondary);
        cursor: pointer;
        transition: background var(--transition-fast), color var(--transition-fast);
      }
      .theme-toggle:hover {
        background: var(--color-surface-hover);
        color: var(--color-text);
      }
    `,
  ],
})
export class ThemeToggleComponent {
  constructor(public theme: ThemeService) {}
}
