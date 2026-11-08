import { HttpClient, HttpHeaders } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { timeout } from 'rxjs';
import {
  Novedad,
  NovedadActualizar,
  NovedadCrear,
  NovedadHistorialFiltros,
  NovedadHistorialItem,
  NovedadHistorialPagina,
  NovedadVehiculoCrear,
  NovedadesPagina,
} from '../models/novedad';

import { API_BASE_URL } from './api.service';

@Injectable({ providedIn: 'root' })
export class NovedadesService {
  private readonly http = inject(HttpClient);
  private readonly base = inject(API_BASE_URL);
  private readonly news = `${this.base}/novedades`;

  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('token_admin');
    return new HttpHeaders({ Authorization: token ? `Bearer ${token}` : '' });
  }

  list(offset: number, limit: number) {
    return this.http
      .get<NovedadesPagina>(this.news, { params: { offset, limit } })
      .pipe(timeout(15000));
  }
  get(id: number) {
    return this.http.get<Novedad>(`${this.news}/${id}`).pipe(timeout(15000));
  }
  create(data: NovedadCrear) {
    return this.http.post<Novedad>(this.news, data).pipe(timeout(15000));
  }
  createForVehicle(data: NovedadVehiculoCrear) {
    return this.http
      .post<NovedadHistorialItem>(`${this.news}/vehiculo`, data, {
        headers: this.getAuthHeaders(),
      })
      .pipe(timeout(15000));
  }
  history(filtros: NovedadHistorialFiltros, offset: number, limit: number) {
    return this.http
      .get<NovedadHistorialPagina>(`${this.news}/historial`, {
        params: {
          offset,
          limit,
          ...(filtros.fecha_desde ? { fecha_desde: filtros.fecha_desde } : {}),
          ...(filtros.fecha_hasta ? { fecha_hasta: filtros.fecha_hasta } : {}),
          ...(filtros.placa ? { placa: filtros.placa } : {}),
        },
        headers: this.getAuthHeaders(),
      })
      .pipe(timeout(15000));
  }
  update(id: number, data: NovedadActualizar) {
    return this.http.patch<Novedad>(`${this.news}/${id}`, data).pipe(timeout(15000));
  }
  delete(id: number) {
    return this.http.delete<void>(`${this.news}/${id}`).pipe(timeout(15000));
  }
}
