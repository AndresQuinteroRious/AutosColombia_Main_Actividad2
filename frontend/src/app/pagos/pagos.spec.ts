import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { API_BASE_URL } from '../services/api.service';
import { Pagos } from './pagos';

describe('Pagos', () => {
  const emptyPage = { items: [], total: 0, offset: 0, limit: 10 };
  const tariffs = { automovil: 250000, motocicleta: 125000 };
  const available = { tiene_pago: false, pago_activo: false };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [Pagos],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: API_BASE_URL, useValue: '' },
      ],
    });
  });

  afterEach(() => {
    localStorage.removeItem('token_admin');
    localStorage.removeItem('rol_admin');
  });

  it('muestra las placas sin buscador y registra la tarifa del vehículo seleccionado', () => {
    const fixture = TestBed.createComponent(Pagos);
    const http = TestBed.inject(HttpTestingController);
    const page = fixture.componentInstance;
    http.expectOne('/pagos?offset=0&limit=10').flush(emptyPage);
    http.expectOne('/pagos/tarifas').flush(tariffs);

    page.newPayment();
    http.expectOne('/pagos/placas').flush([
      { id: 9, placa: 'ABC123', tipo: 'AUTOMOVIL', tarifa: 250000, ...available },
      { id: 1, placa: 'XYZ987', tipo: 'MOTOCICLETA', tarifa: 125000, ...available },
    ]);
    fixture.detectChanges();

    const root = fixture.nativeElement as HTMLElement;
    const plates = root.querySelector<HTMLSelectElement>('#vehiculo_id')!;
    expect(root.querySelector('input[type=search]')).toBeNull();
    expect(Array.from(plates.options).slice(1).map((option) => option.text)).toEqual([
      'ABC123',
      'XYZ987',
    ]);
    plates.selectedIndex = 1;
    plates.dispatchEvent(new Event('change'));
    fixture.detectChanges();
    expect(root.querySelector('#valor')?.textContent).toContain('250.000');
    const today = new Intl.DateTimeFormat('es-CO', {
      day: '2-digit', month: '2-digit', year: 'numeric', timeZone: 'America/Bogota',
    }).format(new Date());
    expect(root.querySelector<HTMLInputElement>('#fecha')?.value).toBe(today);
    page.save();

    const request = http.expectOne({ method: 'POST', url: '/pagos' });
    expect(request.request.body).toEqual({ valor: 250000, vehiculo_id: 9 });
    request.flush(
      { id: 5, valor: '250000.00', placa: 'ABC123', fecha: '2026-11-22T02:00:00Z', vehiculo_id: 9 },
      { status: 201, statusText: 'Created' },
    );
    http.expectOne('/pagos?offset=0&limit=10').flush(emptyPage);
    fixture.detectChanges();
    const confirmation = root.querySelector('[role="status"].success');
    expect(confirmation?.textContent).toContain('Pago registrado correctamente.');
    const details = confirmation?.querySelectorAll('dd');
    expect(details?.[0].textContent).toContain('250.000');
    expect(details?.[0].textContent).toContain('COP');
    expect(details?.[1].textContent).toBe('ABC123');
    expect(details?.[2].textContent).toBe('21/11/2026');
    http.verify();
  });

  it('avisa al seleccionar una placa con pago activo e impide registrarla otra vez', () => {
    const fixture = TestBed.createComponent(Pagos);
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/pagos?offset=0&limit=10').flush(emptyPage);
    http.expectOne('/pagos/tarifas').flush(tariffs);
    const page = fixture.componentInstance;
    page.newPayment();
    http.expectOne('/pagos/placas').flush([
      {
        id: 9, placa: 'ABC123', tipo: 'AUTOMOVIL', tarifa: 250000,
        tiene_pago: true, pago_activo: true,
      },
    ]);
    fixture.detectChanges();
    const root = fixture.nativeElement as HTMLElement;
    const plates = root.querySelector<HTMLSelectElement>('#vehiculo_id')!;
    plates.selectedIndex = 1;
    plates.dispatchEvent(new Event('change'));
    fixture.detectChanges();

    expect(root.querySelector('#placa-error.field-error')?.textContent).toContain('ya tiene un pago activo');
    page.plates.update((items) => items.map((item) => ({ ...item, pago_activo: false })));
    fixture.detectChanges();
    expect(root.querySelector('#placa-error.duplicate-payment-warning')?.textContent)
      .toContain('Esta placa ya tiene un pago registrado.');
    expect(root.querySelector<HTMLButtonElement>('button[type="submit"]')?.disabled).toBe(true);
    page.save();
    http.expectNone({ method: 'POST', url: '/pagos' });
    http.verify();
  });

  it('muestra los pagos con fecha de Colombia y sin acciones por fila', () => {
    const fixture = TestBed.createComponent(Pagos);
    const http = TestBed.inject(HttpTestingController);
    const payment = {
      id: 5, vehiculo_id: 9, placa: 'ABC123', valor: '125000.00', fecha: '2026-11-22T02:00:00Z',
    };
    http.expectOne('/pagos?offset=0&limit=10').flush({ ...emptyPage, items: [payment], total: 1 });
    http.expectOne('/pagos/tarifas').flush(tariffs);

    fixture.detectChanges();
    const root = fixture.nativeElement as HTMLElement;
    expect(root.querySelector('tbody')?.textContent).toContain('21/11/2026');
    expect(Array.from(root.querySelectorAll('thead th'), (cell) => cell.textContent?.trim()))
      .toEqual(['Valor', 'Placa', 'Fecha']);
    expect(root.querySelector('tbody button')).toBeNull();
    http.verify();
  });

  it('muestra las tarifas a empleados y reserva su edición para el administrador', () => {
    localStorage.setItem('token_admin', 'sesion-de-prueba');
    localStorage.setItem('rol_admin', 'EMPLEADO');
    const fixture = TestBed.createComponent(Pagos);
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/pagos?offset=0&limit=10').flush(emptyPage);
    http.expectOne('/pagos/tarifas').flush(tariffs);
    fixture.detectChanges();

    const root = fixture.nativeElement as HTMLElement;
    const section = root.querySelector('[aria-labelledby="tariffs-title"]')!;
    expect(section.textContent).toContain('250.000');
    expect(section.textContent).toContain('125.000');
    expect(section.querySelector('button')).toBeNull();
    fixture.componentInstance.editTariffs();
    expect(fixture.componentInstance.editingTariffs()).toBe(false);
    http.verify();
  });

  it('actualiza tarifas con sesión de administrador y aplica el valor a un pago abierto', () => {
    localStorage.setItem('token_admin', 'sesion-de-prueba');
    localStorage.setItem('rol_admin', 'ADMINISTRADOR');
    const fixture = TestBed.createComponent(Pagos);
    const page = fixture.componentInstance;
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/pagos?offset=0&limit=10').flush(emptyPage);
    http.expectOne('/pagos/tarifas').flush(tariffs);
    page.newPayment();
    http.expectOne('/pagos/placas').flush([
      { id: 9, placa: 'ABC123', tipo: 'AUTOMOVIL', tarifa: 250000, ...available },
    ]);
    page.form.controls.vehiculo_id.setValue(9);
    fixture.detectChanges();

    const root = fixture.nativeElement as HTMLElement;
    root.querySelector<HTMLButtonElement>('[aria-labelledby="tariffs-title"] button')!.click();
    page.tariffForm.controls.automovil.setValue(0);
    page.saveTariffs();
    http.expectNone({ method: 'PUT', url: '/pagos/tarifas' });

    page.tariffForm.controls.automovil.setValue(300000.25);
    page.saveTariffs();
    const request = http.expectOne({ method: 'PUT', url: '/pagos/tarifas' });
    expect(request.request.headers.get('Authorization')).toBe('Bearer sesion-de-prueba');
    expect(request.request.body).toEqual({ automovil: 300000.25, motocicleta: 125000 });
    request.flush(request.request.body);
    expect(page.selectedVehicle()?.tarifa).toBe(300000.25);
    expect(page.tariffsSuccess()).toContain('actualizadas');
    http.verify();
  });
});
