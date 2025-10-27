import { Component, OnInit, ViewChild } from '@angular/core';
import { ExcelService } from '../../services/excel.service';
import { UsuarioService } from '../../services/usuario.service';
import { AlertService } from '../../services/alert.service';
import { 
  HojaAnalisis, 
  RegistroExcel, 
  ExcelAnalysisResponse 
} from '../../models/excel-analysis.model';
import { Usuario } from '../../models/usuario.model';
import { EstadisticasUsuarios } from '../../models/estadisticas.model';
import { ChartConfiguration, ChartData, ChartType } from 'chart.js';
import { BaseChartDirective } from 'ng2-charts';

@Component({
  selector: 'app-upload-excel',
  templateUrl: './upload-excel.component.html',
  styleUrls: ['./upload-excel.component.css']
})
export class UploadExcelComponent implements OnInit {
  @ViewChild(BaseChartDirective) chart?: BaseChartDirective;

  // Estados del flujo
  currentStep: number = 1; // 1: Upload, 2: Preview, 3: Resultados
  loading: boolean = false;

  // Archivo seleccionado
  selectedFile: File | null = null;
  fileName: string = '';

  // Análisis del Excel
  analysisData: ExcelAnalysisResponse | null = null;
  selectedSheet: HojaAnalisis | null = null;
  editableData: RegistroExcel[] = [];

  // Usuarios guardados
  usuarios: Usuario[] = [];

  // Estadísticas
  estadisticas: EstadisticasUsuarios | null = null;

  // Configuración de gráficos
  public barChartType: ChartType = 'bar';
  public pieChartType: ChartType = 'pie';
  public lineChartType: ChartType = 'line';

  // Datos para gráfico de usuarios por mes
  public barChartData: ChartData<'bar'> = {
    labels: [],
    datasets: [{
      data: [],
      label: 'Usuarios Registrados',
      backgroundColor: 'rgba(79, 70, 229, 0.7)',
      borderColor: 'rgba(79, 70, 229, 1)',
      borderWidth: 1
    }]
  };

