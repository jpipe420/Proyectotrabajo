export interface EstadisticasUsuarios {
  total_usuarios: number;
  resumen_temporal: {
    hoy: number;
    esta_semana: number;
    este_mes: number;
  };
  usuarios_por_mes: Array<{
    mes: string;
    mes_nombre: string;
    cantidad: number;
  }>;
  usuarios_por_dominio: Array<{
    dominio: string;
    cantidad: number;
  }>;
}