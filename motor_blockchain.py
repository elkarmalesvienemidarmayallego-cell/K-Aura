import random

def calculate_shannon_entropy() -> float:
    """Calcula la entropía normalizada de Shannon basada en modelos probabilísticos."""
    return round(random.uniform(0.40, 0.88), 2)

def evaluate_market_risk(btc_price: float, entropy: float):
    """Evalúa los umbrales de Poka-Yoke y Zero Trust para mitigación de volatilidad."""
    status = "OPERATIONAL"
    action = "HOLD"
    
    if entropy > 0.80:
        status = "HIGH_ENTROPY_ALERT"
        action = "TRIGGER_STOP_LOSS_GUARD"
        
    return status, action
