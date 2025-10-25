# main.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import avis_collection, avis_helper
from models import predict

# ========== AJOUT PROMETHEUS ==========
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter

# ====================================================== 
# Modèles Pydantic
# ======================================================
class AvisPredictRequest(BaseModel):
    texte: str

class AvisPredictResponse(BaseModel):
    prediction_ml: int
    sentiment_label: str  # Ajout pour plus de clarté

# ====================================================== 
# Mapping étoiles (1-5) -> labels textuels
# ======================================================
STARS_TO_LABEL = {
    1: "negative",
    2: "negative",
    3: "neutral",
    4: "positive",
    5: "positive"
}

# ====================================================== 
# Initialisation de l'application FastAPI
# ======================================================
app = FastAPI(
    title="API Avis - Satisfaction Client",
    description="API d'analyse des avis clients avec prédiction automatique du sentiment (1 à 5 étoiles).",
    version="1.0.0"
)

# ========== INSTRUMENTATION PROMETHEUS ==========
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# Métriques custom pour l'analyse de sentiment
sentiment_predictions = Counter(
    'sentiment_predictions_total',
    'Nombre total de prédictions de sentiment',
    ['sentiment_label']
)

print("✅ Prometheus metrics enabled on /metrics")
print("📊 Custom metrics: sentiment_predictions_total")

# ====================================================== 
# Endpoints
# ======================================================

@app.get("/avis")
async def get_all_avis():
    avis_list = []
    async for avis in avis_collection.find():
        avis_list.append(avis_helper(avis))
    return avis_list

@app.get("/avis/etoiles/{nombre_etoile}")
async def get_avis_by_etoiles(nombre_etoile: int):
    avis_list = []
    async for avis in avis_collection.find():
        etoiles = avis.get("nombre_etoile") or avis.get("Nombre_etoile")
        if etoiles is not None:
            try:
                if int(str(etoiles).strip()) == nombre_etoile:
                    avis_list.append(avis_helper(avis))
            except ValueError:
                continue
    if not avis_list:
        raise HTTPException(status_code=404, detail=f"Aucun avis avec {nombre_etoile} étoiles")
    return avis_list

@app.get("/avis/pays/{pays}")
async def get_avis_by_pays(pays: str):
    avis_list = []
    async for avis in avis_collection.find({"pays": {"$regex": f"^{pays}$", "$options": "i"}}):
        avis_list.append(avis_helper(avis))
    if not avis_list:
        raise HTTPException(status_code=404, detail=f"Aucun avis trouvé pour le pays '{pays}'")
    return avis_list

@app.post("/avis/predict", response_model=AvisPredictResponse)
async def predict_avis(request: AvisPredictRequest):
    texte = request.texte
    pipeline_path = os.environ.get("PIPELINE_PATH", "/app/sentiment_pipeline.joblib")
    
    if not os.path.exists(pipeline_path):
        raise HTTPException(status_code=500, detail=f"Fichier de pipeline introuvable à {pipeline_path}")
    
    try:
        # ========== CORRECTION DU BUG ==========
        result = predict(texte, pipeline_path=pipeline_path, train_if_missing=True)
        prediction_stars = result.get("predictions")  # Récupère l'INT (1-5)
        
        # Validation
        if not isinstance(prediction_stars, int) or prediction_stars not in range(1, 6):
            print(f"⚠️ Prédiction invalide reçue: {prediction_stars}, résultat brut: {result}")
            prediction_stars = 3  # Fallback
        
        # Conversion vers label textuel pour Prometheus
        sentiment_label = STARS_TO_LABEL.get(prediction_stars, "neutral")
        
        # ========== DEBUG LOGS ==========
        print(f"📝 Texte: {texte[:80]}...")
        print(f"⭐ Prédiction: {prediction_stars} étoiles")
        print(f"🏷️  Label: {sentiment_label}")
        
        # ========== MÉTRIQUE CUSTOM PROMETHEUS ==========
        sentiment_predictions.labels(sentiment_label=sentiment_label).inc()
        
    except Exception as e:
        print(f"❌ Erreur lors de la prédiction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction : {str(e)}")
    
    return AvisPredictResponse(
        prediction_ml=prediction_stars,
        sentiment_label=sentiment_label
    )

# ====================================================== 
# Dashboard
# ====================================================== 
from dashboard import router as dashboard_router
app.include_router(dashboard_router)