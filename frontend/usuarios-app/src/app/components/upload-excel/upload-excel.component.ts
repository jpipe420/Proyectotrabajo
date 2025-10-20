import { Component, Output, EventEmitter } from '@angular/core';
import { UsuarioService } from '../../services/usuario.service';

@Component({
  selector: 'app-upload-excel',
  templateUrl: './upload-excel.component.html',
  styleUrls: ['./upload-excel.component.css']
})
export class UploadExcelComponent {
  @Output() cerrar = new EventEmitter<void>();
  @Output() guardado = new EventEmitter<void>();

  selectedFile: File | null = null;
  loading = false;
  mensaje = '';
  tipoMensaje = '';
  resultado: any = null;

  constructor(private usuarioService: UsuarioService) { }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      const extension = file.name.split('.').pop()?.toLowerCase();
      if (extension === 'xlsx' || extension === 'xls') {
        this.selectedFile = file;
        this.mensaje = '';
      } else {
        this.mensaje = 'Solo se permiten archivos .xlsx o .xls';
        this.tipoMensaje = 'danger';
        this.selectedFile = null;
      }
    }
  }

  subirArchivo(): void {
    if (!this.selectedFile) {
      this.mensaje = 'Por favor selecciona un archivo';
      this.tipoMensaje = 'danger';
      return;
    }

    this.loading = true;
    this.mensaje = '';
    this.resultado = null;

    const formData = new FormData();
    formData.append('file', this.selectedFile);

    this.usuarioService.subirExcel(formData).subscribe(
      (response) => {
        this.resultado = response;
        this.mensaje = response.mensaje || 'Carga completada exitosamente';
        this.tipoMensaje = 'success';
        this.selectedFile = null;
        this.loading = false;
        
        // Resetear el input de archivo
        const fileInput = document.getElementById('archivo') as HTMLInputElement;
        if (fileInput) {
          fileInput.value = '';
        }
      },
      (error) => {
        console.error('Error:', error);
        this.mensaje = error.error?.detail || 'Error al subir el archivo';
        this.tipoMensaje = 'danger';
        this.loading = false;
      }
    );
  }

  descargarPlantilla(): void {
    this.usuarioService.descargarPlantilla().subscribe(
      (response: Blob) => {
        const url = window.URL.createObjectURL(response);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'plantilla_usuarios.xlsx';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      },
      (error) => {
        this.mensaje = 'Error al descargar la plantilla';
        this.tipoMensaje = 'danger';
      }
    );
  }

  cancelar(): void {
    this.cerrar.emit();
  }

  finalizar(): void {
    this.guardado.emit();
  }
}