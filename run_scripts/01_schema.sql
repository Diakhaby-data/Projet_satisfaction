-- Création de la base
CREATE DATABASE IF NOT EXISTS projet;
USE projet;

-- Table des sociétés
CREATE TABLE IF NOT EXISTS Societes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Nom_societes VARCHAR(255) NOT NULL,
    Domaine_activite VARCHAR(255)
);

-- Table des avis agrégés
CREATE TABLE IF NOT EXISTS AvisAgreges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    societe_id INT NOT NULL,
    contenu TEXT NOT NULL,
    note INT,
    date_avis DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (societe_id) REFERENCES Societes(id)
);
