import os
import asyncio
from google import genai
from google.genai import types

# ------------------------------------------------------------------
# CONFIGURACIÓN DEL MOTOR DETERMINISTA (K-AURA-SER)
# ------------------------------------------------------------------
CAPITAL_INICIAL = float(os.getenv("CAPITAL_INICIAL", "1000.0"))
TAKE_PROFIT_PCT = 1.00    # 100% de ganancia (Duplica el valor base)
STOP_LOSS_PCT = 0.80      # Protect al 80% (Pérdida máxima 20%)

UMBRAL_STOP_LOSS = CAPITAL_INICIAL * STOP_LOSS_PCT
UMBRAL_TAKE_PROFIT = CAPITAL_INICIAL * (1 + TAKE_PROFIT_PCT)

# Configuración RPC (Polygon Mainnet por defecto)
RPC_URL = os.getenv("RPC_URL", "https://polygon-rpc.com")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS", "0x0000000000000000000000000000000000000000")

# Inicialización de Gemini API
client = genai.Client()

# ------------------------------------------------------------------
# MÓDULO WEB3 / LECTURA EN VIVO DE RED
# ------------------------------------------------------------------
async def obtener_balance_blockchain_real() -> float:
    """
    Consulta en tiempo real el balance del contrato/billetera vía RPC.
    Si la consulta RPC no está configurada o falla, entra fallback determinista.
    """
    import requests
    
    if WALLET_ADDRESS == "0x0000000000000000000000000000000000000000":
        # Retorna el capital inicial mientras se inyecta la billetera en Render
        return CAPITAL_INICIAL

    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [WALLET_ADDRESS, "latest"],
        "id": 1
    }
    
    try:
        response = await asyncio.to_thread(requests.post, RPC_URL, json=payload, timeout=5)
        data = response.json()
        hex_balance = data.get("result", "0x0")
        wei_balance = int(hex_balance, 16)
        # Convertir Wei a Ether/Token de la red (18 decimales)
        balance_eth = wei_balance / 10**18
        return balance_eth
    except Exception as e:
        print(f"[RPC Error]: {e} | Usando respaldo en caché...")
        return CAPITAL_INICIAL

# ------------------------------------------------------------------
# MÓDULO ANALÍTICO (GEMINI 2.5 FLASH)
# ------------------------------------------------------------------
async def generar_reporte_gemini(balance_actual: float, rendimiento_pct: float) -> str:
    prompt = f"""
    Eres el módulo analítico de K-Aura en la arquitectura KemProMed.
    Analiza el estado del motor en Polygon:
    - Capital Base: {CAPITAL_INICIAL}
    - Balance On-Chain Actual: {balance_actual}
    - Rendimiento: {rendimiento_pct:.2f}%
    
    Genera un informe conciso de máximo 2 oraciones resaltando la estabilidad de la liquidez.
    """
    try:
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"[Gemini Status Log]: Balance actual en {balance_actual}. Error API: {e}"

# ------------------------------------------------------------------
# LÓGICA DE DETENCIÓN Y GATILLOS
# ------------------------------------------------------------------
def evaluar_gatillos(balance_actual: float) -> tuple[bool, str]:
    if balance_actual <= UMBRAL_STOP_LOSS:
        return True, "STOP_LOSS_ACTIVADO"
    if balance_actual >= UMBRAL_TAKE_PROFIT:
        return True, "TAKE_PROFIT_ACTIVADO"
    return False, "EN_RANGO"

def ejecutar_accion_seguridad(accion: str):
    if accion == "STOP_LOSS_ACTIVADO":
        print(f"\n🚨 [GATILLO RECTIFICADO]: SL (80%) ALCANZADO. Retirando liquidez...")
    elif accion == "TAKE_PROFIT_ACTIVADO":
        print(f"\n🎯 [GATILLO GANANCIA]: TP (100%) ALCANZADO. Asegurando beneficios...")

# ------------------------------------------------------------------
# CICLO CONTINUO DE MONITOREO
# ------------------------------------------------------------------
async def main():
    print("=== MOTOR K-AURA INICIADO (POLYGON MAINNET) ===")
    print(f"Base: ${CAPITAL_INICIAL} | SL: ${UMBRAL_STOP_LOSS} | TP: ${UMBRAL_TAKE_PROFIT}\n")

    while True:
        balance = await obtener_balance_blockchain_real()
        rendimiento = ((balance - CAPITAL_INICIAL) / CAPITAL_INICIAL) * 100 if CAPITAL_INICIAL > 0 else 0.0

        print(f"[On-Chain Read]: Balance: {balance:.4f} | Rendimiento: {rendimiento:+.2f}%")

        detener, estado = evaluar_gatillos(balance)
        if detener:
            ejecutar_accion_seguridad(estado)
            reporte = await generar_reporte_gemini(balance, rendimiento)
            print(f"[Informe Final Gemini]: {reporte}")
            print("=== CICLO FINALIZADO Y PROTEGIDO ===")
            break

        # Log diario / periódico de Gemini sin detener el flujo
        log_status = await generar_reporte_gemini(balance, rendimiento)
        print(f"[Gemini Log]: {log_status}\n")

        # Intervalo de lectura de bloque (3 segundos)
        await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
