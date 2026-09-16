import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import * as XLSX from 'xlsx';

export interface ColumnaDef {
  key: string;
  label: string;
}

export interface FiltroDef {
  key: string;
  label: string;
  type: 'date' | 'select' | 'text';
  opciones?: string[];
}

export interface FuenteMetadata {
  label: string;
  columnas: ColumnaDef[];
  filtros: FiltroDef[];
}

export interface ReporteResultado {
  columnas: ColumnaDef[];
  datos: Record<string, any>[];
  total: number;
  resumen?: Record<string, any>;
}

@Injectable({ providedIn: 'root' })
export class ReportService {
  private readonly apiUrl = `${environment.apiUrl}/reportes`;

  constructor(private http: HttpClient) {}

  /**
   * Obtiene la definición de metadatos de todas las fuentes, columnas y filtros disponibles.
   */
  getMetadata(): Observable<Record<string, FuenteMetadata>> {
    return this.http.get<Record<string, FuenteMetadata>>(`${this.apiUrl}/metadata/`);
  }

  /**
   * Obtiene el reporte predefinido o filtrado para una fuente específica.
   */
  getReporte(fuente: string, filtros: Record<string, any> = {}, columnas?: string[], orden?: { columna: string; direccion: string }): Observable<ReporteResultado> {
    let params = new HttpParams();
    Object.keys(filtros).forEach(key => {
      const val = filtros[key];
      if (val !== undefined && val !== null && val !== '') {
        params = params.set(key, String(val));
      }
    });

    if (columnas && columnas.length > 0) {
      params = params.set('columnas', columnas.join(','));
    }

    if (orden && orden.columna) {
      params = params.set('orden_columna', orden.columna);
      params = params.set('orden_dir', orden.direccion || 'ASC');
    }

    return this.http.get<ReporteResultado>(`${this.apiUrl}/${fuente}/`, { params });
  }

  /**
   * Genera un reporte personalizado estructurado mediante POST.
   */
  generarPersonalizado(payload: {
    fuente: string;
    columnas?: string[];
    filtros?: Record<string, any>;
    orden?: { columna: string; direccion: string };
  }): Observable<ReporteResultado> {
    return this.http.post<ReporteResultado>(`${this.apiUrl}/personalizado/`, payload);
  }

