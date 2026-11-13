import { Component, inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { ApiService } from './services/api.service';

@Component({
  selector: 'app-root',
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  private readonly api = inject(ApiService);
  private readonly router = inject(Router);

  isLoggedIn(): boolean {
    return this.api.isLoggedIn();
  }

  isAdmin(): boolean {
    return this.api.getRol() === 'ADMINISTRADOR';
  }

  logout(): void {
    this.api.logout();
    void this.router.navigateByUrl('/login');
  }
}
