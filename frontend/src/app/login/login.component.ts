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
    <div style="min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #edf5ff 0%, #fff8d9 45%, #fff1ee 100%); padding: 24px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
      <div style="width: 100%; max-width: 460px; background: rgba(255,255,255,0.9); border: 1px solid rgba(29, 78, 137, 0.12); border-radius: 22px; box-shadow: 0 22px 50px rgba(29, 78, 137, 0.12); padding: 32px 28px 28px; backdrop-filter: blur(8px);">
        <div style="display: flex; align-items: center; justify-content: center; width: 60px; height: 60px; margin: 0 auto 18px; border-radius: 18px; background: linear-gradient(135deg, #1d4e89 0%, #f4c542 50%, #d94b41 100%); color: white; font-size: 28px; font-weight: 800; box-shadow: 0 12px 24px rgba(29, 78, 137, 0.18);">
          A
        </div>

        <div style="text-align: center; margin-bottom: 24px;">
          <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 1.5px; color: #1d4e89; font-weight: 800;">Autos Colombia</div>
          <h2 style="margin: 8px 0 0; font-size: 30px; color: #1a2d3d;">Iniciar sesión</h2>
        </div>

        <div style="display: flex; flex-direction: column; gap: 18px;">
          <label style="display: block;">
            <div style="margin-bottom: 8px; font-weight: 700; color: #1a2d3d; font-size: 14px;">Documento</div>
            <input type="text" [(ngModel)]="documento" placeholder="ADMIN-001" style="width: 100%; padding: 12px 14px; border: 1px solid #dfe8f4; border-radius: 12px; background: #f8fbff; color: #1a2d3d; font-size: 15px; box-sizing: border-box; outline: none; transition: border-color 0.2s ease, box-shadow 0.2s ease; box-shadow: inset 0 1px 2px rgba(29, 78, 137, 0.04);" />
          </label>

          <label style="display: block;">
            <div style="margin-bottom: 8px; font-weight: 700; color: #1a2d3d; font-size: 14px;">Teléfono</div>
            <div style="position: relative;">
              <input
                [type]="showPhone() ? 'text' : 'password'"
                [(ngModel)]="telefono"
                placeholder="3001112222"
                style="width: 100%; padding: 12px 46px 12px 14px; border: 1px solid #dfe8f4; border-radius: 12px; background: #f8fbff; color: #1a2d3d; font-size: 15px; box-sizing: border-box; outline: none; box-shadow: inset 0 1px 2px rgba(29, 78, 137, 0.04);"
              />
              <button
                type="button"
                (click)="togglePhoneVisibility()"
                [attr.aria-label]="showPhone() ? 'Ocultar teléfono' : 'Mostrar teléfono'"
                style="position: absolute; right: 12px; top: 50%; transform: translateY(-50%); border: 0; background: transparent; cursor: pointer; font-size: 18px; color: #1d4e89;"
              >
                {{ showPhone() ? '🙈' : '👁️' }}
              </button>
            </div>
          </label>

        </div>

        <button
          type="button"
          (click)="login()"
          [disabled]="loading()"
          style="margin-top: 22px; width: 100%; padding: 14px 16px; border: 0; border-radius: 12px; background: linear-gradient(135deg, #1d4e89 0%, #f4c542 50%, #d94b41 100%); color: white; font-size: 16px; font-weight: 800; cursor: pointer; box-shadow: 0 12px 24px rgba(29, 78, 137, 0.18);"
        >
          {{ loading() ? 'Ingresando...' : 'Entrar' }}
        </button>

        @if (error()) {
          <p style="margin-top: 18px; margin-bottom: 0; color: #b5312d; font-weight: 700; font-size: 14px;">{{ error() }}</p>
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
        if (res.usuario?.nombre) {
          this.api.guardarNombre(res.usuario.nombre);
        }
        this.loading.set(false);

        const rol = (res.rol ?? '').toString().trim().toUpperCase();
        this.router.navigateByUrl(rol === 'ADMINISTRADOR' ? '/gestion/usuarios' : '/control-acceso');
      },
      error: (err) => {
        this.loading.set(false);
        this.error.set(err?.error?.detail || 'No se pudo iniciar sesión.');
      },
    });
  }
}
