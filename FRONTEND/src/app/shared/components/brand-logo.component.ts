import { booleanAttribute, Component, Input } from '@angular/core';

/**
 * Logo canónico de SIGEPSI: un único glyph (antorcha/psique) + wordmark.
 * `variant="mark"` solo el símbolo; `variant="full"` símbolo + "SIGEPSI".
 * El color se hereda con `currentColor` para funcionar en claro/oscuro/sidebar.
 */
@Component({
  selector: 'app-brand-logo',
  standalone: false,
  template: `
    <span class="brand" [class.brand--mono]="mono" [attr.data-size]="size">
      <span class="brand__badge">
        <svg viewBox="0 0 48 48" fill="none" aria-hidden="true">
          <path
            d="M24 6V42M24 42H16M24 42H32M10 14V22C10 29.732 16.268 36 24 36C31.732 36 38 29.732 38 22V14"
            stroke="currentColor" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round" />
          <circle cx="24" cy="12" r="3.2" fill="currentColor" />
        </svg>
      </span>
      <span class="brand__text" *ngIf="variant === 'full'">
        <span class="brand__name">SIGEPSI</span>
        <span class="brand__sub" *ngIf="showSub">Salud Mental</span>
      </span>
    </span>
  `,
  styleUrls: ['./brand-logo.component.css'],
})
export class BrandLogoComponent {
  @Input() variant: 'mark' | 'full' = 'full';
  @Input() size: 'sm' | 'md' | 'lg' = 'md';
  @Input({ transform: booleanAttribute }) mono = false;
  @Input({ transform: booleanAttribute }) showSub = false;
}
