export interface UsuarioCrear {
  nombre: string;
  documento: string;
  telefono: string;
  fecha_vencimiento: string;
  rol?: string;
}
export type UsuarioActualizar = Partial<UsuarioCrear>;
export interface Usuario extends UsuarioCrear {
  id: number;
  rol: string;
}
export interface UsuariosPagina {
  items: Usuario[];
  total: number;
  offset: number;
  limit: number;
}
