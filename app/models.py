from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Avis(BaseModel):
    id: Optional[str] = None
    titre_avis: str
    contenu_texte: str
    texte_nettoye: Optional[str] = ""
    nombre_etoile: int
    date_avis: Optional[datetime] = None
    pays: str
    langue: str
    reponse_entreprise: bool = False
    texte_entreprise: Optional[str] = None
    date_reponse_entreprise: Optional[datetime] = None
    prediction_ml: Optional[int] = None

class AvisPredictRequest(BaseModel):
    texte: str

class AvisPredictResponse(BaseModel):
    prediction_ml: int
