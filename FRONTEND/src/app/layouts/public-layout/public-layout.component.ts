import { Component } from '@angular/core';
import { TenantContextService } from '../../core/services/tenant-context.service';

@Component({
  selector: 'app-public-layout',
  standalone: false,
  templateUrl: './public-layout.component.html',
  styleUrls: ['./public-layout.component.css'],
})
export class PublicLayoutComponent {
  isPublicDomain: boolean;
  centerName: string;

  constructor(tenant: TenantContextService) {
    this.isPublicDomain = tenant.isPublicDomain;
    this.centerName = tenant.prettyName;
  }
}
