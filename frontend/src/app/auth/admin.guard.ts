import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { ApiService } from '../services/api.service';

export const normalizeRol = (rol: string | null | undefined): string =>
  (rol ?? '').trim().toUpperCase();

export const hasAccessRole = (rol: string | null | undefined): boolean => {
  const normalized = normalizeRol(rol);
  return normalized === 'ADMINISTRADOR' || normalized === 'USUARIO';
};

export const accessGuard: CanActivateFn = () => {
  const api = inject(ApiService);
  const router = inject(Router);

  return api.isLoggedIn() && !api.requiereCambioContrasena()
    ? true
    : router.createUrlTree(['/login']);
};

export const sessionGuard: CanActivateFn = () => {
  const api = inject(ApiService);
  const router = inject(Router);
  return api.isLoggedIn() && !api.requiereCambioContrasena()
    ? true
    : router.createUrlTree(['/login']);
};

export const adminGuard: CanActivateFn = () => {
  const api = inject(ApiService);
  const router = inject(Router);

  if (!api.isLoggedIn() || api.requiereCambioContrasena()) {
    return router.createUrlTree(['/login']);
  }

  if (normalizeRol(api.getRol()) !== 'ADMINISTRADOR') {
    router.navigate(['/']);
    return false;
  }

  return true;
};
