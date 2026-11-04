import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Celda } from '../models/celda';
import { Celdas } from './celdas';

describe('Gestión de celdas', () => {
  let fixture: ComponentFixture<Celdas>;
  let http: HttpTestingController;
  const cell: Celda = { id: 1, codigo: 'A-01', tipo: 'MOTO' };
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Celdas],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
    http = TestBed.inject(HttpTestingController);
    fixture = TestBed.createComponent(Celdas);
    fixture.detectChanges();
    http
      .expectOne('/celdas?offset=0&limit=80')
      .flush({ items: [cell], total: 1, offset: 0, limit: 80 });
  });
  afterEach(() => http.verify());

  it('crea desde el formulario HTML con código normalizado y tipo válido', () => {
    fixture.componentInstance.newCell();
    fixture.detectChanges();
    const root = fixture.nativeElement as HTMLElement;
    for (const [id, value] of Object.entries({
      codigo: ' a-02 ',
      tipo: 'MOTO',
    })) {
      if (id === 'tipo') {
        const select = root.querySelector<HTMLSelectElement>(`#${id}`)!;
        select.value = value;
        select.dispatchEvent(new Event('change', { bubbles: true }));
      } else {
        const input = root.querySelector<HTMLInputElement>(`#${id}`)!;
        input.value = value;
        input.dispatchEvent(new Event('input', { bubbles: true }));
      }
    }
    root
      .querySelector('form')!
      .dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
    fixture.componentInstance.save();
    const request = http.expectOne({ method: 'POST', url: '/celdas' });
    expect(request.request.body).toEqual({ codigo: 'A-02', tipo: 'MOTO' });
    request.flush({ ...cell, codigo: 'A-02' });
    http
      .expectOne('/celdas?offset=0&limit=80')
      .flush({ items: [cell], total: 1, offset: 0, limit: 80 });
    expect(fixture.componentInstance.success()).toContain('registrada');
  });

  it('rechaza blancos y muestra duplicados junto al código', () => {
    const c = fixture.componentInstance;
    c.newCell();
    c.form.controls.codigo.setValue(' ');
    c.save();
    expect(c.form.invalid).toBe(true);
    c.form.setValue({ codigo: 'A-01', tipo: 'MOTO' });
    c.save();
    http.expectOne('/celdas').flush({}, { status: 409, statusText: 'Conflict' });
    expect(c.fieldError('codigo')).toContain('Ya existe');
  });

  it('edita mediante PATCH y recarga la lista', () => {
    const c = fixture.componentInstance;
    c.edit(cell);
    http.expectOne('/celdas/1').flush(cell);
    c.form.controls.tipo.setValue('OTRO');
    c.save();
    const request = http.expectOne({ method: 'PATCH', url: '/celdas/1' });
    expect(request.request.body.id).toBeUndefined();
    request.flush({ ...cell, tipo: 'OTRO' });
    http
      .expectOne('/celdas?offset=0&limit=80')
      .flush({ items: [cell], total: 1, offset: 0, limit: 80 });
  });

  it('muestra el historial de estancias de una celda', () => {
    const c = fixture.componentInstance;
    c.verHistorial(cell);
    const request = http.expectOne(
      (req) => req.url === '/estancias/historial' && req.params.get('celda_id') === '1',
    );
    request.flush({
      items: [
        {
          id: 8,
          vehiculo_id: 3,
          celda_id: 1,
          entrada: '2026-10-19T15:00:00Z',
          salida: '2026-10-19T16:00:00Z',
          operador_entrada_id: 4,
          operador_salida_id: 4,
          vehiculo: {
            id: 3,
            placa: 'ABC123',
            color: 'azul',
            modelo: 2022,
            marca: 'Toyota',
            tipo: 'AUTOMOVIL',
          },
          celda: cell,
        },
      ],
      total: 1,
      offset: 0,
      limit: 10,
    });
    fixture.detectChanges();

    const history = fixture.nativeElement.textContent;
    expect(history).toContain('Historial de estancias · A-01');
    expect(history).toContain('ABC123');
  });

  it('requiere confirmación y permite cancelar antes de eliminar', () => {
    const c = fixture.componentInstance;
    c.confirmDelete(cell);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('[role="alertdialog"]').textContent).toContain(
      'A-01',
    );
    c.cancel();
    http.expectNone((request) => request.method === 'DELETE');
    c.confirmDelete(cell);
    c.remove();
    http
      .expectOne({ method: 'DELETE', url: '/celdas/1' })
      .flush(null, { status: 204, statusText: 'No Content' });
    http
      .expectOne('/celdas?offset=0&limit=80')
      .flush({ items: [], total: 0, offset: 0, limit: 80 });
    expect(c.success()).toContain('eliminada');
  });
});
