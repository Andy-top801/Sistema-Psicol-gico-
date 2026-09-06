import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { BrandLogoComponent } from './components/brand-logo.component';
import { ThemeToggleComponent } from './components/theme-toggle.component';
import { NavIconComponent } from './components/nav-icon.component';
import { PageHeaderComponent } from './components/page-header.component';
import { EmptyStateComponent } from './components/empty-state.component';

const COMPONENTS = [
  BrandLogoComponent,
  ThemeToggleComponent,
  NavIconComponent,
  PageHeaderComponent,
  EmptyStateComponent,
];

@NgModule({
  declarations: COMPONENTS,
  imports: [CommonModule, RouterModule, FormsModule, ReactiveFormsModule],
  exports: [
    CommonModule,
    RouterModule,
    FormsModule,
    ReactiveFormsModule,
    ...COMPONENTS,
  ],
})
export class SharedModule {}
