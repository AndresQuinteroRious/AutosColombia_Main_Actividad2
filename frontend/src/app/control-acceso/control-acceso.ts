import { HttpErrorResponse } from '@angular/common/http';
import { Component, DestroyRef, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormBuilder, ReactiveFormsModule, ValidatorFn, Validators } from '@angular/forms';
import { catchError, forkJoin, of } from 'rxjs';
import { Celda } from '../models/celda';
import { Operador } from '../models/operador';
import { EstadoVehiculo } from '../models/estancia';
import { Vehiculo } from '../models/vehiculo';
import { EstanciasService } from '../services/estancias.service';
import { RolBadge } from '../shared/rol-badge/rol-badge';

const nonBlank: ValidatorFn = (c) =>
  typeof c.value === 'string' && c.value.trim() ? null : { required: true };
const placa = (value: string) => value.trim().toUpperCase();

@Component({
  selector: 'app-control-acceso',
  imports: [ReactiveFormsModule, RolBadge],
  templateUrl: './control-acceso.html',
  styleUrl: './control-acceso.css',
})
export class ControlAcceso {
  private readonly api = inject(EstanciasService);
  private readonly fb = inject(FormBuilder);
  private readonly destroy = inject(DestroyRef);
  private version = 0;
  readonly entrada = this.fb.group({
    placa: this.fb.nonNullable.control('', nonBlank),
    celda_id: this.fb.control<number | null>(null, Validators.required),
    operador_id: this.fb.control<number | null>(null, Validators.required),
  });
  readonly consulta = this.fb.group({
    placa: this.fb.nonNullable.control('', nonBlank),
    operador_id: this.fb.control<number | null>(null, Validators.required),
  });
  readonly celdas = signal<Celda[]>([]);
  readonly vehiculos = signal<Vehiculo[]>([]);
  readonly operadores = signal<Operador[]>([]);
  readonly operadorEntrada = signal<Operador | null>(null);
  readonly catalogLoading = signal(false);
  readonly catalogError = signal('');
  readonly operatorError = signal('');
  readonly saving = signal(false);
  readonly querying = signal(false);
  readonly busy = computed(() => this.saving() || this.querying());
  readonly estado = signal<EstadoVehiculo | null>(null);
  readonly errorEntrada = signal('');
  readonly errorConsulta = signal('');
  readonly exitoEntrada = signal('');
  readonly exitoSalida = signal('');

  constructor() {
    this.consulta.controls.placa.valueChanges
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe(() => {
        this.version++;
        this.estado.set(null);
        this.errorConsulta.set('');
        this.exitoSalida.set('');
      });
    this.cargarCatalogos();
  }

  cargarCatalogos(): void {
    if (this.catalogLoading() || this.saving()) return;
    this.catalogLoading.set(true);
    this.catalogError.set('');
    this.operatorError.set('');
    this.entrada.controls.celda_id.reset();
    this.entrada.controls.operador_id.reset();
    this.consulta.controls.operador_id.reset();
    forkJoin({
      celdas: this.api.celdasDisponibles(),
      vehiculos: this.api.vehiculos(),
      operadores: this.api.operadores(),
      operadorEntrada: this.api.operadorActual().pipe(
        catchError((error: HttpErrorResponse) => {
          this.operatorError.set(error.status === 404
            ? 'No se encontró un operador asociado al usuario que inició sesión. Solicita que vinculen tu documento con un operador.'
            : 'No se pudo identificar al operador de la sesión. Vuelve a cargar los catálogos.'
          );
          return of(null);
        }),
      ),
    })
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe({
        next: (data) => {
          this.celdas.set(data.celdas);
          this.vehiculos.set(data.vehiculos);
          this.operadores.set(data.operadores);
          this.operadorEntrada.set(data.operadorEntrada);
          this.entrada.controls.operador_id.setValue(data.operadorEntrada?.id ?? null);
          this.catalogLoading.set(false);
        },
        error: (error: HttpErrorResponse) => {
          this.catalogLoading.set(false);
          this.celdas.set([]);
          this.vehiculos.set([]);
          this.operadores.set([]);
          this.operadorEntrada.set(null);
          this.catalogError.set('No se pudieron cargar todas las opciones. Reintenta actualizar catálogos.');
        },
      });
  }

