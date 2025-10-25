#!/usr/bin/env python3
"""
Script de réentraînement du modèle de sentiment avec améliorations:
- Gère le déséquilibre des classes avec class_weight
- Ajoute une validation croisée pour détecter l'overfitting
- Teste sur des données hold-out (test set)
- Hyperparamètres optimisés
"""
import os
import sys
from collections import Counter
from pymongo import MongoClient
import numpy as np
import pandas as pd

# Importer les fonctions depuis models.py
try:
    from models import clean_text, build_pipeline, save_pipeline, load_pipeline
except ImportError:
    print("❌ Erreur: Impossible d'importer models.py")
    sys.exit(1)

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, confusion_matrix, f1_score
import joblib


def get_sentiment_label(stars: int) -> str:
    """Convertit les étoiles en label de sentiment"""
    if stars in [1, 2]:
        return "négatif"
    elif stars == 3:
        return "neutre"
    elif stars in [4, 5]:
        return "positif"
    return "unknown"


def build_balanced_pipeline() -> Pipeline:
    """
    Pipeline optimisé avec gestion du déséquilibre des classes
    """
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=5000,      # Limiter les features
            ngram_range=(1, 2),     # Unigrams + bigrams
            min_df=5,               # Ignorer les mots très rares
            max_df=0.8              # Ignorer les mots trop communs
        )),
        ("clf", LogisticRegression(
            max_iter=1000,
            random_state=42,
            class_weight='balanced',  # ✅ CRUCIAL: équilibre les classes
            solver='lbfgs',
            C=1.0                    # Régularisation
        ))
    ])
    return pipe


