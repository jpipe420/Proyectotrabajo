import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AlertService } from '../../services/alert.service';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit {
  currentUser: string = '';
  isLoggedIn: boolean = false;

  constructor(
    private router: Router,
    private alertService: AlertService
  ) {}

  ngOnInit(): void {
    this.currentUser = localStorage.getItem('currentUser') || 'Usuario';
    this.isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
  }

  logout(): void {
    this.alertService.confirm(
      '¿Cerrar sesión?',
      '¿Estás seguro de que deseas salir?',
      'Sí, salir',
      'Cancelar'
    ).then((result) => {
      if (result.isConfirmed) {
        localStorage.removeItem('currentUser');
        localStorage.removeItem('isLoggedIn');
        this.alertService.success('Sesión cerrada', 'Hasta pronto');
        this.router.navigate(['/login']);
      }
    });
  }
}