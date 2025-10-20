import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:8000/api/user/Login';
  private isLoggedIn = false;

  constructor(private http: HttpClient) {
    this.isLoggedIn = !!localStorage.getItem('usuario');
  }

  login(username: string, user_passw: string): Observable<any> {
    return this.http.post<any>(this.apiUrl, { username, user_passw });
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