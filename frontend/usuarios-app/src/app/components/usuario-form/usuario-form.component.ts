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

  constructor(private usuarioService: UsuarioService) { }

  ngOnInit(): void {
    if (this.usuario) {
      this.esEdicion = true;
      this.form = { ...this.usuario };
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
      this.usuarioService.actualizarUsuario(this.usuario.id, this.form).subscribe(
        () => {
          this.loading = false;
          this.guardado.emit();
        },
        (error) => {
          this.error = 'Error al actualizar el usuario';
          console.error(error);
          this.loading = false;
        }
      );
    } else {
      this.usuarioService.crearUsuario(this.form).subscribe(
        () => {
          this.loading = false;
          this.guardado.emit();
        },
        (error) => {
          this.error = 'Error al crear el usuario';
          console.error(error);
          this.loading = false;
        }
      );
    }
  }

  cancelar(): void {
    this.cerrar.emit();
  }
}