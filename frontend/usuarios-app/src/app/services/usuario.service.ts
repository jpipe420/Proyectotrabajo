import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { ApiResponse } from '../models/api-response.model';
import { Usuario } from '../models/usuario.model';
import { EstadisticasUsuarios } from '../models/estadisticas.model';

@Injectable({
  providedIn: 'root'
})
export class UsuarioService {
  private apiUrl = `${environment.apiUrl}/api/user`;

  constructor(private http: HttpClient) {}

  getUsuarios(): Observable<ApiResponse<Usuario[]>> {
    return this.http.get<ApiResponse<Usuario[]>>(this.apiUrl)
      .pipe(catchError(this.handleError));
  }

  getUsuario(id: number): Observable<ApiResponse<Usuario>> {
    return this.http.get<ApiResponse<Usuario>>(`${this.apiUrl}/${id}`)
      .pipe(catchError(this.handleError));
  }

  createUsuario(usuario: Usuario): Observable<ApiResponse<any>> {
    return this.http.post<ApiResponse<any>>(this.apiUrl, usuario)
      .pipe(catchError(this.handleError));
  }

  updateUsuario(id: number, usuario: Usuario): Observable<ApiResponse<Usuario>> {
    return this.http.put<ApiResponse<Usuario>>(`${this.apiUrl}/${id}`, usuario)
      .pipe(catchError(this.handleError));
  }

  deleteUsuario(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`)
      .pipe(catchError(this.handleError));
  }

  getEstadisticas(): Observable<ApiResponse<EstadisticasUsuarios>> {
    return this.http.get<ApiResponse<EstadisticasUsuarios>>(`${this.apiUrl}/statistics`)
      .pipe(catchError(this.handleError));
  }

  login(username: string, password: string): Observable<ApiResponse<any>> {
    return this.http.post<ApiResponse<any>>(`${this.apiUrl}/Login`, {
      username,
      user_passw: password
    }).pipe(catchError(this.handleError));
  }

  private handleError(error: any) {
    console.error('Error en UsuarioService:', error);
    let errorMessage = 'Ocurrió un error desconocido';
    
    if (error.error instanceof ErrorEvent) {
      errorMessage = `Error: ${error.error.message}`;
    } else {
      if (error.error?.message) {
        errorMessage = error.error.message;
      } else if (error.status) {
        errorMessage = `Error ${error.status}: ${error.statusText}`;
      }
    }
    
    return throwError(() => new Error(errorMessage));
  }
}