  public barChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top'
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          precision: 0
        }
      }
    }
  };

  // Datos para gráfico de dominios
  public pieChartData: ChartData<'pie'> = {
    labels: [],
    datasets: [{
      data: [],
      backgroundColor: [
        'rgba(79, 70, 229, 0.7)',
        'rgba(34, 197, 94, 0.7)',
        'rgba(251, 146, 60, 0.7)',
        'rgba(239, 68, 68, 0.7)',
        'rgba(168, 85, 247, 0.7)',
        'rgba(236, 72, 153, 0.7)',
        'rgba(14, 165, 233, 0.7)',
        'rgba(250, 204, 21, 0.7)'
      ]
    }]
  };

  public pieChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'right'
      }
    }
  };

  constructor(
    private excelService: ExcelService,
    private usuarioService: UsuarioService,
    private alertService: AlertService
  ) {}

  ngOnInit(): void {
    this.loadUsuarios();
    this.loadEstadisticas();
  }

  // ========================================
  // PASO 1: SUBIR ARCHIVO
  // ========================================

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      // Validar extensión
      const allowedExtensions = ['xlsx', 'xls'];
      const fileExtension = file.name.split('.').pop()?.toLowerCase();

      if (!fileExtension || !allowedExtensions.includes(fileExtension)) {
        this.alertService.error(
          'Archivo no válido',
          'Solo se permiten archivos .xlsx o .xls'
        );
        event.target.value = '';
        return;
      }

      this.selectedFile = file;
      this.fileName = file.name;
    }
  }

  uploadExcel(): void {
    if (!this.selectedFile) {
      this.alertService.warning('Por favor selecciona un archivo');
      return;
    }

    this.loading = true;
    this.alertService.loading('Analizando archivo Excel...');

    this.excelService.analyzeExcel(this.selectedFile).subscribe({
      next: (response) => {
        this.alertService.closeLoading();
        this.loading = false;

        if (response.status === 'success' && response.data) {
          this.analysisData = response.data;

          if (this.analysisData.hojas_validas.length > 0) {
            // Seleccionar primera hoja válida
            this.selectSheet(this.analysisData.hojas_validas[0]);
            this.currentStep = 2;
            this.alertService.success('Análisis completado', response.message);
          } else {
            this.alertService.error(
              'No hay hojas válidas',
              'El archivo no contiene hojas con la estructura correcta'
            );
          }
        }
      },
      error: (error) => {
        this.alertService.closeLoading();
        this.loading = false;
        this.alertService.error('Error al analizar archivo', error.message);
      }
    });
  }

  downloadTemplate(): void {
    this.loading = true;
    
    this.excelService.downloadTemplate().subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'plantilla_usuarios_multihojas.xlsx';
        link.click();
        window.URL.revokeObjectURL(url);
        
        this.loading = false;
        this.alertService.toast('Plantilla descargada', 'success');
      },
      error: (error) => {
        this.loading = false;
        this.alertService.error('Error al descargar plantilla', error.message);
      }
    });
  }

  // ========================================
  // PASO 2: PREVIEW Y EDICIÓN
  // ========================================

  selectSheet(hoja: HojaAnalisis): void {
    this.selectedSheet = hoja;
    // Clonar datos para edición
    this.editableData = JSON.parse(JSON.stringify(hoja.datos));
    
    // Marcar registros válidos como seleccionados por defecto
    this.editableData.forEach(registro => {
      registro.selected = registro.estado_validacion === 'valido';
      registro.editing = false;
    });
  }

  toggleRowSelection(index: number): void {
    this.editableData[index].selected = !this.editableData[index].selected;
  }

  toggleAllRows(): void {
    const allSelected = this.editableData.every(r => r.selected);
    this.editableData.forEach(registro => {
      registro.selected = !allSelected;
    });
  }

  enableEdit(index: number): void {
    this.editableData[index].editing = true;
  }

  saveEdit(index: number): void {
    this.editableData[index].editing = false;
    // Validar datos editados
    const registro = this.editableData[index];
    
    if (!registro.nombre || !registro.username || !registro.correo || !registro.user_passw) {
      this.alertService.warning('Campos incompletos', 'Todos los campos son requeridos');
      this.editableData[index].editing = true;
      return;
    }

    if (registro.username.length < 3) {
      this.alertService.warning('Username debe tener al menos 3 caracteres');
      this.editableData[index].editing = true;
      return;
    }

    if (registro.user_passw.length < 6) {
      this.alertService.warning('Contraseña debe tener al menos 6 caracteres');
      this.editableData[index].editing = true;
      return;
    }

    this.alertService.toast('Registro actualizado', 'success');
  }

  cancelEdit(index: number): void {
    // Restaurar valores originales
    if (this.selectedSheet) {
      this.editableData[index] = JSON.parse(
        JSON.stringify(this.selectedSheet.datos[index])
      );
    }
  }

  getSelectedCount(): number {
    return this.editableData.filter(r => r.selected).length;
  }

  confirmUpload(): void {
    const selectedRecords = this.editableData.filter(r => r.selected);

    if (selectedRecords.length === 0) {
      this.alertService.warning('Debes seleccionar al menos un registro');
      return;
    }

    this.alertService.confirm(
      '¿Confirmar carga?',
      `Se guardarán ${selectedRecords.length} usuario(s) en la base de datos`,
      'Sí, guardar',
      'Cancelar'
    ).then((result) => {
      if (result.isConfirmed) {
        this.saveToDatabase(selectedRecords);
      }
    });
  }

  saveToDatabase(records: RegistroExcel[]): void {
    this.loading = true;
    this.alertService.loading('Guardando usuarios...');

    const registros = records.map(r => ({
      nombre: r.nombre,
      username: r.username,
      correo: r.correo,
      user_passw: r.user_passw
    }));

    this.excelService.confirmUpload({ registros }).subscribe({
      next: (response) => {
        this.alertService.closeLoading();
        this.loading = false;

        if (response.status === 'success' && response.data) {
          this.alertService.success(
            '¡Carga exitosa!',
            `Se guardaron ${response.data.usuarios_creados} usuario(s)`
          );
          
          // Recargar datos
          this.loadUsuarios();
          this.loadEstadisticas();
          
          // Ir a vista de resultados
          this.currentStep = 3;
        } else if (response.status === 'warning' && response.data) {
          // Carga con errores
          this.alertService.warning(
            'Carga parcial',
            response.message
          );
          
          if (response.errors && response.errors.length > 0) {
            setTimeout(() => {
              this.alertService.errorList('Errores encontrados:', response.errors!);
            }, 500);
          }
          
          this.loadUsuarios();
          this.loadEstadisticas();
          this.currentStep = 3;
        }
      },
      error: (error) => {
        this.alertService.closeLoading();
        this.loading = false;
        this.alertService.error('Error al guardar', error.message);
      }
    });
  }

  // ========================================
  // PASO 3: RESULTADOS Y ESTADÍSTICAS
  // ========================================

  loadUsuarios(): void {
    this.usuarioService.getUsuarios().subscribe({
      next: (response) => {
        if (response.status === 'success' && response.data) {
          this.usuarios = response.data;
        }
      },
      error: (error) => {
        console.error('Error cargando usuarios:', error);
      }
    });
  }

  loadEstadisticas(): void {
    this.usuarioService.getEstadisticas().subscribe({
      next: (response) => {
        if (response.status === 'success' && response.data) {
          this.estadisticas = response.data;
          this.updateCharts();
        }
      },
      error: (error) => {
        console.error('Error cargando estadísticas:', error);
      }
    });
  }

  updateCharts(): void {
    if (!this.estadisticas) return;

    // Actualizar gráfico de barras (usuarios por mes)
    this.barChartData.labels = this.estadisticas.usuarios_por_mes.map(m => m.mes_nombre);
    this.barChartData.datasets[0].data = this.estadisticas.usuarios_por_mes.map(m => m.cantidad);

    // Actualizar gráfico de pie (dominios)
    this.pieChartData.labels = this.estadisticas.usuarios_por_dominio.map(d => d.dominio);
    this.pieChartData.datasets[0].data = this.estadisticas.usuarios_por_dominio.map(d => d.cantidad);

    // Actualizar gráficos
    this.chart?.update();
  }

  deleteUsuario(id: number): void {
    this.alertService.confirm(
      '¿Eliminar usuario?',
      'Esta acción no se puede deshacer',
      'Sí, eliminar',
      'Cancelar'
    ).then((result) => {
      if (result.isConfirmed) {
        this.usuarioService.deleteUsuario(id).subscribe({
          next: () => {
            this.alertService.success('Usuario eliminado');
            this.loadUsuarios();
            this.loadEstadisticas();
          },
          error: (error) => {
            this.alertService.error('Error al eliminar', error.message);
          }
        });
      }
    });
  }

  // ========================================
  // UTILIDADES
  // ========================================

  resetUploader(): void {
    this.currentStep = 1;
    this.selectedFile = null;
    this.fileName = '';
    this.analysisData = null;
    this.selectedSheet = null;
    this.editableData = [];
  }

  goToStep(step: number): void {
    this.currentStep = step;
  }

  getStatusBadgeClass(estado: string): string {
    switch(estado) {
      case 'valido':
        return 'badge bg-success';
      case 'duplicado_bd':
        return 'badge bg-warning';
      default:
        return 'badge bg-danger';
    }
  }

  getStatusText(estado: string): string {
    switch(estado) {
      case 'valido':
        return 'Válido';
      case 'duplicado_bd':
        return 'Duplicado';
      default:
        return 'Error';
    }
  }
}