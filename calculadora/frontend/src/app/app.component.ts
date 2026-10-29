import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from './api.service';

interface Campo {
  clave: string;
  etiqueta: string;
}

interface Operacion {
  id: string;
  nombre: string;
  campos: Campo[];
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <header>
      <h1>Calculadora</h1>
      <p>Cliente → Frontend (Angular) → API Gateway → 5 microservicios → BD</p>
    </header>

    <nav>
      <button
        *ngFor="let op of operaciones"
        [class.activo]="op.id === actual.id"
        (click)="seleccionar(op)"
      >
        {{ op.nombre }}
      </button>
    </nav>

    <main>
      <section class="card">
        <h2>{{ actual.nombre }}</h2>
        <form (ngSubmit)="calcular()">
          <label *ngFor="let c of actual.campos">
            {{ c.etiqueta }}
            <input type="number" step="any" [(ngModel)]="valores[c.clave]" [name]="c.clave" required />
          </label>
          <button type="submit" class="primario" [disabled]="cargando">
            {{ cargando ? 'Calculando...' : 'Calcular' }}
          </button>
        </form>

        <p class="error" *ngIf="error">{{ error }}</p>

        <div class="resultado" *ngIf="resultado">
          <h3>Resultado</h3>
          <div class="fila" *ngFor="let r of claves(resultado)">
            <span>{{ r }}</span>
            <strong>{{ resultado[r] }}</strong>
          </div>
        </div>
      </section>

      <section class="card">
        <h2>Historial (guardado en la BD)</h2>
        <p class="vacio" *ngIf="historial.length === 0">Aún no hay operaciones.</p>
        <ul>
          <li *ngFor="let h of historial">
            <small>#{{ h.id }} · {{ h.fecha | date: 'short' }}</small>
            <div>Entrada: {{ resumen(h.entrada) }}</div>
            <div>Resultado: {{ resumen(h.resultado) }}</div>
          </li>
        </ul>
      </section>
    </main>
  `,
  styles: [`
    header { text-align: center; padding: 28px 16px 8px; }
    header h1 { margin: 0; }
    header p { margin: 6px 0 0; color: var(--muted); font-size: 14px; }
    nav { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; padding: 16px; }
    nav button {
      padding: 8px 16px; border: 1px solid var(--line); background: var(--card);
      border-radius: 999px; cursor: pointer; font-size: 14px;
    }
    nav button.activo { background: var(--brand); color: #fff; border-color: var(--brand); }
    main {
      display: grid; gap: 16px; padding: 0 16px 32px; max-width: 900px; margin: 0 auto;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    }
    .card { background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 20px; }
    .card h2 { margin-top: 0; font-size: 18px; }
    form { display: grid; gap: 12px; }
    label { display: grid; gap: 4px; font-size: 14px; color: var(--muted); }
    input { padding: 10px; border: 1px solid var(--line); border-radius: 8px; font-size: 15px; }
    .primario {
      padding: 10px; border: 0; border-radius: 8px; background: var(--brand);
      color: #fff; font-size: 15px; cursor: pointer;
    }
    .primario:disabled { opacity: .6; cursor: default; }
    .error { color: var(--err); margin-top: 12px; }
    .resultado { margin-top: 16px; padding-top: 12px; border-top: 1px solid var(--line); }
    .resultado h3 { margin: 0 0 8px; font-size: 15px; }
    .fila { display: flex; justify-content: space-between; padding: 4px 0; color: var(--ok); }
    ul { list-style: none; padding: 0; margin: 0; display: grid; gap: 10px; max-height: 420px; overflow: auto; }
    li { padding: 10px; border: 1px solid var(--line); border-radius: 8px; font-size: 13px; }
    li small { color: var(--muted); }
    .vacio { color: var(--muted); }
  `],
})
export class AppComponent {
  operaciones: Operacion[] = [
    { id: 'circulo', nombre: 'Círculo', campos: [{ clave: 'radio', etiqueta: 'Radio' }] },
    { id: 'cuadrado', nombre: 'Cuadrado', campos: [{ clave: 'lado', etiqueta: 'Lado' }] },
    {
      id: 'triangulo',
      nombre: 'Triángulo',
      campos: [
        { clave: 'base', etiqueta: 'Base' },
        { clave: 'altura', etiqueta: 'Altura' },
        { clave: 'lado_a', etiqueta: 'Lado A' },
        { clave: 'lado_b', etiqueta: 'Lado B' },
      ],
    },
    {
      id: 'potencia',
      nombre: 'Potencia',
      campos: [
        { clave: 'base', etiqueta: 'Base' },
        { clave: 'exponente', etiqueta: 'Exponente' },
      ],
    },
    {
      id: 'ecuacion_cuadratica',
      nombre: 'Ecuación cuadrática',
      campos: [
        { clave: 'a', etiqueta: 'a' },
        { clave: 'b', etiqueta: 'b' },
        { clave: 'c', etiqueta: 'c' },
      ],
    },
  ];

  actual: Operacion = this.operaciones[0];
  valores: Record<string, number> = {};
  resultado: Record<string, any> | null = null;
  historial: any[] = [];
  error = '';
  cargando = false;

  constructor(private api: ApiService) {
    this.cargarHistorial();
  }

  seleccionar(op: Operacion) {
    this.actual = op;
    this.valores = {};
    this.resultado = null;
    this.error = '';
    this.cargarHistorial();
  }

  calcular() {
    this.cargando = true;
    this.error = '';
    this.api.calcular(this.actual.id, this.valores).subscribe({
      next: (resp) => {
        this.resultado = resp.resultado;
        this.cargando = false;
        this.cargarHistorial();
      },
      error: (err) => {
        this.resultado = null;
        this.cargando = false;
        this.error = this.mensajeError(err);
      },
    });
  }

  cargarHistorial() {
    this.api.historial(this.actual.id).subscribe({
      next: (h) => (this.historial = h),
      error: () => (this.historial = []),
    });
  }

  claves(obj: Record<string, any>) {
    return Object.keys(obj);
  }

  resumen(obj: Record<string, any>) {
    return Object.entries(obj)
      .map(([k, v]) => `${k}=${v}`)
      .join(', ');
  }

  private mensajeError(err: any): string {
    const detail = err?.error?.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) return detail.map((d) => d.msg).join('; ');
    if (err?.status === 0) return 'No se pudo conectar con el API Gateway (¿está corriendo en el puerto 8000?)';
    return 'Ocurrió un error al calcular';
  }
}
