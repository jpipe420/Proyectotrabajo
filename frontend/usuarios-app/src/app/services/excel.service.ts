import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { ApiResponse } from '../models/api-response.model';
import {
  ExcelAnalysisResponse,
  ConfirmacionCarga,
  ConfirmacionResponse
} from '../models/excel-analysis.model';

@Injectable({
  providedIn: 'root'
})
export class ExcelService {
  private apiUrl = `${environment.apiUrl}/api/user`;

  constructor(private http: HttpClient) {}

  analyzeExcel(file: File): Observable<ApiResponse<ExcelAnalysisResponse>> {
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post<ApiResponse<ExcelAnalysisResponse>>(
      `${this.apiUrl}/upload/excel/analyze`,
      formData
    ).pipe(
      catchError(this.handleError)
    );
  }

  confirmUpload(data: ConfirmacionCarga): Observable<ApiResponse<ConfirmacionResponse>> {
    return this.http.post<ApiResponse<ConfirmacionResponse>>(
      `${this.apiUrl}/upload/excel/confirm`,
      data
    ).pipe(
      catchError(this.handleError)
    );
  }

  downloadTemplate(): Observable<Blob> {
    return this.http.get(
      `${this.apiUrl}/template/excel`,
      { responseType: 'blob' }
    ).pipe(
      catchError(this.handleError)
    );
  }

  getExcelRequirements(): Observable<ApiResponse<any>> {
    return this.http.get<ApiResponse<any>>(
      `${this.apiUrl}/excel/requirements`
    ).pipe(
      catchError(this.handleError)
    );
  }

  private handleError(error: any) {
    console.error('Error en ExcelService:', error);
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