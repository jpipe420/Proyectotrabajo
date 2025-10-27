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
import { ChartConfiguration } from 'chart.js';
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

  // Selección de hojas
  hojasSeleccionadas: Set<string> = new Set();

  // Usuarios guardados
  usuarios: Usuario[] = [];

  // Estadísticas
  estadisticas: EstadisticasUsuarios | null = null;

  // Gráfico de pastel - Usuarios por hoja cargada
  public pieChartData: ChartConfiguration<'pie'>['data'] = {
    labels: [],
    datasets: [{
      data: [],
      backgroundColor: [
        'rgba(79, 70, 229, 0.8)',
        'rgba(34, 197, 94, 0.8)',
        'rgba(251, 146, 60, 0.8)',
        'rgba(239, 68, 68, 0.8)',
        'rgba(168, 85, 247, 0.8)',
        'rgba(236, 72, 153, 0.8)',
        'rgba(14, 165, 233, 0.8)',
        'rgba(250, 204, 21, 0.8)'
      ],
      borderColor: [
        'rgba(79, 70, 229, 1)',
        'rgba(34, 197, 94, 1)',
        'rgba(251, 146, 60, 1)',
        'rgba(239, 68, 68, 1)',
        'rgba(168, 85, 247, 1)',
        'rgba(236, 72, 153, 1)',
        'rgba(14, 165, 233, 1)',
        'rgba(250, 204, 21, 1)'
      ],
      borderWidth: 2
    }]
  };

  public pieChartOptions: ChartConfiguration<'pie'>['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'right',
        labels: {
          font: {
            size: 12
          },
          padding: 15,
          generateLabels: (chart) => {
            const data = chart.data;
            if (data.labels && data.datasets.length) {
              return data.labels.map((label, i) => {
                const dataset = data.datasets[0];
                const value = dataset.data[i] as number;
                const total = (dataset.data as number[]).reduce((a, b) => a + b, 0);
                const percentage = ((value / total) * 100).toFixed(1);
                
                return {
                  text: `${label}: ${value} (${percentage}%)`,
                  fillStyle: (dataset.backgroundColor as string[])[i],
                  hidden: false,
                  index: i
                };
              });
            }
            return [];
          }
        }
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const label = context.label || '';
            const value = context.parsed;
            const total = (context.dataset.data as number[]).reduce((a, b) => a + b, 0);
            const percentage = ((value / total) * 100).toFixed(1);
            return `${label}: ${value} usuarios (${percentage}%)`;
          }
        }
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
            this.selectSheet(this.analysisData.hojas_validas[0]);
            this.currentStep = 2;
            
            // Seleccionar todas las hojas válidas por defecto
            this.hojasSeleccionadas.clear();
            this.analysisData.hojas_validas.forEach(hoja => {
              this.hojasSeleccionadas.add(hoja.nombre_hoja);
            });
            
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
    this.editableData = JSON.parse(JSON.stringify(hoja.datos));
    
    this.editableData.forEach(registro => {
      registro.selected = registro.estado_validacion === 'valido';
      registro.editing = false;
    });
  }

  toggleHojaSelection(nombreHoja: string): void {
    if (this.hojasSeleccionadas.has(nombreHoja)) {
      this.hojasSeleccionadas.delete(nombreHoja);
    } else {
      this.hojasSeleccionadas.add(nombreHoja);
    }
  }

  isHojaSelected(nombreHoja: string): boolean {
    return this.hojasSeleccionadas.has(nombreHoja);
  }

  getHojasSeleccionadasCount(): number {
    return this.hojasSeleccionadas.size;
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
    if (!this.analysisData) return;

    if (this.hojasSeleccionadas.size === 0) {
      this.alertService.warning('Debes seleccionar al menos una hoja para cargar');
      return;
    }

    // Recopilar todos los registros seleccionados de todas las hojas seleccionadas
    const todosLosRegistrosSeleccionados: any[] = [];
    
    this.analysisData.hojas_validas.forEach(hoja => {
      if (this.hojasSeleccionadas.has(hoja.nombre_hoja)) {
        const registrosDeEstaHoja = hoja.datos.filter(r => r.estado_validacion === 'valido');
        todosLosRegistrosSeleccionados.push(...registrosDeEstaHoja);
      }
    });

    if (todosLosRegistrosSeleccionados.length === 0) {
      this.alertService.warning('No hay registros válidos para cargar en las hojas seleccionadas');
      return;
    }

    const hojasNombres = Array.from(this.hojasSeleccionadas).join(', ');

    this.alertService.confirm(
      '¿Confirmar carga?',
      `Se cargarán ${todosLosRegistrosSeleccionados.length} usuario(s) de ${this.hojasSeleccionadas.size} hoja(s): ${hojasNombres}`,
      'Sí, cargar todo',
      'Cancelar'
    ).then((result) => {
      if (result.isConfirmed) {
        this.saveToDatabase(todosLosRegistrosSeleccionados);
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
            `Se guardaron ${response.data.usuarios_creados} usuario(s) de ${this.hojasSeleccionadas.size} hoja(s)`
          );
          
          this.loadUsuarios();
          this.loadEstadisticas();
          this.updateChartWithLoadedSheets();
          
          this.currentStep = 3;
        } else if (response.status === 'warning' && response.data) {
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
          this.updateChartWithLoadedSheets();
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

  updateChartWithLoadedSheets(): void {
    if (!this.analysisData) return;

    const labels: string[] = [];
    const data: number[] = [];

    this.analysisData.hojas_validas.forEach(hoja => {
      if (this.hojasSeleccionadas.has(hoja.nombre_hoja)) {
        labels.push(hoja.nombre_hoja);
        data.push(hoja.total_validos);
      }
    });

    this.pieChartData = {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: this.pieChartData.datasets[0].backgroundColor,
        borderColor: this.pieChartData.datasets[0].borderColor,
        borderWidth: 2
      }]
    };

    this.chart?.update();
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
        }
      },
      error: (error) => {
        console.error('Error cargando estadísticas:', error);
      }
    });
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

  resetUploader(): void {
    this.currentStep = 1;
    this.selectedFile = null;
    this.fileName = '';
    this.analysisData = null;
    this.selectedSheet = null;
    this.editableData = [];
    this.hojasSeleccionadas.clear();
  }

  goToStep(step: number): void {
    this.currentStep = step;
  }

  getStatusBadgeClass(estado: string): string {
    switch(estado) {
      case 'valido':
        return 'badge bg-success';
      case 'duplicado_bd':
      case 'duplicado_excel':
      case 'correo_duplicado':
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
        return 'Duplicado en BD';
      case 'duplicado_excel':
        return 'Duplicado en Excel';
      case 'correo_duplicado':
        return 'Correo duplicado';
      default:
        return 'Error';
    }
  }
}