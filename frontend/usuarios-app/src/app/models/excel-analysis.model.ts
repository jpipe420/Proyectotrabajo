export interface RegistroExcel {
  nombre: string;
  username: string;
  correo: string;
  user_passw: string;
  fila_original?: number;
  estado_validacion?: 'valido' | 'duplicado_bd' | 'error';
  mensaje_validacion?: string;
  selected?: boolean;
  editing?: boolean;
}

export interface HojaAnalisis {
  nombre_hoja: string;
  total_filas: number;
  es_valida: boolean;
  datos: RegistroExcel[];
  errores: string[];
  total_validos: number;
  total_duplicados: number;
}

export interface ExcelAnalysisResponse {
  nombre_archivo: string;
  total_hojas: number;
  hojas_validas: HojaAnalisis[];
  hojas_invalidas: HojaAnalisis[];
  resumen: {
    hojas_procesables: number;
    hojas_con_errores: number;
    total_registros_validos: number;
    total_registros_duplicados: number;
  };
}

export interface ConfirmacionCarga {
  registros: any[];
}

export interface ConfirmacionResponse {
  usuarios_creados: number;
  total_procesados: number;
  tasa_exito?: string;
}