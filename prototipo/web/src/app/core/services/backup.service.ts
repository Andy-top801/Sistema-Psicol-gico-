import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface BackupItem {
  archivo: string;
  tamano_bytes: number;
  tamano_mb: number;
  checksum_sha256: string;
  fecha_creacion: string;
  ambito: string;
  schema?: string;
  url_descarga: string;
  origen?: string;
  estado?: string;
}

export interface BackupResult {
  archivo: string;
  ruta: string;
  url_descarga: string;
  tamano_bytes: number;
  tamano_mb: number;
  checksum_sha256: string;
  schema: string;
  ambito: string;
  fecha: string;
  metodo: string;
  origen: string;
  estado: string;
  mensaje?: string;
}

export interface CronStatus {
  tarea_programada: string;
  cron_expresion: string;
  hora_ejecucion: string;
  estado: string;
  servidor: string;
  almacenamiento: string;
  ultimo_respaldo_cron?: {
    archivo: string;
    fecha: string;
    checksum: string;
    tamano_mb: number;
  };
}

@Injectable({
  providedIn: 'root'
})
export class BackupService {
  private readonly baseUrl = `${environment.apiUrl}/tenants`;

  constructor(private http: HttpClient) {}

  /**
   * Operación 1 (Diagrama de Secuencia & Comunicación):
   * Solicitar generación de Backup Manual (Global o Tenant).
   * POST /api/tenants/{id}/backup/
   */
  solicitarBackupManual(tenantId?: string, ambito: 'TENANT' | 'GLOBAL' = 'TENANT'): Observable<BackupResult> {
    const targetId = ambito === 'GLOBAL' || !tenantId ? 'global' : tenantId;
    return this.http.post<BackupResult>(`${this.baseUrl}/${targetId}/backup/`, {
      ambito: ambito,
      tenant_id: tenantId
    });
  }

  /**
   * Operación 2 (Diagrama de Secuencia & Comunicación):
   * Cargar archivo de respaldo para restauración.
   * POST /api/tenants/{id}/restore/
   */
  restaurarBackup(tenantId: string, options: {
    archivo?: string;
    file?: File;
    checksum?: string;
    corrupto?: boolean;
  }): Observable<any> {
    const targetId = tenantId || 'global';
    
    if (options.file) {
      const formData = new FormData();
      formData.append('dump_file', options.file);
      if (options.checksum) formData.append('checksum', options.checksum);
      if (options.corrupto) formData.append('corrupto', 'true');
      return this.http.post(`${this.baseUrl}/${targetId}/restore/`, formData);
    } else {
      return this.http.post(`${this.baseUrl}/${targetId}/restore/`, {
        archivo: options.archivo,
        checksum: options.checksum,
        corrupto: options.corrupto
      });
    }
  }

  /**
   * Obtiene la lista de backups disponibles.
   */
  listarBackups(tenantId?: string): Observable<BackupItem[]> {
    if (tenantId && tenantId !== 'global') {
      return this.http.get<BackupItem[]>(`${this.baseUrl}/${tenantId}/backup/`);
    }
    return this.http.get<BackupItem[]>(`${this.baseUrl}/backups/todos/`);
  }

  /**
   * Paso 1 BDD / Criterio a:
   * Consulta el estado de la tarea programada de cron en la nube (03:00 AM hora boliviana).
   */
  obtenerEstadoCron(): Observable<CronStatus> {
    return this.http.get<CronStatus>(`${this.baseUrl}/backups/cron-status/`);
  }

  /**
   * Paso 1 BDD: Ejecutar / simular tarea cron diaria y registrar en bitácora.
   */
  ejecutarCronTarea(): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/backups/cron-status/`, {});
  }

  /**
   * Descarga binaria con HttpClient (adjunta Bearer token automáticamente).
   */
  descargarArchivoBlob(archivo: string): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/backups/descargar/`, {
      params: { archivo },
      responseType: 'blob'
    });
  }

  /**
   * URL de descarga de volcado binario (incluye token JWT para compatibilidad con tags <a> directos).
   */
  getDescargaUrl(archivo: string): string {
    const token = localStorage.getItem('sigepsi_access');
    const tokenParam = token ? `&token=${encodeURIComponent(token)}` : '';
    return `${this.baseUrl}/backups/descargar/?archivo=${encodeURIComponent(archivo)}${tokenParam}`;
  }
}
