# Itou - La communauté de l'inclusion

## Poetry

### Lancer le serveur local

#### Configuration environnement

```bash
$ cp env.default.sh env.local.sh
# Préparation de l'environnement local
$ source ./env.local.sh
```

#### Lancement

```bash
$ poetry run python manage.py runserver
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

## Générer les fichiers `requirements`

```bash
poetry run poe export
poetry run poe export_dev
```