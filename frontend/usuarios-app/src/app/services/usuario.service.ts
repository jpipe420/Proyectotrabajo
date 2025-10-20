import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class UsuarioService {
  private apiUrl = environment.apiUrl + '/api/user';

  constructor(private http: HttpClient) { }

  getUsuarios(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl);
  }

  getUsuario(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/${id}`);
  }

  crearUsuario(usuario: any): Observable<any> {
    return this.http.post<any>(this.apiUrl, usuario);
  }

  actualizarUsuario(id: number, usuario: any): Observable<any> {
    console.log('Actualizando usuario con ID:', id);
    console.log('Datos a enviar:', usuario);
    return this.http.put<any>(`${this.apiUrl}/${id}`, usuario);
  }

  eliminarUsuario(id: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/${id}`);
  }

  subirExcel(formData: FormData): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/upload/excel`, formData);
  }

  descargarPlantilla(): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/template/excel`, {
      responseType: 'blob'
    });
  }
}