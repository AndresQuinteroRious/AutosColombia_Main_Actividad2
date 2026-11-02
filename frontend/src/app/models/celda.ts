export const TIPOS_CELDA = ['MOTO', 'CARRO', 'CAMION', 'OTRO'] as const;
export type TipoCelda = (typeof TIPOS_CELDA)[number];

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
