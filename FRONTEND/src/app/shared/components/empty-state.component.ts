import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-empty-state',
  standalone: false,
  template: `
    <div class="empty-state">
      <div class="empty-state__icon">
        <svg viewBox="0 0 24 24" fill="none" width="28" height="28">
          <path d="M4 7h16M4 7l1 12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2l1-12M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"
            stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <h3 class="empty-state__title">{{ title }}</h3>
      <p class="empty-state__msg" *ngIf="message">{{ message }}</p>
      <div class="empty-state__action"><ng-content select="[action]"></ng-content></div>
    </div>
  `,
  styles: [
    `
      .empty-state {
        text-align: center;
        padding: var(--space-10) var(--space-4);
        color: var(--color-text-secondary);
      }
      .empty-state__icon {
        display: inline-grid;
        place-items: center;
        width: 56px;
        height: 56px;
        border-radius: var(--radius-lg);
        background: var(--color-surface-2);
        color: var(--color-text-muted);
        margin-bottom: var(--space-3);
      }
      .empty-state__title {
        font-size: var(--font-size-lg);
        font-weight: 700;
        color: var(--color-text);
        margin: 0 0 var(--space-1);
      }
      .empty-state__msg {
        margin: 0 auto;
        max-width: 42ch;
      }
      .empty-state__action {
        margin-top: var(--space-4);
      }
    `,
  ],
})
export class EmptyStateComponent {
  @Input() title = 'Sin datos';
  @Input() message = '';
}
