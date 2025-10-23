import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent {
  // Hacemos el servicio público (public) para poder usar sus métodos en el HTML (ej. authService.estaAutenticado())
  constructor(public authService: AuthService, private router: Router) { } 

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  getUsuario(): string {
    const usuario = this.authService.getUsuario();
    // Añadimos una verificación para que no muestre 'Usuario' si el objeto está vacío al desloguearse.
    if (!this.authService.estaAutenticado()) {
      return '';
    }
    return usuario.username || 'Usuario';
  }
}