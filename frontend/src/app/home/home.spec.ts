import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Home as App } from './home';

describe('App', () => {
  let fixture: ComponentFixture<App>;
  let http: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
    http = TestBed.inject(HttpTestingController);
    fixture = TestBed.createComponent(App);
    fixture.detectChanges();
  });

  afterEach(() => http.verify());

  function flushAll(options: { health?: object; abiertas?: object } = {}) {
    http.match({ method: 'GET', url: '/health' }).forEach((r) =>
      r.flush(options.health ?? { status: 'ok' }),
    );
    http.match({ method: 'GET', url: '/estancias/abiertas' }).forEach((r) =>
      r.flush(options.abiertas ?? []),
    );
  }

  function statusText() {
    fixture.detectChanges();
    return (fixture.nativeElement as HTMLElement)
      .querySelector('[role="status"]')
      ?.textContent?.trim();
  }

  it('muestra el nombre y la descripción de Autos Colombia', () => {
    const element = fixture.nativeElement as HTMLElement;
    expect(element.querySelector('h1')?.textContent).toBe('Autos Colombia');
    expect(element.querySelector('.description')?.textContent).toBe(
      'Control de entradas y salidas de vehículos',
    );
    flushAll();
  });

  it('muestra el estado de comprobación mientras espera la respuesta', () => {
    expect(statusText()).toContain('Comprobando conexión');
    flushAll();
  });

  it('muestra el servicio disponible cuando la API responde ok', () => {
    flushAll({ health: { status: 'ok' } });
    expect(statusText()).toBe('Servicio disponible');
  });

  it('muestra el error cuando el servidor falla', () => {
    http.match({ method: 'GET', url: '/health' }).forEach((r) =>
      r.flush({}, { status: 503, statusText: 'Service Unavailable' }),
    );
    http.match({ method: 'GET', url: '/estancias/abiertas' }).forEach((r) =>
      r.flush([]),
    );
    expect(statusText()).toBe('No se pudo conectar con el servicio');
  });

  it('muestra el error cuando no hay conexión de red', () => {
    http.match({ method: 'GET', url: '/health' }).forEach((r) =>
      r.error(new ProgressEvent('error')),
    );
    http.match({ method: 'GET', url: '/estancias/abiertas' }).forEach((r) =>
      r.flush([]),
    );
    expect(statusText()).toBe('No se pudo conectar con el servicio');
  });

  it('no considera disponible una respuesta inesperada', () => {
    http.match({ method: 'GET', url: '/health' }).forEach((r) => r.flush(null));
    http.match({ method: 'GET', url: '/estancias/abiertas' }).forEach((r) =>
      r.flush([]),
    );
    expect(statusText()).toBe('No se pudo conectar con el servicio');
  });

  it('muestra las estancias abiertas con vehículo, celda e ingreso', () => {
    flushAll({
      abiertas: [
        {
          id: 8,
          vehiculo_id: 3,
          celda_id: 2,
          entrada: '2026-11-04T12:30:00Z',
          salida: null,
          operador_entrada_id: 5,
          operador_salida_id: null,
          vehiculo: {
            id: 3,
            placa: 'ABC123',
            color: 'rojo',
            modelo: 2022,
            marca: 'Toyota',
            tipo: 'AUTOMOVIL',
          },
          celda: { id: 2, codigo: 'A-02', tipo: 'AUTOMOVIL' },
        },
      ],
    });
    fixture.detectChanges();

    const element = fixture.nativeElement as HTMLElement;
    expect(element.querySelector('.estancias-grid')?.textContent).toContain('ABC123');
    expect(element.querySelector('.estancias-grid')?.textContent).toContain('A-02');
    expect(element.querySelector('.estancias-grid')?.textContent).toContain('Toyota 2022');
  });

  it('indica cuando no hay estancias abiertas', () => {
    flushAll();
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('No hay vehículos dentro del parqueadero.');
  });
});
