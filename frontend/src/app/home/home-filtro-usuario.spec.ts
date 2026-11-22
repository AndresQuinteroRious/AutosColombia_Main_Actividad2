import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { Home } from './home';

describe('Filtro por usuario del historial', () => {
  afterEach(() => localStorage.clear());
  it('envía el nombre, conserva el filtro al paginar y lo elimina al limpiar', async () => {
    localStorage.clear();
    localStorage.setItem('token_admin', 'sesion-prueba');
    await TestBed.configureTestingModule({
      imports: [Home],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
    const http = TestBed.inject(HttpTestingController);
    const fixture = TestBed.createComponent(Home);
    fixture.detectChanges();
    const empty = { items: [], total: 20, offset: 0, limit: 10 };
    http.expectOne((r) => r.url === '/estancias/abiertas').flush([
      { id: 42, placa: 'ABC123', marca: 'Marca', modelo: 2026, color: 'Azul',
        tipo: 'MOTO', celda: 'A1', entrada: '2026-11-15T08:00:00Z', operador_entrada: 'Ana' },
    ]);
    http.expectOne((r) => r.url === '/usuarios/opciones-historial').flush([
      { id: 2, nombre: 'Ana', documento: 'DOC2' },
      { id: 1, nombre: 'Luis', documento: 'DOC1' },
    ]);
    fixture.detectChanges();
    http.expectOne((r) => r.url === '/estancias/historial').flush(empty);
    const element = fixture.nativeElement as HTMLElement;
    const input = element.querySelector<HTMLSelectElement>('#history-user')!;
    expect(Array.from(input.options).map((option) => option.text)).toEqual([
      'Todos los usuarios', 'Ana', 'Luis',
    ]);
    input.value = '2';
    input.dispatchEvent(new Event('change'));
    element.querySelector<HTMLFormElement>('.history-filters')!.dispatchEvent(new Event('submit'));
    const request = http.expectOne((r) => r.url === '/estancias/historial');
    expect(request.request.params.get('usuario_id')).toBe('2');
    request.flush(empty);
    fixture.componentInstance.cargarHistorial(10);
    const next = http.expectOne((r) => r.url === '/estancias/historial');
    expect(next.request.params.get('usuario_id')).toBe('2');
    expect(next.request.params.get('offset')).toBe('10');
    next.flush({ ...empty, offset: 10 });
    fixture.componentInstance.limpiarFiltros();
    const reset = http.expectOne((r) => r.url === '/estancias/historial');
    expect(reset.request.params.has('usuario_id')).toBe(false);
    expect(reset.request.params.get('estado')).toBe('ABIERTAS');
    reset.flush(empty);
    expect(input.value).toBe('');
    fixture.detectChanges();
    const plates = element.querySelector<HTMLSelectElement>('#novelty-plate')!;
    expect(Array.from(plates.options).map((option) => option.value)).toEqual(['', 'ABC123']);
    plates.value = 'ABC123';
    plates.dispatchEvent(new Event('change'));
    const description = element.querySelector<HTMLTextAreaElement>('#novelty-description')!;
    description.value = 'Espejo rayado';
    description.dispatchEvent(new Event('input'));
    fixture.componentInstance.registrarNovedad();
    const save = http.expectOne({ method: 'POST', url: '/novedades' });
    expect(save.request.body).toEqual({ id_estancia: 42, descripcion: 'Espejo rayado' });
    save.flush({ id: 7, id_estancia: 42, descripcion: 'Espejo rayado', fecha: '2026-11-15T09:00:00Z' });
    http.verify();
  });
});
