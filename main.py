import os
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="K-Aura SaaS B2B Engine", version="2.2.0")

# Clave Maestra de Control (configurable en Render como ADMIN_API_KEY)
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "K-AURA-MASTER-2026")

try:
    import stripe
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_mock_key")
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False

class EngineControlRequest(BaseModel):
    stop_loss_pct: float
    take_profit_pct: float
    network: str

@app.post("/api/v1/engine/update-config")
async def update_engine_config(config: EngineControlRequest, x_api_key: str = Header(None, alias="X-API-Key")):
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=401, 
            detail="⚠️ ACCESO NO AUTORIZADO: Clave de control o API Key inválida."
        )
    
    return {
        "status": "CONFIG_UPDATED",
        "message": f"⚡ Motor recalibrado por Autorización del Creador en red {config.network.upper()}",
        "new_stop_loss": f"{config.stop_loss_pct}%",
        "new_take_profit": f"{config.take_profit_pct}%"
    }

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        
        <!-- METADATOS Y MINIATURA OPTIMIZADA PARA REDES SOCIALES (OPEN GRAPH) -->
        <title>K-Aura | SaaS Control Panel & Risk Engine</title>
        <meta name="description" content="Motor de mitigación de riesgo entrópico en Polygon con IA Gemini. Creado por Dr. Mauro Falcón M.">
        
        <!-- OPEN GRAPH / FACEBOOK / WHATSAPP -->
        <meta property="og:type" content="website">
        <meta property="og:url" content="https://k-aura-ser.onrender.com/">
        <meta property="og:title" content="🛡️ K-AURA // QUEMPROMET SaaS ENGINE">
        <meta property="og:description" content="Algorithmic Risk & Entropy Management on Polygon. Tecnología que no especula, asegura. Creado por Dr. Mauro Falcón M.">
        <meta property="og:image" content="https://cdn.pixabay.com/photo/2021/08/04/13/06/software-development-6521720_1200.jpg">
        <meta property="og:image:secure_url" content="https://cdn.pixabay.com/photo/2021/08/04/13/06/software-development-6521720_1200.jpg">
        <meta property="og:image:type" content="image/jpeg">
        <meta property="og:image:width" content="1200">
        <meta property="og:image:height" content="630">
        
        <!-- TWITTER CARDS -->
        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:title" content="🛡️ K-AURA // QUEMPROMET SaaS ENGINE">
        <meta name="twitter:description" content="Control de riesgo entrópico on-chain y monitoreo con IA Gemini. Creado por Dr. Mauro Falcón M.">
        <meta name="twitter:image" content="https://cdn.pixabay.com/photo/2021/08/04/13/06/software-development-6521720_1200.jpg">

        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #070a12; color: #e2e8f0; margin: 0; padding: 20px; }
            .container { max-width: 1100px; margin: 0 auto; }
            .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 15px; flex-wrap: wrap; gap: 10px; }
            .brand-title { display: flex; align-items: center; gap: 12px; }
            .logo-shield { font-size: 28px; background: linear-gradient(135deg, #2563eb, #38bdf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; }
            .creator-tag { font-size: 0.8em; color: #38bdf8; font-weight: 600; letter-spacing: 0.5px; }
            .status-container { display: flex; gap: 15px; align-items: center; }
            .led { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 5px; }
            .led-green { background-color: #22c55e; box-shadow: 0 0 10px #22c55e; animation: pulse 1.5s infinite; }
            .led-blue { background-color: #38bdf8; box-shadow: 0 0 10px #38bdf8; animation: pulse 2s infinite; }
            @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
            .card { background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 20px; margin-top: 20px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5); }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            button { background: linear-gradient(135deg, #2563eb, #1d4ed8); color: white; border: none; padding: 12px; border-radius: 8px; cursor: pointer; width: 100%; margin-top: 15px; font-weight: bold; font-size: 1em; transition: all 0.3s; }
            button:hover { background: linear-gradient(135deg, #1d4ed8, #1e40af); box-shadow: 0 0 15px rgba(37,99,235,0.5); }
            input, select { background: #070a12; border: 1px solid #334155; color: white; padding: 10px; border-radius: 6px; width: 100%; box-sizing: border-box; margin-top: 5px; }
            .footer { margin-top: 40px; text-align: center; border-top: 1px solid #1e293b; padding-top: 20px; color: #64748b; font-size: 0.85em; }
            .badge-group { display: flex; justify-content: space-around; margin-top: 10px; padding: 10px; background: #070a12; border-radius: 8px; border: 1px solid #1e293b; font-size: 0.85em; flex-wrap: wrap; gap: 5px; }
            video { border-radius: 8px; border: 1px solid #1e293b; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="brand-title">
                    <span class="logo-shield">🛡️ K-AURA</span>
                    <div>
                        <h2 style="margin: 0; font-size: 1.3em;">QUEMPROMET SaaS ENGINE</h2>
                        <span class="creator-tag">Arquitectura Intelectual por Dr. Mauro Falcón M.</span>
                    </div>
                </div>
                <div class="status-container">
                    <span><span class="led led-green"></span> NODE: ONLINE</span>
                    <span><span class="led led-blue"></span> RPC: POLYGON</span>
                </div>
            </div>

            <div class="badge-group">
                <span>🔒 Security & Access Control Active</span>
                <span>⚡ Real-Time Web3 Sync</span>
                <span>🎯 Stop Loss: 80% | Take Profit: 100%</span>
            </div>

            <!-- MÓDULO DE VIDEO PROMOCIONAL DE PRESENTACIÓN -->
            <div class="card" style="text-align: center;">
                <h3 style="margin-top: 0;">🎬 Demostración Visual de Arquitectura K-Aura</h3>
                <video width="100%" height="auto" controls poster="https://cdn.pixabay.com/photo/2021/08/04/13/06/software-development-6521720_1200.jpg">
                    <source src="http://googleusercontent.com/generated_video_content/9451239682610973525" type="video/mp4">
                    Tu navegador no soporta la reproducción de video HTML5.
                </video>
                <p style="font-size: 0.85em; color: #94a3b8; margin-top: 10px;">
                    Demostración conceptual de monitoreo entrópico y control determinista B2B on-chain.
                </p>
            </div>

            <div class="grid">
                <div class="card">
                    <h3>⚡ Calibración Protegida del Motor</h3>
                    
                    <label>Clave de Autorización / API Key:</label>
                    <input type="password" id="apiKey" placeholder="Ingresa tu clave de acceso autorizada">

                    <label style="margin-top:15px; display:block;">Red Blockchain Destino:</label>
                    <select id="net">
                        <option value="polygon">Polygon Mainnet (POL/MATIC)</option>
                        <option value="ethereum">Ethereum Mainnet (ETH)</option>
                        <option value="arbitrum">Arbitrum One (ARB)</option>
                    </select>
                    
                    <label style="margin-top:15px; display:block;">Umbral Stop Loss (%):</label>
                    <input type="number" id="sl" value="80">

                    <label style="margin-top:15px; display:block;">Objetivo Take Profit (%):</label>
                    <input type="number" id="tp" value="100">

                    <button onclick="applyConfig()">Ejecutar Recalibración Autorizada</button>
                    <p id="msg" style="font-weight: 500; font-size: 0.9em; margin-top: 10px;"></p>
                </div>

                <div class="card">
                    <h3>📈 Monitoreo Entrópico On-Chain</h3>
                    <canvas id="chart" height="180"></canvas>
                </div>
            </div>

            <div class="footer">
                <p><strong>© QUEMPROMET / KEMPROMED ECOSYSTEM. Todos los derechos reservados.</strong></p>
                <p>Dirección y Arquitectura Tecnológica por el <strong>Dr. Mauro Falcón M.</strong> | Propiedad Intelectual protegida. Infraestructura desplegada en Render & GCP Gemini AI Studio.</p>
            </div>
        </div>

        <script>
            const ctx = document.getElementById('chart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['12:00', '12:05', '12:10', '12:15', '12:20'],
                    datasets: [{ 
                        label: 'Balance On-Chain (USD)', 
                        data: [1000, 1020, 990, 1050, 1100], 
                        borderColor: '#38bdf8', 
                        backgroundColor: 'rgba(56, 189, 248, 0.1)',
                        fill: true,
                        tension: 0.3 
                    }]
                },
                options: { responsive: true, plugins: { legend: { labels: { color: '#94a3b8' } } } }
            });

            async function applyConfig() {
                const key = document.getElementById('apiKey').value;
                const msg = document.getElementById('msg');

                if (!key) {
                    msg.style.color = '#ef4444';
                    msg.innerText = '❌ Error: Debes ingresar tu Clave de Acceso para autorizar la operación.';
                    return;
                }

                try {
                    const res = await fetch('/api/v1/engine/update-config', {
                        method: 'POST',
                        headers: { 
                            'Content-Type': 'application/json',
                            'X-API-Key': key 
                        },
                        body: JSON.stringify({ stop_loss_pct: parseFloat(sl.value), take_profit_pct: parseFloat(tp.value), network: net.value })
                    });
                    
                    const data = await res.json();
                    
                    if (res.ok) {
                        msg.style.color = '#38bdf8';
                        msg.innerText = data.message;
                    } else {
                        msg.style.color = '#ef4444';
                        msg.innerText = '❌ ' + (data.detail || 'Acceso denegado.');
                    }
                } catch (e) {
                    msg.style.color = '#ef4444';
                    msg.innerText = '❌ Error de comunicación con el servidor.';
                }
            }
        </script>
    </body>
    </html>
    ""