  registrarEntrada(): void {
    if (this.busy() || this.catalogLoading() || this.catalogError()) return;
    this.entrada.markAllAsTouched();
    const operador = this.operadorEntrada();
    if (!operador) {
      this.errorEntrada.set(this.operatorError());
      return;
    }
    if (this.entrada.invalid) return;
    const raw = this.entrada.getRawValue();
    const data = {
      placa: placa(raw.placa),
      celda_id: raw.celda_id!,
      operador_id: operador.id,
    };
    const codigo =
      this.celdas().find((c) => c.id === data.celda_id)?.codigo ?? String(data.celda_id);
    this.entrada.controls.placa.setValue(data.placa);
    this.saving.set(true);
    this.errorEntrada.set('');
    this.exitoEntrada.set('');
    this.version++;
    this.estado.set(null);
    this.api
      .entrada(data)
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe({
        next: (result) => {
          this.saving.set(false);
          this.exitoEntrada.set(
            `Entrada registrada: ${data.placa}, celda ${codigo}, ${this.fecha(result.entrada)}.`,
          );
          this.cargarCatalogos();
        },
        error: (error) => {
          this.saving.set(false);
          this.errorEntrada.set(this.mensaje(error));
        },
      });
  }

  buscar(): void {
    if (this.busy()) return;
    this.consulta.controls.placa.markAsTouched();
    if (this.consulta.controls.placa.invalid) return;
    const value = placa(this.consulta.controls.placa.value);
    this.consulta.controls.placa.setValue(value, { emitEvent: false });
    const version = ++this.version;
    this.estado.set(null);
    this.errorConsulta.set('');
    this.querying.set(true);
    this.api
      .consultar(value)
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe({
        next: (result) => {
          this.querying.set(false);
          if (version === this.version) this.estado.set(result);
        },
        error: (error) => {
          this.querying.set(false);
          if (version === this.version)
            this.errorConsulta.set(
              error.status === 404 ? 'Vehículo no registrado.' : this.mensaje(error),
            );
        },
      });
  }

  registrarSalida(): void {
    if (this.busy() || this.catalogLoading() || this.catalogError()) return;
    this.consulta.markAllAsTouched();
    const state = this.estado();
    const value = placa(this.consulta.controls.placa.value);
    if (
      this.consulta.invalid ||
      !state?.estancia ||
      !state.esta_dentro ||
      state.vehiculo.placa !== value
    )
      return;
    const version = this.version;
    this.saving.set(true);
    this.errorConsulta.set('');
    this.exitoSalida.set('');
    this.api
      .salida({ placa: value, operador_id: this.consulta.controls.operador_id.value! })
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe({
        next: (result) => {
          this.saving.set(false);
          this.estado.set(null);
          if (version !== this.version) return;
          this.exitoSalida.set(
            `Salida registrada: ${value}, celda ${state.estancia!.celda.codigo}, ${this.fecha(result.salida!)}.`,
          );
          this.cargarCatalogos();
          this.buscar();
        },
        error: (error) => {
          this.saving.set(false);
          this.estado.set(null);
          if (version === this.version)
            this.errorConsulta.set(
              this.mensaje(error) + ' Consulta nuevamente antes de confirmar otra salida.',
            );
        },
      });
  }

  fecha(value: string): string {
    return (
      new Intl.DateTimeFormat('es-CO', {
        timeZone: 'America/Bogota',
        dateStyle: 'medium',
        timeStyle: 'medium',
      }).format(new Date(value)) + ' (Bogotá)'
    );
  }

  private mensaje(error: HttpErrorResponse): string {
    if ([404, 409].includes(error.status) && typeof error.error?.detail === 'string')
      return error.error.detail;
    if (error.status === 422)
      return 'Datos inválidos. Revisa la placa y selecciona una celda y un operador válidos según la operación.';
    return 'No se pudo conectar con el servicio. Consulta el vehículo antes de reintentar: la operación podría haberse completado.';
  }
}
