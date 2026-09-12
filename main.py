import os
from fastapi import FastAPI, HTTPException
from google.cloud import firestore
from pydantic import BaseModel

app = FastAPI(title="K-Aura Core", version="1.1.0")

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