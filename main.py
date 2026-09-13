import os
from fastapi import FastAPI, HTTPException
from google.cloud import firestore
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

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
