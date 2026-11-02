import { TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';
import { App } from './app';
import { accessGuard } from './auth/admin.guard';
import { ApiService } from './services/api.service';

describe('Navegación', () => {
  it('muestra acceso al inicio de sesión', async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [provideRouter([])],
    }).compileComponents();
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();
    expect((fixture.nativeElement as HTMLElement).querySelector('a[href="/login"]')?.textContent).toContain(
      'Iniciar sesión',
    );
  });

  it('ofrece acceso a la gestión de vehículos', async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [provideRouter([])],
    }).compileComponents();
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();
    expect(
      (fixture.nativeElement as HTMLElement).querySelector('a[href="/gestion/vehiculos"]')
        ?.textContent,
    ).toBe('Vehículos');
  });

  it('bloquea el acceso al control de acceso para administradores', () => {
    const api = jasmine.createSpyObj<ApiService>('ApiService', ['isLoggedIn', 'getRol']);
    api.isLoggedIn.and.returnValue(true);
    api.getRol.and.returnValue('ADMINISTRADOR');

    const router = jasmine.createSpyObj<Router>('Router', ['navigate']);

    TestBed.configureTestingModule({
      providers: [
        { provide: ApiService, useValue: api },
        { provide: Router, useValue: router },
      ],
    });

    const result = TestBed.runInInjectionContext(() => accessGuard({} as any, {} as any));

    expect(result).toBeFalse();
    expect(router.navigate).toHaveBeenCalledWith(['/']);
  });
});
