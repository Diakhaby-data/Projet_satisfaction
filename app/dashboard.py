from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pymongo import MongoClient
from collections import Counter

router = APIRouter()

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    client = MongoClient("mongodb://dkb:diakhaby@mongo_service:27017/")
    db = client["satisfaction"]
    collection = db["avis"]
    
    total = collection.count_documents({})
    par_etoile = Counter()
    par_sentiment = Counter()
    
    for avis in collection.find():
        par_etoile[avis["nombre_etoile"]] += 1
        if "sentiment" in avis:
            par_sentiment[avis["sentiment"]] += 1
    
    bars_etoile = ""
    for etoile, count in sorted(par_etoile.items(), reverse=True):
        pct = (count/total)*100
        bars_etoile += f"<div class=\"bar\" style=\"width: {pct}%\">{etoile} ⭐ : {count} avis ({pct:.1f}%)</div>"
    
    bars_sentiment = ""
    for sentiment, count in sorted(par_sentiment.items(), key=lambda x: x[1], reverse=True):
        pct = (count/total)*100
        bars_sentiment += f"<div class=\"bar {sentiment}\" style=\"width: {pct}%\">{sentiment.upper()} : {count} avis ({pct:.1f}%)</div>"
    
    return f"""
    <html>
        <head>
            <title>Dashboard Satisfaction</title>
            <style>
                body {{ font-family: Arial; margin: 40px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .stat {{ background: white; padding: 20px; margin: 10px 0; border-radius: 8px; }}
                .bar {{ background: #4CAF50; height: 40px; margin: 8px 0; color: white; padding: 10px; border-radius: 4px; }}
                .bar.negatif {{ background: #f44336; }}
                .bar.neutre {{ background: #ff9800; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Dashboard Satisfaction Client</h1>
                <div class="stat"><h2>Total: {total} avis</h2></div>
                <div class="stat"><h2>Par étoiles</h2>{bars_etoile}</div>
                <div class="stat"><h2>Par sentiment</h2>{bars_sentiment}</div>
            </div>
        </body>
    </html>
    """
