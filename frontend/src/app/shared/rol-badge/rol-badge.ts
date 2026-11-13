import { Component, computed, inject } from '@angular/core';
import { Router } from '@angular/router';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-rol-badge',
  standalone: true,
  template: `
    @if (isLoggedIn()) {
      <div class="rol-badge" [style.background-color]="rolDisplay().color">
        <span class="rol-icon">{{ rolDisplay().icon }}</span>
        <div class="rol-info">
          <span class="rol-label">{{ rolDisplay().label }}</span>
          @if (userName()) {
            <span class="rol-name">{{ userName() }}</span>
          }
        </div>
        <button type="button" (click)="logout()" class="logout-btn" aria-label="Cerrar sesión">✕</button>
      </div>
    }
  `,
  styleUrl: './rol-badge.css',
})
export class RolBadge {
  private readonly api = inject(ApiService);
  private readonly router = inject(Router);
  
  readonly isLoggedIn = computed(() => this.api.isLoggedIn());
  readonly userRol = computed(() => this.api.getRol()?.toUpperCase() || '');
  readonly userName = computed(() => this.api.getNombre() || '');
  readonly rolDisplay = computed(() => {
    const rol = this.userRol();
    if (rol === 'ADMINISTRADOR') {
      return { label: 'Administrador', icon: '👑', color: '#1f7a5d' };
    }
    return { label: 'Usuario', icon: '👤', color: '#64748b' };
  });

  logout(): void {
    this.api.logout();
    void this.router.navigateByUrl('/login');
  }
}
