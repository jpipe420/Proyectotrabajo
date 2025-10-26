export interface ApiResponse<T = any> {
  status: 'success' | 'error' | 'warning' | 'info';
  message: string;
  data?: T;
  errors?: string[];
  metadata?: {
    timestamp: string;
    version: string;
    execution_time_ms?: number;
    path?: string;
    method?: string;
  };
}