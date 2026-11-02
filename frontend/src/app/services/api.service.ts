import { HttpClient, HttpHeaders } from '@angular/common/http';
import { inject, Injectable, InjectionToken } from '@angular/core';
import { timeout } from 'rxjs';
import { Vehiculo, VehiculoActualizar, VehiculoCrear, VehiculosPagina } from '../models/vehiculo';

// Mismo origen: el proxy de desarrollo define el destino real del backend.
export const API_BASE_URL = new InjectionToken<string>('API_BASE_URL', { factory: () => '' });

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly base = inject(API_BASE_URL);
  private readonly vehicles = `${this.base}/vehiculos`;

  health() {
    return this.http.get<{ status?: unknown } | null>(`${this.base}/health`);
  }

  login(documento: string, telefono: string) {
    return this.http.post<any>(`${this.base}/usuarios/login`, {
      documento,
      telefono,
    }).pipe(timeout(15000));
  }

  guardarToken(token: string) {
    localStorage.setItem('token_admin', token);
  }

  guardarRol(rol: string) {
    localStorage.setItem('rol_admin', rol.trim().toUpperCase());
  }

  guardarNombre(nombre: string) {
    localStorage.setItem('nombre_usuario', nombre);
  }

  getRol(): string | null {
    const rol = localStorage.getItem('rol_admin');
    return rol ? rol.trim().toUpperCase() : null;
  }

  getNombre(): string | null {
    const nombre = localStorage.getItem('nombre_usuario');
    return nombre ? nombre.trim() : null;
  }

  logout() {
    localStorage.removeItem('token_admin');
    localStorage.removeItem('rol_admin');
    localStorage.removeItem('nombre_usuario');
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  getToken(): string | null {
    return localStorage.getItem('token_admin');
  }

  getAuthHeaders() {
    const token = this.getToken();
    return new HttpHeaders({
      Authorization: token ? `Bearer ${token}` : '',
    });
  }

  list(offset: number, limit: number) {
    return this.http
      .get<VehiculosPagina>(this.vehicles, {
        params: { offset, limit },
        headers: this.getAuthHeaders(),
      })
      .pipe(timeout(15000));
  }
  get(id: number) {
    return this.http.get<Vehiculo>(`${this.vehicles}/${id}`, {
      headers: this.getAuthHeaders(),
    }).pipe(timeout(15000));
  }
  create(data: VehiculoCrear) {
    return this.http.post<Vehiculo>(this.vehicles, data, {
      headers: this.getAuthHeaders(),
    }).pipe(timeout(15000));
  }
  update(id: number, data: VehiculoActualizar) {
    return this.http.patch<Vehiculo>(`${this.vehicles}/${id}`, data, {
      headers: this.getAuthHeaders(),
    }).pipe(timeout(15000));
  }
  delete(id: number) {
    return this.http.delete<void>(`${this.vehicles}/${id}`, {
      headers: this.getAuthHeaders(),
    }).pipe(timeout(15000));
  }
}
