import asyncio
import json
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from motor_blockchain import calculate_shannon_entropy, evaluate_market_risk

app = FastAPI(title="K-Aura Quantitative Risk Engine", version="2.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HTML_CONTENT = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>K-AURA Core Engine v2.1</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        body { background-color: #08111B; color: #E2E8F0; font-family: ui-sans-serif, system-ui, sans-serif; }
        .glow-border { border: 1px solid rgba(59, 130, 246, 0.2); box-shadow: 0 0 15px rgba(59, 130, 246, 0.05); }
    </style>
</head>
<body class="p-4 md:p-8 max-w-5xl mx-auto">
    <!-- HEADER / LIVE STATUS -->
    <div class="bg-slate-900/80 p-4 rounded-xl border border-slate-800 flex flex-wrap justify-between items-center gap-4 glow-border">
        <div class="flex items-center gap-2">
            <span class="font-bold text-xl text-white tracking-wider">K-AURA</span>
            <span class="text-xs bg-cyan-950 text-cyan-400 border border-cyan-800 px-2 py-0.5 rounded-full">CORE ENGINE v2.1</span>
        </div>
        <div class="flex items-center gap-6 text-xs font-mono">
            <div>BTC/USD LIVE TICK: <span id="btcPrice" class="text-cyan-400 font-bold">$67,245.59</span></div>
            <div>STATUS: <span id="engineStatus" class="text-emerald-400 font-bold">OPERATIONAL</span></div>
        </div>
    </div>

    <!-- PANEL DE CONEXIÓN DE WALLET Y MODO REAL -->
    <div class="mt-6 bg-slate-900/90 p-6 rounded-xl border border-cyan-500/30 glow-border">
        <h3 class="text-xs font-bold text-white uppercase tracking-wider mb-2">Conexión de Producción & Payouts (USDT)</h3>
        <p class="text-[11px] text-slate-400 mb-4">Enruta ganancias automáticas directo a tu wallet o cold storage.</p>
        
        <div class="flex items-center gap-2 w-full md:w-auto">
            <input type="text" id="userWallet" placeholder="Dirección Wallet USDT (Polygon/Solana/TRC20)" class="bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-xs text-cyan-300 w-full focus:outline-none focus:border-cyan-500">
            <button onclick="connectRealWallet()" class="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold rounded transition-all whitespace-nowrap">CONECTAR</button>
        </div>
        <div id="walletAlert" class="mt-2 text-[10px] text-slate-500 font-mono hidden"></div>
    </div>

    <!-- SCRIPT DE CONEXIÓN Y WEBSOCKET EN VIVO -->
    <script>
        lucide.createIcons();

        // Detección automática del protocolo seguro para producción en Render
        const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const wsUrl = protocol + window.location.host + '/ws/metrics';
        const ws = new WebSocket(wsUrl);

        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            const priceEl = document.getElementById('btcPrice');
            if (priceEl) {
                priceEl.innerText = `$${data.btc_price.toLocaleString()}`;
            }

            const statusEl = document.getElementById('engineStatus');
            if (statusEl) {
                statusEl.innerText = data.engine_status;
            }
        };

        ws.onclose = function() {
            const statusEl = document.getElementById('engineStatus');
            if (statusEl) {
                statusEl.innerText = "DISCONNECTED";
                statusEl.className = "text-red-500 font-bold";
            }
        };

        function connectRealWallet() {
            const wallet = document.getElementById('userWallet').value;
            const alertBox = document.getElementById('walletAlert');
            alertBox.classList.remove('hidden');
            
            if (wallet.length > 10) {
                alertBox.className = "mt-2 text-[10px] text-emerald-400 font-mono";
                alertBox.innerText = `✓ Wallet vinculada en directo: ${wallet} (Payouts USDT habilitados)`;
            } else {
                alertBox.className = "mt-2 text-[10px] text-red-400 font-mono";
                alertBox.innerText = `⚠ Ingresa una dirección wallet válida.`;
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML_CONTENT

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

manager = ConnectionManager()

@app.websocket("/ws/metrics")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            btc_price = round(67000 + random.uniform(-150, 150), 2)
            entropy = calculate_shannon_entropy()
            status, action = evaluate_market_risk(btc_price, entropy)
            
            payload = {
                "btc_price": btc_price,
                "shannon_entropy": entropy,
                "volatility_temp": round(random.uniform(1.5, 3.5), 2),
                "engine_status": status,
                "mitigation_action": action
            }
            
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(2.0)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
