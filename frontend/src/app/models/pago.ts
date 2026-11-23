import type { TipoVehiculo } from './vehiculo';

export interface PagoCrear {
  valor: number;
  vehiculo_id: number;
}
export type PagoActualizar = Partial<PagoCrear>;
export interface Pago extends Omit<PagoCrear, 'valor' | 'vehiculo_id'> {
  id: number;
  fecha: string;
  valor: string;
  vehiculo_id: number | null;
  placa: string | null;
}
export interface PlacaPago {
  id: number;
  placa: string;
  tipo: TipoVehiculo;
  tarifa: number | null;
  tiene_pago: boolean;
  pago_activo: boolean;
}
export interface TarifasPago {
  automovil: number;
  motocicleta: number;
}
export interface PagosPagina {
  items: Pago[];
  total: number;
  offset: number;
  limit: number;
}
