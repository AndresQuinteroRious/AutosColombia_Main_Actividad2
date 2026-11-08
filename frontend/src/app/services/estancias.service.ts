import { HttpClient, HttpHeaders } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { EMPTY, Observable, expand, reduce, throwError, timeout } from 'rxjs';
import { Celda } from '../models/celda';
import { Operador } from '../models/operador';
import { EntradaCrear, SalidaCrear, Estancia, EstadoVehiculo } from '../models/estancia';
import { Vehiculo } from '../models/vehiculo';
import { API_BASE_URL, ApiService } from './api.service';
import { OperadoresService } from './operadores.service';

interface Pagina<T> {
  items: T[];
  offset: number;
  limit: number;
  total: number;
}

@Injectable({ providedIn: 'root' })
export class EstanciasService {
  private readonly http = inject(HttpClient);
  private readonly base = `${inject(API_BASE_URL)}/estancias`;
  private readonly vehicleApi = inject(ApiService);
  private readonly operators = inject(OperadoresService);

  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('token_admin');
    return new HttpHeaders({
      Authorization: token ? `Bearer ${token}` : '',
    });
  }

  entrada(data: EntradaCrear) {
    return this.http.post<Estancia>(`${this.base}/entrada`, data, {
      headers: this.getAuthHeaders(),
    }).pipe(timeout(15000));
  }
  salida(data: SalidaCrear) {
    return this.http.post<Estancia>(`${this.base}/salida`, data, {
      headers: this.getAuthHeaders(),
    }).pipe(timeout(15000));
  }
  consultar(placa: string) {
    return this.http
      .get<EstadoVehiculo>(`${this.base}/vehiculo/${encodeURIComponent(placa)}`, {
        headers: this.getAuthHeaders(),
      })
      .pipe(timeout(15000));
  }
  celdasDisponibles(): Observable<Celda[]> {
    return this.http
      .get<Celda[]>(`${this.base}/celdas-disponibles`, { headers: this.getAuthHeaders() })
      .pipe(timeout(15000));
  }
  operadorActual(): Observable<Operador> {
    return this.http
      .get<Operador>(`${this.base}/operador-actual`, { headers: this.getAuthHeaders() })
      .pipe(timeout(15000));
  }
  vehiculos(): Observable<Vehiculo[]> {
    return this.todas((offset) => this.vehicleApi.list(offset, 100));
  }
  operadores(): Observable<Operador[]> {
    return this.todas((offset) => this.operators.list(offset, 100));
  }

  private todas<T>(load: (offset: number) => Observable<Pagina<T>>): Observable<T[]> {
    return load(0).pipe(
      expand((page) => {
        const next = page.offset + page.items.length;
        if (next >= page.total) return EMPTY;
        if (!page.items.length)
          return throwError(() => new Error('Catálogo incompleto. Recarga las opciones.'));
        return load(next);
      }),
      reduce((items, page) => [...items, ...page.items], [] as T[]),
    );
  }
}
