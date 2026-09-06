import { ReactiveFormsModule } from '@angular/forms';
import { provideHttpClient } from '@angular/common/http';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RoleFormComponent } from './role-form.component';

describe('RoleFormComponent', () => {
  let component: RoleFormComponent;
  let fixture: ComponentFixture<RoleFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReactiveFormsModule],
      providers: [provideHttpClient()],
      declarations: [RoleFormComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RoleFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
