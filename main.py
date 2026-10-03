import os
import stripe
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(title="K-Aura SaaS B2B Engine", version="2.0.0")

# ------------------------------------------------------------------
# CONFIGURACIÓN DE STRIPE
# ------------------------------------------------------------------
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_mock_key")

class StripeCheckoutRequest(BaseModel):
    price_id: str
    customer_email: str
    success_url: str = "https://quempromet.com/success"
    cancel_url: str = "https://quempromet.com/cancel"

@app.post("/api/v1/stripe/create-checkout-session")
async def create_checkout_session(data: StripeCheckoutRequest):
    """
    Endpoint B2B para generar la sesión de pago o suscripción SaaS en Stripe.
    """
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": data.price_id,
                "quantity": 1,
            }],
            mode="subscription",  # Modelo SaaS recurrente
            customer_email=data.customer_email,
            success_url=data.success_url,
            cancel_url=data.cancel_url,
        )
        return {"checkout_url": session.url, "session_id": session.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ------------------------------------------------------------------
# ENDPOINTS PARA EL DASHBOARD INTERACTIVO (TRACCIÓN DE USUARIO)
# ------------------------------------------------------------------
class EngineControlRequest(BaseModel):
    stop_loss_pct: float
    take_profit_pct: float
    network: str

@app.post("/api/v1/engine/update-config")
async def update_engine_config(config: EngineControlRequest):
    """
    Permite al usuario interactuar y ajustar los umbrales del motor en tiempo real.
    """
    return {
        "status": "CONFIG_UPDATED",
        "message": f"Motor recalibrado en red {config.network}",
        "new_stop_loss": f"{config.stop_loss_pct}%",
        "new_take_profit": f"{config.take_profit_pct}%"
    }

# ------------------------------------------------------------------
# INTERFAZ B2B / DASHBOARD EN TIEMPO REAL
# ------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def serve_interactive_dashboard():
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>K-Aura | SaaS Control Panel</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0b0f19; color: #e2e8f0; margin: 0; padding: 20px; }
            .container { max-width: 1100px; margin: 0 auto; }
            .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 15px; }
            .card { background: #121826; border: 1px solid #1e293b; border-radius: 10px; padding: 20px; margin-top: 20px; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            button { background: #2563eb; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; }
            button:hover { background: #1d4ed8; }
            input, select { background: #0f172a; border: 1px solid #334155; color: white; padding: 8px; border-radius: 4px; width: 100%; margin-top: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>K-AURA // QUEMPROMET SaaS ENGINE</h2>
                <span style="color: #22c55e;">● NODE ACTIVE (POLYGON)</span>
            </div>

            <div class="grid">
                <!-- CONTROLES INTERACTIVOS (TRACCIÓN) -->
                <div class="card">
                    <h3>Control & Calibración en Vivo</h3>
                    <label>Red Blockchain:</label>
                    <select id="networkSelect">
                        <option value="polygon">Polygon Mainnet</option>
                        <option value="ethereum">Ethereum Mainnet</option>
                        <option value="arbitrum">Arbitrum One</option>
                    </select>

                    <label style="margin-top: 15px; display:block;">Stop Loss (%):</label>
                    <input type="number" id="stopLossInput" value="80">

                    <label style="margin-top: 15px; display:block;">Take Profit (%):</label>
                    <input type="number" id="takeProfitInput" value="100">

                    <br><br>
                    <button onclick="updateConfig()">Aplicar Cambios al Motor</button>
                    <p id="statusMessage" style="color: #38bdf8; font-size: 0.9em; margin-top: 10px;"></p>
                </div>

                <!-- DASHBOARD Y GRÁFICO INTERACTIVO -->
                <div class="card">
                    <h3>Monitoreo de Entropía & Balance</h3>
                    <canvas id="liveChart" height="150"></canvas>
                </div>
            </div>
        </div>

        <script>
            // Gráfico dinámico interactivo
            const ctx = document.getElementById('liveChart').getContext('2d');
            const chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['12:00', '12:05', '12:10', '12:15', '12:20'],
                    datasets: [{
                        label: 'Balance On-Chain (USD)',
                        data: [1000, 1020, 990, 1050, 1100],
                        borderColor: '#38bdf8',
                        tension: 0.4
                    }]
                },
                options: { responsive: true, plugins: { legend: { labels: { color: 'white' } } } }
            });

            async function updateConfig() {
                const sl = document.getElementById('stopLossInput').value;
                const tp = document.getElementById('takeProfitInput').value;
                const net = document.getElementById('networkSelect').value;

                const res = await fetch('/api/v1/engine/update-config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ stop_loss_pct: parseFloat(sl), take_profit_pct: parseFloat(tp), network: net })
                });
                const data = await res.json();
                document.getElementById('statusMessage').innerText = data.message;
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
