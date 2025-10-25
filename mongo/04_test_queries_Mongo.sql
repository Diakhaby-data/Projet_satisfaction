# 1. 5 premiers avis (aperçu des documents)

db.reviews.find().limit(5);

# 2. Distribution des avis par nombre d’étoiles
db.reviews.aggregate([
  { $group: { _id: "$Nombre_etoile", count: { $sum: 1 } } },
  { $sort: { _id: 1 } }
]);

# 3. Nombre d’avis 5 étoiles (satisfaction maximale)
db.reviews.countDocuments({ "Nombre_etoile": 5 });

# 4. Nombre d’avis par langue
db.reviews.aggregate([
  { $group: { _id: "$langue", total: { $sum: 1 } } },
  { $project: { langue: "$_id", total: 1, _id: 0 } }
]);

# (*) Cette requête permet de valider la répartition par langue
# et de contrôler la normalisation des codes (ex: "fr", "es", "it").

# 5. Index existants (diagnostic performance)
db.reviews.getIndexes();