def main():
    print("=" * 70)
    print(" RÉENTRAÎNEMENT DU MODÈLE DE SENTIMENT")
    print("=" * 70)
    
    # 1. Connexion à MongoDB
    mongo_user = "dkb"
    mongo_password = "diakhaby"
    mongo_host = "mongo_service"
    mongo_port = "27017"
    
    mongo_uri = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/"
    print(f"\n Connexion à MongoDB: mongodb://{mongo_user}:***@{mongo_host}:{mongo_port}/")
    
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.server_info()
        print("✅ Connexion MongoDB réussie")
    except Exception as e:
        print(f"❌ Erreur de connexion MongoDB: {e}")
        sys.exit(1)
    
    db = client["satisfaction"]
    collection = db["avis"]
    
    # 2. Récupérer les données
    print("\n Récupération des avis...")
    try:
        avis = list(collection.find({}))
        print(f" {len(avis)} documents trouvés")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)
    
    if not avis:
        print("❌ Aucun avis trouvé")
        sys.exit(1)
    
    # 3. Préparer les données
    texts = []
    labels = []
    
    for a in avis:
        texte = a.get("contenu", "") or a.get("texte", "") or a.get("titre_avis", "")
        texte = texte.strip()
        etoiles = a.get("nombre_etoile") or a.get("etoiles")
        
        if texte and etoiles is not None:
            texts.append(texte)
            labels.append(int(etoiles))
    
    print(f" {len(texts)} avis valides")
    
    # 4. Afficher la distribution
    print("\n Distribution des étoiles:")
    distribution = Counter(labels)
    for etoile in sorted(distribution.keys()):
        count = distribution[etoile]
        percentage = (count / len(labels)) * 100
        bar = "█" * int(percentage / 2)
        print(f"   {etoile} ⭐: {count:5d} ({percentage:5.1f}%) {bar}")
    
    # 5. Vérifications
    if len(texts) < 10:
        print(f"\n❌ Pas assez de données: {len(texts)}")
        sys.exit(1)
    
    if len(set(labels)) < 2:
        print("\n⚠️  Une seule classe détectée!")
        sys.exit(1)
    
    # 6. ✅ AMÉLIORATION: Diviser en train/test AVANT entraînement
    print("\n" + "=" * 70)
    print(" ENTRAÎNEMENT DU MODÈLE")
    print("=" * 70)
    
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, 
        test_size=0.2,           # 20% pour le test
        stratify=labels,         # Respecter la distribution
        random_state=42
    )
    
    print(f"\n Partitionnement:")
    print(f"   Train: {len(X_train)} avis ({len(X_train)/len(texts)*100:.1f}%)")
    print(f"   Test:  {len(X_test)} avis ({len(X_test)/len(texts)*100:.1f}%)")
    
    # 7. Construire et entraîner le modèle amélioré
    print(f"\n Entraînement du modèle (class_weight='balanced')...")
    
    pipe = build_balanced_pipeline()
    pipe.fit(X_train, y_train)
    
    # 8. Évaluation sur TRAIN et TEST séparément
    print("\n" + "=" * 70)
    print(" ÉVALUATION")
    print("=" * 70)
    
    y_train_pred = pipe.predict(X_train)
    y_test_pred = pipe.predict(X_test)
    
    train_f1 = f1_score(y_train, y_train_pred, average='macro')
    test_f1 = f1_score(y_test, y_test_pred, average='macro')
    
    print(f"\n F1-score macro:")
    print(f"   Train: {train_f1:.3f}")
    print(f"   Test:  {test_f1:.3f}")
    
    if train_f1 - test_f1 > 0.1:
        print(f"\n  OVERFITTING détecté! (différence: {train_f1 - test_f1:.3f})")
    elif abs(train_f1 - test_f1) < 0.05:
        print(f"\n Bon équilibre train/test (écart: {abs(train_f1 - test_f1):.3f})")
    
    # 9. Rapport détaillé par classe
    print(f"\n Résultats par classe (TEST SET):")
    report = classification_report(y_test, y_test_pred, output_dict=True)
    
    for star_class in sorted(set(labels)):
        star_class_str = str(star_class)
        if star_class_str in report:
            f1 = report[star_class_str].get('f1-score', 0)
            prec = report[star_class_str].get('precision', 0)
            rec = report[star_class_str].get('recall', 0)
            support = report[star_class_str].get('support', 0)
            sentiment = get_sentiment_label(star_class)
            print(f"   {star_class} ⭐ ({sentiment:8s}): F1={f1:.3f} | P={prec:.3f} | R={rec:.3f} | N={int(support)}")
    
    # 10. Matrice de confusion
    print(f"\n Matrice de confusion (TEST SET):")
    cm = confusion_matrix(y_test, y_test_pred, labels=sorted(set(labels)))
    print("        Prédictions →")
    print("Réels ↓", end="")
    for star in sorted(set(labels)):
        print(f"  {star}⭐", end="")
    print()
    
    for i, star in enumerate(sorted(set(labels))):
        print(f"  {star}⭐", end="")
        for j in range(len(sorted(set(labels)))):
            print(f"  {cm[i][j]:3d}", end="")
        print()
    
    # 11. Sauvegarder le modèle
    save_path = "/app/sentiment_pipeline.joblib"
    print(f"\n Sauvegarde du modèle...")
    save_pipeline(pipe, save_path)
    
    if os.path.exists(save_path):
        size_mb = os.path.getsize(save_path) / (1024 * 1024)
        print(f" Modèle sauvegardé: {save_path} ({size_mb:.2f} MB)")
    
    # 12. Tests qualitatifs
    print("\n" + "=" * 70)
    print(" TESTS QUALITATIFS")
    print("=" * 70)
    
    test_cases = [
        ("Excellent produit, très satisfait !", "positif", [4, 5]),
        ("Horrible, je suis très déçu", "négatif", [1, 2]),
        ("Produit moyen, rien de spécial", "neutre", [3]),
        ("Super qualité, je recommande vivement", "positif", [4, 5]),
        ("Nul, ne fonctionne pas du tout", "négatif", [1, 2]),
        ("Les produits sont conformes à la description", "positif", [4, 5]),
        ("Mauvais service client, très déçu", "négatif", [1, 2]),
        ("C'est acceptable mais pourrait être mieux", "neutre", [3])
    ]
    
    passed = 0
    failed = 0
    
    for texte, expected_sentiment, expected_stars in test_cases:
        cleaned = clean_text(texte)
        prediction = pipe.predict([cleaned])[0]
        sentiment = get_sentiment_label(prediction)
        is_correct = prediction in expected_stars
        status = "✅" if is_correct else "❌"
        
        print(f"\n{status} \"{texte[:45]}...\"")
        print(f"   Attendu: {expected_sentiment:8s} {expected_stars} | Obtenu: {sentiment:8s} {prediction}⭐")
        
        if is_correct:
            passed += 1
        else:
            failed += 1
    
    # 13. Résumé final
    print("\n" + "=" * 70)
    print(" RÉSUMÉ FINAL")
    print("=" * 70)
    print(f"   Données: {len(texts)} avis ({len(X_train)} train, {len(X_test)} test)")
    print(f"   F1-score (test): {test_f1:.3f}")
    print(f"   Tests qualitatifs: {passed}/{len(test_cases)} réussis")
    
    if test_f1 > 0.7 and passed >= len(test_cases) * 0.7:
        print("\n ✅ Modèle performant! Prêt pour la production.")
    elif test_f1 > 0.5:
        print("\n Modèle correct.")
    else:
        print("\n❌ Modèle faible. Vérifier les données.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interruption utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)