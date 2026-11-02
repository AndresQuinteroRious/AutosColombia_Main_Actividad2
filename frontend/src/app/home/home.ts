import { ApiService } from '../services/api.service';
import { Component, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RolBadge } from '../shared/rol-badge/rol-badge';

import { timeout } from 'rxjs';

@Component({
  imports: [RolBadge],
  selector: 'app-home',
  styleUrl: './home.css',
  templateUrl: './home.html',
})
export class Home {
  private readonly api = inject(ApiService);
  protected readonly connectionState = signal<'checking' | 'available' | 'unavailable'>('checking');
  protected readonly connectionMessage = computed(() => {
    switch (this.connectionState()) {
      case 'available':
        return 'Servicio disponible';
      case 'unavailable':
        return 'No se pudo conectar con el servicio';
      default:
        return 'Comprobando conexión…';
    }
  });

  constructor() {
    inject(ApiService)
      .health()
      .pipe(timeout(5000), takeUntilDestroyed())
      .subscribe({
        next: (response) =>
          this.connectionState.set(response?.status === 'ok' ? 'available' : 'unavailable'),
        error: () => this.connectionState.set('unavailable'),
      });
  }
}
