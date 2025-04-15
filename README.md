# Call Film

## Quick start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

## Technos

https://developer.themoviedb.org/reference/intro/getting-started

## Cahier des charges

- [x] Une page avec avec tout les films actuellement en salle
- [x] Une page avec la liste des series les plus populaires
- [x] Pourvoir trier par genre
- [x] Faire en sorte que l'API puisse être inaccessible et que le site puisse quand même fonctionner: stocker les données dans le local storage ou dans le serveur.
- [x] Implémentez une suggestion de film ou de série selon des critères choisi par l'utilisateur
- [ ] Séparation du code en trois couches:
  - Application
  - Domaine/Infra (BDD/API)
- [ ] Ajouter un fonctionnalité qui permet à l'utilisateur d'enregistrer un liste de film/série à voir
- [ ] L'utilisateur doit pouvoir ajouter un film ou une série même si la BDD ne répond pas, la liste doit être mise à jour au rétablissement du système
- [ ] Comment gérer la communication avec l' utilisateur