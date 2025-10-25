-- Script SQL : Création et Transformation des données
-- Projet : Satisfaction Client (Supply Chain)

-- 1. Création de la base (RESET)
DROP DATABASE IF EXISTS projet;
CREATE DATABASE projet;
USE projet;

-- 2. Tables principales
CREATE TABLE Societes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Nom_societes VARCHAR(255) NOT NULL,
    domaine VARCHAR(255),
    trustscore DECIMAL(3,2),
    slug VARCHAR(255) UNIQUE
) ENGINE=InnoDB;

CREATE TABLE AvisClients (
    Id_avis INT AUTO_INCREMENT PRIMARY KEY,
    langue VARCHAR(10),
    Nombre_etoile TINYINT CHECK (Nombre_etoile BETWEEN 1 AND 5),
    commentaire TEXT,
    Reponse_entreprise BOOLEAN DEFAULT 0,
    date_avis DATETIME
) ENGINE=InnoDB;

CREATE TABLE Societes_avis (
    id_societes INT,
    Id_avis INT,
    PRIMARY KEY (id_societes, Id_avis),
    FOREIGN KEY (id_societes) REFERENCES Societes(id) ON DELETE CASCADE,
    FOREIGN KEY (Id_avis) REFERENCES AvisClients(Id_avis) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 3. Index utiles
CREATE INDEX idx_avis_date ON AvisClients(date_avis);
CREATE INDEX idx_avis_etoiles ON AvisClients(Nombre_etoile);
CREATE INDEX idx_societes_slug ON Societes(slug);

-- 4. Insertions de la société
INSERT INTO Societes (Nom_societes, domaine, trustscore, slug)
VALUES ('Showroom prive', 'e-commerce', 3.8, 'showroom-prive');

-- 5. Table agrégée : Societes_stats
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

-- 6. Requêtes de vérification
SELECT * FROM Societes LIMIT 5;
SELECT COUNT(*) AS nb_avis FROM AvisClients;
SELECT s.Nom_societes, st.nb_avis, st.note_moyenne, st.pct_excellent
FROM Societes_stats st
JOIN Societes s ON s.id = st.id_societe
ORDER BY st.nb_avis DESC;
