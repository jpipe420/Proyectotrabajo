import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  username = '';
  user_passw = '';
  error = '';
  loading = false;

  constructor(private authService: AuthService, private router: Router) { }

  login(): void {
    this.error = '';
    this.loading = true;

    if (!this.username || !this.user_passw) {
      this.error = 'Por favor completa todos los campos';
      this.loading = false;
      return;
    }

    this.authService.login(this.username, this.user_passw).subscribe(
      (response) => {
        if (response === 'Succes') {
          this.authService.setUsuario({ username: this.username });
          this.router.navigate(['/usuarios']);
        } else {
          this.error = 'Usuario o contraseña incorrectos';
        }
        this.loading = false;
      },
      (error) => {
        this.error = 'Error en la conexión con el servidor';
        console.error(error);
        this.loading = false;
      }
    );
  }
}