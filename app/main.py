from fastapi import FastAPI, HTTPException
from app.database import avis_collection, avis_helper
from app.models import AvisPredictRequest, AvisPredictResponse

app = FastAPI(title="API Avis - Satisfaction Client")

# -----------------------------
# 1. Récupérer tous les avis
# -----------------------------
@app.get("/avis")
async def get_all_avis():
    avis_list = []
    async for avis in avis_collection.find():
        avis_list.append(avis_helper(avis))
    return avis_list

# -----------------------------
# 2. Récupérer les avis par nombre d'étoiles
# -----------------------------
@app.get("/avis/etoiles/{nombre_etoile}")
async def get_avis_by_etoiles(nombre_etoile: int):
    avis_list = []
    async for avis in avis_collection.find({"nombre_etoile": nombre_etoile}):
        avis_list.append(avis_helper(avis))
    if not avis_list:
        raise HTTPException(status_code=404, detail=f"Aucun avis avec {nombre_etoile} étoiles")
    return avis_list

# -----------------------------
# 3. Récupérer les avis par pays
# -----------------------------
@app.get("/avis/pays/{pays}")
async def get_avis_by_pays(pays: str):
    avis_list = []
    async for avis in avis_collection.find({"pays": {"$regex": f"^{pays}$", "$options": "i"}}):
        avis_list.append(avis_helper(avis))
    if not avis_list:
        raise HTTPException(status_code=404, detail=f"Aucun avis trouvé pour le pays '{pays}'")
    return avis_list

# -----------------------------
# 4. Endpoint de prédiction ML
# -----------------------------
@app.post("/avis/predict", response_model=AvisPredictResponse)
async def predict_avis(request: AvisPredictRequest):
    texte = request.texte.lower()
    # Exemple rapide, à remplacer par ton pipeline ML réel
    prediction = 1 if "catastrophe" in texte else 5
    return AvisPredictResponse(prediction_ml=prediction)
