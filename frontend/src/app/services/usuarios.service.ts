import { HttpClient, HttpHeaders } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { timeout } from 'rxjs';
import { Usuario, UsuarioActualizar, UsuarioCrear, UsuariosPagina } from '../models/usuario';

import { API_BASE_URL } from './api.service';

@Injectable({ providedIn: 'root' })
export class UsuariosService {
  private readonly http = inject(HttpClient);
  private readonly base = inject(API_BASE_URL);
  private readonly users = `${this.base}/usuarios`;

  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('token_admin');
    return new HttpHeaders({
      Authorization: token ? `Bearer ${token}` : '',
    });
  }

  list(offset: number, limit: number) {
    return this.http
      .get<UsuariosPagina>(this.users, {
        params: { offset, limit },
        headers: this.getAuthHeaders(),
      })
      .pipe(timeout(15000));
  }
  get(id: number) {
    return this.http.get<Usuario>(`${this.users}/${id}`, {
      headers: this.getAuthHeaders(),
    }).pipe(timeout(15000));
  }
  create(data: UsuarioCrear) {
    return this.http.post<Usuario>(this.users, data, {
      headers: this.getAuthHeaders(),
    }).pipe(timeout(15000));
  }
  update(id: number, data: UsuarioActualizar) {
    return this.http.patch<Usuario>(`${this.users}/${id}`, data, {
      headers: this.getAuthHeaders(),
    }).pipe(timeout(15000));
  }
  delete(id: number) {
    return this.http.delete<void>(`${this.users}/${id}`, {
      headers: this.getAuthHeaders(),
    }).pipe(timeout(15000));
  }
}
