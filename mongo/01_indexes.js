// A exécuter dans mongosh
// Connexion: mongosh "mongodb://dkb:diakhaby@localhost:27017/?authSource=admin"
use projet;

// Indexs utiles
db.reviews.createIndex({ hash: 1 }, { unique: true });
db.reviews.createIndex({ Date_avis: -1 });
db.reviews.createIndex({ langue: 1 });
db.reviews.createIndex({ "Nombre_etoile": 1 });

// Extraits de contrôle
db.reviews.find({}, { langue:1, "Nombre_etoile":1, "Contenu (texte)":1 }).limit(5);
