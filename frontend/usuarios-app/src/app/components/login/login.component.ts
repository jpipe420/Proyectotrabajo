import { Component } from '@angular/core';
import { Router } from '@angular/router';
// Importamos la interfaz para asegurar el tipado
import { AuthService, LoginData } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  username = '';
  // 1. Renombramos a 'password' para ser coherentes con el backend y el servicio
  password = ''; 
  error = '';
  loading = false;

  constructor(private authService: AuthService, private router: Router) { }

  login(): void {
    this.error = '';
    this.loading = true;

    // Usamos 'password' en la validación
    if (!this.username || !this.password) { 
      this.error = 'Por favor completa todos los campos';
      this.loading = false;
      return;
    }

    // 2. Creamos el objeto que espera el servicio
    const loginData: LoginData = {
        username: this.username,
        password: this.password
    };

    // 3. Llamamos al servicio con el objeto
    this.authService.login(loginData).subscribe( 
      (response) => {
          // 4. El backend ahora devuelve un objeto, no un string
        if (response.message === 'Success') { 
          this.authService.setUsuario({ username: this.username });
          this.router.navigate(['/usuarios']);
        } else {
              // Esto debería ser raro si el backend maneja el 401 correctamente
            this.error = 'Usuario o contraseña incorrectos';
        }
        this.loading = false;
      },
      (error) => {
          // El backend ahora devuelve 401 si falla el login
          if (error.status === 401) {
              this.error = 'Usuario o contraseña incorrectos';
          } else {
              this.error = 'Error en la conexión con el servidor';
          }
        console.error(error);
        this.loading = false;
      }
    );
  }
}