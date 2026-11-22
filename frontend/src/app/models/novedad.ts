export interface NovedadCrear {
  descripcion: string;
  id_estancia: number;
}
export type NovedadActualizar = Partial<Pick<NovedadCrear, 'descripcion'>>;
export interface Novedad {
  descripcion: string;
  id_estancia: number | null;
  id: number;
  fecha: string;
}
export interface NovedadesPagina {
  items: Novedad[];
  total: number;
  offset: number;
  limit: number;
}

export interface NovedadVehiculoCrear {
  vehiculo_id: number;
  descripcion: string;
}

export interface NovedadHistorialFiltros {
  fecha_desde?: string;
  fecha_hasta?: string;
  placa?: string;
}

export interface NovedadHistorialItem {
  id: number;
  placa: string | null;
  descripcion: string;
  fecha: string;
  id_estancia?: number | null;
  entrada?: string | null;
  salida?: string | null;
  celda?: string | null;
}

export interface NovedadHistorialPagina {
  items: NovedadHistorialItem[];
  total: number;
  offset: number;
  limit: number;
}
