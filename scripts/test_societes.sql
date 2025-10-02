USE projet_satis;

SELECT * FROM societes LIMIT 10;

SELECT COUNT(*) AS total_societes FROM societes;

SELECT * FROM societes WHERE nom_societes LIKE '%Colis%';
