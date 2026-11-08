export const TIPOS_VEHICULO = ['MOTO', 'AUTOMOVIL', 'CAMIONETA', 'FURGON', 'CAMION', 'OTROS'] as const;
export type TipoVehiculo = (typeof TIPOS_VEHICULO)[number];
export type EstadoMensualidad = 'activo' | 'desactivado';
export interface VehiculoCrear {
  placa: string;
  color: string;
  modelo: number;
  marca: string;
  tipo: TipoVehiculo;
  celda_id?: number;
  estado_mensualidad: EstadoMensualidad;
}
export type VehiculoActualizar = Partial<VehiculoCrear>;
export interface Vehiculo extends Omit<VehiculoCrear, 'estado_mensualidad'> {
  id: number;
  estado_mensualidad?: EstadoMensualidad | null;
}
export interface MensualidadRespuesta {
  id_mensualidad: number;
  id_vehiculo: number;
  estado: EstadoMensualidad;
}
export interface VehiculosPagina {
  items: Vehiculo[];
  total: number;
  offset: number;
  limit: number;
}
export interface ErrorValidacion {
  loc: (string | number)[];
  msg: string;
  type: string;
}
export interface ErrorApi {
  detail?: string | ErrorValidacion[];
}
