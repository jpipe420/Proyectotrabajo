import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

// --- INTERFACES DE DATOS ---

export interface RegisterData {
  nombre: string;
  username: string;
  correo: string;
  password: string; // <-- Campo 'password' para el registro
}

export interface LoginData {
  username: string;
  password: string; // <-- Campo 'password' para el login
}
// ------------------------------

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private baseUrl = environment.apiUrl + '/api/user';
  private isLoggedIn = false;

  constructor(private http: HttpClient) {
    this.isLoggedIn = !!localStorage.getItem('usuario');
  }

  register(data: RegisterData): Observable<any> {
    // La URL es: http://localhost:8000/api/user/register
    return this.http.post(`${this.baseUrl}/register`, data);
  }

  // --- FUNCIÓN LOGIN AJUSTADA ---
  login(data: LoginData): Observable<any> {
    // La URL es: http://localhost:8000/api/user/Login
    // El backend de FastAPI espera {username: "...", password: "..."}
    return this.http.post<any>(`${this.baseUrl}/Login`, data);
  }

  logout(): void {
    localStorage.removeItem('usuario');
    this.isLoggedIn = false;
  }

  setUsuario(usuario: any): void {
    localStorage.setItem('usuario', JSON.stringify(usuario));
    this.isLoggedIn = true;
  }

  getUsuario(): any {
    return JSON.parse(localStorage.getItem('usuario') || '{}');
  }

  estaAutenticado(): boolean {
    return this.isLoggedIn;
  }
}