import { NgModule } from '@angular/core';
import { SharedModule } from '../shared/shared.module';

import { AdminLayoutComponent } from './admin-layout/admin-layout.component';
import { PublicLayoutComponent } from './public-layout/public-layout.component';
import { PatientLayoutComponent } from './patient-layout/patient-layout.component';

const LAYOUTS = [AdminLayoutComponent, PublicLayoutComponent, PatientLayoutComponent];

@NgModule({
  declarations: LAYOUTS,
  imports: [SharedModule],
  exports: LAYOUTS,
})
export class LayoutsModule {}
