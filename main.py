<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>K-AURA | A/B Validation Engine & Risk Analytics</title>
  <!-- Chart.js para Renderizado de Gráficas de Rendimiento en Tiempo Real -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {
      --bg-dark: #070B14;
      --card-bg: #0D1527;
      --border-color: #1E293B;
      --cyan-accent: #00D4B2;
      --blue-accent: #3B82F6;
      --green-success: #10B981;
      --red-alert: #EF4444;
      --text-white: #FFFFFF;
      --text-gray: #94A3B8;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background-color: var(--bg-dark); color: var(--text-white); padding: 20px 15px; line-height: 1.5; }

    /* CABECERA TÉCNICA Y ESTADO DE PRUEBA */
    header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 15px; margin-bottom: 25px; flex-wrap: wrap; gap: 10px; }
    .title-block h1 { font-size: 20px; font-weight: 800; }
    .title-block p { font-size: 12px; color: var(--cyan-accent); font-family: monospace; }
    
    .status-pill { background: rgba(0, 212, 178, 0.1); border: 1px solid var(--cyan-accent); color: var(--cyan-accent); padding: 6px 12px; border-radius: 20px; font-size: 11px; font-weight: 700; text-transform: uppercase; }

    /* METRICAS KPI COMPARATIVAS */
    .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; margin-bottom: 25px; }
    .kpi-card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 16px; }
    .kpi-label { font-size: 11px; color: var(--text-gray); text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-value { font-size: 22px; font-weight: 800; margin: 6px 0; }
    .kpi-sub { font-size: 11px; font-weight: 600; }
    .text-green { color: var(--green-success); }
    .text-blue { color: var(--blue-accent); }
    .text-cyan { color: var(--cyan-accent); }

    /* SECCIÓN DE GRÁFICA COMPARATIVA */
    .chart-container { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; margin-bottom: 25px; }
    .chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
    .chart-title { font-size: 15px; font-weight: 700; }

    /* TABLA DE AUDITORÍA DE EJECUCIÓN */
    .table-container { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 18px; overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; text-align: left; font-size: 12px; }
    th { color: var(--text-gray); font-weight: 600; border-bottom: 1px solid var(--border-color); padding: 10px; }
    td { padding: 12px 10px; border-bottom: 1px solid rgba(255,255,255,0.05); }
    .badge-a { background: rgba(59, 130, 246, 0.2); color: var(--blue-accent); padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 10px; }
    .badge-b { background: rgba(0, 212, 178, 0.2); color: var(--cyan-accent); padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 10px; }

    /* PANEL DE CONTROL DEL EXPERIMENTO */
    .control-panel { display: flex; gap: 10px; margin-top: 20px; flex-wrap: wrap; }
    .btn-action { background: var(--blue-accent); color: #FFF; border: none; padding: 10px 18px; border-radius: 8px; font-weight: 700; font-size: 12px; cursor: pointer; }
    .btn-danger { background: rgba(239, 68, 68, 0.2); border: 1px solid var(--red-alert); color: var(--red-alert); }
  </style>
</head>
<body>

  <header>
    <div class="title-block">
      <h1>K-AURA | Validation Engine A/B</h1>
      <p>Prueba de Concepto: Parámetros Fijos vs. Motor Estocástico Quant/Orb</p>
    </div>
    <div class="status-pill">Prueba Activa en Vivo</div>
  </header>

  <!-- TARJETAS DE MÉTRICAS KPI COMPARA ATIVAS -->
  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-label">Modelo Base (Fijo / Control)</div>
      <div class="kpi-value text-blue">+$1,450.00 USD</div>
      <div class="kpi-sub text-green">✓ Retorno Real Protegido</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Modelo Dinámico (Quant / Orb)</div>
      <div class="kpi-value text-cyan">+$1,620.00 USD</div>
      <div class="kpi-sub text-cyan">▲ +11.7% Rendimiento Bruto</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Fricción de Red (Fuerza de Gas)</div>
      <div class="kpi-value text-green">-$140.00 USD</div>
      <div class="kpi-sub text-green">Deducido por Filtro CEET</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Diferencial Neto A/B</div>
      <div class="kpi-value text-green">+$30.00 USD</div>
      <div class="kpi-sub text-green">Margen Ganador Actual: Modelo B</div>
    </div>
  </div>

  <!-- VISUALIZADOR GRÁFICO COMPARATIVO EN TIEMPO REAL -->
  <div class="chart-container">
    <div class="chart-header">
      <div class="chart-title">Curva de Rendimiento Neto Acumulado (60 Minutos)</div>
    </div>
    <canvas id="abChart" height="100"></canvas>
  </div>

  <!-- REGISTRO DE AUDITORÍA OPERATIVA EN VIVO -->
  <div class="table-container">
    <div class="chart-title" style="margin-bottom: 12px;">Auditoría Transaccional de Validación</div>
    <table>
      <thead>
        <tr>
          <th>Timestamp</th>
          <th>Estrategia</th>
          <th>Costo Ejecución (CEET)</th>
          <th>Stop-Loss / Take-Profit</th>
          <th>Estado Operativo</th>
          <th>Resultado Neto</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>16:40:12</td>
          <td><span class="badge-a">RAMA A (BASE)</span></td>
          <td>$1.20 USD</td>
          <td>TP +15% / SL -5% (Fijo)</td>
          <td><span class="text-green">Ejecutado</span></td>
          <td class="text-green">+$45.00 USD</td>
        </tr>
        <tr>
          <td>16:41:05</td>
          <td><span class="badge-b">RAMA B (QUANT)</span></td>
          <td>$3.50 USD (Priority)</td>
          <td>TP +22% / SL -3.2% (Dinamico)</td>
          <td><span class="text-green">Ejecutado (Orb +60%)</span></td>
          <td class="text-green">+$62.00 USD</td>
        </tr>
        <tr>
          <td>16:43:20</td>
          <td><span class="badge-b">RAMA B (QUANT)</span></td>
          <td>$8.90 USD (Alta Red)</td>
          <td>Ajuste Cancelado</td>
          <td><span style="color: var(--text-gray);">Abortado por Filtro Quant</span></td>
          <td>$0.00 USD (Riesgo Evitado)</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- PANEL DE DECISIÓN DE INGENIERÍA -->
  <div class="control-panel">
    <button class="btn-action" onclick="alert('Simulación actualizada con nuevo bloque de datos.')">Simular Siguiente Bloque (60 min)</button>
    <button class="btn-action btn-danger" onclick="alert('Estrategia Dinámica descartada. Retornando 100% a Parámetros Fijos Base.')">Descartar Modelo B (Retener Solo Base)</button>
  </div>

  <script>
    // Configuración de Gráfica de Comparación de Rendimiento
    const ctx = document.getElementById('abChart').getContext('2d');
    const abChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['10m', '20m', '30m', '40m', '50m', '60m'],
        datasets: [
          {
            label: 'Modelo Base Fijo (Control Real)',
            data: [200, 450, 700, 950, 1200, 1450],
            borderColor: '#3B82F6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderWidth: 2,
            tension: 0.3
          },
          {
            label: 'Modelo Dinámico Quant/Orb (Prueba)',
            data: [180, 500, 820, 1100, 1350, 1620],
            borderColor: '#00D4B2',
            backgroundColor: 'rgba(0, 212, 178, 0.1)',
            borderWidth: 2,
            tension: 0.3
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { labels: { color: '#94A3B8', font: { size: 12 } } }
        },
        scales: {
          x: { ticks: { color: '#94A3B8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
          y: { ticks: { color: '#94A3B8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
        }
      }
    });
  </script>

</body>
</html>
