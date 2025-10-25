
USE projet;

-- 1) S'assurer que la société existe
INSERT INTO Societes (Nom_societes, domaine, trustscore, slug)
SELECT 'Showroom prive', 'e-commerce', 3.8, 'showroom-prive'
WHERE NOT EXISTS (SELECT 1 FROM Societes WHERE slug='showroom-prive');

SET @id_showroom = (SELECT id FROM Societes WHERE slug='showroom-prive');

-- 2) Lier tous les avis non encore liés
INSERT IGNORE INTO Societes_avis (id_societes, Id_avis)
SELECT @id_showroom, ac.Id_avis
FROM AvisClients ac
LEFT JOIN Societes_avis sa ON sa.Id_avis = ac.Id_avis
WHERE sa.Id_avis IS NULL;

-- 3) Recréer la table d'agrégats
DROP TABLE IF EXISTS Societes_stats;
CREATE TABLE Societes_stats AS
SELECT s.id AS id_societe,
       COUNT(sa.Id_avis) AS nb_avis,
       AVG(ac.Nombre_etoile) AS note_moyenne,
       SUM(ac.Reponse_entreprise) AS nb_reponses,
       100 * SUM(CASE WHEN ac.Nombre_etoile=5 THEN 1 ELSE 0 END) / NULLIF(COUNT(*),0) AS pct_excellent
FROM Societes s
JOIN Societes_avis sa ON s.id = sa.id_societes
JOIN AvisClients ac ON sa.Id_avis = ac.Id_avis
GROUP BY s.id;

-- 4) Vérif rapide
SELECT s.Nom_societes, COUNT(sa.Id_avis) AS nb_avis
FROM Societes s
LEFT JOIN Societes_avis sa ON s.id = sa.id_societes
GROUP BY s.id
ORDER BY nb_avis DESC;
