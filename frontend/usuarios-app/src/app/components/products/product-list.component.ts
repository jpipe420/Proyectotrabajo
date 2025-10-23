import { Component, OnInit } from '@angular/core';
import { Product, ProductService } from 'src/app/services/product.service'; // Asegúrese de ajustar la ruta de importación si es necesario

@Component({
  selector: 'app-product-list',
  templateUrl: './product-list.component.html',
  styleUrls: ['./product-list.component.css']
})
export class ProductListComponent implements OnInit {
  products: Product[] = [];
  errorMessage: string = '';
  
  // Modelo para el formulario de creación/edición
  newProduct: Product = {
    referencia: '',
    nombre: '',
    descripcion: '',
    precio: 0,
    stock: 0
  };
  isEditing: boolean = false;
  editingId: number | null = null;

  // Inyectamos el servicio
  constructor(private productService: ProductService) { }

  ngOnInit(): void {
    this.loadProducts();
  }

  loadProducts(): void {
    this.productService.getProducts().subscribe({
      next: (data) => {
        this.products = data;
        this.errorMessage = '';
      },
      error: (err) => {
        // Manejo de error si el backend no está disponible o falla
        this.errorMessage = 'Error al cargar productos: ' + (err.error?.detail || err.message);
        console.error('Error fetching products:', err);
      }
    });
  }
  
  // --- Manejo del Formulario ---

  submitForm(): void {
    if (this.isEditing && this.editingId !== null) {
      this.updateProduct();
    } else {
      this.createProduct();
    }
  }

  createProduct(): void {
    this.productService.createProduct(this.newProduct).subscribe({
      next: (product) => {
        // CORRECCIÓN DE SINTAXIS: Uso de comillas invertidas (`) para template literals
        alert(`Producto ${product.nombre} creado correctamente.`);
        this.loadProducts(); // Recargar la lista
        this.resetForm();
      },
      error: (err) => {
        alert('Error al crear: ' + (err.error?.detail || 'Error desconocido'));
        console.error('Error creating product:', err);
      }
    });
  }

  editProduct(product: Product): void {
    this.isEditing = true;
    this.editingId = product.id!;
    // Clona el objeto para evitar modificar la lista directamente
    this.newProduct = { ...product }; 
  }

  updateProduct(): void {
    if (this.editingId === null) return;

    this.productService.updateProduct(this.editingId, this.newProduct).subscribe({
      next: () => {
        alert('Producto actualizado correctamente.');
        this.loadProducts();
        this.resetForm();
      },
      error: (err) => {
        alert('Error al actualizar: ' + (err.error?.detail || 'Error desconocido'));
        console.error('Error updating product:', err);
      }
    });
  }

  deleteProduct(id: number): void {
    // Es mejor usar window.confirm para entornos que lo soportan, en lugar de solo confirm
    if (window.confirm('¿Estás seguro de que quieres eliminar este producto?')) {
      this.productService.deleteProduct(id).subscribe({
        next: () => {
          alert('Producto eliminado.');
          this.loadProducts();
        },
        error: (err) => {
          alert('Error al eliminar: ' + (err.error?.detail || 'Error desconocido'));
          console.error('Error deleting product:', err);
        }
      });
    }
  }

  resetForm(): void {
    this.isEditing = false;
    this.editingId = null;
    this.newProduct = {
      referencia: '', nombre: '', descripcion: '', precio: 0, stock: 0
    };
  }
}