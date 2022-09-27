# Itou - La communauté de l'inclusion

## Poetry

### Lancer le serveur local

#### Configuration environnement

```bash
$ cp .env.template .env
```

Installation de Poetry
```bash
$ poetry install
```

#### Lancement

Pour utiliser Poetry avec les commandes du fichier `Makefile`, ajoutez les variables d'environnement :

* `USE_POETRY` à la valeur 1
* `DJANGO_SETTINGS_MODULE` pour activer les settings de prod (`config.settings.base`) ou de dev (`config.settings.dev`)


```bash
$ make server
```


### Ajout de dépendance

Ajout d'une dépendance :

```bash
poetry add django-anymail
```

Ajout d'une dépendance de développement :

```bash
poetry add --group dev poethepoet
```

### Mise à jour des dépendances

```bash
poetry update
poetry lock
```

## Générer les fichiers `requirements`

```bash
poetry run poe export
poetry run poe export_dev
```
