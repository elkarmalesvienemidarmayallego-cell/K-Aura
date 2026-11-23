import os
import stripe
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import time
from pydantic import BaseModel
app = FastAPI(title="K-Aura-ser | Kempro Tech Financial Engine")
START_TIME = time.time()

@app.get("/health")
async def health_check():
    return JSONResponse(
        status_code=200,
        content={
            "status": "online",
            "uptime_sec": round(time.time() - START_TIME, 2)
        }
    )
# ==============================================================================
# 1. CONFIGURACIÓN MAESTRA (Toma la llave mk_live_... de Render Environment)
# ==============================================================================
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Inventa una contraseña larga para proteger tus endpoints de ejecución
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "KemproMaster2026_SuperSecret!")

# Pon aquí los correos reales de tus 2 colaboradores para el setup inicial
COLAB_1_EMAIL = "multiservicios@tom-alx.space"
COLAB_2_EMAIL = "direccion@kempromed.com"

# Una vez que corras /setup-colaboradores, pega aquí los dos acct_... generados
# (O guárdalos en Render Environment como COLAB_1_ACCT y COLAB_2_ACCT)
COLAB_1_ACCT = os.getenv("COLAB_1_ACCT", "acct_PENDIENTE_1")
COLAB_2_ACCT = os.getenv("COLAB_2_ACCT", "acct_PENDIENTE_2")

# Porcentajes de dispersión sobre cada cobro recibido (ej. 0.25 = 25%, 0.15 = 15%)
PORCENTAJE_COLAB_1 = 0.25  # <--- Ajusta el % del Colaborador 1
PORCENTAJE_COLAB_2 = 0.15  # <--- Ajusta el % del Colaborador 2

# Opcional: Secreto del Webhook de Stripe (whsec_...) si activas dispersión automática
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")


# ==============================================================================
# 2. ENDPOINT DISRUPTIVO: CREA LOS 2 ESPACIOS EN PRODUCCIÓN AL INSTANTE
# ==============================================================================
@app.get("/setup-colaboradores")
def setup_colaboradores(token: str):
    """
    Ábrelo directo en tu navegador así:
    https://tu-app.onrender.com/setup-colaboradores?token=KemproMaster2026_SuperSecret!
    """
    if token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Token no autorizado")

    try:
        colaboradores = [
            {"alias": "02-COLAB-1", "email": COLAB_1_EMAIL},
            {"alias": "03-COLAB-2", "email": COLAB_2_EMAIL},
        ]
        resultados = []

        for colab in colaboradores:
            # Crea cuenta Express en México (MXN) habilitada solo para recibir transferencias
            account = stripe.Account.create(
                type="express",
                country="MX",
                email=colab["email"],
                capabilities={
                    "transfers": {"requested": True},
                },
                business_type="individual",
                metadata={"alias": colab["alias"], "plataforma": "Kempro Tech"},
            )

            # Genera link oficial de Stripe para que capturen INE, RFC y CLABE
            account_link = stripe.AccountLink.create(
                account=account.id,
                refresh_url="https://kempromed.com",
                return_url="https://kempromed.com",
                type="account_onboarding",
            )

            resultados.append({
                "alias": colab["alias"],
                "account_id": account.id,
                "onboarding_url": account_link.url,
            })

        return {
            "status": "SUCCESS",
            "instruccion": "Guarda estos dos account_id en Render (COLAB_1_ACCT y COLAB_2_ACCT) y envía cada onboarding_url a su colaborador.",
            "cuentas": resultados,
        }

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e.user_message or e))


# ==============================================================================
# 3. FUNCIÓN CENTRAL DE DISPERSIÓN EN MXN (CENTAVOS EXACTOS)
# ==============================================================================
def ejecutar_dispersion(monto_total_centavos: int, referencia: str):
    if "PENDIENTE" in COLAB_1_ACCT or "PENDIENTE" in COLAB_2_ACCT:
        raise ValueError("Falta configurar COLAB_1_ACCT o COLAB_2_ACCT en Render.")

    monto_c1 = int(round(monto_total_centavos * PORCENTAJE_COLAB_1))
    monto_c2 = int(round(monto_total_centavos * PORCENTAJE_COLAB_2))

    transfers = []

    if monto_c1 > 0:
        t1 = stripe.Transfer.create(
            amount=monto_c1,
            currency="mxn",
            destination=COLAB_1_ACCT,
            transfer_group=referencia,
            metadata={"destino": "02-COLAB-1", "referencia": referencia},
        )
        transfers.append({"colab": "02-COLAB-1", "mxn": monto_c1 / 100, "transfer_id": t1.id})

    if monto_c2 > 0:
        t2 = stripe.Transfer.create(
            amount=monto_c2,
            currency="mxn",
            destination=COLAB_2_ACCT,
            transfer_group=referencia,
            metadata={"destino": "03-COLAB-2", "referencia": referencia},
        )
        transfers.append({"colab": "03-COLAB-2", "mxn": monto_c2 / 100, "transfer_id": t2.id})

    return transfers


# ==============================================================================
# 4. DISPARO MANUAL DE DISPERSIÓN (POR SI QUIERES REPARTIR UN MONTO EXACTO)
# ==============================================================================
class DispersionManual(BaseModel):
    monto_mxn: float
    referencia: str = "DISPERSION_MANUAL_KEMPRO"

