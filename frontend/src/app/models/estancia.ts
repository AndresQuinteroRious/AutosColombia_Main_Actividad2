import { Celda } from './celda';
import { Vehiculo } from './vehiculo';

export interface EntradaCrear {
  placa: string;
  celda_id: number;
  operador_id: number;
}
export interface SalidaCrear {
  placa: string;
  operador_id: number;
}
export interface Estancia {
  id: number;
  vehiculo_id: number;
  celda_id: number;
  entrada: string;
  salida: string | null;
  operador_entrada_id: number;
  operador_salida_id: number | null;
}
export interface EstadoVehiculo {
  vehiculo: Vehiculo;
  esta_dentro: boolean;
  estancia: (Estancia & { celda: Celda }) | null;
}

export interface EstanciaHistorialItem {
  id: number;
  placa: string;
  celda: string;
  operador_entrada: string;
  operador_salida: string | null;
  entrada: string;
  salida: string | null;
}

export interface EstanciasHistorialPagina {
  items: EstanciaHistorialItem[];
  total: number;
  offset: number;
  limit: number;
}

export interface EstanciasHistorialFiltros {
  fecha_desde?: string;
  fecha_hasta?: string;
  placa?: string;
}
