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
          <h2 style="margin: 8px 0 0; font-size: 30px; color: #1a2d3d;">{{ requiereCambioContrasena() ? 'Crea tu contraseña' : 'Iniciar sesión' }}</h2>
        </div>

        <div style="display: flex; flex-direction: column; gap: 18px;">
          @if (!requiereCambioContrasena()) {
            <label style="display: block;">
              <div style="margin-bottom: 8px; font-weight: 700; color: #1a2d3d; font-size: 14px;">Documento</div>
              <input type="text" [(ngModel)]="documento" placeholder="ADMIN-001" style="width: 100%; padding: 12px 14px; border: 1px solid #dfe8f4; border-radius: 12px; background: #f8fbff; color: #1a2d3d; font-size: 15px; box-sizing: border-box; outline: none;" />
            </label>

            <label style="display: block;">
              <div style="margin-bottom: 8px; font-weight: 700; color: #1a2d3d; font-size: 14px;">Teléfono o contraseña actual</div>
              <div style="position: relative;">
                <input [type]="showPhone() ? 'text' : 'password'" [(ngModel)]="telefono" placeholder="Teléfono o contraseña" style="width: 100%; padding: 12px 46px 12px 14px; border: 1px solid #dfe8f4; border-radius: 12px; background: #f8fbff; color: #1a2d3d; font-size: 15px; box-sizing: border-box; outline: none;" />
                <button type="button" (click)="togglePhoneVisibility()" [attr.aria-label]="showPhone() ? 'Ocultar credencial' : 'Mostrar credencial'" style="position: absolute; right: 12px; top: 50%; transform: translateY(-50%); border: 0; background: transparent; cursor: pointer; font-size: 18px; color: #1d4e89;">{{ showPhone() ? '🙈' : '👁️' }}</button>
              </div>
            </label>
          }

          @if (requiereCambioContrasena() || modoCambioOpcional()) {
            <p style="margin: 0; color: #5b6b7d;">{{ requiereCambioContrasena() ? 'Por seguridad, crea una contraseña para continuar.' : 'Confirma tu credencial actual y crea una contraseña nueva.' }} Debe tener al menos 10 caracteres.</p>
            <label style="display: block;">
              <div style="margin-bottom: 8px; font-weight: 700; color: #1a2d3d; font-size: 14px;">Nueva contraseña</div>
              <input type="password" [(ngModel)]="contrasenaNueva" autocomplete="new-password" style="width: 100%; padding: 12px 14px; border: 1px solid #dfe8f4; border-radius: 12px; background: #f8fbff; color: #1a2d3d; font-size: 15px; box-sizing: border-box;" />
            </label>
            <label style="display: block;">
              <div style="margin-bottom: 8px; font-weight: 700; color: #1a2d3d; font-size: 14px;">Confirmar contraseña</div>
              <input type="password" [(ngModel)]="confirmarContrasena" autocomplete="new-password" style="width: 100%; padding: 12px 14px; border: 1px solid #dfe8f4; border-radius: 12px; background: #f8fbff; color: #1a2d3d; font-size: 15px; box-sizing: border-box;" />
            </label>
          }
        </div>

        <button
          type="button"
          (click)="accionPrincipal()"
          [disabled]="loading()"
          style="margin-top: 22px; width: 100%; padding: 14px 16px; border: 0; border-radius: 12px; background: linear-gradient(135deg, #1d4e89 0%, #f4c542 50%, #d94b41 100%); color: white; font-size: 16px; font-weight: 800; cursor: pointer; box-shadow: 0 12px 24px rgba(29, 78, 137, 0.18);"
        >
          {{ loading() ? (requiereCambioContrasena() || modoCambioOpcional() ? 'Guardando...' : 'Ingresando...') : (requiereCambioContrasena() ? 'Guardar contraseña' : modoCambioOpcional() ? 'Cambiar contraseña' : 'Entrar') }}
        </button>

        @if (modoCambioOpcional() && !requiereCambioContrasena()) {
          <button type="button" (click)="cancelarCambioOpcional()" style="margin-top: 12px; width: 100%; padding: 12px; border: 1px solid #dfe8f4; border-radius: 12px; background: white; color: #1d4e89; font-weight: 700; cursor: pointer;">Cancelar</button>
        } @else if (requiereCambioContrasena()) {
          <button type="button" (click)="cancelarCambioContrasena()" style="margin-top: 12px; width: 100%; padding: 12px; border: 1px solid #dfe8f4; border-radius: 12px; background: white; color: #1d4e89; font-weight: 700; cursor: pointer;">Cerrar sesión</button>
        } @else {
          <button type="button" (click)="iniciarCambioOpcional()" style="margin-top: 12px; width: 100%; padding: 12px; border: 1px solid #dfe8f4; border-radius: 12px; background: white; color: #1d4e89; font-weight: 700; cursor: pointer;">Cambiar contraseña</button>
        }

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

  documento = 'ADMIN-001';
  telefono = '3001112222';
  contrasenaNueva = '';
  confirmarContrasena = '';
  readonly loading = signal(false);
  readonly error = signal('');
  readonly showPhone = signal(false);
  readonly requiereCambioContrasena = signal(this.api.requiereCambioContrasena());
  readonly modoCambioOpcional = signal(false);

  togglePhoneVisibility(): void {
    this.showPhone.set(!this.showPhone());
  }

  accionPrincipal(): void {
    if (this.requiereCambioContrasena()) {
      this.guardarContrasena();
    } else if (this.modoCambioOpcional()) {
      this.cambiarContrasenaDesdeLogin();
    } else {
      this.login();
    }
  }

  iniciarCambioOpcional(): void {
    this.error.set('');
    this.modoCambioOpcional.set(true);
  }

  cancelarCambioOpcional(): void {
    this.modoCambioOpcional.set(false);
    this.contrasenaNueva = '';
    this.confirmarContrasena = '';
    this.error.set('');
  }

  login(): void {
    this.error.set('');
    this.loading.set(true);

    this.api.login(this.documento, this.telefono).subscribe({
      next: (res) => {
        this.api.guardarToken(res.token);
        this.api.guardarRol(res.rol);
        this.api.guardarCambioContrasenaRequerido(res.requiere_cambio_contrasena);
        if (res.usuario?.nombre) {
          this.api.guardarNombre(res.usuario.nombre);
        }
        this.loading.set(false);

        if (res.requiere_cambio_contrasena) {
          this.requiereCambioContrasena.set(true);
          return;
        }

        const rol = (res.rol ?? '').toString().trim().toUpperCase();
        this.router.navigateByUrl(rol === 'ADMINISTRADOR' ? '/gestion/usuarios' : '/control-acceso');
      },
      error: (err) => {
        this.loading.set(false);
        this.error.set(err?.error?.detail || 'No se pudo iniciar sesión.');
      },
    });
  }

  guardarContrasena(): void {
    this.error.set('');
    if (!this.validarNuevaContrasena()) return;
    this.loading.set(true);
    this.api.cambiarContrasena(this.contrasenaNueva).subscribe({
      next: () => {
        this.loading.set(false);
        this.api.guardarCambioContrasenaRequerido(false);
        this.requiereCambioContrasena.set(false);
        this.irAlInicioPorRol();
      },
      error: (err) => {
        this.loading.set(false);
        this.error.set(err?.error?.detail || 'No se pudo guardar la contraseña.');
      },
    });
  }

  cancelarCambioContrasena(): void {
    this.api.logout();
    this.requiereCambioContrasena.set(false);
    this.contrasenaNueva = '';
    this.confirmarContrasena = '';
  }

  private cambiarContrasenaDesdeLogin(): void {
    this.error.set('');
    if (!this.validarNuevaContrasena()) return;
    this.loading.set(true);
    this.api.login(this.documento, this.telefono).subscribe({
      next: (res) => {
        this.guardarSesion(res);
        this.requiereCambioContrasena.set(!!res.requiere_cambio_contrasena);
        this.api.cambiarContrasena(this.contrasenaNueva).subscribe({
          next: () => {
            this.loading.set(false);
            this.api.guardarCambioContrasenaRequerido(false);
            this.requiereCambioContrasena.set(false);
            this.modoCambioOpcional.set(false);
            this.irAlInicioPorRol();
          },
          error: (err) => {
            this.loading.set(false);
            this.error.set(err?.error?.detail || 'No se pudo guardar la contraseña.');
          },
        });
      },
      error: (err) => {
        this.loading.set(false);
        this.error.set(err?.error?.detail || 'No se pudo validar el documento y la credencial actual.');
      },
    });
  }

  private guardarSesion(res: any): void {
    this.api.guardarToken(res.token);
    this.api.guardarRol(res.rol);
    this.api.guardarCambioContrasenaRequerido(!!res.requiere_cambio_contrasena);
    if (res.usuario?.nombre) this.api.guardarNombre(res.usuario.nombre);
  }

  private validarNuevaContrasena(): boolean {
    if (this.contrasenaNueva.length < 10) {
      this.error.set('La contraseña debe tener al menos 10 caracteres.');
      return false;
    }
    if (this.contrasenaNueva !== this.confirmarContrasena) {
      this.error.set('Las contraseñas no coinciden.');
      return false;
    }
    return true;
  }

  private irAlInicioPorRol(): void {
    const rol = this.api.getRol();
    void this.router.navigateByUrl(rol === 'ADMINISTRADOR' ? '/gestion/usuarios' : '/control-acceso');
  }
}
