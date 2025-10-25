USE projet;

# 1. Vérification de l'existence des tables
SHOW TABLES LIKE 'Societes';

# 2. Requêtes de description
SHOW TABLES;
DESCRIBE Societes;
DESCRIBE Societes_avis;
DESCRIBE AvisAgreges;
DESCRIBE AvisClients;
DESCRIBE Societes_stats;

# 3. Vérification cohérence des données après ingestion
SELECT * FROM Societes LIMIT 5;
SELECT * FROM Societes_avis LIMIT 5;
SELECT * FROM AvisAgreges LIMIT 5;

# Liste de 5 sociétés et domaine d’activité associé
SELECT Nom_societes, domaine_activite
FROM Societes
LIMIT 5;

# Liaison par clés des tables et nombre/répartition (%) des avis
SELECT s.Nom_societes,
       COUNT(sa.Id_avis) AS nb_avis,
       ROUND(100 * COUNT(sa.Id_avis) / (SELECT COUNT(*) FROM Societes_avis), 2) AS pct_avis
FROM Societes s
JOIN Societes_avis sa ON s.id = sa.id_societes
GROUP BY s.id;

# 4. Requêtes exploratoires

# a. Statistiques consolidées par société
SELECT * FROM Societes_stats;

# b. Répartition des avis par langue et incidence langue & note
SELECT ac.langue, ac.Nombre_etoile, COUNT(*) AS nb_avis
FROM AvisClients ac
JOIN Societes_avis sa ON ac.Id_avis = sa.Id_avis
JOIN Societes s ON sa.id_societes = s.id
GROUP BY ac.langue, ac.Nombre_etoile
ORDER BY ac.langue, ac.Nombre_etoile;

# c. Répartition avis répondus (%) = mesure de l’engagement des entreprises
SELECT s.Nom_societes,
       ROUND(100 * SUM(ac.Reponse_entreprise) / COUNT(*), 2) AS pct_reponse
FROM Societes s
JOIN Societes_avis sa ON s.id = sa.id_societes
JOIN AvisClients ac ON sa.Id_avis = ac.Id_avis
GROUP BY s.id;

# d. Analyse temporelle des avis (pics / périodes positives ou négatives)
SELECT DATE_FORMAT(ac.date_avis, '%Y-%m') AS mois,
       COUNT(*) AS nb_avis,
       ROUND(AVG(ac.Nombre_etoile),2) AS note_moyenne
FROM AvisClients ac
GROUP BY mois
ORDER BY mois;

# Distribution par langue / étoiles
SELECT langue, Nombre_etoile, COUNT(*) AS nb_avis
FROM AvisClients
GROUP BY langue, Nombre_etoile
ORDER BY langue, Nombre_etoile;

# Tendance mensuelle (volume + moyenne des notes)
SELECT DATE_FORMAT(date_avis, '%Y-%m') AS mois,
       COUNT(*) AS nb_avis,
       AVG(Nombre_etoile) AS note_moy
FROM AvisClients
GROUP BY mois
ORDER BY mois;
