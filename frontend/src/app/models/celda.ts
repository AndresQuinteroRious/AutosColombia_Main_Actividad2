import { TIPOS_VEHICULO, TipoVehiculo } from './vehiculo';

export const TIPOS_CELDA = TIPOS_VEHICULO;
export type TipoCelda = TipoVehiculo;

export interface CeldaCrear {
  codigo: string;
  tipo: TipoCelda;
}
export type CeldaActualizar = Partial<CeldaCrear>;
export interface Celda extends CeldaCrear {
  id: number;
}
export interface CeldasPagina {
  items: Celda[];
  total: number;
  offset: number;
  limit: number;
}
