import { Component, OnInit } from '@angular/core';
import { UsuarioService } from '../../services/usuario.service';
import { AlertService } from '../../services/alert.service';
import { Usuario } from '../../models/usuario.model';
import { EstadisticasUsuarios } from '../../models/estadisticas.model';

@Component({
  selector: 'app-usuarios',
  templateUrl: './usuarios.component.html',
  styleUrls: ['./usuarios.component.css']
})
export class UsuariosComponent implements OnInit {
  usuarios: Usuario[] = [];
  usuariosFiltrados: Usuario[] = [];
  loading: boolean = false;
  estadisticas: EstadisticasUsuarios | null = null;
  
  // Filtros
  searchTerm: string = '';
  
  // Paginación
  currentPage: number = 1;
  itemsPerPage: number = 10;
  totalPages: number = 1;

  // Modal de edición
  showEditModal: boolean = false;
  usuarioEditando: Usuario = {
    id: 0,
    nombre: '',
    username: '',
    correo: '',
    user_passw: ''
  };
  editandoPassword: boolean = false;

  constructor(
    private usuarioService: UsuarioService,
    private alertService: AlertService
  ) {}

  ngOnInit(): void {
    this.cargarUsuarios();
    this.cargarEstadisticas();
  }

  cargarUsuarios(): void {
    this.loading = true;
    this.usuarioService.getUsuarios().subscribe({
      next: (response) => {
        this.loading = false;
        
        // 🔍 DEBUG: Ver qué datos llegan del backend
        console.log('📊 Respuesta completa del backend:', response);
        console.log('👥 Usuarios recibidos:', response.data);
        if (response.data && response.data.length > 0) {
          console.log('🔍 Primer usuario (ejemplo):', response.data[0]);
          console.log('📅 Campo created_at del primer usuario:', response.data[0].created_at);
        }
        
        if (response.status === 'success' && response.data) {
          this.usuarios = response.data;
          this.usuariosFiltrados = [...this.usuarios];
          this.calcularPaginacion();
        }
      },
      error: (error) => {
        this.loading = false;
        console.error('❌ Error al cargar usuarios:', error);
        this.alertService.error('Error al cargar usuarios', error.message);
      }
    });
  }

  cargarEstadisticas(): void {
    this.usuarioService.getEstadisticas().subscribe({
      next: (response) => {
        if (response.status === 'success' && response.data) {
          this.estadisticas = response.data;
        }
      },
      error: (error) => {
        console.error('Error cargando estadísticas:', error);
      }
    });
  }

  filtrarUsuarios(): void {
    if (!this.searchTerm.trim()) {
      this.usuariosFiltrados = [...this.usuarios];
    } else {
      const term = this.searchTerm.toLowerCase();
      this.usuariosFiltrados = this.usuarios.filter(user =>
        user.nombre.toLowerCase().includes(term) ||
        user.username.toLowerCase().includes(term) ||
        user.correo.toLowerCase().includes(term)
      );
    }
    this.currentPage = 1;
    this.calcularPaginacion();
  }

  calcularPaginacion(): void {
    this.totalPages = Math.ceil(this.usuariosFiltrados.length / this.itemsPerPage);
  }

  get usuariosPaginados(): Usuario[] {
    const start = (this.currentPage - 1) * this.itemsPerPage;
    const end = start + this.itemsPerPage;
    return this.usuariosFiltrados.slice(start, end);
  }

  cambiarPagina(page: number): void {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
    }
  }

  get paginasArray(): number[] {
    return Array.from({ length: this.totalPages }, (_, i) => i + 1);
  }

  // ============================================
  // FUNCIONES DE EDICIÓN
  // ============================================

  abrirModalEditar(usuario: Usuario): void {
    this.usuarioEditando = {
      id: usuario.id,
      nombre: usuario.nombre,
      username: usuario.username,
      correo: usuario.correo,
      user_passw: '' // No mostramos la contraseña actual
    };
    this.editandoPassword = false;
    this.showEditModal = true;
  }

  cerrarModalEditar(): void {
    this.showEditModal = false;
    this.usuarioEditando = {
      id: 0,
      nombre: '',
      username: '',
      correo: '',
      user_passw: ''
    };
    this.editandoPassword = false;
  }

  guardarEdicion(): void {
    // Validaciones
    if (!this.usuarioEditando.nombre || !this.usuarioEditando.username || !this.usuarioEditando.correo) {
      this.alertService.warning('Campos incompletos', 'Por favor completa todos los campos obligatorios');
      return;
    }

    if (this.usuarioEditando.username.length < 3) {
      this.alertService.warning('Username inválido', 'El username debe tener al menos 3 caracteres');
      return;
    }

    // Validar email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(this.usuarioEditando.correo)) {
      this.alertService.warning('Email inválido', 'Por favor ingresa un email válido');
      return;
    }

    // Si está editando la contraseña, validarla
    if (this.editandoPassword) {
      if (!this.usuarioEditando.user_passw || this.usuarioEditando.user_passw.length < 6) {
        this.alertService.warning('Contraseña inválida', 'La contraseña debe tener al menos 6 caracteres');
        return;
      }
    } else {
      // Si no está editando password, usar una temporal para el backend
      this.usuarioEditando.user_passw = 'temp_password_123456';
    }

    // Guardar
    this.loading = true;
    this.usuarioService.updateUsuario(this.usuarioEditando.id!, this.usuarioEditando).subscribe({
      next: (response) => {
        this.loading = false;
        if (response.status === 'success') {
          this.alertService.success('Usuario actualizado', 'Los cambios se guardaron correctamente');
          this.cerrarModalEditar();
          this.cargarUsuarios();
          this.cargarEstadisticas();
        }
      },
      error: (error) => {
        this.loading = false;
        this.alertService.error('Error al actualizar', error.message);
      }
    });
  }

  eliminarUsuario(id: number, username: string): void {
    this.alertService.confirm(
      '¿Eliminar usuario?',
      `¿Estás seguro de eliminar al usuario "${username}"? Esta acción no se puede deshacer.`,
      'Sí, eliminar',
      'Cancelar'
    ).then((result) => {
      if (result.isConfirmed) {
        this.usuarioService.deleteUsuario(id).subscribe({
          next: () => {
            this.alertService.success('Usuario eliminado', `El usuario "${username}" ha sido eliminado`);
            this.cargarUsuarios();
            this.cargarEstadisticas();
          },
          error: (error) => {
            this.alertService.error('Error al eliminar', error.message);
          }
        });
      }
    });
  }

  exportarExcel(): void {
    this.alertService.info('Función próximamente', 'La exportación a Excel estará disponible pronto');
  }

  limpiarFiltros(): void {
    this.searchTerm = '';
    this.filtrarUsuarios();
  }
}