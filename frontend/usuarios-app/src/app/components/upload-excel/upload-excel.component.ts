import { Component } from '@angular/core';
import { UsuarioService } from '../../services/usuario.service';

@Component({
  selector: 'app-upload-excel',
  templateUrl: './upload-excel.component.html',
  styleUrls: ['./upload-excel.component.css']
})
export class UploadExcelComponent {
  selectedFile: File | null = null;
  loading = false;
  mensaje = '';
  tipoMensaje = '';
  resultado: any = null;

  constructor(private usuarioService: UsuarioService) { }

  onFileSelected(event: any): void {
    this.selectedFile = event.target.files[0];
  }

  subirArchivo(): void {
    if (!this.selectedFile) {
      this.mensaje = 'Por favor selecciona un archivo';
      this.tipoMensaje = 'danger';
      return;
    }

    this.loading = true;
    this.mensaje = '';

    const formData = new FormData();
    formData.append('file', this.selectedFile);

    // Necesitas agregar este método en UsuarioService
    this.usuarioService.subirExcel(formData).subscribe(
      (response) => {
        this.resultado = response;
        this.mensaje = 'Carga completada exitosamente';
        this.tipoMensaje = 'success';
        this.selectedFile = null;
        this.loading = false;
      },
      (error) => {
        this.mensaje = error.error.detail || 'Error al subir el archivo';
        this.tipoMensaje = 'danger';
        this.loading = false;
      }
    );
  }

  descargarPlantilla(): void {
    this.usuarioService.descargarPlantilla().subscribe(
      (response: any) => {
        const url = window.URL.createObjectURL(response);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'plantilla_usuarios.xlsx';
        a.click();
      },
      (error) => {
        this.mensaje = 'Error al descargar la plantilla';
        this.tipoMensaje = 'danger';
      }
    );
  }
}