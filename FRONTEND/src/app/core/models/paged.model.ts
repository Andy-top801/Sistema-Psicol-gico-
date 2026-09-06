import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

/** Respuesta paginada estándar de DRF (PageNumberPagination). */
export interface Paged<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

/**
 * Operador RxJS que normaliza la respuesta de una lista: si el backend devuelve
 * un array plano lo deja igual; si devuelve `{ count, results }` extrae
 * `results`. Permite activar la paginación en el backend sin romper el frontend.
 */
export function unwrap<T>() {
  return (source: Observable<T[] | Paged<T>>): Observable<T[]> =>
    source.pipe(map((r) => (Array.isArray(r) ? r : (r?.results ?? []))));
}
