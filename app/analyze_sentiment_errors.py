#!/usr/bin/env python3
"""
Diagnostic des erreurs du modèle de sentiment
Analyse les textes par classe pour comprendre les confusions
"""
import sys
from pymongo import MongoClient
from collections import Counter
import pandas as pd

try:
    from models import clean_text, load_pipeline
except ImportError:
    print("❌ Erreur: Impossible d'importer models.py")
    sys.exit(1)


def main():
    print("=" * 70)
    print(" DIAGNOSTIC DES ERREURS DU MODÈLE")
    print("=" * 70)
    
    # 1. Connexion MongoDB
    mongo_uri = "mongodb://dkb:diakhaby@mongo_service:27017/"
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.server_info()
        print(" Connexion MongoDB OK")
    except Exception as e:
        print(f"❌ Erreur MongoDB: {e}")
        sys.exit(1)
    
    db = client["satisfaction"]
    collection = db["avis"]
    
    # 2. Charger le modèle
    pipeline_path = "/app/sentiment_pipeline.joblib"
    pipe = load_pipeline(pipeline_path)
    if pipe is None:
        print(f"❌ Pipeline introuvable: {pipeline_path}")
        sys.exit(1)
    print(f" Pipeline chargé: {pipeline_path}")
    
    # 3. Récupérer les données
    print("\n Récupération des avis...")
    avis = list(collection.find({}))
    
    texts = []
    labels = []
    
    for a in avis:
        texte = a.get("contenu", "") or a.get("texte", "") or a.get("titre_avis", "")
        texte = texte.strip()
        etoiles = a.get("nombre_etoile") or a.get("etoiles")
        
        if texte and etoiles is not None:
            texts.append(texte)
            labels.append(int(etoiles))
    
    print(f" {len(texts)} avis chargés")
    
    # 4. Prédire sur tous les avis
    print("\n Prédictions en cours...")
    cleaned_texts = [clean_text(t) for t in texts]
    predictions = pipe.predict(cleaned_texts)
    
    # 5. Analyser les erreurs par classe
    print("\n" + "=" * 70)
    print(" ANALYSE PAR CLASSE")
    print("=" * 70)
    
    for true_class in sorted(set(labels)):
        print(f"\n🔹 VRAIE CLASSE: {true_class} ⭐")
        print("-" * 70)
        
        # Filtrer les avis de cette classe
        indices = [i for i, l in enumerate(labels) if l == true_class]
        
        if not indices:
            print("   Aucun avis")
            continue
        
        # Compter les prédictions
        preds_for_class = [predictions[i] for i in indices]
        pred_counts = Counter(preds_for_class)
        
        print(f"   Total: {len(indices)} avis")
        print(f"   Distribution des prédictions:")
        
        for pred_class in sorted(pred_counts.keys()):
            count = pred_counts[pred_class]
            pct = (count / len(indices)) * 100
            correct = "✅" if pred_class == true_class else "❌"
            print(f"      {correct} Prédiction {pred_class}⭐: {count:5d} ({pct:5.1f}%)")
        
        # Afficher quelques exemples de confusion
        confusions = [(i, preds_for_class[indices.index(i)]) for i in indices if predictions[i] != true_class]
        
        if confusions:
            print(f"\n   Exemples d'erreurs ({len(confusions)} total):")
            for i, (idx, pred) in enumerate(confusions[:3]):  # Top 3
                texte_original = texts[idx]
                texte_clean = cleaned_texts[idx]
                
                print(f"\n      Erreur #{i+1}:")
                print(f"         Texte: \"{texte_original[:60]}...\"")
                print(f"         Nettoye: \"{texte_clean[:60]}...\"")
                print(f"         Vrai: {true_class}⭐ → Prédit: {pred}⭐")
    
    # 6. Résumé des confusions principales
    print("\n" + "=" * 70)
    print(" MATRICE DE CONFUSION GLOBALE")
    print("=" * 70)
    
    from sklearn.metrics import confusion_matrix
    import numpy as np
    
    classes = sorted(set(labels))
    cm = confusion_matrix(labels, predictions, labels=classes)
    
    print("\n        Prédictions →")
    print("Réels ↓", end="")
    for star in classes:
        print(f"  {star}⭐", end="")
    print("  | Total")
    
    for i, true_class in enumerate(classes):
        print(f"  {true_class}⭐", end="")
        total = 0
        for j in range(len(classes)):
            count = cm[i][j]
            total += count
            # Colorer les diagonales
            if i == j:
                print(f"  {count:3d}", end="")
            else:
                print(f"  {count:3d}", end="")
        print(f"  | {total:5d}")
    
    # Calculer les taux d'erreur par classe
    print("\n Taux de prédiction correcte par classe:")
    for i, true_class in enumerate(classes):
        total = cm[i].sum()
        correct = cm[i][i]
        accuracy = (correct / total * 100) if total > 0 else 0
        status = "✅" if accuracy >= 90 else "⚠️" if accuracy >= 70 else "❌"
        print(f"   {status} {true_class}⭐: {accuracy:.1f}% ({correct}/{total})")
    
    
    # Analyser les pires confusions
    confusion_errors = []
    for i in range(len(classes)):
        for j in range(len(classes)):
            if i != j and cm[i][j] > 0:
                confusion_errors.append((cm[i][j], i, j, classes[i], classes[j]))
    
    confusion_errors.sort(reverse=True)
    
    print("\nPrincipales confusions:")
    for count, i, j, true_star, pred_star in confusion_errors[:5]:
        pct = (count / cm[i].sum() * 100) if cm[i].sum() > 0 else 0
        print(f"   • {true_star}⭐ → {pred_star}⭐: {count} avis ({pct:.1f}%)")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)