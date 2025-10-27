import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { UsuarioService } from '../../services/usuario.service';
import { AlertService } from '../../services/alert.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  username: string = '';
  password: string = '';
  loading: boolean = false;
  errorMessage: string = '';

  constructor(
    private usuarioService: UsuarioService,
    private alertService: AlertService,
    private router: Router
  ) {}

  onLogin(): void {
    // Validaciones básicas
    if (!this.username || !this.password) {
      this.errorMessage = 'Por favor ingrese usuario y contraseña';
      return;
    }

    this.loading = true;
    this.errorMessage = '';

    this.usuarioService.login(this.username, this.password).subscribe({
      next: (response) => {
        this.loading = false;
        
        // Verificar el status de la respuesta
        if (response.status === 'success') {
          // Guardar datos del usuario en localStorage
          localStorage.setItem('currentUser', this.username);
          localStorage.setItem('isLoggedIn', 'true');
          
          // Mostrar alerta de éxito
          this.alertService.success('¡Bienvenido!', `Login exitoso como ${this.username}`);
          
          // Redirigir al dashboard o usuarios
          setTimeout(() => {
            this.router.navigate(['/upload-excel']);
          }, 1000);
        } else {
          this.errorMessage = response.message || 'Error en el login';
        }
      },
      error: (error) => {
        this.loading = false;
        console.error('Error en login:', error);
        
        // Manejar diferentes tipos de error
        if (error.message) {
          this.errorMessage = error.message;
        } else if (error.error?.message) {
          this.errorMessage = error.error.message;
        } else {
          this.errorMessage = 'Usuario o contraseña incorrectos';
        }
        
        this.alertService.error('Error de autenticación', this.errorMessage);
      }
    });
  }
}