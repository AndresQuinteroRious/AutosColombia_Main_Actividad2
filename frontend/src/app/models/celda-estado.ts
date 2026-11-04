/** Información pública del vehículo que ocupa una celda. */
export interface VehiculoEnCelda {
  placa: string;
  marca: string;
  modelo: number;
  color: string;
  tipo: string;
}

/** Estado de una celda con información de ocupación. */
export interface CeldaEstado {
  id: number;
  codigo: string;
  tipo: string;
  ocupada: boolean;
  vehiculo: VehiculoEnCelda | null;
}

/** Respuesta completa del endpoint /celdas/estado. */
export interface CeldasEstado {
  items: CeldaEstado[];
  total: number;
  libres: number;
  ocupadas: number;
}