  /**
   * Envía el reporte por correo electrónico.
   */
  enviarEmail(payload: {
    email: string;
    fuente: string;
    asunto?: string;
    filtros?: Record<string, any>;
    columnas?: string[];
  }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/email/`, payload);
  }

  /**
   * Descarga directa en Excel (.xlsx con estilos) desde el servidor Django.
   */
  descargarExcelServer(fuente: string, filtros: Record<string, any> = {}, columnas?: string[]): Observable<Blob> {
    let params = new HttpParams();
    Object.keys(filtros).forEach(key => {
      const val = filtros[key];
      if (val !== undefined && val !== null && val !== '') {
        params = params.set(key, String(val));
      }
    });
    if (columnas && columnas.length > 0) {
      params = params.set('columnas', columnas.join(','));
    }
    return this.http.get(`${this.apiUrl}/${fuente}/export/excel/`, { params, responseType: 'blob' });
  }

  /**
   * Descarga directa en CSV desde el servidor.
   */
  descargarCSVServer(fuente: string, filtros: Record<string, any> = {}): Observable<Blob> {
    let params = new HttpParams();
    Object.keys(filtros).forEach(key => {
      const val = filtros[key];
      if (val !== undefined && val !== null && val !== '') {
        params = params.set(key, String(val));
      }
    });
    return this.http.get(`${this.apiUrl}/${fuente}/export/csv/`, { params, responseType: 'blob' });
  }

  /**
   * Descarga directa en HTML desde el servidor.
   */
  descargarHTMLServer(fuente: string, filtros: Record<string, any> = {}, columnas?: string[]): Observable<Blob> {
    let params = new HttpParams();
    Object.keys(filtros).forEach(key => {
      const val = filtros[key];
      if (val !== undefined && val !== null && val !== '') {
        params = params.set(key, String(val));
      }
    });
    if (columnas && columnas.length > 0) {
      params = params.set('columnas', columnas.join(','));
    }
    return this.http.get(`${this.apiUrl}/${fuente}/export/html/`, { params, responseType: 'blob' });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // GENERACIÓN DE REPORTES PREMIUM (Súper Estéticos, Formales y Firmes)
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Genera un nombre de archivo institucional, formal y compatible con Windows/Linux.
   */
  public formatearNombre(titulo: string, ext: string): string {
    const hoy = new Date();
    const anio = hoy.getFullYear();
    const mes = String(hoy.getMonth() + 1).padStart(2, '0');
    const dia = String(hoy.getDate()).padStart(2, '0');

    let limpio = (titulo || 'Reporte_SIGEPSI')
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '') // eliminar tildes
      .replace(/[^a-zA-Z0-9]/g, '_')   // caracteres alfanuméricos
      .replace(/_+/g, '_')            // compactar guiones
      .replace(/^_|_$/g, '');

    if (!limpio) limpio = 'Reporte_SIGEPSI';
    const extensionLimpia = ext.replace(/^\./, '');
    return `${limpio}_${anio}_${mes}_${dia}.${extensionLimpia}`;
  }

  /**
   * Disparador de descarga infalible para navegadores modernos (Chrome, Edge, Firefox).
   * Garantiza que el nombre de archivo y la extensión (.pdf, .xlsx, .csv, .html)
   * se preserven SIEMPRE, evitando que Chromium guarde archivos con hash UUID sin extensión.
   */
  public triggerDownload(blob: Blob, nombreArchivoCompleto: string): void {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.style.display = 'none';
    link.href = url;
    link.setAttribute('download', nombreArchivoCompleto);
    document.body.appendChild(link);

    try {
      const clickEvent = new MouseEvent('click', {
        bubbles: true,
        cancelable: true,
        view: window
      });
      link.dispatchEvent(clickEvent);
    } catch (e) {
      link.click();
    }

    // Retener la URL 60 segundos antes de revocar para permitir que el sistema de archivos de Windows
    // complete la escritura con el nombre y extensión correctos.
    setTimeout(() => {
      try {
        if (document.body.contains(link)) {
          document.body.removeChild(link);
        }
        window.URL.revokeObjectURL(url);
      } catch (err) {}
    }, 60000);
  }

  /**
   * Genera y descarga un PDF de grado clínico e institucional de máxima calidad:
   * Membrete institucional, folio oficial, metadatos, tabla formateada,
   * totales, firmas y pie de página legal en todas las hojas.
   */
  exportToPDF(resultado: ReporteResultado, titulo: string, tenantName?: string, userName?: string): void {
    const isWide = resultado.columnas.length > 6;
    const orientation = isWide ? 'landscape' : 'portrait';
    const doc = new jsPDF(orientation, 'pt', 'a4');
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();

    const currentTenant = tenantName || 'Centro Psicológico';
    const currentUser = userName || 'Administrador Clínico';
    const folioCode = `REP-${Date.now().toString().slice(-8)}`;
    const fechaEmision = new Date().toLocaleString('es-BO', {
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit'
    });

    // ── 1. ENCABEZADO SUPERIOR / MEMBRETE INSTITUCIONAL ──
    doc.setFillColor(15, 41, 34); // #0F2922
    doc.rect(0, 0, pageWidth, 56, 'F');

    doc.setFillColor(46, 196, 134); // #2EC486
    doc.rect(0, 56, pageWidth, 4, 'F');

    // Emblema Clínico Ψ
    doc.setFillColor(255, 255, 255);
    doc.roundedRect(26, 12, 32, 32, 6, 6, 'F');
    doc.setTextColor(15, 41, 34);
    doc.setFont('times', 'bold');
    doc.setFontSize(20);
    doc.text('Ψ', 36, 35);

    // Texto Institucional Membrete
    doc.setTextColor(255, 255, 255);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(13);
    doc.text('SIGEPSI — PLATAFORMA CLÍNICA SAAS', 68, 28);

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(9);
    doc.setTextColor(179, 222, 203);
    doc.text(`${currentTenant.toUpperCase()} — DEPARTAMENTO CLÍNICO & ADMINISTRATIVO`, 68, 43);

    // Folio
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(8.5);
    doc.setTextColor(255, 255, 255);
    doc.text(`FOLIO: ${folioCode}`, pageWidth - 30, 26, { align: 'right' });

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(7.5);
    doc.setTextColor(179, 222, 203);
    doc.text('DOCUMENTO CLÍNICO OFICIAL', pageWidth - 30, 40, { align: 'right' });

    // ── 2. TARJETA DE METADATOS Y CLASIFICACIÓN (startY: 72) ──
    const cardY = 72;
    const cardH = 46;
    doc.setFillColor(247, 250, 248);
    doc.setDrawColor(211, 224, 216);
    doc.setLineWidth(0.75);
    doc.roundedRect(26, cardY, pageWidth - 52, cardH, 4, 4, 'FD');

    doc.setTextColor(15, 41, 34);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(11);
    doc.text(titulo.toUpperCase(), 38, cardY + 18);

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(8);
    doc.setTextColor(85, 117, 104);
    doc.text(`Operador / Emisor: ${currentUser}`, 38, cardY + 34);

    doc.setFont('helvetica', 'bold');
    doc.setFontSize(8.5);
    doc.setTextColor(25, 115, 78);
    doc.text(`Total de registros: ${resultado.total}`, pageWidth - 38, cardY + 18, { align: 'right' });

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(7.5);
    doc.setTextColor(100, 116, 139);
    doc.text(`Fecha y hora de emisión: ${fechaEmision}`, pageWidth - 38, cardY + 34, { align: 'right' });

    // ── 3. CUERPO DE LA TABLA CON AUTO-TABLE ──
    const headers = resultado.columnas.map(c => c.label.toUpperCase());
    const body = resultado.datos.map(fila =>
      resultado.columnas.map(col => {
        const v = fila[col.key];
        if (v === null || v === undefined) return '—';
        if (['costo', 'monto', 'tarifa_base'].includes(col.key)) {
          const num = parseFloat(v);
          return isNaN(num) ? String(v) : `Bs. ${num.toFixed(2)}`;
        }
        if (['activo', 'resuelta'].includes(col.key)) {
          return (v === true || v === 'true') ? 'SÍ' : 'NO';
        }
        return String(v);
      })
    );

    const columnStylesObj: Record<number, any> = {};
    resultado.columnas.forEach((col, idx) => {
      if (['costo', 'monto', 'tarifa_base'].includes(col.key)) {
        columnStylesObj[idx] = { halign: 'right', fontStyle: 'bold' };
      } else if (['fecha', 'hora_inicio', 'hora_fin', 'ci', 'codigo_expediente', 'estado', 'activo', 'resuelta'].includes(col.key)) {
        columnStylesObj[idx] = { halign: 'center' };
      }
    });

    autoTable(doc, {
      head: [headers],
      body: body,
      startY: 128,
      theme: 'grid',
      styles: {
        font: 'helvetica',
        fontSize: isWide ? 7.5 : 8.5,
        cellPadding: isWide ? 4 : 5.5,
        textColor: [30, 41, 59],
        lineColor: [220, 230, 224],
        lineWidth: 0.5,
      },
      headStyles: {
        fillColor: [22, 78, 61], // #164E3D
        textColor: [255, 255, 255],
        fontStyle: 'bold',
        fontSize: isWide ? 7.5 : 8.5,
        halign: 'center',
        valign: 'middle',
      },
      alternateRowStyles: {
        fillColor: [248, 251, 249],
      },
      columnStyles: columnStylesObj,
      margin: { left: 26, right: 26, bottom: 65 },
      didDrawPage: (data) => {
        doc.setDrawColor(220, 230, 224);
        doc.setLineWidth(0.5);
        doc.line(26, pageHeight - 32, pageWidth - 26, pageHeight - 32);

        doc.setFont('helvetica', 'normal');
        doc.setFontSize(7.5);
        doc.setTextColor(110, 130, 120);
        doc.text('SIGEPSI — Documento Confidencial sujeto a Secreto Médico y Ley de Protección de Datos.', 26, pageHeight - 20);

        doc.setFont('helvetica', 'bold');
        doc.text(`Página ${data.pageNumber}`, pageWidth - 26, pageHeight - 20, { align: 'right' });
      }
    });

    // ── 4. BLOQUE DE RESUMEN Y FIRMAS FORMALES ──
    const lastY = (doc as any).lastAutoTable?.finalY || 200;
    let finalBlockY = lastY + 20;

    if (finalBlockY + 90 > pageHeight) {
      doc.addPage();
      finalBlockY = 40;
    }

    if (resultado.resumen && Object.keys(resultado.resumen).length > 0) {
      doc.setFillColor(242, 248, 244);
      doc.setDrawColor(185, 216, 200);
      doc.roundedRect(26, finalBlockY, pageWidth - 52, 34, 3, 3, 'FD');

      doc.setFont('helvetica', 'bold');
      doc.setFontSize(8.5);
      doc.setTextColor(25, 115, 78);
      doc.text('RESUMEN EJECUTIVO:', 38, finalBlockY + 14);

      doc.setFont('helvetica', 'normal');
      doc.setFontSize(8);
      doc.setTextColor(30, 41, 59);

      let summaryText = `Total de registros: ${resultado.total}`;
      if (resultado.resumen['total_ingresos'] !== undefined) {
        summaryText += `  |  Monto Total Recaudado: Bs. ${parseFloat(resultado.resumen['total_ingresos']).toFixed(2)}`;
      }
      doc.text(summaryText, 38, finalBlockY + 26);
      finalBlockY += 46;
    }

    if (finalBlockY + 60 > pageHeight) {
      doc.addPage();
      finalBlockY = 40;
    }

    const col1X = 70;
    const col2X = pageWidth - 250;
    const lineW = 180;

    doc.setDrawColor(80, 100, 90);
    doc.setLineWidth(0.75);
    doc.line(col1X, finalBlockY + 30, col1X + lineW, finalBlockY + 30);
    doc.line(col2X, finalBlockY + 30, col2X + lineW, finalBlockY + 30);

    doc.setFont('helvetica', 'bold');
    doc.setFontSize(8);
    doc.setTextColor(15, 41, 34);
    doc.text('Responsable de Emisión', col1X + (lineW / 2), finalBlockY + 42, { align: 'center' });
    doc.text('Dirección Médica / Sello de Validación', col2X + (lineW / 2), finalBlockY + 42, { align: 'center' });

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(7);
    doc.setTextColor(100, 116, 139);
    doc.text(currentUser, col1X + (lineW / 2), finalBlockY + 52, { align: 'center' });
    doc.text('SIGEPSI Auditoría Clínica', col2X + (lineW / 2), finalBlockY + 52, { align: 'center' });

    // Descargar con nombre seguro y extensión .pdf garantizada
    const pdfBlob = doc.output('blob');
    const nombreArchivo = this.formatearNombre(titulo, 'pdf');
    this.triggerDownload(pdfBlob, nombreArchivo);
  }

  /**
   * Genera y descarga un archivo Microsoft Excel (.xlsx) altamente estructurado y profesional
   * con cabecera formal, metadatos, columnas autoajustadas, filas de datos y pie de firmas.
   */
  exportToExcel(resultado: ReporteResultado, filename: string, tenantName?: string, userName?: string): void {
    const currentTenant = tenantName || 'Centro Psicológico';
    const currentUser = userName || 'Administrador Clínico';
    const fechaEmision = new Date().toLocaleString('es-BO');

    const sheetData: any[][] = [];
    sheetData.push(['SISTEMA INTEGRADO DE GESTIÓN PSICOLÓGICA — SIGEPSI']);
    sheetData.push([`REPORTE OFICIAL: ${filename.toUpperCase().replace(/_/g, ' ')} — ${currentTenant.toUpperCase()}`]);
    sheetData.push([
      'EMISIÓN:', fechaEmision,
      'EMISOR:', currentUser,
      'TOTAL REGISTROS:', resultado.total,
      'CLASIFICACIÓN:', 'Documento Clínico Confidencial'
    ]);
    sheetData.push([]);

    const colLabels = resultado.columnas.map(c => c.label);
    const colKeys = resultado.columnas.map(c => c.key);
    sheetData.push(colLabels);

    for (const fila of resultado.datos) {
      const rowVals: any[] = [];
      for (const key of colKeys) {
        let val = fila[key];
        if (['costo', 'monto', 'tarifa_base'].includes(key) && val !== null && val !== undefined && val !== '') {
          const num = parseFloat(val);
          val = isNaN(num) ? val : num;
        } else if (['activo', 'resuelta'].includes(key)) {
          val = (val === true || val === 'true') ? 'SÍ' : 'NO';
        }
        rowVals.push(val !== undefined && val !== null ? val : '');
      }
      sheetData.push(rowVals);
    }

    if (resultado.resumen && Object.keys(resultado.resumen).length > 0) {
      sheetData.push([]);
      sheetData.push(['--- RESUMEN EJECUTIVO Y ESTADÍSTICO ---']);
      for (const [k, v] of Object.entries(resultado.resumen)) {
        if (typeof v === 'object' && v !== null) {
          sheetData.push([k.replace(/_/g, ' ').toUpperCase()]);
          for (const [sk, sv] of Object.entries(v)) {
            sheetData.push(['', sk, sv]);
          }
        } else {
          sheetData.push([k.replace(/_/g, ' ').toUpperCase(), v]);
        }
      }
    }

    sheetData.push([]);
    sheetData.push(['_______________________________________', '', '', '_______________________________________']);
    sheetData.push(['Responsable de Emisión / Administración', '', '', 'Dirección Médica / Validación Clínica']);

    const ws = XLSX.utils.aoa_to_sheet(sheetData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Reporte Clínico');

    const colWidths = colLabels.map((label, idx) => {
      let maxLen = label.length;
      for (const row of resultado.datos) {
        const val = row[colKeys[idx]];
        if (val) {
          maxLen = Math.max(maxLen, String(val).length);
        }
      }
      return { wch: Math.max(maxLen + 4, 14) };
    });
    ws['!cols'] = colWidths;

    // Generar buffer XLSX y descargar con MIME y extensión oficial
    const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
    const excelBlob = new Blob([wbout], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    });
    const nombreArchivo = this.formatearNombre(filename, 'xlsx');
    this.triggerDownload(excelBlob, nombreArchivo);
  }

  /**
   * Exporta a archivo CSV compatible con Microsoft Excel (UTF-8 con BOM).
   */
  exportToCSV(resultado: ReporteResultado, filename: string): void {
    const headers = resultado.columnas.map(c => `"${c.label.replace(/"/g, '""')}"`).join(',');
    const rows = resultado.datos.map(fila =>
      resultado.columnas.map(col => {
        const val = fila[col.key];
        const strVal = val !== undefined && val !== null ? String(val) : '';
        return `"${strVal.replace(/"/g, '""')}"`;
      }).join(',')
    );

    let csvContent = '\uFEFF' + headers + '\r\n' + rows.join('\r\n');

    if (resultado.resumen && Object.keys(resultado.resumen).length > 0) {
      csvContent += '\r\n\r\n"--- RESUMEN ---"\r\n';
      for (const [k, v] of Object.entries(resultado.resumen)) {
        if (typeof v === 'object' && v !== null) {
          csvContent += `"${k}"\r\n`;
          for (const [sk, sv] of Object.entries(v)) {
            csvContent += `,"${sk}","${sv}"\r\n`;
          }
        } else {
          csvContent += `"${k}","${v}"\r\n`;
        }
      }
    }

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const nombreArchivo = this.formatearNombre(filename, 'csv');
    this.triggerDownload(blob, nombreArchivo);
  }

  /**
   * Exporta a un archivo HTML estilizado para abrir en navegador o imprimir.
   */
  exportToHTML(resultado: ReporteResultado, titulo: string, tenantName?: string): void {
    const colLabels = resultado.columnas.map(c => `<th>${c.label}</th>`).join('');
    const rows = resultado.datos.map(fila => {
      const cells = resultado.columnas.map(col => {
        let v = fila[col.key];
        if (['costo', 'monto', 'tarifa_base'].includes(col.key) && v !== null && v !== undefined && v !== '') {
          const num = parseFloat(v);
          v = isNaN(num) ? v : `Bs. ${num.toFixed(2)}`;
        } else if (['activo', 'resuelta'].includes(col.key)) {
          v = (v === true || v === 'true') ? 'SÍ' : 'NO';
        }
        return `<td>${v !== undefined && v !== null ? v : '—'}</td>`;
      }).join('');
      return `<tr>${cells}</tr>`;
    }).join('');

    let resumenHtml = '';
    if (resultado.resumen && Object.keys(resultado.resumen).length > 0) {
      resumenHtml = '<div class="resumen"><h3>Resumen Ejecutivo</h3><ul>';
      for (const [k, v] of Object.entries(resultado.resumen)) {
        if (typeof v === 'object' && v !== null) {
          resumenHtml += `<li><strong>${k}:</strong><ul>`;
          for (const [sk, sv] of Object.entries(v)) {
            resumenHtml += `<li>${sk}: ${sv}</li>`;
          }
          resumenHtml += '</ul></li>';
        } else {
          resumenHtml += `<li><strong>${k}:</strong> ${v}</li>`;
        }
      }
      resumenHtml += '</ul></div>';
    }

    const htmlContent = `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>${titulo} — SIGEPSI</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 30px; color: #12271f; background: #fafcfb; }
    .header { background: #0f2922; color: #ffffff; padding: 20px 24px; border-radius: 12px; margin-bottom: 24px; border-bottom: 4px solid #2ec486; }
    .header h1 { margin: 0 0 6px 0; font-size: 1.5rem; letter-spacing: 0.5px; }
    .header p { margin: 0; font-size: 0.85rem; color: #a4c4b8; }
    .meta-bar { display: flex; justify-content: space-between; margin-bottom: 16px; font-size: 0.9rem; font-weight: 600; color: #19734e; }
    table { width: 100%; border-collapse: collapse; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    th { background: #164e3d; color: #ffffff; text-align: left; padding: 12px 14px; font-size: 0.82rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
    td { padding: 10px 14px; border-bottom: 1px solid #e7efe9; font-size: 0.88rem; color: #1e352b; }
    tr:nth-child(even) { background-color: #f7faf8; }
    tr:hover { background-color: #eaf4ee; }
    .resumen { margin-top: 24px; padding: 16px 20px; background: #e8f5ed; border-left: 4px solid #19734e; border-radius: 6px; }
    .resumen h3 { margin-top: 0; color: #0f2922; font-size: 1rem; }
    .firmas-grid { margin-top: 40px; display: flex; justify-content: space-between; padding: 0 40px; }
    .firma-col { text-align: center; width: 220px; border-top: 1px solid #0f2922; padding-top: 8px; font-size: 0.82rem; font-weight: 600; color: #3b5a4e; }
    .footer { margin-top: 30px; text-align: center; font-size: 0.8rem; color: #8ba59b; }
  </style>
</head>
<body>
  <div class="header">
    <h1>SIGEPSI — ${titulo}</h1>
    <p>Centro: ${tenantName || 'Centro Clínico'} | Fecha: ${new Date().toLocaleString('es-BO')}</p>
  </div>
  <div class="meta-bar">
    <span>Total de registros generados: ${resultado.total}</span>
    <span>Documento Oficial Confidencial</span>
  </div>
  <table>
    <thead><tr>${colLabels}</tr></thead>
    <tbody>${rows}</tbody>
  </table>
  ${resumenHtml}
  <div class="firmas-grid">
    <div class="firma-col">Responsable de Emisión</div>
    <div class="firma-col">Dirección Médica / Validación</div>
  </div>
  <div class="footer">
    Sistema Integrado de Gestión Psicológica (SIGEPSI) — Reporte Confidencial
  </div>
</body>
</html>`;

    const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8;' });
    const nombreArchivo = this.formatearNombre(titulo, 'html');
    this.triggerDownload(blob, nombreArchivo);
  }

  /**
   * Abre la ventana de impresión nativa con formato estético e institucional.
   */
  printReport(resultado: ReporteResultado, titulo: string, tenantName?: string): void {
    const printWindow = window.open('', '_blank', 'width=1000,height=700');
    if (!printWindow) return;

    const colLabels = resultado.columnas.map(c => `<th style="border: 1px solid #ccc; padding: 8px; background: #164e3d; color: #fff; font-size: 11px;">${c.label}</th>`).join('');
    const rows = resultado.datos.map(fila => {
      const cells = resultado.columnas.map(col => {
        let v = fila[col.key];
        if (['costo', 'monto', 'tarifa_base'].includes(col.key) && v !== null && v !== undefined && v !== '') {
          const num = parseFloat(v);
          v = isNaN(num) ? v : `Bs. ${num.toFixed(2)}`;
        } else if (['activo', 'resuelta'].includes(col.key)) {
          v = (v === true || v === 'true') ? 'SÍ' : 'NO';
        }
        return `<td style="border: 1px solid #ddd; padding: 6px; font-size: 11px;">${v !== undefined && v !== null ? v : '—'}</td>`;
      }).join('');
      return `<tr>${cells}</tr>`;
    }).join('');

    printWindow.document.write(`
      <html>
      <head>
        <title>${titulo} - Imprimir</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 25px; color: #12271f; }
          .header { border-bottom: 2px solid #0f2922; padding-bottom: 10px; margin-bottom: 15px; }
          h2 { margin: 0 0 5px 0; color: #0f2922; }
          p { margin: 0; color: #555; font-size: 12px; }
          table { width: 100%; border-collapse: collapse; margin-top: 15px; }
          .firmas { margin-top: 50px; display: flex; justify-content: space-between; padding: 0 60px; }
          .sig-line { text-align: center; width: 220px; border-top: 1px solid #000; padding-top: 6px; font-size: 11px; }
        </style>
      </head>
      <body>
        <div class="header">
          <h2>SIGEPSI — ${titulo}</h2>
          <p>Centro: ${tenantName || 'Centro Clínico'} | Fecha: ${new Date().toLocaleString()} | Total: ${resultado.total} registros</p>
        </div>
        <table>
          <thead><tr>${colLabels}</tr></thead>
          <tbody>${rows}</tbody>
        </table>
        <div class="firmas">
          <div class="sig-line">Responsable de Emisión</div>
          <div class="sig-line">Dirección Médica / Sello</div>
        </div>
      </body>
      </html>
    `);
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => {
      printWindow.print();
    }, 500);
  }
}
