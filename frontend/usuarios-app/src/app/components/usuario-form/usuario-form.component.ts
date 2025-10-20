import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { UsuarioService } from '../../services/usuario.service';

@Component({
  selector: 'app-usuario-form',
  templateUrl: './usuario-form.component.html',
  styleUrls: ['./usuario-form.component.css']
})
export class UsuarioFormComponent implements OnInit {
  @Input() usuario: any = null;
  @Output() cerrar = new EventEmitter<void>();
  @Output() guardado = new EventEmitter<void>();

  form = {
    nombre: '',
    username: '',
    correo: '',
    user_passw: ''
  };

  error = '';
  loading = false;
  esEdicion = false;
  usuarioId: any = null;

  constructor(private usuarioService: UsuarioService) { }

  ngOnInit(): void {
    if (this.usuario) {
      this.esEdicion = true;
      this.usuarioId = this.usuario.id;
      this.form = {
        nombre: this.usuario.nombre || '',
        username: this.usuario.username || '',
        correo: this.usuario.correo || '',
        user_passw: this.usuario.user_passw || ''
      };
    }
  }

  guardar(): void {
    this.error = '';

    if (!this.form.nombre || !this.form.username || !this.form.correo || !this.form.user_passw) {
      this.error = 'Por favor completa todos los campos';
      return;
    }

    this.loading = true;

    if (this.esEdicion) {
      this.usuarioService.actualizarUsuario(this.usuarioId, this.form).subscribe(
        (response) => {
          console.log('Respuesta del servidor:', response);
          this.loading = false;
          this.guardado.emit();
        },
        (error) => {
          console.error('Error completo:', error);
          this.error = 'Error al actualizar el usuario: ' + (error.error?.detail || error.message || 'Error desconocido');
          this.loading = false;
        }
      );
    } else {
      this.usuarioService.crearUsuario(this.form).subscribe(
        (response) => {
          console.log('Usuario creado:', response);
          this.loading = false;
          this.guardado.emit();
        },
        (error) => {
          console.error('Error al crear:', error);
          this.error = 'Error al crear el usuario: ' + (error.error?.detail || error.message || 'Error desconocido');
          this.loading = false;
        }
      );
    }
  }

  cancelar(): void {
    this.cerrar.emit();
  }
}