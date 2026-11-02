import { Routes } from '@angular/router';
import { accessGuard, adminGuard } from './auth/admin.guard';

export const routes: Routes = [
  {
    path: 'login',
    title: 'Iniciar sesión | Autos Colombia',
    loadComponent: () => import('./login/login.component').then((m) => m.LoginComponent),
  },
  {
    path: 'control-acceso',
    title: 'Control de acceso | Autos Colombia',
    canActivate: [accessGuard],
    loadComponent: () => import('./control-acceso/control-acceso').then((m) => m.ControlAcceso),
  },
  {
    path: 'gestion/operadores',
    title: 'Operadores | Autos Colombia',
    canActivate: [adminGuard],
    loadComponent: () => import('./operadores/operadores').then((m) => m.Operadores),
  },
  {
    path: 'gestion/celdas',
    title: 'Celdas | Autos Colombia',
    canActivate: [adminGuard],
    loadComponent: () => import('./celdas/celdas').then((m) => m.Celdas),
  },
  { path: '', pathMatch: 'full', loadComponent: () => import('./home/home').then((m) => m.Home) },
  {
    path: 'gestion/vehiculos',
    title: 'Vehículos | Autos Colombia',
    canActivate: [adminGuard],
    loadComponent: () => import('./vehiculos/vehiculos').then((m) => m.Vehiculos),
  },
  {
    path: 'gestion/usuarios',
    title: 'Usuarios | Autos Colombia',
    canActivate: [adminGuard],
    loadComponent: () => import('./usuarios/usuarios').then((m) => m.Usuarios),
  },
  {
    path: 'gestion/novedades',
    title: 'Novedades | Autos Colombia',
    canActivate: [adminGuard],
    loadComponent: () => import('./novedades/novedades').then((m) => m.Novedades),
  },
  {
    path: 'gestion/pagos',
    title: 'Pagos | Autos Colombia',
    canActivate: [adminGuard],
    loadComponent: () => import('./pagos/pagos').then((m) => m.Pagos),
  },
  { path: '**', redirectTo: '' },
];
