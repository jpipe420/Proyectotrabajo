import { Component, OnInit } from '@angular/core';
import { UsuarioService } from '../../services/usuario.service';

@Component({
  selector: 'app-usuarios',
  templateUrl: './usuarios.component.html',
  styleUrls: ['./usuarios.component.css']
})
export class UsuariosComponent implements OnInit {
  usuarios: any[] = [];
  loading = false;
  error = '';
  mostrarForm = false;
  usuarioEditar: any = null;

  constructor(private usuarioService: UsuarioService) { }

  ngOnInit(): void {
    this.cargarUsuarios();
  }

  cargarUsuarios(): void {
    this.loading = true;
    this.error = '';
    this.usuarioService.getUsuarios().subscribe(
      (data) => {
        this.usuarios = data;
        this.loading = false;
      },
      (error) => {
        this.error = 'Error al cargar los usuarios';
        console.error(error);
        this.loading = false;
      }
    );
  }

  abrirFormulario(): void {
    this.mostrarForm = true;
    this.usuarioEditar = null;
  }

  cerrarFormulario(): void {
    this.mostrarForm = false;
    this.usuarioEditar = null;
  }

  editar(usuario: any): void {
    this.usuarioEditar = { ...usuario };
    this.mostrarForm = true;
  }

  eliminar(id: number): void {
    if (confirm('¿Estás seguro de que deseas eliminar este usuario?')) {
      this.usuarioService.eliminarUsuario(id).subscribe(
        () => {
          this.cargarUsuarios();
        },
        (error) => {
          this.error = 'Error al eliminar el usuario';
          console.error(error);
        }
      );
    }
  }

  usuarioGuardado(): void {
    this.cargarUsuarios();
    this.cerrarFormulario();
  }
}