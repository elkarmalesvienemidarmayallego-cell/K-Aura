import os
from fastapi import FastAPI, HTTPException
from google.cloud import firestore
from pydantic import BaseModel

app = FastAPI(title="K-Aura Core", version="1.0.0")

# Inicialización de Firestore usando la infraestructura estándar de GCP
db = firestore.Client()


class TrafficEvent(BaseModel):
  source: str
  campaign: str
  metadata_tag: str


@app.get("/")
def health_check():
  return {"status": "active", "ecosystem": "K-Aura"}


@app.post("/api/v1/track")
def track_traffic(event: TrafficEvent):
  try:
    doc_ref = db.collection("kaura_traffic").document()
    doc_ref.set({
        "source": event.source,
        "campaign": event.campaign,
        "metadata_tag": event.metadata_tag,
        "timestamp": firestore.SERVER_TIMESTAMP,
    })
    return {"status": "success", "id": doc_ref.id}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
