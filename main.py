import os
from fastapi import FastAPI, HTTPException
from google.cloud import firestore
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types


app = FastAPI(title="K-Aura Core", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite conexiones desde cualquier origen web
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Safe Firestore initialization
db = None
try:
    db = firestore.Client()
except Exception as e:
    print(f"Firestore not initialized: {e}")




class TrafficEvent(BaseModel):
  source: str
  campaign: str
  rhythm_tag: str
  technologic_flag: bool
  license_id: str


@app.get("/")
def health_check():
  return {
      "status": "active",
      "ecosystem": "K-Aura",
      "module": "Technologic & Rhythm Engine",
  }


@app.post("/api/v1/track")
def track_traffic(event: TrafficEvent):
  try:
    doc_ref = db.collection("kaura_traffic").document()
    doc_ref.set({
        "source": event.source,
        "campaign": event.campaign,
        "rhythm_tag": event.rhythm_tag,
        "technologic_flag": event.technologic_flag,
        "license_id": event.license_id,
        "timestamp": firestore.SERVER_TIMESTAMP,
    })
    return {"status": "success", "id": doc_ref.id}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

BOTS_REGULADOS = {
    "stephenie-rodiles": {
        "nombre": "Stephenie Rodiles S.",
        "enfoque": "Esgrima dialéctica e intelecto afilado.",
        "estado": "activo",
    },
    "cynthia-aviles": {
        "nombre": "Cynthia Aviles",
        "enfoque": "Interacción directa y flujo visual dinámico.",
        "estado": "activo",
    },
    "lorena-sanchez": {
        "nombre": "Lorena Sanchez",
        "enfoque": "Línea de interacción estratégica.",
        "estado": "activo",
    },
    "azul-gallareta": {
        "nombre": "Azul Gallareta",
        "enfoque": "Identidad directa y de alta afinidad.",
        "estado": "activo",
    },
}


@app.get("/api/v1/bots")
async def listar_bots():
  return {"status": "success", "bots_regulados": BOTS_REGULADOS}

@app.post("/api/v1/interaccion-ia")
async def interactuar_con_ia(evento: TrafficEvent):
  try:
    # Inicializa el cliente oficial consumiendo la API Key de las variables de entorno de Render
    client = genai.Client()
    
    # Definimos la directriz de personalidad basada en el contexto del módulo
    system_prompt = (
        f"Eres el núcleo inteligente del módulo {evento.source} de K-Aura, "
        f"enfocado en la campaña {evento.campaign} con etiqueta {evento.rhythm_tag}. "
        "Mantén una respuesta afilada, directa y alineada con la identidad corporativa."
    )
    
    # Llamada oficial a Google AI Studio (modelo Gemini)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Interacción del usuario para el ecosistema. Contexto técnico: {evento.technologic_flag}",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7,
        ),
    )
    
    respuesta_ia = response.text

    # Guardado automático de la interacción en el Dashboard de Firestore
    doc_ref = db.collection("k_aura_dashboard_interacciones").document()
    doc_ref.set({
        "source": evento.source,
        "campaign": evento.campaign,
        "rhythm_tag": evento.rhythm_tag,
        "technologic_flag": evento.technologic_flag,
        "license_id": evento.license_id,
        "respuesta_generada": respuesta_ia,
        "timestamp": firestore.SERVER_TIMESTAMP,
    })

    return {
        "status": "success",
        "interaccion_id": doc_ref.id,
        "respuesta_ia": respuesta_ia,
    }

  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

