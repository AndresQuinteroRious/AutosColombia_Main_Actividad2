import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Celdas } from './celdas';

describe('Gestión de celdas', () => {
  let fixture: ComponentFixture<Celdas>;
  let http: HttpTestingController;
  const cell = { id: 1, codigo: 'A-01', tipo: 'AUTOMOVIL' } as const;
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

  it('crea desde el formulario HTML con código normalizado y tipo del catálogo', () => {
    fixture.componentInstance.newCell();
    fixture.detectChanges();
    const root = fixture.nativeElement as HTMLElement;
    const code = root.querySelector<HTMLInputElement>('#codigo')!;
    const type = root.querySelector<HTMLSelectElement>('#tipo')!;
    expect(Array.from(type.options, (option) => option.value)).toEqual([
      '', 'AUTOMOVIL', 'MOTOCICLETA',
    ]);
    code.value = ' a-02 ';
    code.dispatchEvent(new Event('input'));
    type.value = 'MOTOCICLETA';
    type.dispatchEvent(new Event('change'));
    root.querySelector('form')!.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
    const request = http.expectOne({ method: 'POST', url: '/celdas' });
    expect(request.request.body).toEqual({ codigo: 'A-02', tipo: 'MOTOCICLETA' });
    request.flush({ ...cell, codigo: 'A-02', tipo: 'MOTOCICLETA' });
    http
      .expectOne('/celdas?offset=0&limit=80')
      .flush({ items: [cell], total: 1, offset: 0, limit: 80 });
    expect(fixture.componentInstance.success()).toContain('registrada');
  });

  it('rechaza blancos y muestra duplicados junto al código', () => {
    const c = fixture.componentInstance;
    c.newCell();
    c.form.setValue({ codigo: ' ', tipo: '' });
    c.save();
    expect(c.form.invalid).toBe(true);
    c.form.setValue({ codigo: 'A-01', tipo: 'AUTOMOVIL' });
    c.save();
    http.expectOne('/celdas').flush({}, { status: 409, statusText: 'Conflict' });
    expect(c.fieldError('codigo')).toContain('Ya existe');
  });

  it('edita mediante PATCH y recarga la lista', () => {
    const c = fixture.componentInstance;
    c.edit(cell);
    http.expectOne('/celdas/1').flush(cell);
    c.form.controls.tipo.setValue('MOTOCICLETA');
    c.save();
    const request = http.expectOne({ method: 'PATCH', url: '/celdas/1' });
    expect(request.request.body.id).toBeUndefined();
    request.flush({ ...cell, tipo: 'MOTOCICLETA' });
    http
      .expectOne('/celdas?offset=0&limit=80')
      .flush({ items: [cell], total: 1, offset: 0, limit: 80 });
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
