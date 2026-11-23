import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { timeout } from 'rxjs';
import { Pago, PagoActualizar, PagoCrear, PagosPagina, PlacaPago, TarifasPago } from '../models/pago';

import { API_BASE_URL, ApiService } from './api.service';

@Injectable({ providedIn: 'root' })
export class PagosService {
  private readonly http = inject(HttpClient);
  private readonly session = inject(ApiService);
  private readonly base = inject(API_BASE_URL);
  private readonly payments = `${this.base}/pagos`;

  getTariffs() {
    return this.http.get<TarifasPago>(`${this.payments}/tarifas`).pipe(timeout(15000));
  }

  updateTariffs(data: TarifasPago) {
    return this.http
      .put<TarifasPago>(`${this.payments}/tarifas`, data, {
        headers: this.session.getAuthHeaders(),
      })
      .pipe(timeout(15000));
  }

  listPlates() {
    return this.http.get<PlacaPago[]>(`${this.payments}/placas`).pipe(timeout(15000));
  }

  list(offset: number, limit: number) {
    return this.http
      .get<PagosPagina>(this.payments, { params: { offset, limit } })
      .pipe(timeout(15000));
  }
  get(id: number) {
    return this.http.get<Pago>(`${this.payments}/${id}`).pipe(timeout(15000));
  }
  create(data: PagoCrear) {
    return this.http.post<Pago>(this.payments, data).pipe(timeout(15000));
  }
  update(id: number, data: PagoActualizar) {
    return this.http.patch<Pago>(`${this.payments}/${id}`, data).pipe(timeout(15000));
  }
  delete(id: number) {
    return this.http.delete<void>(`${this.payments}/${id}`).pipe(timeout(15000));
  }
}
