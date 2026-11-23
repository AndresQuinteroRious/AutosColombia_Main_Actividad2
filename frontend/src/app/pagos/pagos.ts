import { HttpErrorResponse } from '@angular/common/http';
import { Component, DestroyRef, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed, toSignal } from '@angular/core/rxjs-interop';
import { FormBuilder, ReactiveFormsModule, ValidatorFn, Validators } from '@angular/forms';
import { ApiService } from '../services/api.service';
import { PagosService } from '../services/pagos.service';
import { Pago, PagoCrear, PlacaPago, TarifasPago } from '../models/pago';
import { ErrorApi } from '../models/vehiculo';
import { RolBadge } from '../shared/rol-badge/rol-badge';

type Field = keyof PagoCrear;

const validTariff: ValidatorFn = ({ value }) =>
  typeof value === 'number' && /^\d{1,8}(\.\d{1,2})?$/.test(String(value)) && value > 0
    ? null
    : { amount: true };

@Component({
  selector: 'app-pagos',
  imports: [ReactiveFormsModule, RolBadge],
  templateUrl: './pagos.html',
  styleUrl: './pagos.css',
})
export class Pagos {
  private readonly api = inject(PagosService);
  private readonly session = inject(ApiService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly fb = inject(FormBuilder);
  private readonly currency = new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
  });
  private readonly dateFormat = new Intl.DateTimeFormat('es-CO', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    timeZone: 'America/Bogota',
  });
  readonly registrationDate = signal('');
  readonly tariffs = signal<TarifasPago | null>(null);
  readonly tariffsLoading = signal(false);
  readonly tariffsSaving = signal(false);
  readonly tariffsError = signal('');
  readonly tariffsSuccess = signal('');
  readonly editingTariffs = signal(false);
  readonly tariffForm = this.fb.group({
    automovil: this.fb.control<number | null>(null, validTariff),
    motocicleta: this.fb.control<number | null>(null, validTariff),
  });
  readonly form = this.fb.group({
    valor: this.fb.control<number | null>(null),
    vehiculo_id: this.fb.control<number | null>(null, Validators.required),
  });
  readonly plates = signal<PlacaPago[]>([]);
  private readonly selectedId = toSignal(this.form.controls.vehiculo_id.valueChanges);
  readonly selectedVehicle = computed(() =>
    this.plates().find((vehicle) => vehicle.id === this.selectedId()),
  );
  readonly tariffLabel = computed(() => {
    const vehicle = this.selectedVehicle();
    if (!vehicle || vehicle.tarifa === null) return '';
    const type = vehicle.tipo === 'MOTOCICLETA' ? 'Motocicleta' : 'Automóvil';
    return `${type} — ${this.formatCurrency(vehicle.tarifa)}`;
  });
  readonly loadingPlates = signal(false);
  readonly platesError = signal('');
  readonly items = signal<Pago[]>([]);
  readonly total = signal(0);
  readonly offset = signal(0);
  readonly limit = 10;
  readonly loading = signal(false);
  readonly saving = signal(false);
  readonly busy = computed(() => this.loading() || this.saving() || this.tariffsSaving());
  readonly showForm = signal(false);
  readonly listError = signal('');
  readonly actionError = signal('');
  readonly registeredPayment = signal<Pago | null>(null);
  readonly page = computed(() => Math.floor(this.offset() / this.limit) + 1);
  readonly pages = computed(() => Math.max(1, Math.ceil(this.total() / this.limit)));

  constructor() {
    this.load();
    this.loadTariffs();
  }

  canUpdateTariffs(): boolean {
    return this.session.isLoggedIn() && this.session.getRol() === 'ADMINISTRADOR';
  }

  formatCurrency(value: number | string): string {
    return `${this.currency.format(Number(value))} COP`;
  }

  loadTariffs(): void {
    if (this.tariffsLoading() || this.tariffsSaving()) return;
    this.tariffsLoading.set(true);
    this.tariffsError.set('');
    this.api.getTariffs().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (data) => {
        this.tariffs.set(data);
        this.tariffsLoading.set(false);
      },
      error: () => {
        this.tariffsError.set('No se pudieron consultar las tarifas vigentes.');
        this.tariffsLoading.set(false);
      },
    });
  }

  editTariffs(): void {
    const current = this.tariffs();
    if (!current || !this.canUpdateTariffs() || this.tariffsLoading()) return;
    this.tariffForm.reset(current);
    this.tariffsError.set('');
    this.tariffsSuccess.set('');
    this.editingTariffs.set(true);
  }

  cancelTariffs(): void {
    if (this.tariffsSaving()) return;
    this.editingTariffs.set(false);
    this.tariffsError.set('');
  }

  saveTariffs(): void {
    if (
      this.tariffsSaving() || this.loadingPlates() || this.saving() ||
      !this.editingTariffs() || !this.canUpdateTariffs()
    ) return;
    this.tariffForm.markAllAsTouched();
    const { automovil, motocicleta } = this.tariffForm.getRawValue();
    if (this.tariffForm.invalid || automovil === null || motocicleta === null) return;
    this.tariffsSaving.set(true);
    this.tariffsError.set('');
    this.api.updateTariffs({ automovil, motocicleta }).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (data) => {
        this.tariffs.set(data);
        this.plates.update((plates) =>
          plates.map((vehicle) => ({
            ...vehicle,
            tarifa: vehicle.tipo === 'AUTOMOVIL' ? data.automovil : data.motocicleta,
          })),
        );
        this.tariffsSaving.set(false);
        this.editingTariffs.set(false);
        this.tariffsSuccess.set('Tarifas actualizadas correctamente.');
      },
      error: (error: HttpErrorResponse) => {
        this.tariffsSaving.set(false);
        this.tariffsError.set(error.status === 401 || error.status === 403
          ? 'Inicia sesión como administrador para actualizar las tarifas.'
          : 'No se pudieron actualizar las tarifas. Revisa los valores e inténtalo de nuevo.');
      },
    });
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
    this.registrationDate.set(this.formatDate(new Date()));
    this.showForm.set(true);
    this.actionError.set('');
    this.registeredPayment.set(null);
    this.loadPlates();
  }

  loadPlates(): void {
    if (this.loadingPlates() || this.tariffsSaving()) return;
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

  cancel(): void {
    if (this.busy()) return;
    this.showForm.set(false);
    this.actionError.set('');
  }

  formatDate(date: Date | string): string {
    return this.dateFormat.format(new Date(date));
  }

  fieldError(field: Field): string {
    const control = this.form.controls[field];
    if (!control.touched || !control.errors) return '';
    if (control.errors['server']) return String(control.errors['server']);
    if (control.errors['required']) return 'Este campo es obligatorio y no puede estar vacío.';
    return 'Revisa este campo.';
  }

  save(): void {
    if (this.busy() || !this.plates().length || this.selectedVehicle()?.tiene_pago) return;
    this.form.markAllAsTouched();
    const { vehiculo_id } = this.form.getRawValue();
    const valor = this.selectedVehicle()?.tarifa ?? null;
    if (vehiculo_id === null || valor === null) {
      this.actionError.set('Revisa los campos señalados antes de guardar el pago.');
      return;
    }
    this.saving.set(true);
    this.actionError.set('');
    this.registeredPayment.set(null);
    this.api.create({ valor, vehiculo_id }).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: (payment) => {
        this.saving.set(false);
        this.showForm.set(false);
        this.registeredPayment.set(payment);
        this.load();
      },
      error: (error: HttpErrorResponse) => {
        this.saving.set(false);
        this.actionError.set(this.errorMessage(error));
        const body = error.error as ErrorApi | null;
        if (error.status === 409) {
          this.loadPlates();
        } else if (error.status === 422 && typeof body?.detail === 'string') {
          this.loadPlates();
          this.loadTariffs();
        }
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

  private errorMessage(error: HttpErrorResponse): string {
    if (error.status === 404) return 'El pago ya no existe. Actualiza el listado.';
    if (error.status === 409)
      return typeof error.error?.detail === 'string'
        ? error.error.detail
        : 'La operación entra en conflicto con los datos existentes.';
    if (error.status === 422)
      return typeof error.error?.detail === 'string'
        ? error.error.detail
        : 'Revisa los datos del pago.';
    return 'No se pudo conectar con el servicio. Comprueba la conexión y actualiza el listado antes de reintentar.';
  }
}
