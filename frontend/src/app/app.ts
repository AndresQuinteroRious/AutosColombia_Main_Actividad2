import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { ApiService } from './services/api.service';

@Component({
  selector: 'app-root',
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  private readonly api = inject(ApiService);

  isLoggedIn(): boolean {
    return this.api.isLoggedIn();
  }

  isAdmin(): boolean {
    return this.api.getRol() === 'ADMINISTRADOR';
  }

  logout(): void {
    this.api.logout();
  }
}
