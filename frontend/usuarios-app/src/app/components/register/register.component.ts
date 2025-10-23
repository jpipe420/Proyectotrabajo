import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService, RegisterData } from '../../services/auth.service'; // Importamos RegisterData
import { Router } from '@angular/router';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent implements OnInit {
  registerForm: FormGroup;
  errorMessage: string = '';
  successMessage: string = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    // Inicializa el formulario reactivo
    this.registerForm = this.fb.group({
      nombre: ['', Validators.required],
      username: ['', Validators.required],
      // Utilizamos Validators.email para validar el formato
      correo: ['', [Validators.required, Validators.email]], 
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  ngOnInit(): void { }

  onSubmit(): void {
    this.errorMessage = '';
    this.successMessage = '';

    if (this.registerForm.invalid) {
      this.errorMessage = 'Por favor, completa todos los campos válidos.';
      return;
    }
      
    const data: RegisterData = this.registerForm.value;

    this.authService.register(data).subscribe({
      next: (response) => {
        // Registro exitoso.
        this.successMessage = '¡Registro exitoso! Redirigiendo a Login...';
        
        // Limpiamos el formulario después del éxito
        this.registerForm.reset(); 
        
        // Redirigir al login después de un breve tiempo
        setTimeout(() => {
          this.router.navigate(['/login']); 
        }, 2000);
      },
      error: (error) => {
        // Manejamos el error 409 (Conflicto) de FastAPI
        if (error.status === 409) {
          this.errorMessage = error.error.detail || 'El usuario o correo ya están registrados.';
        } else {
          this.errorMessage = 'Error en el servidor al intentar registrar.';
        }
        console.error('Error de registro:', error);
      }
    });
  }
}