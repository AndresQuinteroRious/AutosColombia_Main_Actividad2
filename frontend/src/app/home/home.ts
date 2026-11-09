import { HttpErrorResponse } from '@angular/common/http';
import { Component, DestroyRef, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormBuilder, ReactiveFormsModule, ValidatorFn } from '@angular/forms';
import {
  EstanciasHistorialFiltros,
  EstanciaHistorialItem,
} from '../models/estancia';
import { ApiService } from '../services/api.service';
import { EstanciasService } from '../services/estancias.service';
import { NovedadesService } from '../services/novedades.service';
import {
  NovedadHistorialFiltros,
  NovedadHistorialItem,
  NovedadVehiculoCrear,
} from '../models/novedad';
import { Vehiculo } from '../models/vehiculo';
import { RolBadge } from '../shared/rol-badge/rol-badge';

const nonBlank: ValidatorFn = (control) =>
  typeof control.value === 'string' && control.value.trim() ? null : { required: true };

@Component({
  imports: [ReactiveFormsModule, RolBadge],
  selector: 'app-home',
  styleUrl: './home.css',
  templateUrl: './home.html',
})
export class Home {
  private readonly api = inject(ApiService);
  private readonly estanciasApi = inject(EstanciasService);
  private readonly novedadesApi = inject(NovedadesService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly fb = inject(FormBuilder);
  private historialRequest = 0;
  private historialNovedadesRequest = 0;

  protected readonly historialForm = this.fb.nonNullable.group({
    fecha_desde: '',
    fecha_hasta: '',
    placa: '',
  });
  protected readonly filtros = signal<EstanciasHistorialFiltros>({ estado: 'ABIERTAS' });
  protected readonly mostrandoAbiertasPorDefecto = signal(true);
  protected readonly registros = signal<EstanciaHistorialItem[]>([]);
  protected readonly total = signal(0);
  protected readonly offset = signal(0);
  protected readonly limit = 10;
  protected readonly loadingHistorial = signal(false);
  protected readonly consultado = signal(false);
  protected readonly errorHistorial = signal('');
  protected readonly errorFiltros = signal('');
  protected readonly pagina = computed(() => Math.floor(this.offset() / this.limit) + 1);
  protected readonly paginas = computed(() => Math.max(1, Math.ceil(this.total() / this.limit)));
  protected readonly isAuthenticated = this.api.isLoggedIn();
  protected readonly isAdmin = this.api.getRol() === 'ADMINISTRADOR';
  protected readonly vehiculosNovedad = signal<Vehiculo[]>([]);
  protected readonly loadingVehiculosNovedad = signal(false);
  protected readonly errorVehiculosNovedad = signal('');
  protected readonly novedadForm = this.fb.nonNullable.group({
    placa: this.fb.nonNullable.control('', nonBlank),
    descripcion: this.fb.nonNullable.control('', nonBlank),
  });
  protected readonly savingNovedad = signal(false);
  protected readonly errorNovedad = signal('');
  protected readonly successNovedad = signal('');
  protected readonly historialNovedadForm = this.fb.nonNullable.group({
    fecha_desde: '',
    fecha_hasta: '',
    placa: '',
  });
  protected readonly filtrosNovedad = signal<NovedadHistorialFiltros>({});
  protected readonly novedades = signal<NovedadHistorialItem[]>([]);
  protected readonly totalNovedades = signal(0);
  protected readonly offsetNovedades = signal(0);
  protected readonly loadingNovedades = signal(false);
  protected readonly consultadoNovedades = signal(false);
  protected readonly errorNovedades = signal('');
  protected readonly errorFiltrosNovedad = signal('');
  protected readonly limitNovedades = 10;
  protected readonly paginaNovedades = computed(
    () => Math.floor(this.offsetNovedades() / this.limitNovedades) + 1,
  );
  protected readonly paginasNovedades = computed(
    () => Math.max(1, Math.ceil(this.totalNovedades() / this.limitNovedades)),
  );

  constructor() {
    this.consultado.set(true);
    this.cargarHistorial(0);

    if (this.isAuthenticated) {
      this.loadingVehiculosNovedad.set(true);
      this.estanciasApi
        .vehiculos()
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe({
          next: (vehicles) => {
            this.vehiculosNovedad.set(vehicles);
            this.loadingVehiculosNovedad.set(false);
          },
          error: () => {
            this.errorVehiculosNovedad.set('No se pudieron cargar los vehículos registrados.');
            this.loadingVehiculosNovedad.set(false);
          },
        });
    }
    if (this.isAdmin) this.buscarNovedades();
  }

  registrarNovedad(): void {
    this.novedadForm.markAllAsTouched();
    this.errorNovedad.set('');
    this.successNovedad.set('');
    if (this.novedadForm.invalid || this.savingNovedad()) return;
    const form = this.novedadForm.getRawValue();
    const vehicle = this.vehiculosNovedad().find((item) => item.placa === form.placa);
    if (!vehicle) {
      this.errorNovedad.set('Selecciona un vehículo registrado.');
      return;
    }
    const data: NovedadVehiculoCrear = {
      vehiculo_id: vehicle.id,
      descripcion: form.descripcion.trim(),
    };
    this.savingNovedad.set(true);
    this.novedadesApi
      .createForVehicle(data)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (record) => {
          this.savingNovedad.set(false);
          this.novedadForm.reset();
          this.successNovedad.set(
            `Novedad #${record.id} registrada para ${record.placa ?? form.placa} el ${this.fecha(record.fecha)}.`,
          );
          if (this.isAdmin) {
            this.historialNovedadForm.reset();
            this.buscarNovedades();
          }
        },
        error: (error: HttpErrorResponse) => {
          this.savingNovedad.set(false);
          this.errorNovedad.set(
            typeof error.error?.detail === 'string'
              ? error.error.detail
              : 'No se pudo registrar la novedad. Intenta nuevamente.',
          );
        },
      });
  }

  buscarNovedades(): void {
    if (!this.isAdmin) return;
    const form = this.historialNovedadForm.getRawValue();
    if (form.fecha_desde && form.fecha_hasta && form.fecha_desde > form.fecha_hasta) {
      this.errorFiltrosNovedad.set('La fecha desde no puede ser posterior a la fecha hasta.');
      return;
    }
    this.errorFiltrosNovedad.set('');
    this.historialNovedadesRequest++;
    this.loadingNovedades.set(false);
    this.filtrosNovedad.set({
      fecha_desde: form.fecha_desde || undefined,
      fecha_hasta: form.fecha_hasta || undefined,
      placa: form.placa.trim().toUpperCase() || undefined,
    });
    this.offsetNovedades.set(0);
    this.consultadoNovedades.set(true);
    this.cargarNovedades(0);
  }

  limpiarFiltrosNovedad(): void {
    this.historialNovedadesRequest++;
    this.historialNovedadForm.reset();
    this.errorFiltrosNovedad.set('');
    this.filtrosNovedad.set({});
    this.offsetNovedades.set(0);
    this.consultadoNovedades.set(false);
    this.novedades.set([]);
    this.totalNovedades.set(0);
    this.errorNovedades.set('');
    this.loadingNovedades.set(false);
  }

  cargarNovedades(offset: number): void {
    if (!this.isAdmin || this.loadingNovedades()) return;
    const request = ++this.historialNovedadesRequest;
    this.loadingNovedades.set(true);
    this.errorNovedades.set('');
    this.novedadesApi
      .history(this.filtrosNovedad(), offset, this.limitNovedades)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (page) => {
          if (request !== this.historialNovedadesRequest) return;
          this.novedades.set(page.items);
          this.totalNovedades.set(page.total);
          this.offsetNovedades.set(page.offset);
          this.loadingNovedades.set(false);
        },
        error: (error: HttpErrorResponse) => {
          if (request !== this.historialNovedadesRequest) return;
          this.loadingNovedades.set(false);
          this.errorNovedades.set(
            typeof error.error?.detail === 'string'
              ? error.error.detail
              : 'No se pudo consultar el historial de novedades.',
          );
        },
      });
  }

  buscarHistorial(): void {
    const value = this.historialForm.getRawValue();
    if (value.fecha_desde && value.fecha_hasta && value.fecha_desde > value.fecha_hasta) {
      this.errorFiltros.set('La fecha desde no puede ser posterior a la fecha hasta.');
      return;
    }
    this.errorFiltros.set('');
    this.historialRequest++;
    this.loadingHistorial.set(false);
    this.filtros.set({
      fecha_desde: value.fecha_desde || undefined,
      fecha_hasta: value.fecha_hasta || undefined,
      placa: value.placa.trim().toUpperCase() || undefined,
    });
    this.mostrandoAbiertasPorDefecto.set(false);
    this.consultado.set(true);
    this.registros.set([]);
    this.total.set(0);
    this.offset.set(0);
    this.cargarHistorial(0);
  }

  limpiarFiltros(): void {
    this.historialRequest++;
    this.historialForm.reset();
    this.filtros.set({ estado: 'ABIERTAS' });
    this.mostrandoAbiertasPorDefecto.set(true);
    this.registros.set([]);
    this.total.set(0);
    this.offset.set(0);
    this.loadingHistorial.set(false);
    this.consultado.set(false);
    this.errorHistorial.set('');
    this.errorFiltros.set('');
    this.consultado.set(true);
    this.cargarHistorial(0);
  }

  cargarHistorial(offset = this.offset()): void {
    if (this.loadingHistorial()) return;
    const request = ++this.historialRequest;
    this.loadingHistorial.set(true);
    this.errorHistorial.set('');
    this.estanciasApi
      .historial(this.filtros(), offset, this.limit)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (page) => {
          if (request !== this.historialRequest) return;
          this.registros.set(page.items);
          this.total.set(page.total);
          this.offset.set(page.offset);
          this.loadingHistorial.set(false);
        },
        error: () => {
          if (request !== this.historialRequest) return;
          this.loadingHistorial.set(false);
          this.errorHistorial.set('No se pudo consultar el historial. Intenta nuevamente.');
        },
      });
  }

  fecha(value: string | null): string {
    if (!value) return '—';
    return new Intl.DateTimeFormat('es-CO', {
      timeZone: 'America/Bogota',
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date(value));
  }
}
