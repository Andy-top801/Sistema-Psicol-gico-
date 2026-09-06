import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-page-header',
  standalone: false,
  template: `
    <header class="page-header">
      <div class="page-header__text">
        <p class="page-header__eyebrow" *ngIf="eyebrow">{{ eyebrow }}</p>
        <h1 class="page-header__title">{{ title }}</h1>
        <p class="page-header__desc" *ngIf="subtitle">{{ subtitle }}</p>
      </div>
      <div class="page-header__actions">
        <ng-content select="[actions]"></ng-content>
      </div>
    </header>
  `,
  styles: [
    `
      .page-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: var(--space-4);
        flex-wrap: wrap;
        margin-bottom: var(--space-6);
      }
      .page-header__eyebrow {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: var(--color-primary);
        margin: 0 0 var(--space-2);
      }
      .page-header__title {
        font-family: var(--font-heading);
        font-size: var(--font-size-2xl);
        font-weight: 800;
        color: var(--color-text);
        margin: 0;
      }
      .page-header__desc {
        color: var(--color-text-secondary);
        margin: var(--space-2) 0 0;
        max-width: 60ch;
      }
      .page-header__actions {
        display: flex;
        gap: var(--space-2);
        flex-shrink: 0;
      }
    `,
  ],
})
export class PageHeaderComponent {
  @Input() title = '';
  @Input() subtitle = '';
  @Input() eyebrow = '';
}
