import { NgModule } from '@angular/core';

import { SharedModule } from '../../shared/shared.module';
import { AuthRoutingModule } from './auth-routing.module';

import { LoginComponent } from './components/login/login.component';
import { PasswordResetComponent } from './components/password-reset/password-reset.component';
import { PasswordResetConfirmComponent } from './components/password-reset-confirm/password-reset-confirm.component';

@NgModule({
  declarations: [
    LoginComponent,
    PasswordResetComponent,
    PasswordResetConfirmComponent,
  ],
  imports: [SharedModule, AuthRoutingModule],
})
export class AuthModule {}
