import { HttpErrorResponse } from '@angular/common/http';
import { Component, DestroyRef, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormBuilder, ReactiveFormsModule, ValidatorFn, Validators } from '@angular/forms';
import { PagosService } from '../services/pagos.service';
import { Pago, PagoCrear, PlacaPago } from '../models/pago';
import { ErrorApi } from '../models/vehiculo';
import { RolBadge } from '../shared/rol-badge/rol-badge';

const nonBlank: ValidatorFn = (control) =>
  typeof control.value === 'string' && control.value.trim() ? null : { required: true };
const positiveValue: ValidatorFn = (control) => {
  const value = Number(control.value);
  return value > 0 ? null : { positive: true };
};
type Field = keyof PagoCrear;

@Component({
  selector: 'app-pagos',
  imports: [ReactiveFormsModule, RolBadge],
  templateUrl: './pagos.html',
  styleUrl: './pagos.css',
})
export class Pagos {
  private readonly api = inject(PagosService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly fb = inject(FormBuilder);
  readonly tariffs = [
    { value: 125000, label: 'Moto — $125.000 COP' },
    { value: 250000, label: 'Automóvil — $250.000 COP' },
  ];
  readonly form = this.fb.group({
    valor: this.fb.control<number | null>(null, [Validators.required, positiveValue]),
    periodo: this.fb.nonNullable.control('', nonBlank),
    vehiculo_id: this.fb.control<number | null>(null),
  });
  readonly plates = signal<PlacaPago[]>([]);
  readonly loadingPlates = signal(false);
  readonly platesError = signal('');
  readonly legacyPayment = signal(false);
  readonly items = signal<Pago[]>([]);
  readonly total = signal(0);
  readonly offset = signal(0);
  readonly limit = 10;
  readonly loading = signal(false);
  readonly saving = signal(false);
  readonly busy = computed(() => this.loading() || this.saving());
  readonly showForm = signal(false);
  readonly editing = signal<number | null>(null);
  readonly pendingDelete = signal<Pago | null>(null);
  readonly listError = signal('');
  readonly actionError = signal('');
  readonly success = signal('');
  readonly page = computed(() => Math.floor(this.offset() / this.limit) + 1);
  readonly pages = computed(() => Math.max(1, Math.ceil(this.total() / this.limit)));

  constructor() {
    this.load();
  }

  load(offset = this.offset()): void {
    if (this.busy()) return;
    this.loading.set(true);
    this.listError.set('');
    this.api
      .list(offset, this.limit)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (data) => {
          this.loading.set(false);
          if (offset > 0 && offset >= data.total) {
            this.load(Math.max(0, Math.floor((data.total - 1) / this.limit) * this.limit));
            return;
          }
          this.items.set(data.items);
          this.total.set(data.total);
          this.offset.set(offset);
        },
        error: (error) => {
          this.loading.set(false);
          this.listError.set(this.errorMessage(error));
        },
      });
  }

  newPayment(): void {
    if (this.busy()) return;
    this.form.reset();
    this.legacyPayment.set(false);
    this.form.controls.vehiculo_id.setValidators(Validators.required);
    this.form.controls.vehiculo_id.updateValueAndValidity();
    this.editing.set(null);
    this.showForm.set(true);
    this.pendingDelete.set(null);
    this.actionError.set('');
    this.success.set('');
    this.loadPlates();
  }

  loadPlates(): void {
    if (this.loadingPlates()) return;
    this.plates.set([]);
    this.platesError.set('');
    this.loadingPlates.set(true);
    this.api.listPlates().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (plates) => {
        this.plates.set(plates);
        this.loadingPlates.set(false);
      },
      error: () => {
        this.platesError.set('No se pudo cargar la lista de placas.');
        this.loadingPlates.set(false);
      },
    });
  }

  edit(payment: Pago): void {
    if (this.busy()) return;
    this.loading.set(true);
    this.actionError.set('');
    this.success.set('');
    this.pendingDelete.set(null);
    this.api
      .get(payment.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (data) => {
          this.loading.set(false);
          this.editing.set(data.id);
          this.legacyPayment.set(data.vehiculo_id === null);
          this.form.controls.vehiculo_id.setValidators(
            this.legacyPayment() ? null : Validators.required,
          );
          this.form.reset({ ...data, valor: Number(data.valor) });
          this.showForm.set(true);
          if (!this.legacyPayment()) this.loadPlates();
        },
        error: (error) => {
          this.loading.set(false);
          this.actionError.set(this.errorMessage(error));
        },
      });
  }

  cancel(): void {
    if (this.busy()) return;
    this.showForm.set(false);
    this.pendingDelete.set(null);
    this.actionError.set('');
  }

  fieldError(field: Field): string {
    const control = this.form.controls[field];
    if (!control.touched || !control.errors) return '';
    if (control.errors['server']) return String(control.errors['server']);
    if (control.errors['required']) return 'Este campo es obligatorio y no puede estar vacío.';
    if (field === 'valor') return 'El valor debe ser mayor que 0.';
    return 'Revisa este campo.';
  }

  save(): void {
    if (this.busy() || (!this.legacyPayment() && !this.plates().length)) return;
    this.form.markAllAsTouched();
    const { valor, periodo, vehiculo_id } = this.form.getRawValue();
    const id = this.editing();
    if (this.form.invalid || valor === null || (id === null && vehiculo_id === null)) {
      this.actionError.set('Revisa los campos señalados antes de guardar el pago.');
      return;
    }
    const payload = { valor, periodo: periodo.trim() };
    this.saving.set(true);
    this.actionError.set('');
    this.success.set('');
    const request = id === null
      ? this.api.create({ ...payload, vehiculo_id: vehiculo_id! })
      : this.api.update(id, vehiculo_id === null ? payload : { ...payload, vehiculo_id });
    request.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: () => {
        this.saving.set(false);
        this.showForm.set(false);
        this.success.set(
          `Pago ${id === null ? 'registrado' : 'actualizado'} correctamente.`,
        );
        this.load();
      },
      error: (error: HttpErrorResponse) => {
        this.saving.set(false);
        this.actionError.set(this.errorMessage(error));
        const body = error.error as ErrorApi | null;
        if (error.status === 422 && Array.isArray(body?.detail)) {
          for (const issue of body.detail) {
            const field = issue.loc.at(-1);
            if (typeof field === 'string' && Object.hasOwn(this.form.controls, field)) {
              this.setFieldError(
                field as Field,
                'El servicio rechazó este valor. Revisa el campo.',
              );
            }
          }
        }
      },
    });
  }

  private setFieldError(field: Field, message: string): void {
    this.form.controls[field].setErrors({ server: message });
    this.form.controls[field].markAsTouched();
  }

  confirmDelete(payment: Pago): void {
    if (this.busy()) return;
    this.pendingDelete.set(payment);
    this.showForm.set(false);
    this.actionError.set('');
    this.success.set('');
  }

  remove(): void {
    const payment = this.pendingDelete();
    if (!payment || this.busy()) return;
    this.saving.set(true);
    this.actionError.set('');
    this.api
      .delete(payment.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.saving.set(false);
          this.pendingDelete.set(null);
          this.success.set(`Pago eliminado correctamente.`);
          this.load();
        },
        error: (error) => {
          this.saving.set(false);
          this.actionError.set(this.errorMessage(error, true));
          if (error.status === 404) {
            this.pendingDelete.set(null);
            this.load();
          }
        },
      });
  }

  private errorMessage(error: HttpErrorResponse, deleting = false): string {
    if (error.status === 404) return 'El pago ya no existe. Actualiza el listado.';
    if (error.status === 409)
      return deleting
        ? 'No se puede eliminar: el pago tiene registros relacionados o un conflicto con otros datos.'
        : 'La operación entra en conflicto con los datos existentes.';
    if (error.status === 422)
      return typeof error.error?.detail === 'string'
        ? error.error.detail
        : 'Revisa los datos del pago.';
    return 'No se pudo conectar con el servicio. Comprueba la conexión y actualiza el listado antes de reintentar.';
  }
}
