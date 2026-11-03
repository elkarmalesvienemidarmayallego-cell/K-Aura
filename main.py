import asyncio
import json
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
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

# <-- AÑADE ESTA RUTA AQUÍ PARA EVITAR EL "NOT FOUND" EN LA RAÍZ -->
@app.get("/")
async def root():
    return {
        "status": "ONLINE",
        "engine": "K-Aura Core Engine v2.1",
        "websocket_endpoint": "/ws/metrics"
    }

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
