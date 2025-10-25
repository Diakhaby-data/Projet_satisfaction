# Diagramme ER

```mermaid
erDiagram
    Societes ||--o{ Societes_avis : lie
    AvisClients ||--o{ Societes_avis : lie

    Societes {
        int id PK
        varchar Nom_societes
        varchar domaine
        decimal trustscore
        varchar slug
    }

    AvisClients {
        int Id_avis PK
        varchar langue
        tinyint Nombre_etoile
        text commentaire
        boolean Reponse_entreprise
        datetime date_avis
    }

    Societes_avis {
        int id_societes FK
        int Id_avis FK
    }
