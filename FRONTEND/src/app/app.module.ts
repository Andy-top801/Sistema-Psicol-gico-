import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { provideHttpClient, withInterceptors } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LayoutsModule } from './layouts/layouts.module';
import { authInterceptor } from './core/interceptors/auth.interceptor';
import { errorInterceptor } from './core/interceptors/error.interceptor';

@NgModule({
  declarations: [AppComponent],
  imports: [BrowserModule, LayoutsModule, AppRoutingModule],
  providers: [
    provideHttpClient(withInterceptors([authInterceptor, errorInterceptor])),
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}
