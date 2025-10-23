import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

// IMPORTACIONES DE COMPONENTES
import { ProductListComponent } from './components/products/product-list.component'; 
import { RegisterComponent } from './components/register/register.component';
import { LoginComponent } from './components/login/login.component'; 
import { UsuariosComponent } from './components/usuarios/usuarios.component'; // ¡Necesario para /usuarios!

const routes: Routes = [
  // RUTAS HABILITADAS
  { path: 'products', component: ProductListComponent }, // Ruta para Productos
  { path: 'usuarios', component: UsuariosComponent },    // Ruta para Usuarios (Arregla el error de inicio de sesión)
  { path: 'register', component: RegisterComponent },
  { path: 'login', component: LoginComponent },
  { path: '', redirectTo: '/login', pathMatch: 'full' }, 
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }