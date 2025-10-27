import { Component, OnInit } from '@angular/core';
import { UsuarioService } from '../../services/usuario.service';
import { AlertService } from '../../services/alert.service';
import { Usuario } from '../../models/usuario.model';

@Component({
  selector: 'app-usuarios',
  templateUrl: './usuarios.component.html',
  styleUrls: ['./usuarios.component.css']
})
export class UsuariosComponent implements OnInit {
  usuarios: Usuario[] = [];
  loading: boolean = false;
  usuarioEditar: Usuario | null = null;
  mostrarFormulario: boolean = false;

  constructor(
    private usuarioService: UsuarioService,
    private alertService: AlertService
  ) {}

  ngOnInit(): void {
    this.cargarUsuarios();
  }

  cargarUsuarios(): void {
    this.loading = true;
    this.usuarioService.getUsuarios().subscribe({
      next: (response) => {
        this.loading = false;
        if (response.status === 'success' && response.data) {
          this.usuarios = response.data;
        }
      },
      error: (error) => {
        this.loading = false;
        this.alertService.error('Error al cargar usuarios', error.message);
      }
    });
  }

  editarUsuario(usuario: Usuario): void {
    this.usuarioEditar = { ...usuario };
    this.mostrarFormulario = true;
  }

  eliminarUsuario(id: number): void {
    this.alertService.confirm(
      '¿Eliminar usuario?',
      'Esta acción no se puede deshacer',
      'Sí, eliminar',
      'Cancelar'
    ).then((result) => {
      if (result.isConfirmed) {
        this.usuarioService.deleteUsuario(id).subscribe({
          next: () => {
            this.alertService.success('Usuario eliminado exitosamente');
            this.cargarUsuarios();
          },
          error: (error) => {
            this.alertService.error('Error al eliminar', error.message);
          }
        });
      }
    });
  }

  nuevoUsuario(): void {
    this.usuarioEditar = null;
    this.mostrarFormulario = true;
  }

  cerrarFormulario(): void {
    this.mostrarFormulario = false;
    this.usuarioEditar = null;
  }

  usuarioGuardado(): void {
    this.cerrarFormulario();
    this.cargarUsuarios();
  }
}