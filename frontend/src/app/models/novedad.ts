export interface NovedadCrear {
  descripcion: string;
}
export type NovedadActualizar = Partial<NovedadCrear>;
export interface Novedad extends NovedadCrear {
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
}

export interface NovedadHistorialPagina {
  items: NovedadHistorialItem[];
  total: number;
  offset: number;
  limit: number;
}
