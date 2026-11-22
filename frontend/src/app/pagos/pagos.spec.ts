import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { API_BASE_URL } from '../services/api.service';
import { Pagos } from './pagos';

describe('Pagos', () => {
  it('muestra las placas y registra la tarifa seleccionada con el vehículo', () => {
    TestBed.configureTestingModule({
      imports: [Pagos],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: API_BASE_URL, useValue: '' },
      ],
    });
    const fixture = TestBed.createComponent(Pagos);
    const http = TestBed.inject(HttpTestingController);
    const page = fixture.componentInstance;
    const emptyPage = { items: [], total: 0, offset: 0, limit: 10 };
    http.expectOne('/pagos?offset=0&limit=10').flush(emptyPage);

    page.newPayment();
    http.expectOne('/pagos/placas').flush([
      { id: 9, placa: 'ABC123' },
      { id: 1, placa: 'XYZ987' },
    ]);
    fixture.detectChanges();

    const root = fixture.nativeElement as HTMLElement;
    const plates = root.querySelector<HTMLSelectElement>('#vehiculo_id')!;
    const tariffs = root.querySelector<HTMLSelectElement>('#valor')!;
    expect(Array.from(plates.options).slice(1).map((option) => option.text)).toEqual([
      'ABC123',
      'XYZ987',
    ]);
    expect(Array.from(tariffs.options).slice(1).map((option) => option.text)).toEqual([
      'Moto — $125.000 COP',
      'Automóvil — $250.000 COP',
    ]);
    plates.selectedIndex = 1;
    plates.dispatchEvent(new Event('change'));
    tariffs.selectedIndex = 2;
    tariffs.dispatchEvent(new Event('change'));
    page.form.controls.periodo.setValue('Noviembre');
    page.save();

    const request = http.expectOne({ method: 'POST', url: '/pagos' });
    expect(request.request.body).toEqual({ valor: 250000, periodo: 'Noviembre', vehiculo_id: 9 });
    request.flush({}, { status: 201, statusText: 'Created' });
    http.expectOne('/pagos?offset=0&limit=10').flush(emptyPage);
    expect(page.success()).toContain('registrado');
    http.verify();
  });
});
