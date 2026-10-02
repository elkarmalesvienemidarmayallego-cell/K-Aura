import os
import asyncio
from google import genai
from google.genai import types

# ------------------------------------------------------------------
# CONFIGURACIÓN DEL MOTOR Y LÍMITES DETERMINISTAS
# ------------------------------------------------------------------
CAPITAL_INICIAL = 1000.0  # Cambia por tu balance base en USD/Token
TAKE_PROFIT_PCT = 1.00    # 100% de ganancia (Duplicar el capital a $2000)
STOP_LOSS_PCT = 0.80      # 80% de caída (Proteger si cae al 80% del valor base / o perder el 80% según tu lógica)

# Límite inferior y superior en monto real
UMBRAL_STOP_LOSS = CAPITAL_INICIAL * STOP_LOSS_PCT   # Ej. $800
UMBRAL_TAKE_PROFIT = CAPITAL_INICIAL * (1 + TAKE_PROFIT_PCT) # Ej. $2000

# Inicialización del cliente de Gemini
# Requiere la variable de entorno: export GEMINI_API_KEY="tu_api_key"
client = genai.Client()

# ------------------------------------------------------------------
# MÓDULO DE GEMINI (Análisis de logs y estado sin tocar los gatillos)
# ------------------------------------------------------------------
async def obtener_reporte_gemini(balance_actual: float, rendimiento_pct: float, historial_eventos: list) -> str:
    """Envía métricas a Gemini únicamente para estructurar reportes analíticos."""
    prompt = f"""
    Eres el módulo analítico de un motor determinista en blockchain.
    Genera un informe ejecutivo conciso sobre el estado del sistema con estos datos:

    - Balance Inicial: {CAPITAL_INICIAL} USD
    - Balance Actual: {balance_actual} USD
    - Rendimiento Acumulado: {rendimiento_pct:.2f}%
    - Últimos eventos procesados: {historial_eventos}

    Instrucciones:
    1. Sé breve y directo (máximo 3 oraciones).
    2. Enfócate en la estabilidad operativa y liquidez.
    """
    
    try:
        # Uso asíncrono para no bloquear la ejecución del bucle principal
        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        # Fallback de seguridad: Si la API de Gemini falla, el motor NO se detiene
        return f"[Gemini Offline - Análisis interno]: Balance en ${balance_actual}. Error API: {e}"

# ------------------------------------------------------------------
# LÓGICA DETERMINISTA (Stop Loss / Take Profit / Ejecución)
# ------------------------------------------------------------------
def evaluar_gatillos_financieros(balance_actual: float) -> tuple[bool, str]:
    """
    Evaluación matemática PURA. No depende de IA ni peticiones externas.
    """
    if balance_actual <= UMBRAL_STOP_LOSS:
        return True, "STOP_LOSS_TRIGGERED"
    
    if balance_actual >= UMBRAL_TAKE_PROFIT:
        return True, "TAKE_PROFIT_TRIGGERED"
    
    return False, "OPERANDO_NORMAL"

def ejecutar_orden_blockchain(accion: str):
    """Aquí conectas tus llamadas RPC / Web3 para liquidar o pausar contratos."""
    if accion == "STOP_LOSS_TRIGGERED":
        print("\n🚨 [GATILLO DE SEGURIDAD]: STOP LOSS ALCANZADO (80%).")
        print("-> Cerrando posiciones y transfiriendo liquidez a bóveda segura...")
    elif accion == "TAKE_PROFIT_TRIGGERED":
        print("\n🎯 [GATILLO DE GANANCIA]: TAKE PROFIT ALCANZADO (100%).")
        print("-> Asegurando ganancias y asegurando el capital objetivo...")

# ------------------------------------------------------------------
# BUCLE PRINCIPAL DE EJECUCIÓN (MAIN LOOP)
# ------------------------------------------------------------------
async def ciclo_principal():
    print("=== MOTOR DE AUTOGESTIÓN INICIADO ===")
    print(f"Capital Base: ${CAPITAL_INICIAL} | SL: ${UMBRAL_STOP_LOSS} | TP: ${UMBRAL_TAKE_PROFIT}\n")

    # Simulación de balances recibidos por la Blockchain (reemplazar por tu lectura RPC real)
    simulacion_lecturas_blockchain = [1050.0, 1200.0, 950.0, 790.0, 2100.0]
    historial = []

    for balance in simulacion_lecturas_blockchain:
        rendimiento = ((balance - CAPITAL_INICIAL) / CAPITAL_INICIAL) * 100
        historial.append(f"Lectura: ${balance}")

        print(f"--- [Lectura On-Chain]: Balance actual ${balance} ({rendimiento:+.2f}%) ---")

        # 1. EVALUACIÓN MATEMÁTICA INMEDIATA (Cero Latencia)
        debe_detenerse, estado = evaluar_gatillos_financieros(balance)

        if debe_detenerse:
            ejecutar_orden_blockchain(estado)
            
            # Gemini hace el reporte final de la detención
            reporte_final = await obtener_reporte_gemini(balance, rendimiento, historial)
            print(f"\n[Informe Final Gemini]:\n{reporte_final}")
            print("\n=== MOTOR DETENIDO POR REGLA DETERMINISTA ===")
            break

        # 2. SI TODO ESTÁ NORMAL, GEMINI GENERA LOG DE ESTADO
        reporte_rutina = await obtener_reporte_gemini(balance, rendimiento, historial[-3:])
        print(f"[Gemini Status]: {reporte_rutina}\n")

        # Pausa entre cada ciclo de monitoreo
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(ciclo_principal())
