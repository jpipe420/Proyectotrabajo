import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

// --- INTERFACES DE DATOS (Asegúrate que coincidan con tu backend Pydantic) ---
export interface Product {
  id?: number; // Opcional para la creación
  referencia: string;
  nombre: string;
  descripcion: string;
  precio: number;
  stock: number;
}

@Injectable({
  providedIn: 'root'
})
export class ProductService {
  // La base URL se obtiene del entorno (que ya corregimos a http://backend:8000)
  private baseUrl = environment.apiUrl + '/api/products'; 

  constructor(private http: HttpClient) { }

  // ----------------------
  // CRUD - Peticiones
  // ----------------------

  // OBTENER TODOS LOS PRODUCTOS (R - Read All)
  getProducts(): Observable<Product[]> {
    return this.http.get<Product[]>(this.baseUrl);
  }

  // OBTENER UN PRODUCTO POR ID (R - Read One)
  getProductById(id: number): Observable<Product> {
    return this.http.get<Product>(`${this.baseUrl}/${id}`);
  }

  // CREAR UN NUEVO PRODUCTO (C - Create)
  createProduct(product: Product): Observable<Product> {
    return this.http.post<Product>(this.baseUrl, product);
  }

  // ACTUALIZAR UN PRODUCTO (U - Update)
  updateProduct(id: number, product: Partial<Product>): Observable<Product> {
    return this.http.put<Product>(`${this.baseUrl}/${id}`, product);
  }

  // ELIMINAR UN PRODUCTO (D - Delete)
  deleteProduct(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }
}