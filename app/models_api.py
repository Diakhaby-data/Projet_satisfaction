# app/models_api.py
from pydantic import BaseModel

class AvisPredictRequest(BaseModel):
    texte: str

class AvisPredictResponse(BaseModel):
    sentiment: int  # ou str si tu renvoies "positif/negatif"
