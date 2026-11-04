import { ApiService } from '../services/api.service';
import { EstanciasService } from '../services/estancias.service';
import { Component, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CommonModule } from '@angular/common';
import { timeout } from 'rxjs';
import { EstanciaAbierta } from '../models/estancia';

@Component({
  imports: [CommonModule],
  selector: 'app-home',
  styleUrl: './home.css',
  templateUrl: './home.html',
})
export class Home {
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

  protected readonly estanciasAbiertas = signal<EstanciaAbierta[]>([]);
  protected readonly estanciasLoading = signal(true);
  protected readonly estanciasError = signal('');

  constructor() {
    const api = inject(ApiService);
    const estanciasApi = inject(EstanciasService);

    api
      .health()
      .pipe(timeout(5000), takeUntilDestroyed())
      .subscribe({
        next: (response) =>
          this.connectionState.set(response?.status === 'ok' ? 'available' : 'unavailable'),
        error: () => this.connectionState.set('unavailable'),
      });

    estanciasApi
      .abiertas()
      .pipe(takeUntilDestroyed())
      .subscribe({
        next: (data) => {
          this.estanciasAbiertas.set(data);
          this.estanciasLoading.set(false);
        },
        error: () => {
          this.estanciasLoading.set(false);
          this.estanciasError.set(
            'No se pudieron cargar las estancias abiertas. Verifica la conexión con el servidor.',
          );
        },
      });
  }
}
