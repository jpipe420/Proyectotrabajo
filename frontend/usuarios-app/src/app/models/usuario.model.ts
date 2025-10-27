export interface Usuario {
  id?: number;
  nombre: string;
  username: string;
  correo: string;
  user_passw?: string;
  rol_id?: number;
  telefono?: string;
  avatar_url?: string;
  estado?: 'activo' | 'inactivo' | 'bloqueado';
  email_verificado?: boolean;
  created_at?: string | Date;  // ← Campo de fecha de creación
  updated_at?: string | Date;  // ← Campo de fecha de actualización
}