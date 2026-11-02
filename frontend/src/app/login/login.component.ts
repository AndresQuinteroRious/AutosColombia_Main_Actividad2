import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div style="min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #edf3f0 0%, #f7f9fb 100%); padding: 24px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
      <div style="width: 100%; max-width: 460px; background: rgba(255,255,255,0.9); border: 1px solid rgba(15, 23, 42, 0.07); border-radius: 22px; box-shadow: 0 22px 50px rgba(15, 23, 42, 0.10); padding: 32px 28px 28px; backdrop-filter: blur(8px);">
        <div style="display: flex; align-items: center; justify-content: center; width: 56px; height: 56px; margin: 0 auto 18px; border-radius: 16px; background: linear-gradient(135deg, #dfeee8, #cfe5da); color: #1d4d3b; font-size: 26px; font-weight: 700;">
          A
        </div>

        <div style="text-align: center; margin-bottom: 24px;">
          <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 1.5px; color: #64748b; font-weight: 700;">Autos Colombia</div>
          <h2 style="margin: 8px 0 0; font-size: 30px; color: #0f172a;">Iniciar sesión</h2>
        </div>

        <div style="display: flex; flex-direction: column; gap: 18px;">
          <label style="display: block;">
            <div style="margin-bottom: 8px; font-weight: 700; color: #334155; font-size: 14px;">Documento</div>
            <input type="text" [(ngModel)]="documento" placeholder="ADMIN-001" style="width: 100%; padding: 12px 14px; border: 1px solid #dfe7ee; border-radius: 12px; background: #f8fafc; color: #0f172a; font-size: 15px; box-sizing: border-box; outline: none; transition: border-color 0.2s ease;" />
          </label>

          <label style="display: block;">
            <div style="margin-bottom: 8px; font-weight: 700; color: #334155; font-size: 14px;">Teléfono</div>
            <div style="position: relative;">
              <input
                [type]="showPhone() ? 'text' : 'password'"
                [(ngModel)]="telefono"
                placeholder="3001112222"
                style="width: 100%; padding: 12px 46px 12px 14px; border: 1px solid #dfe7ee; border-radius: 12px; background: #f8fafc; color: #0f172a; font-size: 15px; box-sizing: border-box; outline: none;"
              />
              <button
                type="button"
                (click)="togglePhoneVisibility()"
                [attr.aria-label]="showPhone() ? 'Ocultar teléfono' : 'Mostrar teléfono'"
                style="position: absolute; right: 12px; top: 50%; transform: translateY(-50%); border: 0; background: transparent; cursor: pointer; font-size: 18px; color: #475569;"
              >
                {{ showPhone() ? '🙈' : '👁️' }}
              </button>
            </div>
          </label>

          <div>
            <label style="display: block; margin-bottom: 8px; font-weight: 700; color: #334155; font-size: 14px;">Rol de acceso</label>
            <select
              [(ngModel)]="rolSeleccionado"
              (ngModelChange)="cambiarRol($event)"
              style="width: 100%; padding: 12px 14px; border: 1px solid #dfe7ee; border-radius: 12px; background: #f8fafc; color: #0f172a; font-size: 15px; box-sizing: border-box; outline: none;"
            >
              @for (rol of roles; track rol.value) {
                <option [value]="rol.value">{{ rol.label }}</option>
              }
            </select>
            <small style="display: block; margin-top: 8px; color: #475569; font-size: 12px;">Sesión actual: {{ rolActual() }}</small>
          </div>
        </div>

        <button
          type="button"
          (click)="login()"
          [disabled]="loading()"
          style="margin-top: 22px; width: 100%; padding: 14px 16px; border: 0; border-radius: 12px; background: linear-gradient(135deg, #1f7a5d, #0f766e); color: white; font-size: 16px; font-weight: 700; cursor: pointer; box-shadow: 0 10px 20px rgba(15, 118, 110, 0.20);"
        >
          {{ loading() ? 'Ingresando...' : 'Entrar' }}
        </button>

        @if (error()) {
          <p style="margin-top: 18px; margin-bottom: 0; color: #b42318; font-weight: 700; font-size: 14px;">{{ error() }}</p>
        }
      </div>
    </div>
  `,
})
export class LoginComponent {
  private readonly api = inject(ApiService);
  private readonly router = inject(Router);

  readonly roles = [
    {
      value: 'administrador',
      label: 'Administrador',
      documento: 'ADMIN-001',
      telefono: '3001112222',
    },
    {
      value: 'usuario',
      label: 'Usuario',
      documento: '',
      telefono: '',
    },
  ];

  documento = 'ADMIN-001';
  telefono = '3001112222';
  rolSeleccionado = 'administrador';
  readonly loading = signal(false);
  readonly error = signal('');
  readonly showPhone = signal(false);

  togglePhoneVisibility(): void {
    this.showPhone.set(!this.showPhone());
  }

  rolActual(): string {
    return this.roles.find((rol) => rol.value === this.rolSeleccionado)?.label ?? 'Administrador';
  }

  cambiarRol(nuevoRol: string): void {
    this.rolSeleccionado = nuevoRol;
    const rol = this.roles.find((item) => item.value === nuevoRol);

    if (rol) {
      this.documento = rol.documento;
      this.telefono = rol.telefono;
    }
  }

  login(): void {
    this.error.set('');
    this.loading.set(true);

    this.api.login(this.documento, this.telefono).subscribe({
      next: (res) => {
        this.api.guardarToken(res.token);
        this.api.guardarRol(res.rol);
        this.loading.set(false);
        this.router.navigateByUrl('/control-acceso');
      },
      error: (err) => {
        this.loading.set(false);
        this.error.set(err?.error?.detail || 'No se pudo iniciar sesión.');
      },
    });
  }
}
