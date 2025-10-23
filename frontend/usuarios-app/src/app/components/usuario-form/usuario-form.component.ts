import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { UsuarioService } from '../../services/usuario.service';

// Definimos una Interfaz para el Formulario
interface UsuarioForm {
  nombre: string;
  username: string;
  correo: string;
  user_passw: string;
}

@Component({
  selector: 'app-usuario-form',
  templateUrl: './usuario-form.component.html',
  styleUrls: ['./usuario-form.component.css']
})
export class UsuarioFormComponent implements OnInit {
  // Declaración de tipos explícita
  @Input() usuario: any = null;
  @Output() cerrar = new EventEmitter<void>();
  @Output() guardado = new EventEmitter<void>();

  // Tipamos e inicializamos el objeto form
  form: UsuarioForm = {
    nombre: '',
    username: '',
    correo: '',
    user_passw: ''
  };

  // Tipado de variables simples
  error: string = '';
  loading: boolean = false;
  esEdicion: boolean = false;
  usuarioId: number | null = null;

  constructor(private usuarioService: UsuarioService) { }

  ngOnInit(): void {
    if (this.usuario) {
      this.esEdicion = true;
      // Asumimos que el ID es un número cuando se recibe un usuario
      this.usuarioId = this.usuario.id;
      
      this.form = {
        nombre: this.usuario.nombre || '',
        username: this.usuario.username || '',
        correo: this.usuario.correo || '',
        // Al editar, la contraseña se puede dejar vacía para no cambiarla
        user_passw: this.usuario.user_passw || '' 
      };
    }
  }

  guardar(): void {
    this.error = '';

    // Validación de campos requeridos
    if (!this.form.nombre || !this.form.username || !this.form.correo || (!this.esEdicion && !this.form.user_passw)) {
      this.error = 'Por favor completa todos los campos requeridos (la contraseña solo es obligatoria al crear)';
      return;
    }

    this.loading = true;

    if (this.esEdicion) {
          // CORRECCIÓN TS2345: Usamos el operador '!' (non-null assertion) para indicar
          // que 'usuarioId' no puede ser nulo dentro de este bloque 'esEdicion'.
      this.usuarioService.actualizarUsuario(this.usuarioId!, this.form).subscribe(
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