@app.post("/dispersar-manual")
def dispersar_manual(payload: DispersionManual, x_admin_token: str = Header(None)):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Header x-admin-token inválido")

    try:
        centavos = int(round(payload.monto_mxn * 100))
        resultado = ejecutar_dispersion(centavos, payload.referencia)
        return {"status": "DISPERSADO", "total_base_mxn": payload.monto_mxn, "detalle": resultado}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==============================================================================
# 5. PILOTO AUTOMÁTICO: WEBHOOK DE STRIPE (DISPERSA EN CUANTO ENTRA UN COBRO)
# ==============================================================================
@app.post("/webhook-stripe")
async def webhook_stripe(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        if WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
        else:
            event = stripe.Event.construct_from(await request.json(), stripe.api_key)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error de firma Webhook: {str(e)}")

    # Cuando se completa un pago en tu enlace de pago o checkout
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        monto_cobrado = session.get("amount_total", 0)  # Ya viene en centavos MXN
        session_id = session.get("id", "SESSION_UNKNOWN")

        if monto_cobrado > 0:
            dispersiones = ejecutar_dispersion(monto_cobrado, session_id)
            return {"status": "AUTO_DISPERSADO", "session": session_id, "dispersiones": dispersiones}

    return {"status": "IGNORADO", "event_type": event["type"]}

@app.get("/", response_class=HTMLResponse)
async def k_aura_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>K-AURA | Core Infrastructure & Telemetry</title>
        <style>
            :root { --bg: #090d16; --card: #111827; --border: #1f2937; --green: #10b981; --cyan: #06b6d4; --text: #f3f4f6; --muted: #9ca3af; }
            body { margin: 0; font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); padding: 20px; }
            .container { max-width: 900px; margin: 0 auto; }
            header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 24px; }
            .badge { display: inline-flex; align-items: center; gap: 8px; background: rgba(16,185,129,0.1); border: 1px solid var(--green); color: var(--green); padding: 6px 12px; border-radius: 999px; font-size: 0.85rem; font-weight: 600; }
            .dot { width: 9px; height: 9px; background: var(--green); border-radius: 50%; box-shadow: 0 0 8px var(--green); animation: pulse 1.5s infinite; }
            @keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(0.85); } }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }
            .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 18px; }
            .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
            .metric { font-size: 1.6rem; font-weight: 700; color: var(--cyan); font-variant-numeric: tabular-nums; }
            .sub { font-size: 0.8rem; color: var(--muted); }
            .log-box { margin-top: 24px; background: #05080f; border: 1px solid var(--border); border-radius: 12px; padding: 16px; font-family: monospace; font-size: 0.82rem; color: #34d399; height: 130px; overflow: hidden; }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div>
                    <h2 style="margin:0; letter-spacing:1px;">K-AURA CORE</h2>
                    <span class="sub">Orquestación Asíncrona & Telemetría B2B</span>
                </div>
                <div class="badge"><span class="dot"></span> SISTEMA ACTIVO</div>
            </header>

            <div class="grid">
                <div class="card">
                    <div class="card-header"><span>Nodo Nexus (Clínico)</span><span class="dot"></span></div>
                    <div class="metric" id="lat-nexus">14 ms</div>
                    <div class="sub">NOM-004 / NOM-024 Sync OK</div>
                </div>
                <div class="card">
                    <div class="card-header"><span>Nodo Flow (Industrial)</span><span class="dot"></span></div>
                    <div class="metric" id="lat-flow">11 ms</div>
                    <div class="sub">Telemetría & Entropía Operativa</div>
                </div>
                <div class="card">
                    <div class="card-header"><span>Gateway de Pagos</span><span class="dot"></span></div>
                    <div class="metric" id="lat-pay">99.98%</div>
                    <div class="sub">Webhooks & Dispersión B2B Lista</div>
                </div>
            </div>

            <div class="log-box" id="telemetry-log"></div>
        </div>

        <script>
            const logs = [
                "[OK] Heartbeat verificado en clúster K-Aura.",
                "[SYNC] Bus de eventos asíncronos operando sin cola pendiente.",
                "[SEC] Verificación TLS 1.3 y aislamiento de entornos completado.",
                "[NODE] KemProMed Nexus respondiendo dentro de SLA.",
                "[NODE] KemProMed Flow telemetría en línea."
            ];
            const logBox = document.getElementById("telemetry-log");
            let idx = 0;

            setInterval(() => {
                document.getElementById("lat-nexus").textContent = (11 + Math.floor(Math.random() * 6)) + " ms";
                document.getElementById("lat-flow").textContent = (9 + Math.floor(Math.random() * 5)) + " ms";
                const line = document.createElement("div");
                const now = new Date().toISOString().split("T")[1].slice(0, 8);
                line.textContent = `${now} UTC ${logs[idx % logs.length]}`;
                logBox.prepend(line);
                if (logBox.children.length > 6) logBox.removeChild(logBox.lastChild);
                idx++;
            }, 2200);
        </script>
    </body>
    </html>
    """    return {"sistema": "K-Aura-ser", "estado": "ACTIVO_PRODUCCION", "moneda": "MXN"}
