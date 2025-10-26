import { Injectable } from '@angular/core';
import Swal from 'sweetalert2';

@Injectable({
  providedIn: 'root'
})
export class AlertService {

  success(title: string, message?: string): Promise<any> {
    return Swal.fire({
      icon: 'success',
      title: title,
      text: message,
      confirmButtonColor: '#4f46e5',
      timer: 3000
    });
  }

  error(title: string, message?: string): Promise<any> {
    return Swal.fire({
      icon: 'error',
      title: title,
      text: message,
      confirmButtonColor: '#ef4444'
    });
  }

  warning(title: string, message?: string): Promise<any> {
    return Swal.fire({
      icon: 'warning',
      title: title,
      text: message,
      confirmButtonColor: '#f59e0b'
    });
  }

  info(title: string, message?: string): Promise<any> {
    return Swal.fire({
      icon: 'info',
      title: title,
      text: message,
      confirmButtonColor: '#3b82f6'
    });
  }

  confirm(
    title: string,
    message: string,
    confirmText: string = 'Sí, continuar',
    cancelText: string = 'Cancelar'
  ): Promise<any> {
    return Swal.fire({
      title: title,
      text: message,
      icon: 'question',
      showCancelButton: true,
      confirmButtonColor: '#4f46e5',
      cancelButtonColor: '#6b7280',
      confirmButtonText: confirmText,
      cancelButtonText: cancelText
    });
  }

  errorList(title: string, errors: string[]): Promise<any> {
    const errorHtml = errors.map(err => `<li class="text-left">${err}</li>`).join('');
    
    return Swal.fire({
      icon: 'error',
      title: title,
      html: `<ul class="text-sm">${errorHtml}</ul>`,
      confirmButtonColor: '#ef4444'
    });
  }

  loading(title: string = 'Procesando...'): void {
    Swal.fire({
      title: title,
      allowOutsideClick: false,
      allowEscapeKey: false,
      didOpen: () => {
        Swal.showLoading();
      }
    });
  }

  closeLoading(): void {
    Swal.close();
  }

  toast(message: string, icon: 'success' | 'error' | 'warning' | 'info' = 'success'): void {
    const Toast = Swal.mixin({
      toast: true,
      position: 'top-end',
      showConfirmButton: false,
      timer: 3000,
      timerProgressBar: true
    });

    Toast.fire({
      icon: icon,
      title: message
    });
  }
}