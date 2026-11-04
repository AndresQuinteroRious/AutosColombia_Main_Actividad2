import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { timeout } from 'rxjs';
import { CeldasEstado } from '../models/celda-estado';
import { API_BASE_URL } from './api.service';

/** Servicio público para obtener el estado de ocupación de las celdas.
 *  No requiere autenticación; se usa en la pantalla de inicio. */
@Injectable({ providedIn: 'root' })
export class CeldaEstadoService {
  private readonly http = inject(HttpClient);
  private readonly url = `${inject(API_BASE_URL)}/celdas/estado`;

  obtenerEstado() {
    return this.http.get<CeldasEstado>(this.url).pipe(timeout(15000));
  }
}
