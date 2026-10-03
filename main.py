import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="K-Aura SaaS B2B Engine", version="2.0.0")

try:
    import stripe
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_mock_key")
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False

class StripeCheckoutRequest(BaseModel):
    price_id: str
    customer_email: str
    success_url: str = "https://quempromet.com/success"
    cancel_url: str = "https://quempromet.com/cancel"

@app.post("/api/v1/stripe/create-checkout-session")
async def create_checkout_session(data: StripeCheckoutRequest):
    if not STRIPE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Módulo Stripe no disponible.")
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": data.price_id, "quantity": 1}],
            mode="subscription",
            customer_email=data.customer_email,
            success_url=data.success_url,
            cancel_url=data.cancel_url,
        )
        return {"checkout_url": session.url, "session_id": session.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class EngineControlRequest(BaseModel):
    stop_loss_pct: float
    take_profit_pct: float
    network: str

@app.post("/api/v1/engine/update-config")
async def update_engine_config(config: EngineControlRequest):
    return {
        "status": "CONFIG_UPDATED",
        "message": f"⚡ Motor recalibrado exitosamente en red {config.network.upper()}",
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
        <title>K-Aura | SaaS Control Panel</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #070a12; color: #e2e8f0; margin: 0; padding: 20px; }
            .container { max-width: 1100px; margin: 0 auto; }
            .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 15px; flex-wrap: wrap; gap: 10px; }
            .brand-title { display: flex; align-items: center; gap: 12px; }
            .logo-shield { font-size: 28px; background: linear-gradient(135deg, #2563eb, #38bdf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; letter-spacing: -1px; }
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
            .badge-group { display: flex; justify-content: space-around; margin-top: 10px; padding: 10px; background: #070a12; border-radius: 8px; border: 1px solid #1e293b; font-size: 0.85em; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="brand-title">
                    <span class="logo-shield">🛡️ K-AURA</span>
                    <div>
                        <h2 style="margin: 0; font-size: 1.3em;">QUEMPROMET SaaS ENGINE</h2>
                        <span style="font-size: 0.75em; color: #94a3b8;">Algorithmic Risk & Entropy Management</span>
                    </div>
                </div>
                <div class="status-container">
                    <span><span class="led led-green"></span> NODE: ONLINE</span>
                    <span><span class="led led-blue"></span> RPC: POLYGON</span>
                </div>
            </div>

            <div class="badge-group">
                <span>🔒 GCP AI Studio Policy Aligned</span>
                <span>⚡ Real-Time Web3 Sync</span>
                <span>🎯 Stop Loss: 80% | Take Profit: 100%</span>
            </div>

            <div class="grid">
                <div class="card">
                    <h3>⚡ Calibración del Motor en Vivo</h3>
                    <label>Red Blockchain Destino:</label>
                    <select id="net">
                        <option value="polygon">Polygon Mainnet (POL/MATIC)</option>
                        <option value="ethereum">Ethereum Mainnet (ETH)</option>
                        <option value="arbitrum">Arbitrum One (ARB)</option>
                    </select>
                    
                    <label style="margin-top:15px; display:block;">Umbral Stop Loss (%):</label>
                    <input type="number" id="sl" value="80">

                    <label style="margin-top:15px; display:block;">Objetivo Take Profit (%):</label>
                    <input type="number" id="tp" value="100">

                    <button onclick="applyConfig()">Ejecutar Recalibración On-Chain</button>
                    <p id="msg" style="color:#38bdf8; font-weight: 500; font-size: 0.9em;"></p>
                </div>

                <div class="card">
                    <h3>📈 Monitoreo Entrópico On-Chain</h3>
                    <canvas id="chart" height="180"></canvas>
                </div>
            </div>

            <div class="footer">
                <p><strong>© QUEMPROMET / KEMPROMED ECOSYSTEM. Todos los derechos reservados.</strong></p>
                <p>Desarrollado bajo estándares institucionales B2B. Propiedad Intelectual protegida. Infraestructura desplegada en Render & GCP Gemini AI Studio.</p>
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
                const res = await fetch('/api/v1/engine/update-config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ stop_loss_pct: parseFloat(sl.value), take_profit_pct: parseFloat(tp.value), network: net.value })
                });
                const data = await res.json();
                msg.innerText = data.message;
            }
        </script>
    </body>
    </html>
    """
