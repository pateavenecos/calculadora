import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

// Todas las peticiones pasan por el API Gateway (REST)
export const GATEWAY_URL = 'http://localhost:8000';

@Injectable({ providedIn: 'root' })
export class ApiService {
  constructor(private http: HttpClient) {}

  calcular(servicio: string, datos: Record<string, number>): Observable<any> {
    return this.http.post(`${GATEWAY_URL}/api/${servicio}/calcular`, datos);
  }

  historial(servicio: string): Observable<any[]> {
    return this.http.get<any[]>(`${GATEWAY_URL}/api/${servicio}/historial`);
  }
}
